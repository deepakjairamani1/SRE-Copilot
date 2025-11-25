# Full Traceability System

## Overview

Every investigation is fully traceable from input to output to storage.

## Data Flow

```
Incident → Prompt → LLM → Response → Database + RAG
```

## Storage Locations

### 1. Prompts
**Path**: `data/prompts/{incident_id}.txt`  
**Content**: Exact prompt sent to LLM  
**Size**: ~4KB  

**Example**: `INC-688EC9DC.txt`
```
You are an expert SRE analyzing an incident.

CURRENT INCIDENT:
Service: core-athenamind
Detected: 2025-11-25T13:06:38

=== OBSERVABILITY DATA ===
🔴 http_error_rate_percent: 46.67%
🟢 cpu_usage_percent: 9.75%
...
```

### 2. Responses
**Path**: `data/responses/{incident_id}.txt`  
**Content**: Raw LLM response  
**Size**: ~3KB  

**Example**: `INC-688EC9DC.txt`
```json
{
  "executive_summary": {
    "title": "High Error Rate",
    "severity": "high",
    ...
  },
  "root_cause": {
    "primary_cause": "Database connection refused",
    ...
  }
}
```

### 3. Learning Data
**Path**: `data/learning/incidents/{incident_id}.json`  
**Content**: RAG knowledge (if worth learning)  
**Size**: ~1KB  

**Example**: `INC-688EC9DC.json`
```json
{
  "incident_id": "INC-688EC9DC",
  "title": "High Error Rate",
  "keywords": ["http-error-rate", "backend-service"],
  "root_cause": "Database connection refused",
  "fix_applied": "Restart database service"
}
```

### 4. Database
**Path**: `data/sre_copilot.db`  
**Table**: `incidents`  
**Content**: Full incident record  

**Fields**:
- incident_id
- service
- severity
- status
- title
- root_cause
- confidence_score
- rca_report_json (includes observability_data)
- investigation_steps
- llm_provider
- tokens_used
- cost_usd
- detected_at
- resolved_at

## Mapping

All files use same `incident_id` for easy correlation:

```
INC-688EC9DC
├── data/prompts/INC-688EC9DC.txt
├── data/responses/INC-688EC9DC.txt
├── data/learning/incidents/INC-688EC9DC.json
└── database: incidents WHERE incident_id='INC-688EC9DC'
```

## Investigation Steps

Every step is logged in `investigation_steps`:

```json
[
  {
    "step": "plan",
    "message": "📋 Planning investigation strategy...",
    "timestamp": "2025-11-25T13:06:38Z"
  },
  {
    "step": "act",
    "message": "🔍 Fetching observability data...",
    "timestamp": "2025-11-25T13:06:39Z"
  },
  {
    "step": "check",
    "message": "✓ Data quality sufficient",
    "timestamp": "2025-11-25T13:06:42Z"
  },
  {
    "step": "act",
    "message": "🧠 Generating RCA with AI...",
    "timestamp": "2025-11-25T13:06:42Z"
  }
]
```

## Observability Data

Full observability data stored in `rca_report_json`:

```json
{
  "executive_summary": {...},
  "root_cause": {...},
  "observability_data": {
    "prometheus": {
      "host_metrics": {...},
      "otlp_metrics": {...}
    },
    "loki": {
      "logs": {
        "error_logs": [...],
        "critical_logs": [...]
      }
    },
    "jaeger": {
      "traces": {
        "slow_traces": [...],
        "error_traces": [...]
      }
    },
    "similar_incidents": [...]
  }
}
```

## Use Cases

### 1. Debug LLM Behavior
```bash
# See what we asked
cat data/prompts/INC-XXX.txt

# See what LLM responded
cat data/responses/INC-XXX.txt

# Compare with final RCA
curl http://localhost:7474/api/incidents/INC-XXX
```

### 2. Audit Trail
```bash
# Who investigated?
# What data was available?
# What was the conclusion?
# All answers in database + files
```

### 3. Improve Prompts
```bash
# Review prompts that led to low confidence
SELECT incident_id, confidence_score 
FROM incidents 
WHERE confidence_score < 0.7;

# Check their prompts
cat data/prompts/{incident_id}.txt
```

### 4. Analyze Patterns
```bash
# What keywords lead to good matches?
jq '.keywords' data/learning/incidents/*.json

# What root causes are common?
jq '.root_cause' data/learning/incidents/*.json | sort | uniq -c
```

## Benefits

1. **Complete Transparency**: See every step of investigation
2. **Debugging**: Understand why LLM made certain decisions
3. **Auditing**: Full trail for compliance
4. **Learning**: Analyze patterns across incidents
5. **Improvement**: Identify areas to optimize

## API Access

### Get Full Incident
```bash
GET /api/incidents/{incident_id}
```

Returns:
- RCA report
- Observability data
- Investigation steps
- LLM metadata

### Get Investigation Steps
```bash
curl http://localhost:7474/api/incidents/INC-XXX | jq '.investigation_steps'
```

### Get Observability Data
```bash
curl http://localhost:7474/api/incidents/INC-XXX | jq '.observability_data'
```

## Logging

Console and file logging:
```
2025-11-25 13:06:38 - INFO - [INC-XXX] Starting investigation
2025-11-25 13:06:39 - DEBUG - [INC-XXX] Prompt saved to data/prompts/INC-XXX.txt
2025-11-25 13:06:42 - INFO - [INC-XXX] LLM response received: 2093 chars
2025-11-25 13:06:42 - DEBUG - [INC-XXX] Response saved to data/responses/INC-XXX.txt
2025-11-25 13:06:43 - INFO - [INC-XXX] Successfully saved to database
```

## Retention

All data persisted in Docker volumes:
- Prompts: Indefinite
- Responses: Indefinite
- Learning: Indefinite
- Database: Indefinite

**Cleanup** (if needed):
```bash
# Remove old prompts/responses
find data/prompts -mtime +30 -delete
find data/responses -mtime +30 -delete

# Keep learning data (valuable)
# Keep database (queryable history)
```
