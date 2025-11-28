# Albeyla Architecture Documentation

Complete system architecture and design documentation.

## System Overview

Albeyla is an autonomous incident investigation platform that uses AI-powered agentic loops to analyze observability data and generate comprehensive root cause analysis reports.

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + TypeScript + Vite + TailwindCSS + Framer Motion   │
│                    (Port: 5173)                             │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│              FastAPI + Python 3.11                          │
│                    (Port: 7474)                             │
└─────┬──────────┬──────────┬──────────┬──────────────────────┘
      │          │          │          │
      ▼          ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│Prometheus│ │  Loki  │ │ Jaeger │ │  Redis   │
│  :9090   │ │ :3100  │ │ :16686 │ │  :6379   │
└──────────┘ └────────┘ └────────┘ └──────────┘
      │          │          │
      └──────────┴──────────┘
              │
              ▼
      ┌──────────────┐
      │   Grafana    │
      │    :3001     │
      └──────────────┘
              │
              ▼
      ┌──────────────┐
      │ AWS Bedrock  │
      │ Claude 3.5   │
      └──────────────┘
```

---

## Component Architecture

### Frontend Architecture

```
src/
├── components/
│   ├── ui/                    # Reusable UI components
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Button.tsx
│   │   ├── StatCard.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── SkeletonCard.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── PageTransition.tsx
│   │   └── Toast.tsx
│   ├── layout/                # Layout components
│   │   ├── Header.tsx
│   │   └── Sidebar.tsx
│   └── features/              # Feature-specific components
│       ├── MetricChart.tsx
│       ├── RemediationActions.tsx
│       ├── IncidentTimeline.tsx
│       └── ErrorBoundary.tsx
├── pages/                     # Page components
│   ├── Dashboard.tsx
│   ├── IncidentsList.tsx
│   ├── IncidentDetails.tsx
│   ├── Investigate.tsx
│   └── NotFound.tsx
├── hooks/                     # Custom React hooks
│   ├── useMetrics.ts
│   ├── useIncidents.ts
│   ├── useLogs.ts
│   └── useTraces.ts
├── lib/                       # Utilities
│   ├── api.ts                 # Axios instance
│   └── utils.ts               # Helper functions
├── types/                     # TypeScript types
│   └── index.ts
├── config.ts                  # Configuration
├── App.tsx                    # Main app component
└── main.tsx                   # Entry point
```

**Key Design Patterns:**
- **Component Composition** - Small, reusable components
- **Custom Hooks** - Data fetching logic separated from UI
- **Type Safety** - Full TypeScript coverage
- **Error Boundaries** - Graceful error handling
- **Optimistic Updates** - Immediate UI feedback

---

### Backend Architecture

```
app/
├── main.py                    # FastAPI application
├── routers/
│   ├── metrics.py             # Metrics endpoints
│   ├── incidents.py           # Incidents endpoints
│   ├── logs.py                # Logs endpoints
│   ├── traces.py              # Traces endpoints
│   └── rca.py                 # RCA investigation endpoints
├── services/
│   ├── prometheus_service.py  # Prometheus integration
│   ├── loki_service.py        # Loki integration
│   ├── jaeger_service.py      # Jaeger integration
│   ├── bedrock_service.py     # AWS Bedrock integration
│   └── rca_agent.py           # Agentic RCA loop
├── models/
│   ├── incident.py            # Incident data models
│   ├── rca_report.py          # RCA report models
│   └── observability.py       # Observability data models
├── database/
│   ├── connection.py          # Database connection
│   └── repositories.py        # Data access layer
└── utils/
    ├── logger.py              # Logging configuration
    └── cache.py               # Redis caching
