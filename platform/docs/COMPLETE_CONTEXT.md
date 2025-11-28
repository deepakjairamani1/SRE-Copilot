# Albeyla - Complete Context Documentation

**AI Context Reference Document**

This document contains the complete context of the Albeyla platform for AI-powered code assistance and development.

---

## Project Overview

**Name:** Albeyla (formerly SRE Copilot)  
**Purpose:** Autonomous incident investigation platform using AI-powered root cause analysis  
**Tech Stack:** React + TypeScript + FastAPI + AWS Bedrock + Observability Stack  
**Status:** MVP Complete  

---

## System Architecture

### High-Level Architecture

```
Frontend (React/TS) → Backend (FastAPI) → Observability Stack (Prometheus/Loki/Jaeger)
                           ↓
                      AWS Bedrock (Claude 3.5 Sonnet)
                           ↓
                      RCA Report Generation
```

### Services & Ports

- **Frontend:** http://localhost:5173 (Vite dev server)
- **Backend:** http://localhost:7474 (FastAPI)
- **Prometheus:** http://localhost:9090 (Metrics)
- **Loki:** http://localhost:3100 (Logs)
- **Jaeger:** http://localhost:16686 (Traces)
- **Grafana:** http://localhost:3001 (Visualization)
- **Redis:** localhost:6379 (Cache)

---

## Frontend Complete Context

### Technology Stack
- React 18.3
- TypeScript 5.5
- Vite 5.4
- TailwindCSS 3.4
- React Query (TanStack Query)
- React Router 6
- Framer Motion (animations)
- Recharts (charts)
- Sonner (toasts)
- Lucide React (icons)
- Axios (HTTP client)

### Project Structure
```
sre-copilot-frontend/
├── src/
│   ├── components/
│   │   ├── ui/                    # 10 reusable UI components
│   │   ├── layout/                # Header, Sidebar
│   │   └── features/              # MetricChart, RemediationActions, IncidentTimeline, ErrorBoundary
│   ├── pages/                     # 5 pages (Dashboard, IncidentsList, IncidentDetails, Investigate, NotFound)
│   ├── hooks/                     # 4 custom hooks (useMetrics, useIncidents, useLogs, useTraces)
│   ├── lib/                       # api.ts, utils.ts
│   ├── types/                     # TypeScript interfaces
│   ├── config.ts                  # Configuration constants
│   ├── index.css                  # Global styles + Tailwind
│   ├── App.tsx                    # Main app with routing
│   └── main.tsx                   # Entry point
├── public/                        # Static assets
├── index.html                     # HTML template
├── package.json                   # Dependencies
├── tsconfig.json                  # TypeScript config
├── tailwind.config.js             # Tailwind config
├── postcss.config.js              # PostCSS config
└── vite.config.ts                 # Vite config
```

### All Components

**UI Components (src/components/ui/):**
1. **Card.tsx** - Glassmorphism card container
   - Props: variant ('glass'|'solid'|'neumorphic'), hoverable, className
   - Features: Framer Motion hover animations

2. **Badge.tsx** - Status badge with colors
   - Props: variant ('ok'|'warning'|'critical'|'low'|'medium'|'high'), withDot
   - Features: Pulsing dot animation

3. **Button.tsx** - Customizable button
   - Props: variant ('primary'|'secondary'|'ghost'|'danger'), size ('sm'|'md'|'lg'), loading
   - Features: Loading spinner, disabled state

4. **StatCard.tsx** - Metric statistics card
   - Props: title, value, icon, color, trend
   - Features: Trend indicators (up/down arrows)

5. **LoadingSpinner.tsx** - Animated spinner
   - Props: size ('sm'|'md'|'lg'), message
   - Features: Lucide Loader2 with spin animation

6. **SkeletonCard.tsx** - Loading skeleton
   - Props: lines (number), className
   - Features: Pulse animation

7. **ProgressBar.tsx** - Animated progress bar
   - Props: progress (0-100), color, showLabel
   - Features: Framer Motion width animation

8. **PageTransition.tsx** - Page transition wrapper
   - Features: Fade + slide animation

9. **Toast.tsx** - Toast notification provider
   - Uses: Sonner library
   - Features: Glassmorphism styling, rich colors

