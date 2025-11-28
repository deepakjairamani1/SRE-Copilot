# 🚀 SRE Copilot Platform - Hackathon Presentation

## 🎯 Problem Statement

**Modern applications generate massive amounts of observability data, but when incidents occur:**
- ❌ Engineers spend hours manually correlating metrics, logs, and traces
- ❌ Root cause analysis is time-consuming and error-prone
- ❌ Past incident knowledge is lost or scattered
- ❌ Mean Time To Resolution (MTTR) is too high

## 💡 Our Solution: AI-Powered Autonomous RCA Agent

An intelligent SRE copilot that **automatically investigates incidents** using an agentic AI workflow.

---

## 🤖 Agentic AI Architecture

### The Agent Loop: Plan → Act → Check → Adapt

```
┌─────────────────────────────────────────────────────────────┐
│                    INCIDENT DETECTED                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: PLAN                                                │
│  Agent decides investigation strategy:                       │
│  • Query Prometheus for metrics                              │
│  • Query Loki for error logs                                 │
│  • Query Jaeger for slow traces                              │
│  • Search similar past incidents (RAG)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: ACT                                                 │
│  Agent executes plan in parallel:                            │
│  ┌──────────────┬──────────────┬──────────────┬───────────┐ │
│  │ Prometheus   │    Loki      │   Jaeger     │    RAG    │ │
│  │ 15 metrics   │  Logs by     │  Traces +    │  Similar  │ │
│  │ (CPU, mem,   │  severity    │  spans       │  incidents│ │
│  │  latency)    │  (E/C/W/I)   │  (slow/err)  │  (60%+)   │ │
│  └──────────────┴──────────────┴──────────────┴───────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: CHECK                                               │
│  Agent validates data quality:                               │
│  • Are metrics available? ✓                                  │
│  • Are logs present? ✓                                       │
│  • Are traces captured? ✓                                    │
│  • Is data sufficient for analysis? (≥2 sources)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: ADAPT                                               │
│  Agent adjusts based on findings:                            │
│  • If data insufficient → Retry with wider time range        │
│  • If LLM fails → Fallback to rule-based analysis            │
│  • If successful → Generate comprehensive RCA                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: LEARN                                               │
│  Agent decides if incident is worth learning:                │
│  • Novel issue? Clear root cause? Actionable fix?            │
│  • If YES → Extract keywords, save to knowledge base         │
│  • If NO → Skip (avoid noise in RAG)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Features

### 1. **Smart Data Collection** 🔍
- **Parallel fetching** from 3 observability sources (3-5s total)
- **Intelligent truncation** to fit LLM token limits
- **Metric summarization**: Only critical values with status indicators
- **Log deduplication**: Groups identical messages with occurrence count
- **Trace filtering**: Top slow/error traces with span details

**Before**: 168KB prompts (40K tokens) ❌  
**After**: 4KB prompts (1K tokens) ✅  
**Reduction**: 97% smaller, fits all LLM providers

### 2. **Multi-LLM Support** 🧠
Supports 5 LLM providers with automatic fallback:
- **Groq** (llama-3.3-70b) - Free tier, 8K tokens
- **Claude** (Sonnet 4) - 200K tokens
- **GPT-4o** - 128K tokens
- **Gemini** (2.0 Flash) - 1M tokens
- **Grok** (Beta) - 8K tokens

**Fallback**: If LLM fails → Rule-based analysis (100% uptime)

### 3. **RAG-Powered Learning** 📚
- **Keyword-based matching**: 60% similarity threshold
- **Service-specific**: Only matches same service incidents
- **Quality filter**: LLM decides if incident is worth learning
- **Smart keywords**: LLM generates technical keywords (e.g., `database-connection`, `retry-mechanism`)

**Example**:
```
Current: ['http', 'error', 'rate', 'timeout']
Past:    ['http', 'error', 'rate', 'latency']
Match:   75% → Included in context ✓
```

### 4. **Comprehensive RCA Output** 📊
Agent provides:
- ✅ **What's going RIGHT**: Healthy metrics, normal behavior
- ❌ **What's going WRONG**: Anomalies, errors, degradation
- 🎯 **Root cause**: With evidence from metrics/logs/traces
- ⚡ **Immediate actions**: Step-by-step remediation
- 🛡️ **Prevention**: Long-term fixes and monitoring enhancements

### 5. **Full Traceability** 🔬
Every investigation saves:
- `data/prompts/{incident_id}.txt` - What we asked LLM
- `data/responses/{incident_id}.txt` - What LLM responded
- `data/learning/incidents/{incident_id}.json` - RAG knowledge
- Database record - Full RCA report with observability data

---

## 📈 Results & Impact

### Performance Metrics
| Metric | Value |
|--------|-------|
| Investigation Time | **3-5 seconds** |
| Data Collection | **Parallel (3s)** vs Sequential (15s) |
| LLM Analysis | **2-3 seconds** |
| Token Usage | **~3K tokens** (input + output) |
| Cost per Investigation | **$0.00** (Groq free tier) |
| Prompt Size Reduction | **97%** (168KB → 4KB) |

### Accuracy Metrics
| Metric | Value |
|--------|-------|
| Confidence Score | **0.8 (80%)** average |
| Data Quality Check | **≥2 sources required** |
| RAG Match Threshold | **60% keyword similarity** |
| Learning Filter | **LLM-validated incidents only** |

### Business Impact
- ⚡ **Faster MTTR**: Automated investigation vs manual analysis
- 🎯 **Higher Accuracy**: AI-powered correlation across all data sources
- 📚 **Knowledge Retention**: Every incident improves future investigations
- 💰 **Cost Effective**: Free tier LLMs, minimal infrastructure

---

## 🏗️ Technical Architecture

### Observability Stack
```
┌─────────────────────────────────────────────────────────┐
│                    Applications                          │
└────────┬──────────────┬──────────────┬─────────────────┘
         │              │              │
         ▼              ▼              ▼
    Prometheus       Loki          Jaeger
    (Metrics)       (Logs)        (Traces)
         │              │              │
         └──────────────┴──────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   RCA Agent (AI)    │
              │  Plan→Act→Check→    │
              │      Adapt Loop     │
              └─────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
    Database (SQLite)            RAG (JSON)
    - Full incidents             - Keywords
    - Metrics snapshots          - Root causes
    - Investigation steps        - Fixes applied
