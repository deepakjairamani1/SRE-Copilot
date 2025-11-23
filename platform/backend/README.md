# SRE Copilot Backend API

FastAPI backend for the SRE Copilot platform with configuration management and health monitoring.

## Quick Start

```bash
# Start backend with observability stack
cd platform && docker compose up -d --build backend

# Check backend logs
docker compose logs -f backend

# Test health endpoint
curl http://localhost:7474/health
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |
| `/debug/config` | GET | View current configuration |
| `/docs` | GET | Interactive API documentation |

## Environment Variables

Create a `.env` file in the platform directory:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional (defaults provided)
DB_URL=sqlite:////data/sre_copilot.db
REDIS_URL=redis://redis:6379
ENV=dev
```

## Local Development

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run locally (outside Docker)
cd backend && uvicorn app.main:app --reload --port 7474

# Test endpoints
curl http://localhost:7474/health
curl http://localhost:7474/debug/config
```

## Hot Reload

The backend supports hot reload in Docker:
1. Make changes to files in `backend/app/`
2. Changes are automatically reflected (volume mount)
3. Check logs: `docker compose logs -f backend`

## Architecture

- **Pydantic Settings**: Type-safe configuration management
- **SQLAlchemy**: Database ORM with SQLite
- **FastAPI**: Modern async web framework
- **CORS**: Configured for frontend at localhost:3000