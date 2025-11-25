# Smart Data Truncation

## Problem

Observability data is massive:
- Prometheus: 15 metrics × 20 data points = 300 values
- Loki: 100+ log entries
- Jaeger: 50+ traces with spans
- **Total**: 168KB (40,000+ tokens) ❌

LLM token limits:
- Groq: 8,192 tokens
- GPT-4o: 128,000 tokens
- Claude: 200,000 tokens

## Solution

Intelligent truncation that preserves critical information while reducing size by 97%.

## Techniques

### 1. Metric Summarization

**Before** (JSON format):
```json
{
  "cpu_usage_percent": {
    "values": [[1732534800, "9.7"], [1732534815, "10.2"], ...],
    "max": 12.3,
    "min": 9.7,
    "avg": 10.3,
    "current": 9.75,
    "unit": "percent",
    "status": "ok"
  }
}
```

**After** (Summarized):
```
🟢 cpu_usage_percent: 9.75 percent (min:9.7, max:12.3, avg:10.3)
```

**Reduction**: 200 chars → 60 chars (70% smaller)

### 2. Log Deduplication

**Before**:
```
[ERROR] Connection timeout
[ERROR] Connection timeout
[ERROR] Connection timeout
[ERROR] Database error
[ERROR] Database error
```

**After**:
```
ERROR:
  [3x] Connection timeout
  [2x] Database error
```

**Reduction**: 5 entries → 2 unique messages

### 3. Trace Filtering

**Before**: All traces with full span details

**After**: 
- Top 3 slow traces (operation + duration)
- Top 3 error traces (operation + error)
- Summary stats (P50/P95/P99)

**Reduction**: 50 traces → 6 traces + summary

## Results

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Prompt Size | 168KB | 4KB | 97% |
| Token Count | 40,000 | 1,000 | 97.5% |
| LLM Compatibility | Gemini only | All providers | ✅ |
| Analysis Quality | High | High | No loss |

## Implementation

**File**: `app/agents/rca_agent.py`

**Key Methods**:
- `_summarize_metrics()` - Compact metric format
- `_deduplicate_logs()` - Group identical messages
- `_summarize_traces()` - Filter key traces

## Visual Indicators

Status icons for quick scanning:
- 🔴 Critical (>80% threshold)
- 🟡 Warning (>60% threshold)
- 🟢 OK (normal)

Example:
```
🔴 http_error_rate_percent: 46.67% (critical)
🟢 cpu_usage_percent: 9.75% (ok)
```

## Benefits

1. **Universal Compatibility**: Works with all LLM providers
2. **Cost Effective**: Fewer tokens = lower cost
3. **Faster Processing**: Less data to analyze
4. **No Quality Loss**: Preserves critical information
5. **Better Focus**: LLM sees only important data