```

### Data Flow
1. **Incident Triggered** → API receives alert
2. **Agent Plans** → Defines investigation strategy
3. **Parallel Collection** → Fetches metrics/logs/traces simultaneously
4. **Data Validation** → Checks quality and completeness
5. **Smart Truncation** → Summarizes data for LLM
6. **RAG Retrieval** → Finds similar past incidents (60%+ match)
7. **LLM Analysis** → Generates comprehensive RCA
8. **Learning Decision** → LLM decides if worth storing
9. **Dual Storage** → Database (queries) + JSON (RAG)

---

## 🎨 Innovation Highlights

### 1. **Agentic AI Workflow**
Not just a simple LLM call - implements full autonomous agent loop:
- **Planning**: Decides what data to collect
- **Acting**: Executes plan with error handling
- **Checking**: Validates results
- **Adapting**: Adjusts strategy based on findings

### 2. **Intelligent Token Management**
- Automatic data summarization
- Visual status indicators (🔴🟡🟢)
- Deduplication of logs
- Selective trace inclusion
- **Result**: 97% token reduction

### 3. **Quality-Filtered RAG**
- LLM validates if incident is worth learning
- Keyword-based similarity (not just service name)
- 60% threshold prevents noise
- Technical keywords (not generic words)

### 4. **Multi-Provider Resilience**
- 5 LLM providers supported
- Automatic fallback to rule-based
- Provider-aware token limits
- Cost tracking per investigation

### 5. **Full Observability**
- Every prompt saved
- Every response saved
- Every investigation step logged
- Complete audit trail

---

## 🚀 Demo Scenario

### Incident: High Error Rate

**1. Detection** (t=0s)
```
Service: core-athenamind
Alert: HTTP error rate 47% (threshold: 5%)
```

**2. Agent Investigation** (t=0-5s)
```
✓ Collected 15 metrics (6 host + 9 OTLP)
✓ Found 8 error logs (deduplicated to 4 unique)
✓ Found 1 error trace
✓ Retrieved 1 similar incident (75% match)
```

**3. LLM Analysis** (t=5-8s)
```
Root Cause: Database connection refused
Evidence:
  - 🔴 http_error_rate: 47% (critical)
  - [2x] Connection refused to localhost:5432
  - Error trace: Database timeout
