# Agentic AI Workflow

## Overview

The RCA Agent implements an autonomous investigation loop: **Plan → Act → Check → Adapt**

## The Agent Loop

### 1. PLAN Phase
**What**: Agent decides investigation strategy  
**How**: Creates action list based on incident type  
**Output**: List of data sources to query

```
Actions:
- Query Prometheus for metrics
- Query Loki for error logs
- Query Jaeger for slow traces
- Search similar past incidents (RAG)
```

### 2. ACT Phase
**What**: Agent executes plan in parallel  
**How**: Fetches data from all sources simultaneously  
**Output**: Metrics, logs, traces, similar incidents

**Performance**:
- Parallel: 3-5 seconds
- Sequential: 15+ seconds
- **Speedup: 3-5x faster**

### 3. CHECK Phase
**What**: Agent validates data quality  
**How**: Checks if sufficient data available  
**Output**: Quality score and missing sources

**Validation Rules**:
- Need ≥2 data sources
- Each source must not have errors
- If insufficient → trigger ADAPT

### 4. ADAPT Phase
**What**: Agent adjusts based on findings  
**How**: Retries, fallbacks, or proceeds  
**Output**: Final decision on analysis method

**Adaptation Strategies**:
- Insufficient data → Retry with wider time range
- LLM fails → Fallback to rule-based analysis
- Success → Generate comprehensive RCA

## Why Agentic?

**Traditional Approach**:
```
Query → LLM → Done
```
- No validation
- No retry logic
- No learning

**Agentic Approach**:
```
Plan → Act → Check → Adapt → Learn
```
- ✅ Validates data quality
- ✅ Handles failures gracefully
- ✅ Learns from every incident
- ✅ Autonomous decision-making

## Implementation

**File**: `app/agents/rca_agent.py`

**Key Methods**:
- `investigate()` - Main agent loop
- `_create_investigation_plan()` - PLAN phase
- `_fetch_*_data()` - ACT phase
- `_validate_data()` - CHECK phase
- `_generate_rca_with_rag()` - ADAPT phase

## Logging

Every step is logged for visibility:
```
INFO - [INC-XXX] Planning investigation strategy...
INFO - [INC-XXX] Starting parallel data collection...
INFO - [INC-XXX] Data validation: sufficient=True
INFO - [INC-XXX] Generating RCA with AI...
INFO - [INC-XXX] RCA generation complete. Confidence: 0.8
```

## Benefits

1. **Autonomous**: Makes decisions without human intervention
2. **Resilient**: Handles failures and retries automatically
3. **Transparent**: Every step is logged and traceable
4. **Adaptive**: Adjusts strategy based on data quality
5. **Learning**: Improves with every investigation