```

**Key Design Patterns:**
- **Layered Architecture** - Clear separation of concerns
- **Repository Pattern** - Data access abstraction
- **Service Layer** - Business logic encapsulation
- **Dependency Injection** - Loose coupling
- **Async/Await** - Non-blocking I/O operations

---

## Data Flow

### 1. Metrics Fetching Flow

```
User → Frontend → GET /api/metrics → Backend
                                        ↓
                                   Check Redis Cache
                                        ↓
                                   Cache Miss?
                                        ↓
                                   Query Prometheus
                                        ↓
                                   Process & Format
                                        ↓
                                   Store in Redis (30s TTL)
                                        ↓
                                   Return to Frontend
                                        ↓
                                   Display in Dashboard
```

### 2. RCA Investigation Flow

```
User → Investigate Page → Select Service → Click "Start Investigation"
                                                    ↓
                                          POST /api/rca/investigate
                                                    ↓
                                          ┌─────────────────┐
                                          │  PLAN Phase     │
                                          │  - Analyze      │
                                          │  - Strategy     │
                                          └────────┬────────┘
                                                   ↓
                                          ┌─────────────────┐
                                          │  ACT Phase      │
                                          │  - Prometheus   │
                                          │  - Loki         │
                                          │  - Jaeger       │
                                          └────────┬────────┘
                                                   ↓
                                          ┌─────────────────┐
                                          │  CHECK Phase    │
                                          │  - Validate     │
                                          │  - Quality      │
                                          └────────┬────────┘
                                                   ↓
                                          ┌─────────────────┐
                                          │  ADAPT Phase    │
                                          │  - AWS Bedrock  │
                                          │  - Generate RCA │
                                          └────────┬────────┘
                                                   ↓
                                          Save to Database
                                                   ↓
                                          Return Incident ID
                                                   ↓
                                          Frontend Redirects
                                                   ↓
                                          Display RCA Report
```

### 3. Incident Details Flow

```
User → Click Incident → GET /api/incidents/{id} → Backend
                                                      ↓
                                                 Check Redis Cache
                                                      ↓
                                                 Cache Hit?
                                                      ↓
                                                 Return Cached Data
                                                      ↓
                                                 Frontend Renders:
                                                 - Executive Summary
                                                 - Timeline
                                                 - Root Cause
                                                 - Remediation
                                                 - Technical Details
                                                 - Prevention
```

---

## Agentic Loop Design

The RCA investigation uses a **Plan-Act-Check-Adapt** agentic loop:

### Plan Phase
**Purpose:** Create investigation strategy

**Actions:**
1. Analyze service name
2. Determine relevant metrics to fetch
3. Identify log patterns to search
4. Plan trace queries
5. Create investigation checklist

**Output:** Investigation plan with data sources

---

### Act Phase
**Purpose:** Gather observability data

**Actions:**
1. **Prometheus Queries:**
   - Host metrics (CPU, memory, disk, network)
   - Application metrics (error rate, latency, requests)
   - Custom service metrics

2. **Loki Queries:**
   - Error logs (last 1 hour)
   - Critical logs (last 1 hour)
   - Warning logs (last 1 hour)
   - Service-specific logs

3. **Jaeger Queries:**
   - Error traces (last 1 hour)
   - Slow traces (>1s duration)
   - Sample traces with spans
   - Service dependency traces

**Output:** Comprehensive observability dataset

---

### Check Phase
**Purpose:** Validate data quality

**Actions:**
1. Verify data completeness
2. Check for anomalies
3. Validate timestamp consistency
4. Ensure sufficient data points
5. Identify data gaps

**Decision:**
- If data sufficient → Proceed to Adapt
- If data insufficient → Return to Act with refined queries

**Output:** Validated dataset or request for more data

---

### Adapt Phase
**Purpose:** Generate RCA report using AI

**Actions:**
1. **Prepare Prompt:**
   - Format observability data
   - Add context about service
   - Include investigation goals

2. **AWS Bedrock Call:**
   - Model: Claude 3.5 Sonnet
   - Temperature: 0.3 (focused, deterministic)
   - Max tokens: 4096
   - System prompt: RCA expert persona

3. **Parse Response:**
   - Extract executive summary
   - Identify root cause
   - List contributing factors
   - Generate remediation steps
   - Create prevention recommendations
   - Calculate confidence score

4. **Structure Report:**
   - Timeline of events
   - Technical details
   - Impact assessment
   - Potential causes with probabilities
   - Learning metadata

**Output:** Complete RCA report

---

## Database Schema

### Incidents Table

```sql
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(50) UNIQUE NOT NULL,
    service VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    root_cause TEXT,
    confidence_score FLOAT,
    detected_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    duration_seconds FLOAT,
    cost_usd FLOAT,
    tokens_used INTEGER,
    investigation_steps JSONB,
    rca_report JSONB,
    observability_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_incidents_service ON incidents(service);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_detected_at ON incidents(detected_at DESC);