**Layout Components (src/components/layout/):**
1. **Header.tsx** - Main navigation header
   - Features: Logo, nav links, notification bell, settings
   - Routes: Dashboard, Incidents, Investigate

2. **Sidebar.tsx** - Side navigation panel
   - Features: Menu items, active highlighting

**Feature Components (src/components/features/):**
1. **MetricChart.tsx** - Chart visualization
   - Uses: Recharts (AreaChart, LineChart)
   - Props: title, data, color, unit, type
   - Features: Gradient fills, custom tooltips

2. **RemediationActions.tsx** - Remediation steps display
   - Props: immediateActions, permanentFixes
   - Features: Copy-to-clipboard with toast feedback

3. **IncidentTimeline.tsx** - Event timeline
   - Props: timeline (array of events)
   - Features: Gradient visualization, source badges

4. **ErrorBoundary.tsx** - React error boundary
   - Features: Catches errors, displays friendly UI, refresh button

### All Pages

1. **Dashboard.tsx** - Main monitoring dashboard
   - Route: `/`
   - Features: Stats cards, host metrics, app metrics, charts, recent incidents
   - Data: useMetrics, useIncidents, useIncidentStats

2. **IncidentsList.tsx** - Incidents list with filtering
   - Route: `/incidents`
   - Features: Search, filters (severity/status/service), sorting, CSV export
   - Data: useIncidents, useIncidentStats

3. **IncidentDetails.tsx** - Detailed incident view
   - Route: `/incidents/:incident_id`
   - Features: Executive summary, timeline, RCA, remediation, technical details, impact, prevention
   - Data: useIncidentDetails

4. **Investigate.tsx** - Trigger new investigation
   - Route: `/investigate`
   - Features: Service selection, real-time progress, auto-redirect
   - Data: useTriggerInvestigation

5. **NotFound.tsx** - 404 error page
   - Route: `*` (catch-all)
   - Features: Friendly message, navigation buttons

### All Hooks

1. **useMetrics()** - Fetch observability metrics
   - Endpoint: GET /api/metrics
   - Polling: 5 minutes
   - Returns: host_metrics, otlp_metrics

2. **useIncidents(params)** - Fetch incidents list
   - Endpoint: GET /api/incidents
   - Params: severity, status, service, limit
   - Polling: 5 minutes

3. **useIncidentStats()** - Fetch incident statistics
   - Endpoint: GET /api/incidents/stats
   - Polling: 5 minutes
   - Returns: total, by_severity, by_service

4. **useIncidentDetails(incident_id)** - Fetch incident details
   - Endpoint: GET /api/incidents/{incident_id}
   - Returns: Complete incident with RCA report

5. **useTriggerInvestigation()** - Trigger RCA investigation
   - Endpoint: POST /api/rca/investigate
   - Mutation: Creates new incident
   - Returns: incident_id, result

6. **useLogs()** - Fetch logs from Loki
   - Endpoint: GET /api/logs
   - Polling: 5 minutes

7. **useTraces()** - Fetch traces from Jaeger
   - Endpoint: GET /api/traces
   - Polling: 5 minutes

### TypeScript Types

**Main Interfaces:**
```typescript
interface Incident {
  id: number
  incident_id: string
  service: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'resolved'
  title: string
  root_cause: string
  confidence_score: number
  detected_at: string
  resolved_at?: string
  duration_seconds: number
  cost_usd: number
  tokens_used: number
  investigation_steps: InvestigationStep[]
  rca_report: RCAReport
  observability_data: any
}

interface RCAReport {
  executive_summary: {
    title: string
    severity: string
    impact: string
    user_impact: string
  }
  timeline: TimelineEvent[]
  root_cause: {
    primary_cause: string
    contributing_factors: string[]
    evidence: Evidence[]
    confidence_score: number
  }
  technical_details: {
    affected_components: Component[]
    metrics_snapshot: Record<string, number>
  }
  impact_assessment: {
    severity: string
    users_affected: string
  }
  remediation: {
    immediate_actions: Action[]
    permanent_fixes: Fix[]
  }
  prevention: {
    code_changes: string[]
    monitoring_enhancements: string[]
  }
  potential_causes: PotentialCause[]
  confidence: {
    overall_score: number
    uncertainties: string[]
    recommendation: string
  }
  learning_metadata: {
    worth_learning: boolean
    reason: string
    keywords: string[]
  }
}
```

