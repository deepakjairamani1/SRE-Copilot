#!/usr/bin/env python3
"""Debug script to test vector database functionality"""

import asyncio
import aiohttp
import json

async def test_vector_db():
    """Test vector database endpoints to identify issues"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing Vector Database...")
        
        # Test 1: Health check
        print("\n1. Health Check:")
        try:
            async with session.get(f"{base_url}/api/vector-db/health") as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Data: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
        
        # Test 2: Inspect current embeddings
        print("\n2. Inspect Stored Embeddings:")
        try:
            async with session.get(f"{base_url}/api/vector-db/inspect-embeddings") as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                if data.get('success'):
                    incidents = data['data']['incidents']
                    print(f"   Total incidents: {len(incidents)}")
                    for inc in incidents[:3]:  # Show first 3
                        print(f"   - {inc['incident_id']}: {inc['semantic_text'][:100]}...")
                else:
                    print(f"   ❌ Failed: {data}")
        except Exception as e:
            print(f"   ❌ Inspect failed: {e}")
        
        # Test 3: Test similarity with detailed analysis
        print("\n3. Test Similarity (Detailed):")
        try:
            async with session.post(f"{base_url}/api/vector-db/test-similarity-detailed") as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                if data.get('success'):
                    result = data['data']
                    print(f"   Semantic Text 1: {result['semantic_text_1']}")
                    print(f"   Semantic Text 2: {result['semantic_text_2']}")
                    print(f"   Manual Similarity: {result['manual_similarity_score']:.4f}")
                    print(f"   Threshold: {result['similarity_threshold']}")
                    print(f"   Above Threshold: {result['above_threshold']}")
                    print(f"   ChromaDB Results: {len(result['chromadb_results'])}")
                else:
                    print(f"   ❌ Failed: {data}")
        except Exception as e:
            print(f"   ❌ Similarity test failed: {e}")
        
        # Test 4: Test against all stored incidents
        print("\n4. Test All Similarities:")
        try:
            async with session.post(f"{base_url}/api/vector-db/test-all-similarities") as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                if data.get('success'):
                    result = data['data']
                    print(f"   Total stored: {result['total_stored_incidents']}")
                    print(f"   Max similarity: {result['max_similarity']:.4f}")
                    print(f"   Above threshold: {result['above_threshold_count']}")
                    print(f"   Threshold: {result['similarity_threshold']}")
                    
                    # Show top 3 similarities
                    for sim in result['similarities'][:3]:
                        print(f"   - {sim['incident_id']}: {sim['similarity_score']:.4f} ({'✓' if sim['above_threshold'] else '✗'})")
                else:
                    print(f"   ❌ Failed: {data}")
        except Exception as e:
            print(f"   ❌ All similarities test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_vector_db())