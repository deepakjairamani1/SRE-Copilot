import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.clients.prometheus_client import PrometheusClient

async def main():
    client = PrometheusClient("http://localhost:9090")
    
    print("Testing Prometheus Client...")
    print("=" * 60)
    
    # Test host metrics
    print("\n1. Testing host metrics...")
    host_metrics = await client.query_host_metrics()
    if "error" in host_metrics:
        print(f"❌ Error: {host_metrics['error']}")
    else:
        print(f"✓ Got host metrics")
        if "host_metrics" in host_metrics:
            for metric_name, metric_data in host_metrics["host_metrics"].items():
                print(f"  {metric_name}: current={metric_data.get('current')}, status={metric_data.get('status')}")
    
    # Test OTLP metrics
    print("\n2. Testing OTLP metrics...")
    otlp_metrics = await client.query_otlp_metrics()
    if "error" in otlp_metrics:
        print(f"❌ Error: {otlp_metrics['error']}")
    else:
        print(f"✓ Got OTLP metrics")
        if "otlp_metrics" in otlp_metrics:
            for metric_name, metric_data in otlp_metrics["otlp_metrics"].items():
                print(f"  {metric_name}: current={metric_data.get('current')}, status={metric_data.get('status')}")
    
    # Test combined
    print("\n3. Testing combined metrics...")
    all_metrics = await client.get_critical_metrics()
    print(f"Overall health: {all_metrics.get('overall_health')}")

if __name__ == "__main__":
    asyncio.run(main())
