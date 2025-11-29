# SRE Copilot Platform

An observability platform for Site Reliability Engineering built for hackathon MVP.

## Architecture

- **Jaeger**: Distributed tracing storage and UI
- **Prometheus**: Metrics collection and storage with remote-write API
- **Loki**: Log aggregation and storage
- **Grafana**: Unified observability dashboard
- **Redis**: Cache and session storage
- **DynamoDB** (optional): Investigation tracking to prevent duplicate error analysis

## Quick Start

```bash
# Start all services
cd platform && docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

## Service Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3001 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Jaeger UI | http://localhost:16686 | - |
| Loki | http://localhost:3100 | - |
| Redis | localhost:6379 | - |

## API Endpoints

- **Prometheus Remote Write**: `http://localhost:9090/api/v1/write`
- **Jaeger OTLP gRPC**: `http://localhost:4317`
- **Jaeger OTLP HTTP**: `http://localhost:4318`
- **Loki Push**: `http://localhost:3100/loki/api/v1/push`

## Features

### Auto-Investigation (NEW)

Automatically triggers RCA investigations when:
- CPU/RAM utilization > 90%
- 3+ consecutive error log batches detected

Sends Slack alerts only for high-severity issues (confidence score > 0.6) to prevent false alerts.

**Quick Start:**
```bash
curl -X POST http://localhost:8000/api/auto-investigation/start \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "slack_webhook_url": "YOUR_WEBHOOK_URL"}'
```

📚 See [QUICKSTART_AUTO_INVESTIGATION.md](QUICKSTART_AUTO_INVESTIGATION.md) for setup guide

### DynamoDB Investigation Tracking (Optional)

Prevents duplicate error analysis by tracking the last investigation timestamp per service. Each investigation only fetches data since the last run, eliminating overlapping time windows.

**Quick Setup**:
```bash
# Add to platform/backend/.env
DYNAMODB_ENABLED=true
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

**Benefits**:
- ✅ No duplicate errors in investigations
- ✅ Reduced API costs (~$0.004/month)
- ✅ Better accuracy with clear timelines
- ✅ Graceful fallback if unavailable

📚 See [DYNAMODB_QUICKSTART.md](platform/backend/DYNAMODB_QUICKSTART.md) for setup guide

## Development

```bash
# Stop services
cd platform && docker compose down

# Reset data (removes volumes)
cd platform && docker compose down -v

# Update services
cd platform && docker compose pull && docker compose up -d
```