Confidence: 80%
```

**4. Recommendations** (t=8s)
```
Immediate:
  1. Check PostgreSQL service status
  2. Verify connection pool settings
  3. Review recent deployments

Prevention:
  1. Implement connection retry mechanism
  2. Add database health checks
  3. Set up connection pool monitoring
```

**5. Learning** (t=8s)
```
Worth Learning: YES
Reason: Clear root cause, actionable fix
Keywords: database-connection, connection-refused, retry-mechanism
✓ Saved to knowledge base
```

**Total Time: 8 seconds** ⚡

---

## 💻 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python) |
| Agent Framework | Custom Agentic Loop |
| LLM Integration | Groq, Claude, GPT, Gemini, Grok |
| Metrics | Prometheus |
| Logs | Loki |
| Traces | Jaeger |
| Database | SQLite |
| RAG Storage | JSON |
| Containerization | Docker Compose |

---

## 🎯 Future Enhancements

1. **Real-time Monitoring**: Auto-trigger on alerts
2. **Slack/PagerDuty Integration**: Send RCA reports to teams
3. **Multi-service Correlation**: Analyze cross-service incidents
4. **Predictive Analysis**: Predict incidents before they occur
5. **Custom Playbooks**: Service-specific investigation strategies
6. **Graph RAG**: Use knowledge graphs for better similarity matching
7. **Frontend Dashboard**: Visual incident timeline and metrics

---

## 🏆 Why This Wins

### Technical Excellence
✅ **Agentic AI**: Not just LLM wrapper - full autonomous agent  
✅ **Production Ready**: Error handling, fallbacks, logging  
✅ **Scalable**: Token optimization, parallel processing  
✅ **Extensible**: Multi-provider, pluggable architecture  

### Business Value
✅ **Immediate Impact**: Reduces MTTR from hours to seconds  
✅ **Cost Effective**: Free tier LLMs, minimal infrastructure  
✅ **Knowledge Building**: Every incident improves the system  
✅ **Developer Experience**: Simple API, comprehensive output  

### Innovation
✅ **Smart Truncation**: 97% token reduction while maintaining quality  
✅ **Quality-Filtered RAG**: LLM validates learning value  
✅ **Keyword Matching**: 60% threshold prevents noise  
✅ **Full Traceability**: Complete audit trail  

---

## 📊 Live Demo

**Try it yourself:**
```bash
# Start platform
cd platform && docker compose up -d

# Trigger investigation
curl -X POST http://localhost:7474/api/rca/investigate \
  -H "Content-Type: application/json" \
  -d '{"service": "core-athenamind", "severity": "high"}'

# View results
curl http://localhost:7474/api/incidents/ | jq '.[0]'
```

**Check outputs:**
- Prompt: `backend/data/prompts/INC-XXXXXXXX.txt`
- Response: `backend/data/responses/INC-XXXXXXXX.txt`
- Learning: `backend/data/learning/incidents/INC-XXXXXXXX.json`

---

## 🎤 Closing

**SRE Copilot Platform** transforms incident response from a manual, time-consuming process into an **automated, intelligent, and learning system**.

By combining **agentic AI workflows**, **multi-source observability**, and **quality-filtered RAG**, we've built a platform that not only solves incidents faster but **gets smarter with every investigation**.

**The future of SRE is autonomous. The future is now.** 🚀

---

## 📞 Contact & Links

- **GitHub**: [Repository Link]
- **Demo**: [Live Demo URL]
- **Docs**: `platform/docs/`
- **API**: `http://localhost:7474/docs`

**Built with ❤️ for the Hackathon**
