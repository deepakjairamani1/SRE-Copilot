import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import asyncio
from app.clients.prometheus_client import PrometheusClient


@pytest.mark.asyncio
async def test_host_metrics():
    """Test querying host metrics"""
    client = PrometheusClient("http://localhost:9090")
    result = await client.query_host_metrics()
    
    print("\n=== HOST METRICS ===")
    print(f"Overall Status: {result.get('error', 'OK')}")
    
    if "host_metrics" in result:
        for metric_name, metric_data in result["host_metrics"].items():
            print(f"\n{metric_name}:")
            print(f"  Current: {metric_data['current']} {metric_data['unit']}")
            print(f"  Max: {metric_data['max']}")
            print(f"  Min: {metric_data['min']}")
            print(f"  Avg: {metric_data['avg']}")
            print(f"  Status: {metric_data['status']}")
    
    assert "query_timestamp" in result


@pytest.mark.asyncio
async def test_otlp_metrics():
    """Test querying OTLP application metrics"""
    client = PrometheusClient("http://localhost:9090")
    result = await client.query_otlp_metrics()
    
    print("\n=== OTLP METRICS ===")
    print(f"Overall Status: {result.get('error', 'OK')}")
    
    if "otlp_metrics" in result:
        for metric_name, metric_data in result["otlp_metrics"].items():
            print(f"\n{metric_name}:")
            print(f"  Current: {metric_data['current']} {metric_data['unit']}")
            print(f"  Max: {metric_data['max']}")
            print(f"  Min: {metric_data['min']}")
            print(f"  Avg: {metric_data['avg']}")
            print(f"  Status: {metric_data['status']}")
    
    assert "query_timestamp" in result


@pytest.mark.asyncio
async def test_critical_metrics():
    """Test combined critical metrics with health status"""
    client = PrometheusClient("http://localhost:9090")
    result = await client.get_critical_metrics()
    
    print("\n=== CRITICAL METRICS (COMBINED) ===")
    print(f"Overall Health: {result.get('overall_health', 'unknown')}")
    print(f"Timestamp: {result.get('query_timestamp')}")
    
    if "host_metrics" in result:
        print(f"\nHost Metrics: {len(result['host_metrics'])} metrics")
    
    if "otlp_metrics" in result:
        print(f"OTLP Metrics: {len(result['otlp_metrics'])} metrics")
    
    assert "overall_health" in result
    assert result["overall_health"] in ["healthy", "degraded", "critical", "unknown"]


@pytest.mark.asyncio
async def test_cache():
    """Test that caching works"""
    client = PrometheusClient("http://localhost:9090")
    
    # First call
    result1 = await client.query_host_metrics()
    
    # Second call (should be cached)
    result2 = await client.query_host_metrics()
    
    print("\n=== CACHE TEST ===")
    print(f"First call timestamp: {result1.get('query_timestamp')}")
    print(f"Second call timestamp: {result2.get('query_timestamp')}")
    print(f"Timestamps match (cached): {result1.get('query_timestamp') == result2.get('query_timestamp')}")
    
    assert result1.get('query_timestamp') == result2.get('query_timestamp')


if __name__ == "__main__":
    # Run tests directly
    print("Running Prometheus Client Tests...\n")
    
    asyncio.run(test_host_metrics())
    asyncio.run(test_otlp_metrics())
    asyncio.run(test_critical_metrics())
    asyncio.run(test_cache())
    
    print("\n✅ All tests completed!")
