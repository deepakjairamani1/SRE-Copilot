import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
from datetime import datetime
from app.agents.rca_agent import RCAAgent


async def main():
    print("=" * 60)
    print("RCA AGENT TEST")
    print("=" * 60)
    
    # Create agent with localhost URLs (for testing outside Docker)
    from app.clients.prometheus_client import PrometheusClient
    from app.clients.loki_client import LokiClient
    from app.clients.jaeger_client import JaegerClient
    
    agent = RCAAgent()
    agent.prometheus_client = PrometheusClient("http://localhost:9090")
    agent.loki_client = LokiClient("http://localhost:3100")
    agent.jaeger_client = JaegerClient("http://localhost:16686")
    
    # Test incident - NO TITLE, let LLM determine the issue
    incident_data = {
        "service": "core-athenamind",
        "detected_at": datetime.utcnow().isoformat()
    }
    
    print(f"\n🔍 Starting investigation")
    print(f"Service: {incident_data['service']}")
    print(f"Time: {incident_data['detected_at']}")
    print(f"Alert: Anomaly detected - analyzing observability data...\n")
    
    # Run investigation
    result = await agent.investigate("INC-TEST-001", incident_data)
    
    # Display results
    print("\n" + "=" * 60)
    print("INVESTIGATION STEPS")
    print("=" * 60)
    
    for step in result.get('investigation_steps', []):
        icon = {
            'plan': '📋',
            'act': '🔍',
            'check': '✓',
            'adapt': '🔄'
        }.get(step['step'], '•')
        
        print(f"{icon} [{step['step'].upper()}] {step['message']}")
    
    print("\n" + "=" * 60)
    print("INVESTIGATION SUMMARY")
    print("=" * 60)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✓ Investigation completed successfully")
        print(f"Duration: {result['duration_seconds']}s")
        print(f"Cost: ${result['cost_usd']}")
        
        rca = result['rca_report']
        
        print("\n--- EXECUTIVE SUMMARY ---")
        exec_summary = rca.get('executive_summary', {})
        print(f"Title: {exec_summary.get('title', 'N/A')}")
        print(f"Severity: {exec_summary.get('severity', 'N/A')}")
        print(f"Impact: {exec_summary.get('impact', 'N/A')}")
        
        print("\n--- ROOT CAUSE ---")
        root_cause = rca.get('root_cause', {})
        print(f"Primary Cause: {root_cause.get('primary_cause', 'N/A')}")
        print(f"Confidence: {root_cause.get('confidence_score', 0):.2f}")
        
        if root_cause.get('similar_to_past_incident'):
            print(f"Similar to: {root_cause['similar_to_past_incident']}")
        
        evidence = root_cause.get('evidence', [])
        if evidence:
            print(f"\nEvidence ({len(evidence)} items):")
            for ev in evidence[:3]:
                print(f"  • [{ev.get('type', 'unknown')}] {ev.get('description', 'N/A')}: {ev.get('value', 'N/A')}")
        
        print("\n--- REMEDIATION ---")
        remediation = rca.get('remediation', {})
        immediate = remediation.get('immediate_actions', [])
        
        if immediate:
            print(f"Immediate Actions ({len(immediate)}):")
            for action in immediate[:3]:
                print(f"  • {action.get('action', 'N/A')}")
                if action.get('command'):
                    print(f"    Command: {action['command']}")
                if action.get('estimated_time'):
                    print(f"    Time: {action['estimated_time']}")
        
        print("\n--- CONFIDENCE ---")
        confidence = rca.get('confidence', {})
        print(f"Overall Score: {confidence.get('overall_score', 0):.2f}")
        print(f"Recommendation: {confidence.get('recommendation', 'N/A')}")
        
        uncertainties = confidence.get('uncertainties', [])
        if uncertainties:
            print(f"\nUncertainties:")
            for unc in uncertainties:
                print(f"  • {unc}")
    
    print("\n" + "=" * 60)
    print("FULL RCA REPORT (JSON)")
    print("=" * 60)
    print(json.dumps(result, indent=2)[:2000] + "...")


if __name__ == "__main__":
    asyncio.run(main())
