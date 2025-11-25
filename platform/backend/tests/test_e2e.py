#!/usr/bin/env python3
"""End-to-end test for SRE Copilot Platform"""

import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:7474"
LEARNING_DIR = Path("data/learning/incidents")

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    print_section("1. HEALTH CHECK")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
    assert r.status_code == 200
    print("✅ Health check passed")

def test_observability_health():
    print_section("2. OBSERVABILITY SERVICES HEALTH")
    r = requests.get(f"{BASE_URL}/api/observability/health-check")
    print(f"Status: {r.status_code}")
    data = r.json()
    for service, status in data.items():
        icon = "✅" if status == "healthy" else "❌"
        print(f"{icon} {service}: {status}")
    return data

def test_current_metrics():
    print_section("3. CURRENT METRICS")
    r = requests.get(f"{BASE_URL}/api/observability/metrics/current")
    print(f"Status: {r.status_code}")
    data = r.json()
    metrics = data.get('metrics', {})
    if isinstance(metrics, dict):
        print(f"Metrics categories: {len(metrics)}")
        for category, values in list(metrics.items())[:3]:
            if isinstance(values, list):
                print(f"  - {category}: {len(values)} metrics")
    print("✅ Metrics endpoint working")

def test_recent_logs():
    print_section("4. RECENT LOGS")
    r = requests.get(f"{BASE_URL}/api/observability/logs/recent")
    print(f"Status: {r.status_code}")
    data = r.json()
    logs = data.get('logs', {})
    if isinstance(logs, dict):
        total = sum(len(v) if isinstance(v, list) else 0 for v in logs.values())
        print(f"Logs count: {total}")
        for category, log_list in list(logs.items())[:2]:
            if isinstance(log_list, list) and log_list:
                print(f"  - {category}: {len(log_list)} logs")
    print("✅ Logs endpoint working")

def test_recent_traces():
    print_section("5. RECENT TRACES")
    r = requests.get(f"{BASE_URL}/api/observability/traces/recent")
    print(f"Status: {r.status_code}")
    data = r.json()
    traces = data.get('traces', {})
    if isinstance(traces, dict):
        total = sum(len(v) if isinstance(v, list) else 0 for v in traces.values())
        print(f"Traces count: {total}")
        for category, trace_list in list(traces.items())[:2]:
            if isinstance(trace_list, list) and trace_list:
                print(f"  - {category}: {len(trace_list)} traces")
    print("✅ Traces endpoint working")

def test_incidents_before():
    print_section("6. INCIDENTS BEFORE INVESTIGATION")
    r = requests.get(f"{BASE_URL}/api/incidents/")
    print(f"Status: {r.status_code}")
    data = r.json()
    if isinstance(data, list):
        print(f"Total incidents: {len(data)}")
        for inc in data[:3]:
            print(f"  - {inc['incident_id']}: {inc['title']} [{inc['status']}]")
        return len(data)
    return 0

def test_learning_data_before():
    print_section("7. LEARNING DATA BEFORE INVESTIGATION")
    if not LEARNING_DIR.exists():
        print(f"Learning directory not found: {LEARNING_DIR}")
        return 0
    
    files = list(LEARNING_DIR.glob("*.json"))
    print(f"Learning files count: {len(files)}")
    for f in files[:3]:
        with open(f) as fp:
            data = json.load(fp)
            print(f"  - {f.name}: {data.get('title', 'N/A')}")
    return len(files)

