# Quick Start: Auto-Investigation

Automatically trigger RCA investigations when CPU/RAM > 90% or error logs spike. Sends Slack alerts only for high-severity issues (>0.6).

## 1. Setup Slack Webhook (Optional)

```bash
# Get webhook from: https://api.slack.com/messaging/webhooks
# Add to platform/backend/.env
echo 'SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL' >> platform/backend/.env
```

## 2. Start Backend

```bash
cd platform
docker compose up -d backend
```

## 3. Start Auto-Investigation

```bash
curl -X POST http://localhost:8000/api/auto-investigation/start \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "check_interval": 30,
    "cpu_threshold": 90.0,
    "ram_threshold": 90.0,
    "consecutive_errors_threshold": 3
  }'
```

**Response:**
```json
{
  "status": "started",
  "config": {
    "check_interval": 30,
    "cpu_threshold": 90.0,
    "ram_threshold": 90.0,
    "consecutive_errors_threshold": 3,
    "slack_enabled": true
  }
}
```

## 4. Monitor Status

```bash
# Check status
curl http://localhost:8000/api/auto-investigation/status | jq

# Watch continuously
watch -n 5 'curl -s http://localhost:8000/api/auto-investigation/status | jq'
```

## 5. Test Triggers

```bash
# Test without starting investigation
curl -X POST http://localhost:8000/api/auto-investigation/test-trigger | jq
```

## How It Works

### Triggers Investigation When:
- ✅ CPU usage > 90%
- ✅ RAM usage > 90%
- ✅ 3+ consecutive error log batches

### Sends to Slack When:
- ✅ Severity score > 0.6 (high confidence)
- ❌ Severity score ≤ 0.6 (false alert, ignored)

### Investigation Flow:
```
Monitor (every 30s)
  ↓
Check CPU/RAM + Error Logs
  ↓
Trigger? → Run RCA Investigation
  ↓
Calculate Severity Score (0.0-1.0)
  ↓
Severity > 0.6? → Send to Slack
  ↓
Severity ≤ 0.6? → Ignore (false alert)
```

## Example: Simulate High CPU

```bash
# Install stress-ng
sudo apt-get install stress-ng

# Generate CPU load
stress-ng --cpu 4 --timeout 60s

# Watch for trigger
watch -n 5 'curl -s http://localhost:8000/api/auto-investigation/test-trigger | jq'
```

## Example: Simulate Error Logs

```python
# In your application
import logging
import time

logger = logging.getLogger(__name__)

for i in range(5):
    logger.error(f"Simulated error {i}")
    time.sleep(10)  # Wait 10s between errors
```

## Stop Auto-Investigation

```bash
curl -X POST http://localhost:8000/api/auto-investigation/stop
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `check_interval` | 30 | Seconds between checks |
| `cpu_threshold` | 90.0 | CPU % to trigger |
| `ram_threshold` | 90.0 | RAM % to trigger |
| `consecutive_errors_threshold` | 3 | Error batches to trigger |
| `slack_webhook_url` | None | Slack webhook URL |

## Slack Alert Example

```
🔴 Incident Alert: High CPU Usage Detected

Incident ID: AUTO-A1B2C3D4
Severity Score: 0.85/1.0
Severity: CRITICAL
User Impact: Service degradation possible

Root Cause:
CPU usage exceeded 95% due to memory leak

Immediate Actions:
• Restart service
• Scale up instances
• Enable profiling
```

## Troubleshooting

### Not triggering?
```bash
# Check current metrics
curl http://localhost:8000/api/auto-investigation/test-trigger | jq

# Check logs
docker compose logs -f backend
```

### Slack not working?
```bash
# Test webhook manually
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}'
```

### Too many false alerts?
```bash
# Increase thresholds
curl -X POST http://localhost:8000/api/auto-investigation/start \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "cpu_threshold": 95.0,
    "ram_threshold": 95.0,
    "consecutive_errors_threshold": 5
  }'
```

## Full Documentation

See [AUTO_INVESTIGATION.md](platform/backend/AUTO_INVESTIGATION.md) for complete details.