### Styling System

**Theme Colors:**
```css
--primary: #6366F1 (Indigo)
--accent: #8B5CF6 (Purple)
--success: #10B981 (Green)
--warning: #F59E0B (Amber)
--danger: #EF4444 (Red)
```

**Custom Classes:**
- `.glass-card` - Glassmorphism effect
- `.status-badge` - Status badge styling
- `.pulse-dot` - Pulsing dot animation
- `.hover-lift` - Hover lift effect
- `.animate-shimmer` - Shimmer loading

**Design System:**
- Glassmorphism UI (backdrop-blur, transparency)
- Smooth animations (Framer Motion)
- Responsive design (mobile-first)
- Consistent spacing (Tailwind)

### State Management

- **React Query** for server state
- **useState** for local state
- **useNavigate** for routing
- **Toast** for notifications

### Error Handling

- ErrorBoundary for React errors
- Toast notifications for user feedback
- Try-catch in async operations
- Fallback UI for loading/error states

---

## Backend Complete Context

### Technology Stack
- FastAPI 0.104+
- Python 3.11
- AWS Bedrock (Claude 3.5 Sonnet)
- Redis (caching)
- SQLite (database)
- Prometheus, Loki, Jaeger (observability)

### Project Structure
```
backend/
├── app/
│   ├── main.py                    # FastAPI app
│   ├── routers/                   # API endpoints
│   │   ├── metrics.py
│   │   ├── incidents.py
│   │   ├── logs.py
│   │   ├── traces.py
│   │   └── rca.py
│   ├── services/                  # Business logic
│   │   ├── prometheus_service.py
│   │   ├── loki_service.py
│   │   ├── jaeger_service.py
│   │   ├── bedrock_service.py
│   │   └── rca_agent.py
│   ├── models/                    # Data models
│   ├── database/                  # Database layer
│   └── utils/                     # Utilities
├── data/                          # Mock data
├── logs/                          # Application logs
├── requirements.txt               # Dependencies
└── .env                           # Environment variables
```

### All API Endpoints

**Health Check:**
- `GET /health` - Service health status

**Metrics:**
- `GET /api/metrics` - Fetch current metrics from Prometheus
  - Returns: host_metrics, otlp_metrics
  - Cache: 30s TTL

**Incidents:**
- `GET /api/incidents` - List incidents with filters
  - Query: severity, status, service, limit
  - Cache: 1m TTL

- `GET /api/incidents/stats` - Incident statistics
  - Returns: total, by_severity, by_service, by_status
  - Cache: 1m TTL

- `GET /api/incidents/{incident_id}` - Incident details
  - Returns: Complete incident with RCA report
  - Cache: 5m TTL

**Logs:**
- `GET /api/logs` - Fetch logs from Loki
  - Query: service, level, limit
  - Returns: error_logs, critical_logs, warning_logs

**Traces:**
- `GET /api/traces` - Fetch traces from Jaeger
  - Query: service, limit
  - Returns: error_traces, slow_traces, sample_traces_with_spans

**RCA Investigation:**
- `POST /api/rca/investigate` - Trigger autonomous investigation
  - Body: { service: string }
  - Returns: incident_id, result
  - Process: Plan → Act → Check → Adapt

### Agentic RCA Loop

**Plan Phase:**
1. Analyze service name
2. Create investigation strategy
3. Determine data sources
4. Plan queries

**Act Phase:**
1. Query Prometheus (metrics)
2. Query Loki (logs)
3. Query Jaeger (traces)
4. Collect observability data

**Check Phase:**
1. Validate data quality
2. Check sufficiency
3. Identify anomalies
4. Decide if more data needed

**Adapt Phase:**
1. Format data for AI
2. Call AWS Bedrock (Claude 3.5 Sonnet)
3. Parse AI response
4. Generate RCA report
5. Calculate confidence score
6. Save to database

### AWS Bedrock Integration

**Model:** anthropic.claude-3-5-sonnet-20241022-v2:0  
**Temperature:** 0.3 (focused, deterministic)  
**Max Tokens:** 4096  
**System Prompt:** RCA expert persona  

**Prompt Structure:**
```
You are an expert SRE analyzing observability data.

Service: {service_name}
Metrics: {prometheus_data}
Logs: {loki_data}
Traces: {jaeger_data}

Generate comprehensive RCA report with:
- Executive summary
- Root cause analysis
- Evidence
- Remediation steps
- Prevention recommendations
```

