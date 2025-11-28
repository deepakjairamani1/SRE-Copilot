import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
from app.clients.prometheus_client import PrometheusClient


async def main():
    client = PrometheusClient("http://localhost:9090")
    
    print("=== HOST METRICS ===")
    result = await client.query_host_metrics()
    
    if "host_metrics" in result:
        for metric_name, metric_data in result["host_metrics"].items():
            print(f"\n{metric_name}:")
            print(f"  Current: {metric_data['current']} {metric_data['unit']}")
            print(f"  Max: {metric_data['max']}")
            print(f"  Min: {metric_data['min']}")
            print(f"  Avg: {metric_data['avg']}")
            print(f"  Status: {metric_data['status']}")
    else:
        print(f"Error: {result}")
    
    print("\n\n=== OTLP METRICS ===")
    result = await client.query_otlp_metrics()
    
    if "otlp_metrics" in result:
        for metric_name, metric_data in result["otlp_metrics"].items():
            print(f"\n{metric_name}:")
            print(f"  Current: {metric_data['current']} {metric_data['unit']}")
            print(f"  Max: {metric_data['max']}")
            print(f"  Min: {metric_data['min']}")
            print(f"  Avg: {metric_data['avg']}")
            print(f"  Status: {metric_data['status']}")
    else:
        print(f"Error: {result}")


if __name__ == "__main__":
    asyncio.run(main())
