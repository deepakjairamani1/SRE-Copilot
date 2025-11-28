#!/usr/bin/env python3
"""
Test semantic agent functionality
"""
import asyncio
import json
from app.agents.semantic_agent import SemanticAgent

async def test_semantic_agent():
    print("🧠 Testing Semantic Agent...")
    
    # Mock incident data
    incident_data = {
        'service': 'test-service',
        'severity': 'high',
        'detected_at': '2024-01-15T10:30:00Z',
        'rca_report': {
            'executive_summary': {
                'title': 'Database Connection Pool Exhaustion',
                'impact': 'Service unavailable due to connection timeouts'
            },
            'root_cause': {
                'primary_cause': 'Connection pool reached maximum capacity',
                'contributing_factors': ['High traffic', 'Slow queries'],
                'evidence': [
                    {'type': 'metric', 'description': 'Connection pool usage', 'value': '100%'}
                ]
            },
            'technical_details': {
                'affected_components': [
                    {'component': 'database', 'status': 'degraded'}
                ]
            },
            'learning_metadata': {
                'keywords': ['database', 'connection-pool', 'timeout', 'high-traffic']
            }
        }
    }
    
    try:
        agent = SemanticAgent()
        
        # Test embedding creation
        print("1. Creating incident embedding...")
        embedding = await agent.create_incident_embedding(incident_data)
        print(f"   ✓ Embedding created: {len(embedding)} dimensions")
        
        # Test semantic text building
        print("2. Building semantic text...")
        semantic_text = agent._build_semantic_text(incident_data)
        print(f"   ✓ Semantic text: {semantic_text[:100]}...")
        
        # Test full semantic processing
        print("3. Processing incident semantics...")
        result = await agent.process_incident_semantics("TEST-001", incident_data)
        
        if 'error' in result:
            print(f"   ✗ Error: {result['error']}")
        else:
            print(f"   ✓ Embedding created: {result.get('embedding_created', False)}")
            print(f"   ✓ Similar incidents found: {len(result.get('similar_incidents', []))}")
            print(f"   ✓ Vector stored: {result.get('vector_stored', False)}")
        
        print("\n🎉 Semantic agent test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_semantic_agent())