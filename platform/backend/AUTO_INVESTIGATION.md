# Auto-Investigation System

Automatically triggers RCA investigations when CPU/RAM exceeds 90% or consecutive error logs are detected. Sends alerts to Slack only for high-severity issues (>0.6 confidence score).

## Features

- **CPU/RAM Monitoring**: Triggers when utilization > 90%
- **Error Log Detection**: Triggers after 3-4 consecutive error log batches
- **Severity Filtering**: Only sends to Slack if severity score > 0.6 (prevents false alerts)
- **Automatic RCA**: Runs full investigation with LLM analysis
- **Slack Integration**: Sends formatted incident reports

## Quick Start

### 1. Configure Slack Webhook (Optional)

```bash
# Add to platform/backend/.env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 2. Start Auto-Investigation

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

### 3. Check Status

```bash
curl http://localhost:8000/api/auto-investigation/status
```

### 4. Stop Monitoring

```bash
curl -X POST http://localhost:8000/api/auto-investigation/stop
```

## API Endpoints

### POST `/api/auto-investigation/start`

Start automatic monitoring with configuration.

**Request Body:**
```json
{
  "enabled": true,
  "slack_webhook_url": "https://hooks.slack.com/services/...",
  "check_interval": 30,
  "cpu_threshold": 90.0,
  "ram_threshold": 90.0,
  "consecutive_errors_threshold": 3
}
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

### POST `/api/auto-investigation/stop`

Stop automatic monitoring.

**Response:**
```json
{
  "status": "stopped"
}
```

### GET `/api/auto-investigation/status`

Get current monitoring status.

**Response:**
```json
{
  "status": "running",
  "running": true,
  "investigation_in_progress": false,
  "config": {
    "check_interval": 30,
    "cpu_threshold": 90.0,
    "ram_threshold": 90.0,
    "consecutive_errors_threshold": 3,
    "slack_enabled": true
  }
}
```

### POST `/api/auto-investigation/test-trigger`

Test trigger evaluation without starting investigation.

**Response:**
```json
{
  "trigger_status": {
    "should_investigate": false,
    "metrics": {
      "cpu_usage": 45.2,
      "ram_usage": 62.1,
      "cpu_alert": false,
      "ram_alert": false,
      "alert_triggered": false
    },
    "logs": {
      "error_count": 2,
      "consecutive_errors": false,
      "buffer_size": 2,
      "alert_triggered": false
    }
  },
  "would_investigate": false
}
```

## How It Works

### 1. Monitoring Loop

Every 30 seconds (configurable):
- Check CPU and RAM utilization from Prometheus
- Check error logs from Loki
- Evaluate if investigation should trigger

### 2. Trigger Conditions

Investigation triggers when **ANY** of these conditions are met:
- CPU usage > 90% (configurable)
- RAM usage > 90% (configurable)
- 3+ consecutive error log batches detected (configurable)

### 3. Investigation Flow

When triggered:
1. Generate unique incident ID (e.g., `AUTO-A1B2C3D4`)
2. Run full RCA investigation with LLM
3. Calculate severity score (0.0-1.0) from confidence score
4. If severity > 0.6: Send to Slack
5. If severity ≤ 0.6: Log and ignore (false alert)

### 4. Severity Filtering

**Why filter by severity?**
- CPU spikes can be temporary (e.g., scheduled jobs)
- Minor errors may not require immediate attention
- Prevents alert fatigue from false positives

**Severity Thresholds:**
- `> 0.8`: Critical (🔴 Red alert in Slack)
- `0.6 - 0.8`: High (🟠 Orange alert in Slack)
- `≤ 0.6`: Low/False alert (ignored, not sent to Slack)

## Slack Message Format

```
🔴 Incident Alert: High CPU Usage Detected

Incident ID: AUTO-A1B2C3D4
Severity Score: 0.85/1.0
Severity: CRITICAL
User Impact: Service degradation possible

Root Cause:
CPU usage exceeded 95% due to memory leak in background worker

Immediate Actions:
• Restart background worker service
• Scale up worker instances
• Enable memory profiling
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `check_interval` | 30 | Seconds between checks |
| `cpu_threshold` | 90.0 | CPU % to trigger investigation |
| `ram_threshold` | 90.0 | RAM % to trigger investigation |
| `consecutive_errors_threshold` | 3 | Number of error batches to trigger |
| `slack_webhook_url` | None | Slack webhook for notifications |

## Example: Simulating High CPU

```bash
# Generate CPU load
stress-ng --cpu 4 --timeout 60s

# Monitor triggers
watch -n 5 'curl -s http://localhost:8000/api/auto-investigation/test-trigger | jq'
```

## Example: Simulating Error Logs

```python
import logging
import time

logger = logging.getLogger(__name__)

# Generate consecutive errors
for i in range(5):
    logger.error(f"Simulated error {i}")
    time.sleep(10)
```

## Troubleshooting

### Auto-investigation not triggering

1. Check status: `curl http://localhost:8000/api/auto-investigation/status`
2. Test triggers: `curl -X POST http://localhost:8000/api/auto-investigation/test-trigger`
3. Verify Prometheus/Loki connectivity
4. Check logs: `docker compose logs -f backend`

### Slack notifications not sending

1. Verify webhook URL is correct
2. Check severity score in logs
3. Ensure severity > 0.6
4. Test webhook manually:
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}'
```

### Too many false alerts

Increase thresholds:
```json
{
  "cpu_threshold": 95.0,
  "ram_threshold": 95.0,
  "consecutive_errors_threshold": 5
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Auto-Investigation                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Monitor    │──────│ Prometheus   │                     │
│  │              │      │  (CPU/RAM)   │                     │
│  │  - CPU/RAM   │      └──────────────┘                     │
│  │  - Errors    │                                            │
│  │  - Triggers  │      ┌──────────────┐                     │
│  └──────┬───────┘──────│     Loki     │                     │
│         │              │ (Error Logs) │                     │
│         │              └──────────────┘                     │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │  Evaluate    │                                           │
│  │  Triggers    │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │  RCA Agent   │──────│     LLM      │                    │
│  │ Investigation│      │   Analysis   │                    │
│  └──────┬───────┘      └──────────────┘                    │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │   Severity   │                                           │
│  │   Filter     │                                           │
│  │   (> 0.6)    │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │    Slack     │                                           │
│  │ Notification │                                           │
│  └──────────────┘                                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

1. **Start with conservative thresholds** (90%) and adjust based on your environment
2. **Monitor false positive rate** - if too high, increase thresholds
3. **Set up Slack webhook** for production environments
4. **Review ignored alerts** periodically to tune severity filtering
5. **Use DynamoDB tracking** to prevent duplicate investigations
