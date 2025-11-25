# Multi-LLM Provider Support

## Supported Providers

| Provider | Model | Token Limit | Cost | Status |
|----------|-------|-------------|------|--------|
| **Groq** | llama-3.3-70b-versatile | 8,192 | Free | ✅ Default |
| **Claude** | claude-sonnet-4 | 200,000 | $3/M tokens | ✅ |
| **GPT-4o** | gpt-4o | 128,000 | $2.5/M tokens | ✅ |
| **Gemini** | gemini-2.0-flash-exp | 1,000,000 | Free | ✅ |
| **Grok** | grok-beta | 8,192 | $5/M tokens | ✅ |

## Configuration

**File**: `backend/.env`
```bash
LLM_PROVIDER=groq
LLM_API_KEY=gsk_your_key_here
LLM_MODEL=llama-3.3-70b-versatile  # Optional
```

## Provider Selection

### Groq (Default)
**Why**: Free tier, fast inference, good quality

**Use When**:
- Cost is a concern
- Need fast responses
- Prompts fit in 8K tokens

**Setup**:
```bash
LLM_PROVIDER=groq
LLM_API_KEY=gsk_xxx
```

### Claude
**Why**: Highest quality, largest context

**Use When**:
- Need best analysis quality
- Have large prompts (>8K tokens)
- Budget allows

**Setup**:
```bash
LLM_PROVIDER=claude
LLM_API_KEY=sk-ant-xxx
LLM_MODEL=claude-sonnet-4-20250514
```

### GPT-4o
**Why**: Good balance of quality and cost

**Use When**:
- Need reliable performance
- Moderate prompt sizes
- OpenAI ecosystem preferred

**Setup**:
```bash
LLM_PROVIDER=gpt
LLM_API_KEY=sk-xxx
LLM_MODEL=gpt-4o
```

### Gemini
**Why**: Free tier, massive context window

**Use When**:
- Cost is a concern
- Have very large prompts
- Google ecosystem preferred

**Setup**:
```bash
LLM_PROVIDER=gemini
LLM_API_KEY=AIzaSyxxx
LLM_MODEL=gemini-2.0-flash-exp
```

### Grok
**Why**: xAI's latest model

**Use When**:
- Want to try latest models
- Budget allows
- Need fast inference

**Setup**:
```bash
LLM_PROVIDER=grok
LLM_API_KEY=xai-xxx
LLM_MODEL=grok-beta
```

## Automatic Fallback

If LLM fails, system automatically falls back to rule-based analysis:

```
LLM Call → Error → Rule-Based Analysis
```

**Rule-Based Logic**:
- Check CPU > 80% → High CPU issue
- Check error logs > 10 → Error burst
- Check slow traces → Latency issue

**Result**: 100% uptime, always provides analysis

## Cost Tracking

Every investigation tracks:
- Tokens used (input + output)
- Provider used
- Estimated cost

**Example**:
```json
{
  "llm_provider": "groq",
  "tokens_used": 2474,
  "cost_usd": 0.00
}
```

## Implementation

**File**: `app/agents/rca_agent.py`

**Key Methods**:
- `_call_llm()` - Router to provider
- `_call_groq()` - Groq implementation
- `_call_claude()` - Claude implementation
- `_call_openai()` - GPT implementation
- `_call_gemini()` - Gemini implementation
- `_call_grok()` - Grok implementation

## Error Handling

```python
try:
    response = await self._call_llm(prompt)
except Exception as e:
    logger.error(f"LLM failed: {e}")
    # Automatic fallback
    response = await self._rule_based_rca()
```

## Benefits

1. **Flexibility**: Choose provider based on needs
2. **Resilience**: Automatic fallback ensures uptime
3. **Cost Control**: Use free tiers or paid as needed
4. **Quality Options**: From fast/cheap to slow/expensive
5. **Future-Proof**: Easy to add new providers