### Database Schema

**Incidents Table:**
```sql
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(50) UNIQUE,
    service VARCHAR(100),
    severity VARCHAR(20),
    status VARCHAR(20),
    title TEXT,
    root_cause TEXT,
    confidence_score FLOAT,
    detected_at TIMESTAMP,
    resolved_at TIMESTAMP,
    duration_seconds FLOAT,
    cost_usd FLOAT,
    tokens_used INTEGER,
    investigation_steps JSONB,
    rca_report JSONB,
    observability_data JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Caching Strategy

**Redis Keys:**
- `metrics:current` - TTL: 30s
- `incidents:list:{filters}` - TTL: 1m
- `incidents:stats` - TTL: 1m
- `incidents:detail:{id}` - TTL: 5m

### Environment Variables

```bash
# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx

# Observability
PROMETHEUS_URL=http://localhost:9090
LOKI_URL=http://localhost:3100
JAEGER_URL=http://localhost:16686

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Database
DATABASE_URL=sqlite:///./albeyla.db

# API
API_PORT=8000
LOG_LEVEL=INFO
```

---

## Data Flow Examples

### 1. User Views Dashboard

```
1. User opens http://localhost:5173
2. Dashboard.tsx renders
3. useMetrics() hook called
4. React Query checks cache
5. If stale, GET /api/metrics
6. Backend checks Redis cache
7. If miss, query Prometheus
8. Format and return data
9. Cache in Redis (30s)
10. Frontend displays metrics
```

### 2. User Triggers Investigation

```
1. User navigates to /investigate
2. Selects service "core-athenamind"
3. Clicks "Start Investigation"
4. Toast: "Starting investigation..."
5. POST /api/rca/investigate
6. Backend starts agentic loop:
   - Plan: Create strategy
   - Act: Fetch Prometheus/Loki/Jaeger
   - Check: Validate data
   - Adapt: Call AWS Bedrock
7. Generate RCA report
8. Save to database
9. Return incident_id
10. Toast: "Investigation complete!"
11. Auto-redirect to /incidents/{id}
12. Display full RCA report
```

### 3. User Exports CSV

```
1. User on /incidents page
2. Applies filters (severity: critical)
3. Clicks "Export CSV"
4. Frontend validates data
5. Generates CSV with headers
6. Escapes special characters
7. Creates Blob
8. Triggers download
9. Toast: "CSV exported successfully"
10. File saved: incidents-2024-01-15.csv
```

---

## Key Features

### Frontend Features
1. **Real-time Monitoring** - Live metrics with 5-min polling
2. **Advanced Filtering** - Search, sort, filter incidents
3. **Interactive Charts** - Recharts with gradients
4. **Glassmorphism UI** - Modern design with blur effects
5. **Smooth Animations** - Framer Motion transitions
6. **Toast Notifications** - User feedback for all actions
7. **Error Handling** - ErrorBoundary + fallback UI
8. **Loading States** - Skeleton loaders
9. **CSV Export** - Download incidents data
10. **Responsive Design** - Mobile-friendly

### Backend Features
1. **Autonomous Investigation** - AI-powered RCA
2. **Multi-Source Integration** - Prometheus + Loki + Jaeger
3. **Agentic Loop** - Plan-Act-Check-Adapt
4. **AWS Bedrock** - Claude 3.5 Sonnet
5. **Redis Caching** - Performance optimization
6. **Async Operations** - Non-blocking I/O
7. **Structured Logging** - Debug and monitoring
8. **Error Handling** - Try-catch + custom exceptions
9. **Rate Limiting** - Prevent abuse
10. **Mock Data** - Development without real services

---

## Development Commands

### Frontend
```bash
cd sre-copilot-frontend
npm install
npm run dev          # Start dev server
npm run build        # Production build
npm run preview      # Preview build
npm run lint         # Lint code
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 7474
```

### Infrastructure
```bash
cd platform
docker compose up -d      # Start all services
docker compose ps         # Check status
docker compose logs -f    # View logs
docker compose down       # Stop services
docker compose down -v    # Stop + remove volumes
```

---

## Common Patterns

### Frontend Pattern: Data Fetching
```typescript
const { data, isLoading, error } = useMetrics()

