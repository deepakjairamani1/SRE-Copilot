import json
import boto3
import chromadb
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import os
from ..context import get_context

logger = logging.getLogger(__name__)

class VectorDBAgent:
    """Agent for managing incident embeddings using ChromaDB vector database"""
    
    def __init__(self, 
                 aws_region: str = None,
                 similarity_threshold: float = None,
                 db_path: str = None):
        ctx = get_context()
        self.aws_region = aws_region or ctx.AWS_REGION
        self.similarity_threshold = similarity_threshold or ctx.SIMILARITY_THRESHOLD
        self.db_path = db_path or ctx.VECTOR_DB_PATH
        
        # Initialize Bedrock client
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime', 
                region_name=self.aws_region,
                aws_access_key_id=ctx.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=ctx.AWS_SECRET_ACCESS_KEY
            )
            logger.info("Bedrock client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
        
        # Initialize ChromaDB (try server first, fallback to local)
        try:
            # Try ChromaDB server first
            chroma_host = ctx.CHROMA_HOST
            chroma_port = ctx.CHROMA_PORT
            
            try:
                self.chroma_client = chromadb.HttpClient(
                    host=chroma_host,
                    port=chroma_port
                )
                # Test connection
                self.chroma_client.heartbeat()
                logger.info(f"ChromaDB server connected at {chroma_host}:{chroma_port}")
            except Exception as server_error:
                logger.warning(f"ChromaDB server not available ({server_error}), using local client")
                # Fallback to local persistent client
                if self.db_path:
                    os.makedirs(self.db_path, exist_ok=True)
                    self.chroma_client = chromadb.PersistentClient(path=self.db_path)
                    logger.info(f"ChromaDB local client initialized at {self.db_path}")
                else:
                    logger.error("VECTOR_DB_PATH not configured, cannot use local ChromaDB")
                    raise ValueError("VECTOR_DB_PATH not configured")
            
            self.collection = self.chroma_client.get_or_create_collection(
                name="incident_embeddings",
                metadata={"description": "SRE incident embeddings for similarity search"}
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def create_incident_embedding(self, incident_data: Dict[str, Any]) -> List[float]:
        """Create embedding for incident using Bedrock Titan"""
        try:
            # Build semantic text from incident
            semantic_text = self._build_semantic_text(incident_data)
            
            # Create embedding using Bedrock Titan
            embedding = await self._get_bedrock_embedding(semantic_text)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to create incident embedding: {e}")
            return []
    
    def _build_semantic_text(self, incident_data: Dict[str, Any]) -> str:
        """Build semantic text representation of incident"""
        components = []
        
        # Service and basic info
        if 'service' in incident_data:
            components.append(f"Service: {incident_data['service']}")
        
        if 'severity' in incident_data:
            components.append(f"Severity: {incident_data['severity']}")
        
        # RCA report components
        rca = incident_data.get('rca_report', {})
        
        # Executive summary
        exec_summary = rca.get('executive_summary', {})
        if exec_summary.get('title'):
            components.append(f"Issue: {exec_summary['title']}")
        if exec_summary.get('impact'):
            components.append(f"Impact: {exec_summary['impact']}")
        
        # Root cause
        root_cause = rca.get('root_cause', {})
        if root_cause.get('primary_cause'):
            components.append(f"Root Cause: {root_cause['primary_cause']}")
        
        # Contributing factors
        if root_cause.get('contributing_factors'):
            factors = ', '.join(root_cause['contributing_factors'])
            components.append(f"Contributing Factors: {factors}")
        
        # Technical details
        tech_details = rca.get('technical_details', {})
        if tech_details.get('affected_components'):
            comps = [c.get('component', '') for c in tech_details['affected_components']]
            components.append(f"Affected Components: {', '.join(comps)}")
        
        # Evidence
        if root_cause.get('evidence'):
            evidence_desc = [e.get('description', '') for e in root_cause['evidence']]
            components.append(f"Evidence: {', '.join(evidence_desc)}")
        
        # Learning keywords
        learning = rca.get('learning_metadata', {})
        if learning.get('keywords'):
            keywords = ', '.join(learning['keywords'])
            components.append(f"Keywords: {keywords}")
        
        return ' | '.join(components)
    
    async def _get_bedrock_embedding(self, text: str) -> List[float]:
        """Get embedding from Bedrock Titan model"""
        try:
            body = json.dumps({
                "inputText": text
            })
            
            response = self.bedrock_client.invoke_model(
                modelId="amazon.titan-embed-text-v1",
                body=body,
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['embedding']
            
        except Exception as e:
            logger.error(f"Bedrock embedding failed: {e}")
            return []
    
    async def store_incident_vector(self, incident_id: str, embedding: List[float], 
                                  incident_data: Dict[str, Any]) -> bool:
        """Store incident embedding in ChromaDB"""
        try:
            # Prepare metadata
            metadata = {
                'service': incident_data.get('service', ''),
                'severity': incident_data.get('severity', ''),
                'detected_at': incident_data.get('detected_at', ''),
                'title': incident_data.get('rca_report', {}).get('executive_summary', {}).get('title', ''),
                'primary_cause': incident_data.get('rca_report', {}).get('root_cause', {}).get('primary_cause', ''),
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Get keywords as a single string for metadata
            keywords = incident_data.get('rca_report', {}).get('learning_metadata', {}).get('keywords', [])
            if keywords:
                metadata['keywords'] = ','.join(keywords)
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[self._build_semantic_text(incident_data)],
                metadatas=[metadata],
                ids=[incident_id]
            )
            
            logger.info(f"Stored vector for incident {incident_id} in ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store vector for {incident_id}: {e}")
            return False
    
    async def find_similar_incidents(self, current_embedding: List[float], 
                                   limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar incidents using ChromaDB similarity search"""
        try:
            # Check collection count first
            total_count = self.collection.count()
            logger.info(f"ChromaDB collection has {total_count} stored incidents")
            
            if total_count == 0:
                logger.info("No incidents stored in ChromaDB yet")
                return []
            
            # Query ChromaDB for similar vectors
            results = self.collection.query(
                query_embeddings=[current_embedding],
                n_results=min(limit, total_count),
                include=['metadatas', 'distances', 'documents']
            )
            
            similar_incidents = []
            
            if results['ids'] and results['ids'][0]:
                logger.info(f"ChromaDB returned {len(results['ids'][0])} results")
                logger.info(f"Raw ChromaDB results: ids={results['ids'][0]}, distances={results['distances'][0] if results['distances'] else 'None'}")
                
                for i, incident_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 1000.0
                    # ChromaDB returns squared Euclidean distance, convert to similarity score
                    # Lower distance = higher similarity, normalize to 0-1 range
                    # Use exponential decay: similarity = exp(-distance/scale)
                    import math
                    similarity_score = math.exp(-distance / 100.0)  # Scale factor of 100
                    
                    logger.info(f"Incident {incident_id}: distance={distance:.4f}, similarity={similarity_score:.4f}, threshold={self.similarity_threshold}")
                    
                    # Only include if above threshold
                    if similarity_score >= self.similarity_threshold:
                        metadata = results['metadatas'][0][i]
                        
                        # Parse keywords back to list
                        keywords = []
                        if metadata.get('keywords'):
                            keywords = metadata['keywords'].split(',')
                        
                        similar_incidents.append({
                            'incident_id': incident_id,
                            'similarity_score': float(similarity_score),
                            'metadata': {
                                'service': metadata.get('service'),
                                'severity': metadata.get('severity'),
                                'detected_at': metadata.get('detected_at'),
                                'title': metadata.get('title'),
                                'primary_cause': metadata.get('primary_cause'),
                                'keywords': keywords
                            }
                        })
                    else:
                        logger.info(f"Incident {incident_id} below threshold: {similarity_score:.4f} < {self.similarity_threshold}")
            else:
                logger.warning(f"ChromaDB returned empty results: ids={results.get('ids')}, distances={results.get('distances')}")
                logger.warning(f"Full ChromaDB response: {results}")
            
            # Sort by similarity score (highest first)
            similar_incidents.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"Found {len(similar_incidents)} similar incidents above {self.similarity_threshold} threshold (out of {total_count} total)")
            return similar_incidents
            
        except Exception as e:
            logger.error(f"Failed to find similar incidents: {e}")
            return []
    
    async def get_learning_context(self, similar_incidents: List[Dict[str, Any]]) -> str:
        """Build learning context from similar incidents"""
        if not similar_incidents:
            return "No similar past incidents found in knowledge base."
        
        context_parts = ["=== SIMILAR PAST INCIDENTS ==="]
        
        for i, incident in enumerate(similar_incidents, 1):
            metadata = incident['metadata']
            similarity = incident['similarity_score'] * 100
            
            context_parts.append(f"\n{i}. Incident {incident['incident_id']} (Similarity: {similarity:.1f}%)")
            context_parts.append(f"   Service: {metadata.get('service', 'Unknown')}")
            context_parts.append(f"   Severity: {metadata.get('severity', 'Unknown')}")
            context_parts.append(f"   Issue: {metadata.get('title', 'No title')}")
            context_parts.append(f"   Root Cause: {metadata.get('primary_cause', 'Unknown')}")
            
            if metadata.get('keywords'):
                context_parts.append(f"   Keywords: {', '.join(metadata['keywords'])}")
        
        context_parts.append(f"\nLearn from similar past incidents - if a past fix worked, recommend it.")
        
        return '\n'.join(context_parts)
    
    async def process_incident_semantics(self, incident_id: str, 
                                       incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete semantic processing for an incident"""
        try:
            # Create embedding using Bedrock Titan
            embedding = await self.create_incident_embedding(incident_data)
            
            if not embedding:
                return {'error': 'Failed to create embedding'}
            
            # Find similar incidents
            similar_incidents = await self.find_similar_incidents(embedding)
            
            # Store current incident vector
            await self.store_incident_vector(incident_id, embedding, incident_data)
            
            # Build learning context
            learning_context = await self.get_learning_context(similar_incidents)
            
            return {
                'embedding_created': True,
                'similar_incidents': similar_incidents,
                'learning_context': learning_context,
                'vector_stored': True,
                'vector_db': 'chromadb'
            }
            
        except Exception as e:
            logger.error(f"Semantic processing failed for {incident_id}: {e}")
            return {'error': str(e)}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        try:
            count = self.collection.count()
            return {
                'total_incidents': count,
                'collection_name': 'incident_embeddings',
                'database_type': 'chromadb'
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'error': str(e)}