```

---

## Caching Strategy

### Redis Cache Keys

```
metrics:current              → TTL: 30s
incidents:list:{filters}     → TTL: 1m
incidents:stats              → TTL: 1m
incidents:detail:{id}        → TTL: 5m
```

### Cache Invalidation

- **Metrics:** Auto-expire after 30s
- **Incidents list:** Invalidate on new incident creation
- **Incident details:** Invalidate on status update
- **Stats:** Invalidate on new incident or status change

---

## Security Considerations

### Current (MVP)
- No authentication required
- CORS enabled for localhost
- Rate limiting per IP
- Input validation on all endpoints

### Future Enhancements
- JWT-based authentication
- API key management
- Role-based access control (RBAC)
- Audit logging
- Encryption at rest
- TLS/SSL for all connections

---

## Performance Optimization

### Frontend
1. **Code Splitting** - Lazy load routes
2. **React Query** - Automatic caching and deduplication
3. **Debouncing** - Search inputs debounced
4. **Virtualization** - Large lists virtualized
5. **Image Optimization** - Lazy loading images
6. **Bundle Size** - Tree shaking unused code

### Backend
1. **Connection Pooling** - Reuse database connections
2. **Redis Caching** - Cache frequently accessed data
3. **Async Operations** - Non-blocking I/O
4. **Query Optimization** - Indexed database queries
5. **Response Compression** - Gzip compression
6. **Batch Processing** - Batch similar requests

---

## Monitoring & Observability

### Application Metrics
- Request rate (requests/second)
- Error rate (errors/total requests)
- Response time (P50, P95, P99)
- Active connections
- Cache hit rate

### Business Metrics
- Incidents created per hour
- Average investigation duration
- AI cost per investigation
- Confidence score distribution
- Resolution time

### Infrastructure Metrics
- CPU usage
- Memory usage
- Disk I/O
- Network throughput
- Container health

---

## Deployment Architecture

### Docker Compose Setup

```yaml
services:
  frontend:
    - React app (Vite dev server)
    - Port: 5173
    - Hot reload enabled
  
  backend:
    - FastAPI app (Uvicorn)
    - Port: 7474
    - Auto-reload enabled
  
  prometheus:
    - Metrics storage
    - Port: 9090
    - Remote write enabled
  
  loki:
    - Log aggregation
    - Port: 3100
    - Retention: 7 days
  
  jaeger:
    - Distributed tracing
    - UI Port: 16686
    - OTLP Port: 4317/4318
  
  grafana:
    - Visualization
    - Port: 3001
    - Pre-configured dashboards
  
  redis:
    - Caching
    - Port: 6379
    - Persistence enabled
