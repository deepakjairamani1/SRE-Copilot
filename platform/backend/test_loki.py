import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
from app.clients.loki_client import LokiClient


async def main():
    client = LokiClient("http://localhost:3100")
    
    print("=== QUERYING ALL LOGS ===")
    result = await client.query_logs(time_range="5m", limit=1000)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"\n--- LOG SUMMARY ---")
    summary = result["log_summary"]
    print(f"Total logs: {summary['total_logs']}")
    print(f"Errors: {summary['error_count']}")
    print(f"Critical: {summary['critical_count']}")
    print(f"Warnings: {summary['warning_count']}")
    
    if summary["most_common_errors"]:
        print(f"\nMost common errors:")
        for err in summary["most_common_errors"]:
            print(f"  - {err['message'][:80]}... (count: {err['count']})")
    
    print(f"\n--- ERROR LOGS ---")
    if result["logs"]["error_logs"]:
        for log in result["logs"]["error_logs"][:5]:
            print(f"\n[{log['timestamp']}] {log['level']}")
            print(f"  Message: {log['message'][:100]}")
            if log['trace_id']:
                print(f"  Trace ID: {log['trace_id']}")
            if log['source']:
                print(f"  Source: {log['source']}")
    else:
        print("  No error logs found")
    
    print(f"\n--- WARNING LOGS (Top 3) ---")
    for log in result["logs"]["warning_logs"][:3]:
        print(f"\n[{log['timestamp']}] {log['level']}")
        print(f"  Message: {log['message'][:100]}")
        if 'frequency' in log:
            print(f"  Frequency: {log['frequency']} times")
    
    print(f"\n--- INFO LOGS (Recent 3) ---")
    for log in result["logs"]["info_logs"][:3]:
        print(f"\n[{log['timestamp']}] {log['level']}")
        print(f"  Message: {log['message'][:100]}")
        if log['source']:
            print(f"  Source: {log['source']}")
    
    print(f"\n--- CRITICAL LOGS ---")
    if result["logs"]["critical_logs"]:
        for log in result["logs"]["critical_logs"]:
            print(f"\n[{log['timestamp']}] {log['level']}")
            print(f"  Message: {log['message'][:100]}")
    else:
        print("  No critical logs found")
    
    print(f"\n--- PATTERNS DETECTED ---")
    patterns = result["patterns"]
    print(f"Spike detected: {patterns['spike_detected']}")
    print(f"Repeated errors: {len(patterns['repeated_errors'])}")
    for err in patterns["repeated_errors"][:3]:
        print(f"  - {err['message'][:60]}... ({err['count']} times, severity: {err['severity']})")
    
    print(f"\n\n=== ERROR LOGS ONLY (Quick Query) ===")
    errors = await client.query_error_logs_only()
    print(f"Total errors: {errors.get('total_errors', 0)}")
    print(f"Error logs: {len(errors.get('error_logs', []))}")
    print(f"Critical logs: {len(errors.get('critical_logs', []))}")


if __name__ == "__main__":
    asyncio.run(main())
