from fastapi import APIRouter, HTTPException
from app.agents.vector_db_agent import VectorDBAgent
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/vector-db", tags=["vector-db"])

@router.get("/stats")
async def get_vector_db_stats():
    """Get vector database statistics"""
    try:
        agent = VectorDBAgent()
        stats = agent.get_collection_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get vector DB stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def check_vector_db_health():
    """Check if vector database is accessible"""
    try:
        agent = VectorDBAgent()
        
        # Test basic operations
        collection_name = agent.collection.name
        count = agent.collection.count()
        
        # Test heartbeat if available
        heartbeat_ok = True
        try:
            if hasattr(agent.chroma_client, 'heartbeat'):
                agent.chroma_client.heartbeat()
        except:
            heartbeat_ok = False
        
        return {
            "success": True,
            "data": {
                "collection_name": collection_name,
                "incident_count": count,
                "heartbeat_ok": heartbeat_ok,
                "client_type": type(agent.chroma_client).__name__
            }
        }
    except Exception as e:
        logger.error(f"Vector DB health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-embedding")
async def test_embedding():
    """Test embedding creation"""
    try:
        agent = VectorDBAgent()
        
        # Test incident data
        test_data = {
            'service': 'test-service',
            'severity': 'high',
            'rca_report': {
                'executive_summary': {
                    'title': 'Test Database Connection Issue',
                    'impact': 'Service degradation'
                },
                'root_cause': {
                    'primary_cause': 'Connection pool exhaustion'
                }
            }
        }
        
        embedding = await agent.create_incident_embedding(test_data)
        
        return {
            "success": True,
            "data": {
                "embedding_dimensions": len(embedding),
                "embedding_created": len(embedding) > 0,
                "sample_values": embedding[:5] if embedding else []
            }
        }
    except Exception as e:
        logger.error(f"Failed to test embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug")
async def debug_vector_db():
    """Debug vector database state"""
    try:
        agent = VectorDBAgent()
        
        # Get collection stats
        stats = agent.get_collection_stats()
        
        # Get all stored incidents
        all_results = agent.collection.get(
            include=['metadatas', 'documents']
        )
        
        incidents = []
        if all_results['ids']:
            for i, incident_id in enumerate(all_results['ids']):
                incidents.append({
                    'id': incident_id,
                    'metadata': all_results['metadatas'][i] if all_results['metadatas'] else {},
                    'document': all_results['documents'][i] if all_results['documents'] else ''
                })
        
        return {
            "success": True,
            "data": {
                "stats": stats,
                "stored_incidents": incidents,
                "similarity_threshold": agent.similarity_threshold,
                "chroma_host": agent.chroma_client._host if hasattr(agent.chroma_client, '_host') else 'local'
            }
        }
    except Exception as e:
        logger.error(f"Failed to debug vector DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inspect-embeddings")
async def inspect_embeddings():
    """Inspect stored embeddings and their semantic text"""
    try:
        agent = VectorDBAgent()
        
        # Get all stored incidents with embeddings
        all_results = agent.collection.get(
            include=['metadatas', 'documents']
        )
        
        incidents = []
        if all_results['ids']:
            for i, incident_id in enumerate(all_results['ids']):
                incidents.append({
                    'incident_id': incident_id,
                    'semantic_text': all_results['documents'][i] if all_results['documents'] else '',
                    'metadata': all_results['metadatas'][i] if all_results['metadatas'] else {}
                })
        
        return {
            "success": True,
            "data": {
                "total_incidents": len(incidents),
                "incidents": incidents,
                "similarity_threshold": agent.similarity_threshold
            }
        }
    except Exception as e:
        logger.error(f"Failed to inspect embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-similarity-detailed")