```

### Network Architecture

```
┌─────────────────────────────────────────┐
│         platform-network (bridge)        │
│                                          │
│  ┌──────────┐  ┌──────────┐            │
│  │ Frontend │  │ Backend  │            │
│  │  :5173   │  │  :7474   │            │
│  └────┬─────┘  └────┬─────┘            │
│       │             │                   │
│       └─────────────┴──────┬───────────┤
│                            │           │
│  ┌──────────┐  ┌────────┐ │ ┌────────┐│
│  │Prometheus│  │  Loki  │ │ │ Jaeger ││
│  └──────────┘  └────────┘ │ └────────┘│
│                            │           │
│  ┌──────────┐  ┌────────┐ │           │
│  │ Grafana  │  │ Redis  │ │           │
│  └──────────┘  └────────┘ │           │
└────────────────────────────┴───────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │ AWS Bedrock  │
                    │  (External)  │
                    └──────────────┘
```

---

## Scalability Considerations

### Horizontal Scaling
- **Frontend:** Multiple instances behind load balancer
- **Backend:** Stateless API servers (scale with load)
- **Redis:** Redis Cluster for distributed caching
- **Database:** Read replicas for query distribution

### Vertical Scaling
- **Prometheus:** Increase storage for longer retention
- **Loki:** More memory for log indexing
- **Jaeger:** Larger storage for trace retention

### Future Enhancements
- Kubernetes deployment
- Auto-scaling based on metrics
- Multi-region deployment
- CDN for frontend assets
- Message queue for async processing

---

## Error Handling Strategy

### Frontend
1. **Error Boundaries** - Catch React errors
2. **Toast Notifications** - User-friendly messages
3. **Retry Logic** - Automatic retry on network errors
4. **Fallback UI** - Graceful degradation
5. **Error Logging** - Send errors to monitoring

### Backend
1. **Try-Catch Blocks** - Catch exceptions
2. **Custom Exceptions** - Domain-specific errors
3. **Error Middleware** - Centralized error handling
4. **Logging** - Structured error logs
5. **Circuit Breaker** - Prevent cascade failures

---

## Testing Strategy

### Frontend Testing
- **Unit Tests:** Jest + React Testing Library
- **Component Tests:** Storybook
- **E2E Tests:** Playwright
- **Visual Regression:** Percy

### Backend Testing
- **Unit Tests:** Pytest
- **Integration Tests:** TestClient
- **API Tests:** Postman/Newman
- **Load Tests:** Locust

---

## Development Workflow

```
1. Feature Branch → 2. Development → 3. Testing → 4. Code Review → 5. Merge → 6. Deploy

Developer creates feature branch
    ↓
Implements feature with tests
    ↓
Runs local tests
    ↓
Commits and pushes
    ↓
Creates pull request
    ↓
CI/CD runs tests
    ↓
Code review by team
    ↓
Merge to main
    ↓
Auto-deploy to staging
    ↓
Manual deploy to production
```

---

## Best Practices

### Code Quality
- TypeScript strict mode enabled
- ESLint + Prettier for formatting
- Pre-commit hooks (Husky)
- Code coverage >80%
- Documentation for all public APIs

### Git Workflow
- Feature branches from main
- Conventional commits
- Squash merge to main
- Protected main branch
- Automated changelog

### Security
- Environment variables for secrets
- Input validation on all endpoints
- SQL injection prevention
- XSS protection
- CSRF tokens
- Rate limiting

---

## Future Roadmap

### Phase 1 (Current - MVP)
- ✅ Basic RCA investigation
- ✅ Observability data integration
- ✅ Frontend dashboard
- ✅ Incident management

### Phase 2 (Next 3 months)
- [ ] Authentication & authorization
- [ ] Multi-tenant support
- [ ] Advanced filtering & search
- [ ] Custom alerting rules
- [ ] Slack/Teams integration

### Phase 3 (6 months)
- [ ] Machine learning for anomaly detection
- [ ] Predictive incident prevention
- [ ] Auto-remediation workflows
- [ ] Knowledge base integration
- [ ] Mobile app

### Phase 4 (12 months)
- [ ] Multi-cloud support
- [ ] Custom integrations marketplace
- [ ] Advanced analytics & reporting
- [ ] Compliance & audit features
- [ ] Enterprise features
