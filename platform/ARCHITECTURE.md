# SRE Copilot Platform - Architecture Overview

## End-to-End Flow

```
User Request → API → RCA Agent → Observability Stack → LLM Analysis → Database + RAG Storage
```

---

## 1. API Layer (FastAPI)

**Entry Point**: `app/main.py`

### Routers

| Router | Endpoints | Purpose |
|--------|-----------|---------|
| **incidents** | `/api/incidents/` | List, details, stats |
| **analytics** | `/api/analytics/` | Trends, MTTR, top issues |
| **rca** | `/api/rca/investigate` | Trigger investigation |
| **observability** | `/api/observability/` | Metrics, logs, traces |

---

## 2. RCA Agent (Autonomous Investigation)

**File**: `app/agents/rca_agent.py`

### Agentic Loop: Plan → Act → Check → Adapt

```python
1. PLAN: Define investigation strategy
2. ACT: Fetch data from Prometheus/Loki/Jaeger (parallel)
3. CHECK: Validate data quality (completeness, errors)
4. ADAPT: Generate RCA using LLM + RAG context
```

### Data Collection

```
PrometheusClient → 15 metrics (CPU, memory, HTTP, latency)
LokiClient → Categorized logs (ERROR, CRITICAL, WARNING, INFO)
JaegerClient → Traces with spans (slow, error, sample)
```

### LLM Integration

- **5 Providers**: Claude, GPT, Gemini, Grok, Groq
- **Prompt**: 5700 chars (~1400 tokens) with full observability data
- **RAG**: Past incidents matched by service (exact=5pts, partial=3pts)
- **Fallback**: Rule-based analysis if LLM fails

---

## 3. Observability Stack

### Service URLs (Docker Network)

```yaml
PROMETHEUS_URL: http://prometheus:9090
LOKI_URL: http://loki:3100
JAEGER_QUERY_URL: http://jaeger:16686
```

### Data Flow

```
Application → OTLP → Jaeger (traces)
Application → Remote Write → Prometheus (metrics)
Application → Push API → Loki (logs)
```

---

## 4. Dual Storage System

### Database (SQLite)

**File**: `data/sre_copilot.db`

**Tables**:
- `incidents`: Full incident details, RCA report, LLM metadata
- `incident_metrics`: Metric snapshots at detection time

**Purpose**: Frontend queries, statistics, history

### RAG Storage (JSON)

**Directory**: `data/learning/incidents/*.json`

**Structure**:
```json
{
  "incident_id": "INC-XXX",
  "title": "...",
  "service": "core-athenamind",
  "root_cause": "...",
  "fix_applied": "...",
  "keywords": ["error", "rate", "high"]
}
```

**Purpose**: Fast keyword matching during investigation

---

## 5. RAG (Retrieval-Augmented Generation)

### Matching Algorithm

```python
# Service-based matching (no title bias)
exact_match = service == incident_service  # 5 points
partial_match = service in incident_service  # 3 points

# Top 3 similar incidents included in LLM prompt
```

### Learning Process

```
Investigation Complete → Save to Database → Extract Keywords → Save JSON → RAG Ready
```

---

## 6. Analytics Engine

### Endpoints

| Endpoint | Data Source | Purpose |
|----------|-------------|---------|
| `/trends/incidents` | Database aggregation | Daily incident counts |
| `/trends/mttr` | Duration calculation | Mean time to resolve |
| `/issues/top` | Title grouping | Most common issues |
| `/services/health` | Service grouping | Per-service metrics |

---

## 7. Investigation Flow (Detailed)

### Step 1: Trigger Investigation

```bash
POST /api/rca/investigate
{
  "service": "core-athenamind",
  "severity": "high"
}
```

### Step 2: Create Incident Record

```python
incident_id = generate_id()  # INC-XXXXXXXX
status = "open"
# Save to database immediately
```

### Step 3: Parallel Data Collection

```python
async with asyncio.gather():
    metrics = prometheus.get_critical_metrics()
    logs = loki.query_logs()
    traces = jaeger.query_traces()
```

