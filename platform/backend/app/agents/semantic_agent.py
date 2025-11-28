import json
import boto3
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import asyncio
import os

logger = logging.getLogger(__name__)

class SemanticAgent:
    """Agent for creating and managing incident embeddings for semantic similarity"""
    
    def __init__(self, 
                 aws_region: str = "us-east-1",
                 s3_bucket: str = "sre-copilot-vectors",
                 similarity_threshold: float = 0.75):
        self.aws_region = aws_region
        self.s3_bucket = s3_bucket
        self.similarity_threshold = similarity_threshold
        self.use_s3 = False
        
        # Try to initialize AWS clients
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=aws_region)
            self.s3_client = boto3.client('s3', region_name=aws_region)
            # Test S3 bucket access
            self.s3_client.head_bucket(Bucket=s3_bucket)
            self.use_s3 = True
            logger.info(f"Using S3 bucket: {s3_bucket}")
        except Exception as e:
            logger.warning(f"S3 not available ({e}), using local file storage")
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=aws_region)
            self.use_s3 = False
        
        # Vector storage paths
        self.vectors_path = "incident_vectors/"
        self.local_vectors_path = "data/vectors/"
        
        # Create local directory if using local storage
        if not self.use_s3:
            os.makedirs(self.local_vectors_path, exist_ok=True)
        
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
        """Store incident embedding in S3 or local file"""
        try:
            # Prepare vector data
            vector_data = {
                'incident_id': incident_id,
                'embedding': embedding,
                'metadata': {
                    'service': incident_data.get('service'),
                    'severity': incident_data.get('severity'),
                    'detected_at': incident_data.get('detected_at'),
                    'title': incident_data.get('rca_report', {}).get('executive_summary', {}).get('title'),
                    'primary_cause': incident_data.get('rca_report', {}).get('root_cause', {}).get('primary_cause'),
                    'keywords': incident_data.get('rca_report', {}).get('learning_metadata', {}).get('keywords', [])
                },
                'created_at': datetime.utcnow().isoformat()
            }
            
            if self.use_s3:
                # Store in S3
                key = f"{self.vectors_path}{incident_id}.json"
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=key,
                    Body=json.dumps(vector_data),
                    ContentType='application/json'
                )
                logger.info(f"Stored vector for incident {incident_id} in S3")
            else:
                # Store locally
                filepath = os.path.join(self.local_vectors_path, f"{incident_id}.json")
                with open(filepath, 'w') as f:
                    json.dump(vector_data, f)
                logger.info(f"Stored vector for incident {incident_id} locally")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store vector for {incident_id}: {e}")
            return False
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        # Dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def find_similar_incidents(self, current_embedding: List[float], 
                                   limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar incidents based on embedding similarity"""
        try:
            similar_incidents = []
            
            if self.use_s3:
                # List all vectors in S3
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix=self.vectors_path
                )
                
                if 'Contents' not in response:
                    return []
                
                # Calculate similarities from S3
                for obj in response['Contents']:
                    try:
                        vector_obj = self.s3_client.get_object(
                            Bucket=self.s3_bucket,
                            Key=obj['Key']
                        )
                        vector_data = json.loads(vector_obj['Body'].read())
                        
                        stored_embedding = vector_data['embedding']
                        similarity = self._cosine_similarity(current_embedding, stored_embedding)
                        
                        if similarity >= self.similarity_threshold:
                            similar_incidents.append({
                                'incident_id': vector_data['incident_id'],
                                'similarity_score': float(similarity),
                                'metadata': vector_data['metadata']
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error processing S3 vector {obj['Key']}: {e}")
                        continue
            else:
                # List all local vector files
                if not os.path.exists(self.local_vectors_path):
                    return []
                
                for filename in os.listdir(self.local_vectors_path):
                    if filename.endswith('.json'):
                        try:
                            filepath = os.path.join(self.local_vectors_path, filename)
                            with open(filepath, 'r') as f:
                                vector_data = json.load(f)
                            
                            stored_embedding = vector_data['embedding']
                            similarity = self._cosine_similarity(current_embedding, stored_embedding)
                            
                            if similarity >= self.similarity_threshold:
                                similar_incidents.append({
                                    'incident_id': vector_data['incident_id'],
                                    'similarity_score': float(similarity),
                                    'metadata': vector_data['metadata']
                                })
                                
                        except Exception as e:
                            logger.warning(f"Error processing local vector {filename}: {e}")
                            continue
            
            # Sort by similarity and return top results
            similar_incidents.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_incidents[:limit]
            
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
                'vector_stored': True
            }
            
        except Exception as e:
            logger.error(f"Semantic processing failed for {incident_id}: {e}")
            return {'error': str(e)}

# Pinecone integration placeholder for future use
class PineconeSemanticAgent(SemanticAgent):
    """Extended semantic agent with Pinecone vector database support"""
    
    def __init__(self, pinecone_api_key: str = None, pinecone_environment: str = None, **kwargs):
        super().__init__(**kwargs)
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_environment = pinecone_environment
        # TODO: Initialize Pinecone client when needed
    
    async def store_incident_vector_pinecone(self, incident_id: str, embedding: List[float], 
                                           incident_data: Dict[str, Any]) -> bool:
        """Store incident embedding in Pinecone (future implementation)"""
        # TODO: Implement Pinecone storage
        return await self.store_incident_vector(incident_id, embedding, incident_data)
    
    async def find_similar_incidents_pinecone(self, current_embedding: List[float], 
                                            limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar incidents using Pinecone (future implementation)"""
        # TODO: Implement Pinecone similarity search
        return await self.find_similar_incidents(current_embedding, limit)