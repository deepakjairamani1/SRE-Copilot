# LangChain/LangGraph Multi-Agent Architecture

## Overview
This document describes the LangChain/LangGraph based multi-agent system for autonomous incident response and RCA.

## Architecture Components

### 1. **LangChain Tools** (`agents_langchain/tools.py`)
Custom tools that wrap our observability clients:

- **PrometheusQueryTool**: Query metrics (CPU, memory, HTTP errors, latency)
- **LokiQueryTool**: Query logs (errors, warnings, patterns)
- **JaegerQueryTool**: Query traces (slow traces, bottlenecks)
- **VectorSearchTool**: Semantic similarity search using Bedrock Titan embeddings
- **RCAAnalysisTool**: AI-powered root cause analysis

### 2. **Monitoring Agent** (`agents_langchain/monitoring_agent.py`)
**Responsibility**: Data Collection

**Pattern**: LangChain ReAct Agent
- Uses Prometheus, Loki, and Jaeger tools
- Collects metrics, logs, and traces
- Summarizes observability data

**Tools Used**:
- `query_prometheus_metrics`
- `query_loki_logs`
- `query_jaeger_traces`

### 3. **Diagnostic Agent** (`agents_langchain/diagnostic_agent.py`)
**Responsibility**: Root Cause Analysis

**Pattern**: LangChain ReAct Agent
- Searches for similar past incidents
- Analyzes observability data
- Generates RCA report with remediation steps

**Tools Used**:
- `search_similar_incidents`
- `perform_rca_analysis`

### 4. **Orchestrator Graph** (`agents_langchain/orchestrator_graph.py`)
**Responsibility**: Workflow Coordination

**Pattern**: LangGraph State Machine
- Coordinates all agents in a structured workflow
- Implements Plan → Act → Check → Adapt loop
- Manages state across agents

## Workflow (LangGraph State Machine)

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────────┐
│    PLAN     │  📋 Plan investigation strategy
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   MONITOR   │  🔍 Collect observability data
└──────┬──────┘  (Monitoring Agent)
       │
       ▼
┌─────────────┐
│  DIAGNOSE   │  🧠 Perform RCA analysis
└──────┬──────┘  (Diagnostic Agent)
       │
       ▼
┌─────────────┐
│  VALIDATE   │  ✓ Validate findings
└──────┬──────┘
       │
       ├─── Low Confidence ───┐
       │                      ▼
       │                 ┌─────────┐
       │                 │  ADAPT  │  🔄 Adapt strategy
       │                 └────┬────┘
       │                      │
       │◄─────────────────────┘
       │
       ├─── High Confidence
       │
       ▼
   ┌───────┐
   │  END  │
   └───────┘
```

## Agent State

Shared state across all agents:

```python
{
    "incident_data": {...},           # Input incident details
    "observability_data": {...},      # Collected metrics/logs/traces
    "rca_report": {...},              # Generated RCA report
    "similar_incidents": [...],       # Past similar incidents
    "investigation_steps": [...],     # Audit trail
    "current_step": "...",            # Current workflow step
}
```

## Key Features

### 1. **ReAct Pattern**
Agents use Reasoning + Acting pattern:
- **Thought**: Agent reasons about what to do
- **Action**: Agent uses a tool
- **Observation**: Agent observes the result
- **Repeat**: Until task is complete

### 2. **State Management**
LangGraph manages state transitions:
- Immutable state updates
- Conditional branching
- Cycle detection
- Error handling

### 3. **Tool Integration**
Tools wrap existing functionality:
- Prometheus client → PrometheusQueryTool
- Loki client → LokiQueryTool
- Jaeger client → JaegerQueryTool
- Vector DB → VectorSearchTool
- Bedrock LLM → RCAAnalysisTool

### 4. **LLM Integration**
Uses AWS Bedrock Claude:
- Model: `claude-3-5-sonnet-20241022-v2:0`
- Region: `us-east-1`
- Streaming support
- Token tracking

## Benefits Over Traditional Approach

### Traditional (Current)
```python
# Hardcoded workflow
prometheus_data = await fetch_prometheus()
loki_data = await fetch_loki()
jaeger_data = await fetch_jaeger()
rca = await generate_rca(prometheus_data, loki_data, jaeger_data)
```

### LangChain/LangGraph
```python
# Agent decides what to do
orchestrator = OrchestratorGraph()
result = orchestrator.investigate(incident_data)
# Agents autonomously:
# - Decide which tools to use
# - Adapt based on findings
# - Validate results
# - Retry if needed
```

## Advantages

1. **Autonomous Decision Making**: Agents decide which tools to use based on context
2. **Adaptive Workflow**: Can adapt strategy based on intermediate results
3. **Explainable**: Full reasoning trace in investigation steps
4. **Extensible**: Easy to add new tools and agents
5. **Industry Standard**: LangChain/LangGraph is widely adopted
6. **Production Ready**: Built-in error handling, retries, validation

## Example Usage

```python
from app.agents_langchain.orchestrator_graph import OrchestratorGraph

# Initialize orchestrator
orchestrator = OrchestratorGraph()

# Trigger investigation
incident_data = {
    "incident_id": "INC-001",
    "service": "payment-service",
    "detected_at": "2024-11-29T10:00:00Z",
    "severity": "critical"
}

# Run autonomous investigation
result = orchestrator.investigate(incident_data)

# Result contains:
# - RCA report
# - Investigation steps (audit trail)
# - Observability data
# - Similar incidents
```

## Integration Points

### Current System
- Uses existing Prometheus/Loki/Jaeger clients
- Uses existing Vector DB agent
- Uses existing Bedrock integration
- **No changes to existing code**

### New Capabilities
- Autonomous agent decision making
- Adaptive workflows
- Multi-agent coordination
- State management
- Reasoning traces

## Future Enhancements

1. **More Agents**:
   - Remediation Agent (auto-fix)
   - Communication Agent (Slack notifications)
   - Learning Agent (feedback loop)

2. **Advanced Workflows**:
   - Parallel agent execution
   - Human-in-the-loop
   - Multi-stage validation

3. **Enhanced Tools**:
   - Kubernetes API tool
   - AWS CloudWatch tool
   - GitHub API tool (for code analysis)

## Conclusion

This LangChain/LangGraph architecture provides:
- ✅ Industry-standard agent framework
- ✅ Autonomous decision making
- ✅ Adaptive workflows
- ✅ Full observability
- ✅ Production-ready patterns
- ✅ Easy to demonstrate to jury

**Status**: Ready for demonstration (not integrated into main flow)