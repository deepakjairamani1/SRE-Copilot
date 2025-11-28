# SRE Copilot Platform - Documentation

## 📚 Documentation Structure

### Hackathon Presentation
- **[PRESENTATION.md](hackathon/PRESENTATION.md)** - Complete hackathon pitch deck

### Features
1. **[Agentic Workflow](features/01-AGENTIC-WORKFLOW.md)** - Plan→Act→Check→Adapt loop
2. **[Smart Truncation](features/02-SMART-TRUNCATION.md)** - 97% token reduction
3. **[RAG Learning](features/03-RAG-LEARNING.md)** - Quality-filtered knowledge base
4. **[Multi-LLM Support](features/04-MULTI-LLM-SUPPORT.md)** - 5 providers with fallback
5. **[Traceability](features/05-TRACEABILITY.md)** - Full audit trail

### Quick Links
- **Setup**: See `../DOCKER_SETUP.md`
- **API Docs**: `http://localhost:7474/docs`
- **Debugging**: See `../DEBUGGING_GUIDE.md`

## 🚀 Quick Start

```bash
# 1. Start platform
cd platform && docker compose up -d

# 2. Trigger investigation
curl -X POST http://localhost:7474/api/rca/investigate \
  -H "Content-Type: application/json" \
  -d '{"service": "core-athenamind", "severity": "high"}'

# 3. View results
curl http://localhost:7474/api/incidents/ | jq '.[0]'
```

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| Investigation Time | 3-5 seconds |
| Token Reduction | 97% (168KB → 4KB) |
| LLM Providers | 5 (Groq, Claude, GPT, Gemini, Grok) |
| RAG Match Threshold | 60% keyword similarity |
| Confidence Score | 0.8 average |
| Cost per Investigation | $0.00 (Groq free tier) |

## 🎯 Core Features

### 1. Autonomous Investigation
- **Plan**: Decides what data to collect
- **Act**: Fetches data in parallel (3-5s)
- **Check**: Validates data quality
- **Adapt**: Adjusts strategy or falls back

### 2. Intelligent Data Processing
- Metric summarization with visual indicators
- Log deduplication with occurrence count
- Trace filtering (slow/error + summary)
- 97% token reduction

### 3. Learning System
- LLM validates if incident is worth learning
- Keyword-based similarity matching (60% threshold)
- Service-specific retrieval
- Continuous improvement

### 4. Multi-Provider Support
- 5 LLM providers supported
- Automatic fallback to rule-based
- Cost tracking per investigation
- Provider-aware token limits

### 5. Complete Traceability
- Prompts saved (`data/prompts/`)
- Responses saved (`data/responses/`)
- Learning data (`data/learning/incidents/`)
- Full database records

## 🏗️ Architecture

```
Applications → Observability Stack → RCA Agent → LLM → Storage
                (Prometheus/Loki/Jaeger)   (Agentic)   (DB+RAG)
```

## 📁 Data Structure

```
data/
├── prompts/              # LLM inputs
│   └── INC-XXX.txt
├── responses/            # LLM outputs
│   └── INC-XXX.txt
├── learning/
│   └── incidents/        # RAG knowledge
│       └── INC-XXX.json
└── sre_copilot.db       # Full records
```

## 🔧 Configuration

**File**: `backend/.env`
```bash
# LLM
LLM_PROVIDER=groq
LLM_API_KEY=gsk_xxx

# Observability
PROMETHEUS_URL=http://prometheus:9090
LOKI_URL=http://loki:3100
JAEGER_QUERY_URL=http://jaeger:16686

# Database
DB_URL=sqlite:///data/sre_copilot.db
```

## 📖 Reading Order

**For Hackathon Judges**:
1. Start with [PRESENTATION.md](hackathon/PRESENTATION.md)
2. Deep dive into features as needed

**For Developers**:
1. [Agentic Workflow](features/01-AGENTIC-WORKFLOW.md) - Understand the agent
2. [Smart Truncation](features/02-SMART-TRUNCATION.md) - See optimization
3. [RAG Learning](features/03-RAG-LEARNING.md) - Understand learning
4. [Multi-LLM Support](features/04-MULTI-LLM-SUPPORT.md) - Provider setup
5. [Traceability](features/05-TRACEABILITY.md) - Debug and audit

**For Users**:
1. `../DOCKER_SETUP.md` - Setup instructions
2. `../QUICK_REFERENCE.md` - Common commands
3. `../DEBUGGING_GUIDE.md` - Troubleshooting

## 🎤 Presentation Tips

1. **Start with Problem**: Manual RCA takes hours
2. **Show Agent Loop**: Plan→Act→Check→Adapt
3. **Demo Live**: Trigger investigation, show results
4. **Highlight Innovation**: 97% token reduction, quality-filtered RAG
5. **Show Traceability**: Prompt → Response → Learning
6. **End with Impact**: Seconds vs hours, continuous learning

## 📞 Support

- **Issues**: Check `../DEBUGGING_GUIDE.md`
- **API**: `http://localhost:7474/docs`
- **Logs**: `docker compose logs -f backend`

---

**Built with ❤️ for autonomous incident response**
