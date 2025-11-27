# Development Guide

Complete guide for setting up and developing Albeyla.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Frontend Development](#frontend-development)
- [Backend Development](#backend-development)
- [Testing](#testing)
- [Debugging](#debugging)
- [Common Issues](#common-issues)

---

## Prerequisites

### Required Software

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Node.js** 18+ and **npm** 9+
- **Python** 3.11+
- **Git** 2.30+

### AWS Account Setup

1. Create AWS account
2. Enable AWS Bedrock access
3. Request Claude 3.5 Sonnet model access
4. Create IAM user with Bedrock permissions
5. Generate access keys

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/albeyla.git
cd albeyla/platform
```

### 2. Start Infrastructure

```bash
cd platform
docker compose up -d
```

**Services Started:**
- Prometheus: http://localhost:9090
- Loki: http://localhost:3100
- Jaeger: http://localhost:16686
- Grafana: http://localhost:3001 (admin/admin)
- Redis: localhost:6379

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your AWS credentials
nano .env
```

**.env Configuration:**
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

PROMETHEUS_URL=http://localhost:9090
LOKI_URL=http://localhost:3100
JAEGER_URL=http://localhost:16686
REDIS_HOST=localhost
REDIS_PORT=6379

DATABASE_URL=sqlite:///./albeyla.db
LOG_LEVEL=INFO
```

**Start Backend:**
```bash
uvicorn app.main:app --reload --port 7474
```

Backend running at: http://localhost:7474

### 4. Setup Frontend

```bash
cd sre-copilot-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend running at: http://localhost:5173

---

## Frontend Development

### Project Structure

```
sre-copilot-frontend/
├── src/
│   ├── components/      # React components
│   ├── pages/           # Page components
│   ├── hooks/           # Custom hooks
│   ├── lib/             # Utilities
│   ├── types/           # TypeScript types
│   ├── App.tsx          # Main app
│   └── main.tsx         # Entry point
├── public/              # Static assets
├── index.html           # HTML template
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── tailwind.config.js   # Tailwind config
└── vite.config.ts       # Vite config
```

### Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

### Adding New Components

1. **Create Component File:**
```bash
touch src/components/ui/NewComponent.tsx
```

2. **Component Template:**
```typescript
import { cn } from '../../lib/utils'

interface NewComponentProps {
  className?: string
  children: React.ReactNode
}

export function NewComponent({ className, children }: NewComponentProps) {
  return (
    <div className={cn('base-classes', className)}>
      {children}
    </div>
  )
}
```

3. **Export Component:**
```typescript
// src/components/ui/index.ts
export { NewComponent } from './NewComponent'
```

### Adding New Pages

1. **Create Page File:**
```bash
touch src/pages/NewPage.tsx
```

2. **Page Template:**
```typescript
import { Header } from '../components/layout/Header'
import { Card } from '../components/ui/Card'

export default function NewPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-8">
        <Card>
          <h1>New Page</h1>
        </Card>
      </main>
    </div>
  )
}
```

3. **Add Route:**
```typescript
// src/App.tsx
import NewPage from './pages/NewPage'

<Route path="/new-page" element={<NewPage />} />
```

### Adding New Hooks

1. **Create Hook File:**
```bash
touch src/hooks/useNewData.ts
```

2. **Hook Template:**
```typescript
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export function useNewData() {
  return useQuery({
    queryKey: ['newData'],
    queryFn: async () => {
      const { data } = await api.get('/api/new-endpoint')
      return data
    },
    refetchInterval: 300000, // 5 minutes
    retry: 1
  })
}
```

### Styling Guidelines

**Use Tailwind Classes:**
```tsx
<div className="flex items-center gap-4 p-6 rounded-xl bg-white shadow-lg">
```

**Custom Classes (index.css):**
```css
.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
}
```

**Dynamic Classes:**
```tsx
<div className={cn(
  'base-class',
  isActive && 'active-class',
  className
)}>
```

---

## Backend Development

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── routers/             # API routes
│   ├── services/            # Business logic
│   ├── models/              # Data models
│   ├── database/            # Database layer
│   └── utils/               # Utilities
├── data/                    # Mock data
├── logs/                    # Application logs
├── requirements.txt         # Dependencies
└── .env                     # Environment variables
```

### Available Commands

```bash
# Start development server
uvicorn app.main:app --reload --port 7474

# Run with specific log level
LOG_LEVEL=DEBUG uvicorn app.main:app --reload --port 7474

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

### Adding New Endpoints

1. **Create Router File:**
```bash
touch app/routers/new_endpoint.py
```

2. **Router Template:**
```python
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter(prefix="/api/new", tags=["new"])

@router.get("/items")
async def get_items():
    """Get all items."""
    try:
        # Your logic here
        return {"items": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/items")
async def create_item(item: dict):
    """Create new item."""
    try:
        # Your logic here
        return {"id": 1, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

3. **Register Router:**
```python
# app/main.py
from app.routers import new_endpoint

app.include_router(new_endpoint.router)
```

### Adding New Services

1. **Create Service File:**
```bash
touch app/services/new_service.py
```

2. **Service Template:**
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class NewService:
    def __init__(self):
        self.config = {}
    
    async def fetch_data(self, param: str) -> dict:
        """Fetch data from external source."""
        try:
            # Your logic here
            return {"data": []}
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise
    
    async def process_data(self, data: dict) -> dict:
        """Process fetched data."""
        try:
            # Your logic here
            return {"processed": True}
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            raise
```

### Database Operations

**Create Model:**
```python
# app/models/new_model.py
from pydantic import BaseModel
from datetime import datetime

class NewModel(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**Create Repository:**
```python
# app/database/repositories.py
class NewRepository:
    def __init__(self, db):
        self.db = db
    
    async def create(self, data: dict):
        # Insert logic
        pass
    
    async def get_by_id(self, id: int):
        # Select logic
        pass
    
    async def update(self, id: int, data: dict):
        # Update logic
        pass
    
    async def delete(self, id: int):
        # Delete logic
        pass
```

### Caching with Redis

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Set cache
redis_client.setex(
    'cache_key',
    30,  # TTL in seconds
    json.dumps(data)
)

# Get cache
cached = redis_client.get('cache_key')
if cached:
    data = json.loads(cached)
```

### AWS Bedrock Integration

```python
import boto3
import json

bedrock = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1'
)

def call_claude(prompt: str) -> str:
    """Call Claude 3.5 Sonnet."""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.3,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']
```

---

## Testing

### Frontend Testing

**Unit Tests:**
```typescript
// src/components/ui/__tests__/Button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from '../Button'

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
  
  it('calls onClick when clicked', () => {
    const onClick = jest.fn()
    render(<Button onClick={onClick}>Click</Button>)
    screen.getByText('Click').click()
    expect(onClick).toHaveBeenCalled()
  })
})
```

**Run Tests:**
```bash
npm test
npm test -- --coverage
```

### Backend Testing

**Unit Tests:**
```python
# tests/test_services.py
import pytest
from app.services.prometheus_service import PrometheusService

@pytest.mark.asyncio
async def test_fetch_metrics():
    service = PrometheusService()
    metrics = await service.fetch_metrics()
    assert metrics is not None
    assert 'host_metrics' in metrics

@pytest.mark.asyncio
async def test_fetch_metrics_error():
    service = PrometheusService(url="http://invalid")
    with pytest.raises(Exception):
        await service.fetch_metrics()
```

**API Tests:**
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    assert "host_metrics" in response.json()
```

**Run Tests:**
```bash
pytest
pytest -v
pytest --cov=app
pytest -k test_metrics
```

---

## Debugging

### Frontend Debugging

**Browser DevTools:**
1. Open Chrome DevTools (F12)
2. Go to Sources tab
3. Set breakpoints in code
4. Inspect network requests
5. Check console for errors

**React DevTools:**
```bash
# Install extension
# Chrome: React Developer Tools
# Firefox: React Developer Tools
```

**Debug Hooks:**
```typescript
import { useEffect } from 'react'

useEffect(() => {
  console.log('Component mounted')
  console.log('Data:', data)
}, [data])
```

### Backend Debugging

**Python Debugger:**
```python
import pdb

def my_function():
    pdb.set_trace()  # Breakpoint
    # Your code here
```

**Logging:**
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

**FastAPI Debug Mode:**
```python
# app/main.py
app = FastAPI(debug=True)
```

**Check Logs:**
```bash
# Backend logs
tail -f backend/logs/app.log

# Docker logs
docker compose logs -f backend
docker compose logs -f prometheus
```

---

## Common Issues

### Frontend Issues

**Issue: Module not found**
```bash
# Solution: Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue: Port already in use**
```bash
# Solution: Kill process on port 5173
lsof -ti:5173 | xargs kill -9
# Or use different port
npm run dev -- --port 5174
```

**Issue: TypeScript errors**
```bash
# Solution: Restart TypeScript server
# In VSCode: Cmd+Shift+P → "TypeScript: Restart TS Server"
```

### Backend Issues

**Issue: AWS Bedrock access denied**
```bash
# Solution: Check IAM permissions
# Ensure user has bedrock:InvokeModel permission
# Verify model access is enabled in AWS console
```

**Issue: Prometheus connection failed**
```bash
# Solution: Check if Prometheus is running
docker compose ps
curl http://localhost:9090/-/healthy

# Restart if needed
docker compose restart prometheus
```

**Issue: Redis connection error**
```bash
# Solution: Check Redis status
docker compose ps redis
redis-cli ping

# Restart if needed
docker compose restart redis
```

**Issue: Database locked**
```bash
# Solution: Close all connections
# For SQLite, delete .db-journal file
rm backend/albeyla.db-journal
```

### Docker Issues

**Issue: Container won't start**
```bash
# Solution: Check logs
docker compose logs [service-name]

# Rebuild container
docker compose build [service-name]
docker compose up -d [service-name]
```

**Issue: Port conflicts**
```bash
# Solution: Change ports in docker-compose.yml
# Or stop conflicting services
docker ps
docker stop [container-id]
```

**Issue: Out of disk space**
```bash
# Solution: Clean up Docker
docker system prune -a
docker volume prune
```

---

## Environment Variables

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:7474
VITE_APP_NAME=Albeyla
```

### Backend (.env)
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Observability Services
PROMETHEUS_URL=http://localhost:9090
LOKI_URL=http://localhost:3100
JAEGER_URL=http://localhost:16686

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Database
DATABASE_URL=sqlite:///./albeyla.db

# Application
API_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:5173"]
```

---

## Git Workflow

### Branch Naming
```
feature/add-new-component
bugfix/fix-metrics-display
hotfix/critical-security-issue
refactor/improve-performance
docs/update-readme
```

### Commit Messages
```
feat: add new incident filtering
fix: resolve null pointer in metrics
docs: update API documentation
refactor: improve RCA agent logic
test: add unit tests for hooks
chore: update dependencies
```

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots
(if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

---

## Performance Tips

### Frontend
1. Use React.memo for expensive components
2. Implement virtualization for long lists
3. Lazy load routes and components
4. Optimize images and assets
5. Use production build for testing

### Backend
1. Use async/await for I/O operations
2. Implement caching for frequent queries
3. Use connection pooling
4. Optimize database queries
5. Enable response compression

---

## Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [AWS Bedrock Guide](https://docs.aws.amazon.com/bedrock/)
- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Loki Docs](https://grafana.com/docs/loki/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