### Step 4: RAG Context Retrieval

```python
# Match by service (no title bias)
similar = find_similar_incidents(service="core-athenamind")
# Returns top 3 with keywords
```

### Step 5: LLM Analysis

```python
prompt = f"""
Observability Data:
- Metrics: {metrics[:5000]}
- Logs: {logs[:5000]}
- Traces: {traces[:5000]}

Past Incidents:
{similar_incidents}

Analyze and provide root cause.
"""
```

### Step 6: Save Results

```python
# Database (full details)
incident.root_cause = llm_response
incident.status = "completed"
db.commit()

# RAG (keywords)
save_json({
    "incident_id": incident_id,
    "keywords": extract_keywords(root_cause)
})
```

---

## 8. Data Validation

### Metrics Check

```python
if not metrics or "error" in metrics:
    quality_score -= 30
```

### Logs Check

```python
if not logs or len(logs) == 0:
    quality_score -= 30
```

### Traces Check

```python
if not traces or len(traces) == 0:
    quality_score -= 20
```

**Threshold**: 50% quality required for LLM analysis

---

## 9. Configuration

### Environment Variables

```bash
# LLM
LLM_PROVIDER=groq
LLM_API_KEY=gsk_xxx
LLM_MODEL=llama-3.3-70b-versatile

# Observability
PROMETHEUS_URL=http://prometheus:9090
LOKI_URL=http://loki:3100
JAEGER_QUERY_URL=http://jaeger:16686

# Storage
DB_URL=sqlite:///data/sre_copilot.db
REDIS_URL=redis://redis:6379
```

---

## 10. Testing Results

### ✅ All Components Validated

```
✅ Health check passed
✅ Observability services healthy (Prometheus, Loki, Jaeger)
✅ Metrics endpoint working (15 metrics collected)
✅ Logs endpoint working (categorized by level)
✅ Traces endpoint working (with span details)
✅ RCA investigation completed
✅ Incident saved to database
✅ Learning data appended for RAG
✅ Statistics working (by severity, by service)
✅ Analytics working (trends, MTTR, top issues)
✅ RAG configuration validated
```

### Test Command

```bash
cd platform/backend
python3 test_e2e.py
```

---

## 11. Key Insights

### No Title Bias

- **Before**: Title sent to LLM → biased analysis
- **After**: Only observability data → LLM determines actual issue
- **Example**: Correctly identified "High Error Rate" instead of assumed "High Memory Usage"

### Dual Storage Benefits

- **Database**: Complex queries, joins, aggregations for frontend
- **JSON**: Fast keyword matching, no SQL overhead for RAG

### Parallel Data Collection

- **Sequential**: 3-5 seconds per source = 15 seconds total
- **Parallel**: All sources simultaneously = 3-5 seconds total

### LLM Fallback

- **Primary**: LLM analysis with RAG context
- **Fallback**: Rule-based analysis (error patterns, thresholds)
- **Result**: 100% uptime even if LLM fails

---

## 12. Production Deployment

### Docker Compose

```bash
cd platform
docker compose up -d
```

### Services Started

```
✅ jaeger (traces)
✅ prometheus (metrics)
✅ loki (logs)
✅ grafana (dashboards)
✅ redis (cache)
✅ backend (API + RCA agent)
```

### Data Persistence

```
platform_prometheus-data
platform_loki-data
platform_grafana-data
platform_backend-data (database + learning files)
```

---

## Summary

**Platform Status**: ✅ Fully Operational

- **API**: 4 routers, 15+ endpoints
- **RCA Agent**: Autonomous investigation with Plan→Act→Check→Adapt loop
- **Observability**: Prometheus + Loki + Jaeger integration
- **LLM**: 5 providers with automatic fallback
- **Storage**: Dual system (Database + RAG)
- **Analytics**: Trends, MTTR, top issues, service health
- **Learning**: Automatic RAG data generation after each incident

**Next Phase**: Frontend development, real-time monitoring, alerting integration