async def test_similarity_detailed():
    """Test similarity with detailed analysis"""
    try:
        agent = VectorDBAgent()
        
        # Create two similar incidents
        incident_1 = {
            'service': 'core-athenamind',
            'severity': 'high',
            'rca_report': {
                'executive_summary': {
                    'title': 'Database Connection Timeout',
                    'impact': 'Service unavailable'
                },
                'root_cause': {
                    'primary_cause': 'Database connection pool exhausted'
                },
                'learning_metadata': {
                    'keywords': ['database', 'timeout', 'connection']
                }
            }
        }
        
        incident_2 = {
            'service': 'core-athenamind', 
            'severity': 'critical',
            'rca_report': {
                'executive_summary': {
                    'title': 'Database Timeout Error',
                    'impact': 'Service degraded'
                },
                'root_cause': {
                    'primary_cause': 'Connection pool timeout'
                },
                'learning_metadata': {
                    'keywords': ['database', 'timeout', 'pool']
                }
            }
        }
        
        # Generate semantic text and embeddings
        semantic_1 = agent._build_semantic_text(incident_1)
        semantic_2 = agent._build_semantic_text(incident_2)
        
        embedding_1 = await agent.create_incident_embedding(incident_1)
        embedding_2 = await agent.create_incident_embedding(incident_2)
        
        # Calculate manual cosine similarity
        similarity_score = 0.0
        if embedding_1 and embedding_2:
            import math
            dot_product = sum(a * b for a, b in zip(embedding_1, embedding_2))
            magnitude_1 = math.sqrt(sum(a * a for a in embedding_1))
            magnitude_2 = math.sqrt(sum(a * a for a in embedding_2))
            if magnitude_1 > 0 and magnitude_2 > 0:
                similarity_score = dot_product / (magnitude_1 * magnitude_2)
        
        # Store first incident and search with second
        if embedding_1:
            await agent.store_incident_vector('test-similar-1', embedding_1, incident_1)
        
        # Search for similar incidents (should find the one we just stored)
        similar_incidents = await agent.find_similar_incidents(embedding_2, limit=10) if embedding_2 else []
        
        return {
            "success": True,
            "data": {
                "semantic_text_1": semantic_1,
                "semantic_text_2": semantic_2,
                "embedding_dimensions": len(embedding_1) if embedding_1 else 0,
                "manual_similarity_score": float(similarity_score),
                "similarity_threshold": agent.similarity_threshold,
                "above_threshold": similarity_score >= agent.similarity_threshold,
                "chromadb_results": similar_incidents,
                "embedding_sample_1": embedding_1[:5] if embedding_1 else [],
                "embedding_sample_2": embedding_2[:5] if embedding_2 else []
            }
        }
    except Exception as e:
        logger.error(f"Failed detailed similarity test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-all-similarities")
async def test_all_similarities():
    """Test similarity scores against all stored incidents"""
    try:
        agent = VectorDBAgent()
        
        # Create test incident
        test_incident = {
            'service': 'core-athenamind',
            'severity': 'high',
            'rca_report': {
                'executive_summary': {
                    'title': 'Service Performance Issue',
                    'impact': 'Slow response'
                },
                'root_cause': {
                    'primary_cause': 'High CPU usage'
                }
            }
        }
        
        test_embedding = await agent.create_incident_embedding(test_incident)
        if not test_embedding:
            return {"success": False, "error": "Failed to create test embedding"}
        
        # Get all stored incidents
        all_results = agent.collection.get(
            include=['metadatas', 'documents', 'embeddings']
        )
        
        similarities = []
        if all_results['ids'] and all_results['embeddings']:
            import math
            
            for i, incident_id in enumerate(all_results['ids']):
                stored_embedding = all_results['embeddings'][i]
                
                # Calculate cosine similarity
                if stored_embedding:
                    dot_product = sum(a * b for a, b in zip(test_embedding, stored_embedding))
                    mag_test = math.sqrt(sum(a * a for a in test_embedding))
                    mag_stored = math.sqrt(sum(a * a for a in stored_embedding))
                    
                    similarity = 0.0
                    if mag_test > 0 and mag_stored > 0:
                        similarity = dot_product / (mag_test * mag_stored)
                    
                    similarities.append({
                        'incident_id': incident_id,
                        'similarity_score': float(similarity),
                        'above_threshold': similarity >= agent.similarity_threshold,
                        'semantic_text': all_results['documents'][i] if all_results['documents'] else '',
                        'metadata': all_results['metadatas'][i] if all_results['metadatas'] else {}
                    })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return {
            "success": True,
            "data": {
                "test_semantic_text": agent._build_semantic_text(test_incident),
                "total_stored_incidents": len(similarities),
                "similarity_threshold": agent.similarity_threshold,
                "similarities": similarities,
                "max_similarity": similarities[0]['similarity_score'] if similarities else 0.0,
                "above_threshold_count": sum(1 for s in similarities if s['above_threshold'])
            }
        }
    except Exception as e:
        logger.error(f"Failed to test all similarities: {e}")
        raise HTTPException(status_code=500, detail=str(e))