if (isLoading) return <SkeletonCard />
if (error) return <ErrorMessage />
return <MetricsDisplay data={data} />
```

### Frontend Pattern: Toast Notification
```typescript
import { toast } from 'sonner'

toast.success('Action completed')
toast.error('Action failed', { description: 'Details' })
toast.loading('Processing...', { id: 'unique-id' })
```

### Backend Pattern: Endpoint
```python
@router.get("/api/endpoint")
async def get_data():
    try:
        # Check cache
        cached = redis_client.get('key')
        if cached:
            return json.loads(cached)
        
        # Fetch data
        data = await service.fetch()
        
        # Cache result
        redis_client.setex('key', 30, json.dumps(data))
        
        return data
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Backend Pattern: AWS Bedrock Call
```python
response = bedrock.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
    })
)
```

---

## Testing

### Frontend Tests
- Unit tests: Jest + React Testing Library
- Component tests: Storybook
- E2E tests: Playwright

### Backend Tests
- Unit tests: Pytest
- API tests: TestClient
- Integration tests: Docker Compose

---

## Deployment

### Current (Development)
- Frontend: Vite dev server (port 5173)
- Backend: Uvicorn with reload (port 7474)
- Infrastructure: Docker Compose

### Future (Production)
- Frontend: Nginx + static build
- Backend: Gunicorn + Uvicorn workers
- Infrastructure: Kubernetes
- CDN: CloudFront
- Database: PostgreSQL
- Cache: Redis Cluster

---

## Security

### Current
- No authentication (MVP)
- CORS enabled for localhost
- Input validation
- Rate limiting per IP

### Future
- JWT authentication
- API keys
- RBAC
- Audit logging
- Encryption at rest
- TLS/SSL

---

## Performance

### Frontend Optimizations
- Code splitting (React.lazy)
- React Query caching
- Debounced search
- Virtualized lists
- Image lazy loading

### Backend Optimizations
- Redis caching
- Connection pooling
- Async operations
- Query optimization
- Response compression

---

## Monitoring

### Application Metrics
- Request rate
- Error rate
- Response time (P50, P95, P99)
- Cache hit rate

### Business Metrics
- Incidents per hour
- Investigation duration
- AI cost per investigation
- Confidence score distribution

---

## Known Issues & Limitations

1. **No Authentication** - MVP has no auth
2. **SQLite Database** - Not suitable for production
3. **Single Instance** - No horizontal scaling
4. **Mock Data** - Some endpoints use mock data
5. **Limited Error Recovery** - Basic error handling
6. **No Audit Trail** - No logging of user actions
7. **Basic Rate Limiting** - Simple IP-based limiting

---

## Future Enhancements

### Phase 1 (Next 3 months)
- Authentication & authorization
- Multi-tenant support
- Advanced search
- Custom alerts
- Slack integration

### Phase 2 (6 months)
- ML anomaly detection
- Predictive prevention
- Auto-remediation
- Knowledge base
- Mobile app

### Phase 3 (12 months)
- Multi-cloud support
- Integrations marketplace
- Advanced analytics
- Compliance features
- Enterprise features

---

## Quick Reference

### Important Files
- Frontend entry: `sre-copilot-frontend/src/main.tsx`
- Backend entry: `backend/app/main.py`
- Docker Compose: `platform/docker-compose.yml`
- Frontend config: `sre-copilot-frontend/vite.config.ts`
- Backend config: `backend/.env`

### Important URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:7474
- API Docs: http://localhost:7474/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

### Important Commands
```bash
# Start everything
docker compose up -d && cd backend && uvicorn app.main:app --reload --port 7474 &
cd sre-copilot-frontend && npm run dev

# Stop everything
docker compose down
pkill -f uvicorn
```

---

## Contact & Resources

- **Documentation:** `/platform/docs/`
- **Frontend Docs:** `/platform/docs/frontend/COMPONENTS.md`
- **Backend Docs:** `/platform/docs/backend/API.md`
- **Architecture:** `/platform/docs/ARCHITECTURE.md`
- **Development:** `/platform/docs/DEVELOPMENT.md`

---

**Last Updated:** 2024-01-15  
**Version:** 1.0.0 (MVP)  
**Status:** Development  
**License:** Proprietary
