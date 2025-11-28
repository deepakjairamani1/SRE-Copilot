# SRE Copilot Platform

An observability platform for Site Reliability Engineering built for hackathon MVP.

## Architecture

- **Jaeger**: Distributed tracing storage and UI
- **Prometheus**: Metrics collection and storage with remote-write API
- **Loki**: Log aggregation and storage
- **Grafana**: Unified observability dashboard
- **Redis**: Cache and session storage

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

## Development

```bash
# Stop services
cd platform && docker compose down

# Reset data (removes volumes)
cd platform && docker compose down -v

# Update services
cd platform && docker compose pull && docker compose up -d
```