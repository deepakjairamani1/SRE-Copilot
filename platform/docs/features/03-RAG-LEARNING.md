# RAG-Powered Learning System

## Overview

The platform learns from every incident and uses past knowledge to improve future investigations.

## How It Works

### 1. Keyword Extraction

**From Current Incident**:
- Metrics with critical/warning status → Extract metric names
- Error logs → Extract meaningful words (>4 chars)
- Traces → Extract operation names

**Example**:
```
Metrics: http_error_rate_percent (critical)
Logs: "Database connection refused"
Traces: "GET /api/users"

Keywords: ['http', 'error', 'rate', 'database', 'connection', 'refused']
```

### 2. Similarity Matching

**Algorithm**: Jaccard Similarity
```
similarity = (intersection / union) × 100
```

**Example**:
```
Current:  ['http', 'error', 'rate', 'timeout']
Past:     ['http', 'error', 'rate', 'latency']

Intersection: 3 (http, error, rate)
Union: 5 (http, error, rate, timeout, latency)
Similarity: 3/5 × 100 = 60%
```

**Threshold**: ≥60% required for match

### 3. Quality Filter

**LLM Decides** if incident is worth learning:

**Criteria**:
- ✅ Novel issue (not seen before)
- ✅ Clear root cause identified
- ✅ Actionable fix provided
- ✅ Successful resolution

**Example Decision**:
```json
{
  "worth_learning": true,
  "reason": "Clear root cause with actionable fix",
  "keywords": ["database-connection", "connection-refused", "retry-mechanism"]
}
```

### 4. Storage

**Only worthy incidents** are saved to knowledge base:

**File**: `data/learning/incidents/{incident_id}.json`
```json
{
  "incident_id": "INC-XXX",
  "title": "Database Connection Refused",
  "service": "core-athenamind",
  "root_cause": "PostgreSQL service down",
  "fix_applied": "Restart database service",
  "keywords": ["database-connection", "connection-refused"],
  "learning_reason": "Clear root cause with actionable fix"
}
```

## Retrieval Process

### Step 1: Extract Keywords from Current Incident
```
Current incident → Observability data → Keywords
```

### Step 2: Search Knowledge Base
```
For each past incident:
  - Check if same service ✓
  - Calculate keyword similarity
  - If ≥60% → Include in context
```

### Step 3: Rank by Similarity
```
Sort by similarity score (highest first)
Take top 3 matches
```

### Step 4: Provide to LLM
```
Past Incident: INC-XXX
Title: Database Connection Refused
Root Cause: PostgreSQL service down
Fix Applied: Restart database service
Similarity: 75%
```

## Benefits

### 1. High-Quality Knowledge Base
- Only valuable incidents stored
- No noise from trivial issues
- LLM-validated learning value

### 2. Relevant Matches
- 60% threshold prevents false positives
- Service-specific matching
- Keyword-based (not just title)

### 3. Continuous Improvement
- Every incident improves the system
- Past fixes recommended for similar issues
- Knowledge compounds over time

### 4. Transparent Matching
```
Current keywords: ['http', 'error', 'rate']
Found 1 similar incident (75% match)
  • INC-XXX: 75% match - High Error Rate...
```

## Example Scenario

### Incident 1: Database Connection Issue
```
Keywords: ['database', 'connection', 'refused', 'postgresql']
Worth Learning: YES
Reason: Clear root cause, actionable fix
```

### Incident 2: Similar Database Issue
```
Current Keywords: ['database', 'connection', 'timeout', 'pool']
Past Keywords: ['database', 'connection', 'refused', 'postgresql']

Similarity: 50% (2/4 match)
Result: Not included (below 60% threshold) ✓
```

### Incident 3: Exact Match
```
Current Keywords: ['database', 'connection', 'refused', 'retry']
Past Keywords: ['database', 'connection', 'refused', 'postgresql']

Similarity: 75% (3/4 match)
Result: Included in context ✓
LLM sees past fix and recommends it
```

## Implementation

**File**: `app/agents/rca_agent.py`

**Key Methods**:
- `_extract_current_keywords()` - Extract from observability data
- `_calculate_keyword_similarity()` - Jaccard similarity
- `_fetch_similar_incidents()` - RAG retrieval
- `_save_incident_for_learning()` - Quality-filtered storage

## Metrics

| Metric | Value |
|--------|-------|
| Match Threshold | 60% |
| Max Similar Incidents | 3 |
| Keyword Sources | Metrics + Logs + Traces |
| Quality Filter | LLM-validated |
| Storage Format | JSON |