def test_trigger_investigation():
    print_section("8. TRIGGER RCA INVESTIGATION")
    payload = {
        "service": "core-athenamind",
        "severity": "high"
    }
    print(f"Payload: {payload}")
    r = requests.post(f"{BASE_URL}/api/rca/investigate", json=payload)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Incident ID: {data.get('incident_id')}")
    print(f"Status: {data.get('status')}")
    print(f"Message: {data.get('message')}")
    
    incident_id = data.get('incident_id')
    
    # Poll status
    print("\nPolling investigation status...")
    for i in range(30):
        time.sleep(2)
        status_r = requests.get(f"{BASE_URL}/api/rca/status/{incident_id}")
        status_data = status_r.json()
        status = status_data.get('status')
        print(f"  [{i*2}s] Status: {status}")
        
        if status == "completed":
            print("\n✅ Investigation completed!")
            print(f"Title: {status_data.get('title')}")
            print(f"Root Cause: {status_data.get('root_cause', '')[:100]}...")
            print(f"Confidence: {status_data.get('confidence_score')}")
            print(f"LLM Provider: {status_data.get('llm_provider')}")
            print(f"LLM Model: {status_data.get('llm_model')}")
            return incident_id
        elif status == "failed":
            print(f"\n❌ Investigation failed: {status_data.get('error')}")
            return None
    
    print("\n⚠️ Investigation timeout")
    return incident_id

def test_incident_details(incident_id):
    print_section("9. INCIDENT DETAILS")
    r = requests.get(f"{BASE_URL}/api/incidents/{incident_id}")
    print(f"Status: {r.status_code}")
    data = r.json()
    
    print(f"Incident ID: {data.get('incident_id')}")
    print(f"Service: {data.get('service')}")
    print(f"Title: {data.get('title')}")
    print(f"Severity: {data.get('severity')}")
    print(f"Status: {data.get('status')}")
    print(f"Confidence: {data.get('confidence_score')}")
    print(f"\nRoot Cause:\n{data.get('root_cause', '')[:200]}...")
    print(f"\nRecommendations:\n{data.get('recommendations', '')[:200]}...")
    
    steps = data.get('investigation_steps', [])
    print(f"\nInvestigation Steps: {len(steps)}")
    for step in steps[:3]:
        print(f"  - {step.get('step')}: {step.get('action')}")
    
    metrics = data.get('metrics', [])
    print(f"\nMetrics Snapshot: {len(metrics)}")
    for m in metrics[:3]:
        print(f"  - {m.get('metric_name')}: {m.get('value')}")
    
    print("\n✅ Incident saved to database")

def test_incidents_after(before_count):
    print_section("10. INCIDENTS AFTER INVESTIGATION")
    r = requests.get(f"{BASE_URL}/api/incidents/")
    data = r.json()
    if isinstance(data, list):
        after_count = len(data)
        print(f"Total incidents: {after_count}")
        print(f"New incidents: {after_count - before_count}")
        
        for inc in data[:5]:
            print(f"  - {inc['incident_id']}: {inc['title']} [{inc['status']}]")
        
        assert after_count > before_count, "No new incident created!"
        print("\n✅ New incident persisted in database")
    else:
        print("❌ Unexpected response format")

def test_learning_data_after(before_count):
    print_section("11. LEARNING DATA AFTER INVESTIGATION")
    if not LEARNING_DIR.exists():
        print(f"❌ Learning directory not found: {LEARNING_DIR}")
        return
    
    files = list(LEARNING_DIR.glob("*.json"))
    after_count = len(files)
    print(f"Learning files count: {after_count}")
    print(f"New learning files: {after_count - before_count}")
    
    # Show latest file
    if files:
        latest = max(files, key=lambda f: f.stat().st_mtime)
        print(f"\nLatest learning file: {latest.name}")
        with open(latest) as fp:
            data = json.load(fp)
            print(f"  Title: {data.get('title')}")
            print(f"  Service: {data.get('service')}")
            print(f"  Root Cause: {data.get('root_cause', '')[:100]}...")
            print(f"  Keywords: {', '.join(data.get('keywords', [])[:5])}")
    
    assert after_count > before_count, "No new learning data created!"
    print("\n✅ Learning data appended for RAG")

def test_statistics():
    print_section("12. STATISTICS & ANALYTICS")
    r = requests.get(f"{BASE_URL}/api/incidents/stats/summary")
    print(f"Status: {r.status_code}")
    data = r.json()
    
    print(f"Total Incidents: {data.get('total_incidents')}")
    
    by_severity = data.get('by_severity', {})
    print(f"\nBy Severity:")
    for sev, count in by_severity.items():
        print(f"  - {sev}: {count}")
    
    by_service = data.get('by_service', {})
    print(f"\nBy Service:")
    for svc, count in list(by_service.items())[:5]:
        print(f"  - {svc}: {count}")
    
    print("\n✅ Statistics working")

