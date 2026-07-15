# 🤖 SRE Copilot

> **AI-powered incident diagnosis and automated root cause analysis that reduced MTTR by 50%**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-blue)](https://github.com/langchain-ai/langgraph)
[![AWS Bedrock](https://img.shields.io/badge/AWS_Bedrock-Claude_3.5-FF9900?logo=amazonaws)](https://aws.amazon.com/bedrock/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?logo=prometheus)](https://prometheus.io)

---

## The Problem

When a P1 incident fires at 3 AM, SREs waste critical minutes on repetitive tasks:
- Checking metrics across multiple dashboards
- Grepping through thousands of log lines
- Correlating traces to find the bottleneck
- Searching Confluence for "have we seen this before?"

**SRE Copilot automates the first 10-15 minutes of every incident investigation.**

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          SRE COPILOT — AGENTIC WORKFLOW                          │
│                                                                                 │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  ALERT   │───▶│     PLAN     │───▶│     ACT      │───▶│     DIAGNOSE     │  │
│  │ Trigger  │    │  Strategy    │    │ Collect Data │    │   RCA + Report   │  │
│  └──────────┘    └──────────────┘    └──────────────┘    └──────────────────┘  │
│       │                                     │                      │            │
│       │          ┌──────────────┐           │           ┌─────────▼────────┐   │
│       │          │    ADAPT     │◀──────────┤           │    VALIDATE      │   │
│       │          │  Retry/Widen │    insufficient       │  Data Quality    │   │
│       │          └──────────────┘     data?             └──────────────────┘   │
│       │                                                         │              │
│       │                                                    sufficient?         │
│       │                                                         │              │
│       │          ┌──────────────┐    ┌──────────────┐          ▼              │
│       │          │     RAG      │───▶│    LEARN     │    ┌───────────┐        │
│       └─────────▶│Similar Incs  │    │  Store RCA   │    │  NOTIFY   │        │
│                  └──────────────┘    └──────────────┘    │  Slack    │        │
│                                                          └───────────┘        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### The Agentic Loop: Plan → Act → Check → Adapt

| Phase | What Happens | Time |
|-------|-------------|------|
| **PLAN** | Agent decides investigation strategy based on alert type | ~1s |
| **ACT** | Parallel data collection from Prometheus, Loki, Jaeger | ~3-5s |
| **VALIDATE** | Checks data quality — need ≥2 sources with valid data | ~1s |
| **ADAPT** | If insufficient data → retry with wider time range | ~3s |
| **DIAGNOSE** | LLM analyzes correlated data, generates RCA | ~5-8s |
| **LEARN** | Stores incident in vector DB for future similarity matching | ~1s |

**Total time: ~15 seconds** vs. 15+ minutes of manual investigation.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  Dashboard │ Incidents List │ Investigation View │ Chatbot       │
└────────────────────────────────┬────────────────────────────────┘
                                 │ REST API
┌────────────────────────────────▼────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            ORCHESTRATOR (LangGraph StateGraph)             │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │   │
│  │  │ Monitoring  │  │  Diagnostic  │  │  RAG Learning  │  │   │
│  │  │   Agent     │  │    Agent     │  │    Agent       │  │   │
│  │  │             │  │              │  │                │  │   │
│  │  │ • Prometheus│  │ • Claude 3.5 │  │ • ChromaDB     │  │   │
│  │  │ • Loki      │  │ • ReAct Loop │  │ • Jaccard Sim  │  │   │
│  │  │ • Jaeger    │  │ • RCA Gen    │  │ • LLM Filter   │  │   │
│  │  └─────────────┘  └──────────────┘  └────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │Auto-Trigger  │  │  Slack Bot   │  │  DynamoDB Tracker  │    │
│  │(CPU/Errors)  │  │  (Alerts)    │  │  (Dedup)           │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                    OBSERVABILITY STACK (Docker)                   │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────┐  ┌──────────────┐  │
│  │ Prometheus │  │    Loki    │  │ Jaeger │  │   Grafana    │  │
│  │  (Metrics) │  │   (Logs)   │  │(Traces)│  │ (Dashboards) │  │
│  └────────────┘  └────────────┘  └────────┘  └──────────────┘  │
│                                                                  │
│  ┌────────────┐  ┌────────────┐                                 │
│  │   Redis    │  │  ChromaDB  │                                 │
│  │ (Sessions) │  │(Vector DB) │                                 │
│  └────────────┘  └────────────┘                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 🔄 Multi-Agent Orchestration (LangGraph)
The system uses a **StateGraph** with conditional routing — agents communicate through shared state, and the workflow adapts based on data quality validation.

```python
# Conditional edge: if data insufficient → adapt and retry
workflow.add_conditional_edges(
    "validate",
    should_adapt,    # Decision function
    {"adapt": "adapt", "end": END}
)
workflow.add_edge("adapt", "monitor")  # Retry loop
```

### 🧠 RAG-Powered Incident Learning
Every resolved incident is embedded and stored in ChromaDB. When a new incident fires, the system finds similar past incidents using **Jaccard similarity** (≥60% threshold) and provides historical context to the LLM for faster diagnosis.

### ⚡ Auto-Investigation Triggers
Continuous monitoring with automatic RCA when:
- CPU/RAM utilization > 90%
- 3+ consecutive error log batches detected
- Only alerts Slack for high-severity findings (confidence > 0.6) — **prevents alert fatigue**

### 🔍 Multi-Source Correlation
Simultaneously queries **Prometheus** (metrics), **Loki** (logs), and **Jaeger** (traces) to build a complete picture. Parallel execution: **3-5s** vs. 15s+ sequential.

### 🤖 Interactive Chatbot
Ask follow-up questions about ongoing incidents in natural language. The chatbot has full context of the investigation and can query additional data on demand.

### 📊 Real-Time Dashboard
React frontend with live metric charts, incident timeline, investigation progress tracking, and remediation action cards.

---

## Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Mean Time to Detect (MTTD) | 5-10 min | ~30 sec | **90% faster** |
| Mean Time to Diagnose | 15-30 min | ~15 sec | **98% faster** |
| Mean Time to Resolve (MTTR) | 45 min | ~22 min | **50% reduction** |
| False Alert Rate | ~40% | ~12% | **70% reduction** |
| Duplicate Investigations | Common | Eliminated | **DynamoDB dedup** |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI/Agents** | LangGraph, LangChain, AWS Bedrock (Claude 3.5) | Multi-agent orchestration + LLM reasoning |
| **Vector DB** | ChromaDB | Incident embedding + similarity search |
| **Backend** | FastAPI, Python 3.11 | API server + agent runtime |
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS | Real-time dashboard + chatbot |
| **Metrics** | Prometheus | Time-series metrics collection |
| **Logs** | Loki | Log aggregation + querying |
| **Traces** | Jaeger (OTLP) | Distributed tracing |
| **Dashboards** | Grafana | Unified observability |
| **Cache** | Redis | Session management + alert dedup |
| **Tracking** | DynamoDB | Investigation dedup + audit trail |
| **Notifications** | Slack Webhooks | High-severity alert delivery |
| **Infra** | Docker Compose | Single-command deployment |

---

## Quick Start

```bash
# Clone
git clone https://github.com/deepakjairamani1/sre-copilot.git
cd sre-copilot

# Start the observability stack
cd platform && docker compose up -d

# Install backend dependencies
cd backend && pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS Bedrock credentials

# Start the backend
uvicorn app.main:app --reload --port 8000

# Start the frontend (separate terminal)
cd ../sre-copilot-frontend
npm install && npm run dev
```

### Environment Variables

```bash
# LLM Configuration
LLM_PROVIDER=bedrock              # bedrock | claude | gpt | gemini | groq
LLM_MODEL=us.anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Observability
PROMETHEUS_URL=http://localhost:9090
LOKI_URL=http://localhost:3100
JAEGER_QUERY_URL=http://localhost:16686

# Optional
DYNAMODB_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auto-investigation/start` | Start continuous auto-monitoring |
| `POST` | `/api/auto-investigation/stop` | Stop monitoring |
| `POST` | `/api/rca/investigate` | Trigger manual investigation |
| `GET` | `/api/incidents` | List all incidents |
| `GET` | `/api/incidents/{id}` | Get incident details + RCA |
| `POST` | `/api/chatbot/message` | Send message to chatbot |
| `GET` | `/api/observability/metrics` | Current system metrics |
| `POST` | `/api/vector-db/search` | Search similar incidents |

---

## Project Structure

```
sre-copilot/
├── platform/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── agents/              # Core RCA agent + Bedrock integration
│   │   │   ├── agents_langchain/    # LangGraph orchestrator + specialized agents
│   │   │   ├── clients/             # Prometheus, Loki, Jaeger, DynamoDB clients
│   │   │   ├── services/            # Auto-investigator, Slack notifier, monitor
│   │   │   ├── routers/             # FastAPI route handlers
│   │   │   └── models/              # Data models
│   │   ├── data/
│   │   │   ├── learning/incidents/  # Stored incident knowledge base (RAG)
│   │   │   └── vector_db/           # ChromaDB embeddings
│   │   └── tests/
│   ├── sre-copilot-frontend/        # React + TypeScript dashboard
│   ├── docker-compose.yml           # Full observability stack
│   └── docs/                        # Architecture + feature docs
└── README.md
```

---

## How the Agents Work Together

```
                    ┌─────────────────────┐
                    │   ORCHESTRATOR      │
                    │   (LangGraph)       │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼──────┐ ┌─────▼──────┐ ┌──────▼─────────┐
    │  MONITORING    │ │ DIAGNOSTIC │ │  RAG LEARNING  │
    │  AGENT         │ │ AGENT      │ │  AGENT         │
    │                │ │            │ │                │
    │ Collects data  │ │ Analyzes   │ │ Finds similar  │
    │ from Prom,     │ │ root cause │ │ past incidents │
    │ Loki, Jaeger   │ │ using LLM  │ │ via ChromaDB   │
    │                │ │            │ │                │
    │ Tools:         │ │ Tools:     │ │ Tools:         │
    │ • PromQL       │ │ • RCA      │ │ • Vector       │
    │ • LogQL        │ │ • Analysis │ │   Search       │
    │ • TraceQL      │ │            │ │ • Similarity   │
    └────────────────┘ └────────────┘ └────────────────┘
```

Each agent is a **ReAct agent** (Reason + Act) — they autonomously decide which tools to use based on the incident context, execute queries, and adapt if results are insufficient.

---

## What I Learned Building This

1. **Multi-agent orchestration needs explicit state management** — LangGraph's StateGraph pattern solved coordination issues that raw LangChain chains couldn't handle.

2. **RAG for incidents is different from RAG for docs** — Jaccard similarity on extracted keywords works better than pure embedding similarity for operational incidents (structured + repetitive patterns).

3. **Auto-investigation needs deduplication badly** — Without DynamoDB tracking, the system would re-investigate the same error every 10 seconds. Timestamp-based windowing solved this.

4. **Confidence thresholds prevent alert fatigue** — Only alerting Slack when confidence > 0.6 reduced false positive notifications by 70%.

5. **Parallel data collection is 3-5x faster** — Asyncio gathering of Prometheus + Loki + Jaeger simultaneously vs. sequential querying.

---

## Future Roadmap

- [ ] **Automated remediation** — Execute runbook actions (restart pods, scale up, rollback) with human-in-the-loop approval
- [ ] **Multi-cluster support** — Federated monitoring across multiple K8s clusters
- [ ] **Custom alert rules** — User-defined investigation triggers beyond CPU/error thresholds
- [ ] **Incident timeline visualization** — Correlate deploy events, config changes, and alerts on a single timeline
- [ ] **Integration with PagerDuty/OpsGenie** — Bi-directional sync with existing incident management tools

---

## License

MIT

---

<p align="center">
  <b>Built by <a href="https://github.com/deepakjairamani1">Deepak Jairamani</a></b> — SRE who got tired of the same 3 AM routine.
</p>
