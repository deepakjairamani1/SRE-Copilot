import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import json
from app.clients.jaeger_client import JaegerClient


async def main():
    client = JaegerClient("http://localhost:16686")
    
    print("=== QUERYING TRACES ===")
    result = await client.query_traces(time_range="60m", limit=50)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"\n--- TRACE SUMMARY ---")
    summary = result["trace_summary"]
    print(f"Total traces: {summary['total_traces']}")
    print(f"Slow traces: {summary['slow_trace_count']}")
    print(f"Error traces: {summary['error_trace_count']}")
    print(f"P50 latency: {summary['p50_latency_ms']:.2f}ms")
    print(f"P95 latency: {summary['p95_latency_ms']:.2f}ms")
    print(f"P99 latency: {summary['p99_latency_ms']:.2f}ms")
    print(f"Avg spans/trace: {summary['avg_spans_per_trace']:.1f}")
    
    print(f"\n--- PATTERNS ---")
    patterns = result["patterns"]
    print(f"Slow operation: {patterns['slow_operation']}")
    print(f"Error operation: {patterns['error_operation']}")
    print(f"Bottleneck service: {patterns['bottleneck_service']}")
    
    print(f"\n--- SLOW TRACES (Top 3) ---")
    for trace in result["traces"]["slow_traces"][:3]:
        print(f"\nTrace ID: {trace['trace_id']}")
        print(f"  Duration: {trace['duration_ms']:.2f}ms")
        print(f"  Operation: {trace['root_operation']}")
        print(f"  Services: {', '.join(trace['services'])}")
        if trace.get("slowest_span"):
            print(f"  Slowest span: {trace['slowest_span']['operation']} ({trace['slowest_span']['duration_ms']:.2f}ms)")
    
    print(f"\n--- ERROR TRACES ---")
    for trace in result["traces"]["error_traces"][:3]:
        print(f"\nTrace ID: {trace['trace_id']}")
        print(f"  Duration: {trace['duration_ms']:.2f}ms")
        print(f"  Operation: {trace['root_operation']}")
        print(f"  Error: {trace.get('error_message', 'Unknown error')}")
    
    print(f"\n\n=== SLOW OPERATIONS ===")
    slow_ops = await client.find_slow_operations()
    for op in slow_ops[:5]:
        print(f"\n{op['operation']}")
        print(f"  Avg: {op['avg_duration_ms']:.2f}ms")
        print(f"  P95: {op['p95_duration_ms']:.2f}ms")
        print(f"  Count: {op['count']}")


if __name__ == "__main__":
    asyncio.run(main())