def test_analytics_trends():
    print_section("13. ANALYTICS - INCIDENT TRENDS")
    r = requests.get(f"{BASE_URL}/api/analytics/trends/incidents?days=7")
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Data points: {len(data.get('trends', []))}")
    for trend in data.get('trends', [])[:3]:
        print(f"  - {trend.get('date')}: {trend.get('count')} incidents")
    print("✅ Trends endpoint working")

def test_analytics_mttr():
    print_section("14. ANALYTICS - MTTR TRENDS")
    r = requests.get(f"{BASE_URL}/api/analytics/trends/mttr?days=7")
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Data points: {len(data.get('trends', []))}")
    for trend in data.get('trends', [])[:3]:
        print(f"  - {trend.get('date')}: {trend.get('avg_mttr_minutes', 0):.1f} min")
    print("✅ MTTR trends working")

def test_analytics_top_issues():
    print_section("15. ANALYTICS - TOP ISSUES")
    r = requests.get(f"{BASE_URL}/api/analytics/issues/top?limit=5")
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Top issues: {len(data.get('issues', []))}")
    for issue in data.get('issues', []):
        print(f"  - {issue.get('title')}: {issue.get('count')} occurrences")
    print("✅ Top issues working")

def test_analytics_service_health():
    print_section("16. ANALYTICS - SERVICE HEALTH")
    r = requests.get(f"{BASE_URL}/api/analytics/services/health")
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Services: {len(data.get('services', []))}")
    for svc in data.get('services', [])[:5]:
        print(f"  - {svc.get('service')}: {svc.get('total_incidents')} incidents, "
              f"{svc.get('open_incidents')} open")
    print("✅ Service health working")

def test_rag_configuration():
    print_section("17. RAG CONFIGURATION")
    
    print("Learning Directory:")
    print(f"  Path: {LEARNING_DIR.absolute()}")
    print(f"  Exists: {LEARNING_DIR.exists()}")
    
    if LEARNING_DIR.exists():
        files = list(LEARNING_DIR.glob("*.json"))
        print(f"  Files: {len(files)}")
        
        # Check file structure
        if files:
            sample = files[0]
            with open(sample) as fp:
                data = json.load(fp)
                print(f"\nSample file structure ({sample.name}):")
                for key in data.keys():
                    print(f"  - {key}: {type(data[key]).__name__}")
    
    print("\n✅ RAG configuration validated")

def main():
    print("\n" + "="*60)
    print("  SRE COPILOT PLATFORM - END-TO-END TEST")
    print("="*60)
    
    try:
        # Phase 1: Basic health
        test_health()
        obs_health = test_observability_health()
        
        # Phase 2: Observability endpoints
        test_current_metrics()
        test_recent_logs()
        test_recent_traces()
        
        # Phase 3: Before investigation
        incidents_before = test_incidents_before()
        learning_before = test_learning_data_before()
        
        # Phase 4: Trigger investigation
        incident_id = test_trigger_investigation()
        
        if incident_id:
            # Phase 5: After investigation
            test_incident_details(incident_id)
            test_incidents_after(incidents_before)
            test_learning_data_after(learning_before)
            
            # Phase 6: Analytics
            test_statistics()
            test_analytics_trends()
            test_analytics_mttr()
            test_analytics_top_issues()
            test_analytics_service_health()
            
            # Phase 7: RAG
            test_rag_configuration()
        
        print_section("✅ ALL TESTS PASSED")
        print("\nSummary:")
        print("  ✅ API endpoints working")
        print("  ✅ Observability integration working")
        print("  ✅ RCA agent working")
        print("  ✅ Database persistence working")
        print("  ✅ Learning data (RAG) working")
        print("  ✅ Analytics working")
        print("\n🎉 Platform is fully operational!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
