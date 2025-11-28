# SRE Copilot - Frontend API Reference & Design Guide

**Base URL:** `http://localhost:7474`

---

## 📋 API Endpoints

### 1. RCA Investigation

#### **POST** `/api/rca/investigate`
Trigger autonomous RCA investigation with Plan→Act→Check→Adapt loop.

**Request:**
```json
{
  "service": "core-athenamind"
}
```

**Response:**
```json
{
  "incident_id": "INC-93C8C8AF",
  "status": "completed",
  "result": {
    "incident_id": "INC-93C8C8AF",
    "rca_report": {
      "executive_summary": {
        "title": "High Error Rate in core-athenamind Service",
        "severity": "high",
        "impact": "Elevated HTTP error rate",
        "user_impact": "Users may experience failed requests"
      },
      "root_cause": {
        "primary_cause": "Elevated HTTP error rate due to unknown cause",
        "confidence_score": 0.6,
        "evidence": [
          {"type": "metric", "description": "http_error_rate_percent", "value": "47.06%"}
        ]
      },
      "remediation": {
        "immediate_actions": [
          {"action": "Investigate recent code changes", "command": "git log", "estimated_time": "30m"}
        ]
      }
    },
    "investigation_steps": [
      {"step": "plan", "message": "📋 Planning investigation strategy...", "timestamp": "..."},
      {"step": "act", "message": "🔍 Fetching observability data...", "timestamp": "..."}
    ],
    "duration_seconds": 3.45,
    "cost_usd": 0.0
  }
}
```

---

### 2. Incidents List

#### **GET** `/api/incidents/`
List all incidents with optional filters.

**Query Parameters:**
- `service` (optional): Filter by service name
- `severity` (optional): Filter by severity (critical/high/medium/low)
- `status` (optional): Filter by status (open/resolved)
- `limit` (optional): Max results (default: 50, max: 100)

**Response:**
```json
[
  {
    "id": 1,
    "incident_id": "INC-93C8C8AF",
    "service": "core-athenamind",
    "severity": "high",
    "status": "open",
    "title": "High Error Rate in core-athenamind Service",
    "root_cause": "Elevated HTTP error rate",
    "confidence_score": 0.6,
    "detected_at": "2025-11-26T05:46:11",
    "resolved_at": null,
    "duration_seconds": 3.45,
    "cost_usd": 0.0
  }
]
```

---

### 3. Incident Details

#### **GET** `/api/incidents/{incident_id}`
Get full incident details including RCA report and observability data.

**Response:**
```json
{
  "incident_id": "INC-93C8C8AF",
  "service": "core-athenamind",
  "severity": "high",
  "status": "open",
  "title": "High Error Rate in core-athenamind Service",
  "root_cause": "Elevated HTTP error rate",
  "confidence_score": 0.6,
  "detected_at": "2025-11-26T05:46:11",
  "rca_report": {
    "executive_summary": {...},
    "root_cause": {...},
    "remediation": {...},
    "timeline": [...],
    "learning_metadata": {
      "worth_learning": true,
      "keywords": ["http-error-rate", "elevated-error-rate", "retry-mechanism"]
    }
  },
  "observability_data": {
    "prometheus": {
      "host_metrics": {...},
      "otlp_metrics": {...}
    },
    "loki": {
      "logs": {...}
    },
    "jaeger": {
      "traces": {...}
    },
    "similar_incidents": [...]
  },
  "investigation_steps": [...],
  "llm_provider": "groq",
  "tokens_used": 2160
}
```

---

### 4. Statistics

#### **GET** `/api/incidents/stats/summary`
Get incident statistics.

**Response:**
```json
{
  "total_incidents": 15,
  "by_severity": {
    "critical": 2,
    "high": 8,
    "medium": 4,
    "low": 1
  },
  "by_service": {
    "core-athenamind": 10,
    "api-gateway": 3,
    "auth-service": 2
  }
}
```

---

### 5. Observability Data

#### **GET** `/api/observability/metrics`
Get current Prometheus metrics.

**Response:**
```json
{
  "host_metrics": {
    "cpu_usage_percent": {"current": 14.03, "status": "ok"},
    "memory_usage_percent": {"current": 71.30, "status": "ok"}
  },
  "otlp_metrics": {
    "http_error_rate_percent": {"current": 47.06, "status": "critical"}
  }
}
```

#### **GET** `/api/observability/logs`
Get recent logs from Loki.

**Query Parameters:**
- `time_range` (optional): Time range (default: "5m")
- `level` (optional): Log level filter

**Response:**
```json
{
  "logs": {
    "error_logs": [...],
    "critical_logs": [...],
    "warning_logs": [...]
  }
}
```

#### **GET** `/api/observability/traces`
Get traces from Jaeger.

**Response:**
```json
{
  "traces": {
    "slow_traces": [...],
    "error_traces": [...],
    "sample_traces_with_spans": [...]
  }
}
```

---

## 🎨 Frontend Design Guide

### Page Structure

```
┌─────────────────────────────────────────────────────────┐
│  Header: SRE Copilot | [Trigger Investigation Button]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Dashboard (/)                                          │
│  ├─ Stats Cards (Total, Critical, High, Medium)        │
│  ├─ Recent Incidents Table                             │
│  └─ Quick Actions                                       │
│                                                         │
│  Incident Details (/incidents/:id)                     │
│  ├─ Executive Summary Card                             │
│  ├─ Investigation Timeline (Agentic Steps)             │
│  ├─ Root Cause Analysis                                │
│  ├─ Remediation Actions                                │
│  ├─ Observability Data Tabs                            │
│  │  ├─ Metrics (with status indicators)                │
│  │  ├─ Logs (grouped by level)                         │
│  │  └─ Traces (with spans)                             │
│  └─ Similar Past Incidents (RAG)                       │
│                                                         │
│  Live Investigation (/investigate)                     │
│  ├─ Service Selector                                   │
│  ├─ Real-time Investigation Steps                      │
│  └─ Progress Indicator                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Key UI Components

#### 1. **Dashboard Page** (`/`)
- **Stats Cards**: Show total incidents, breakdown by severity
- **Recent Incidents Table**: 
  - Columns: Incident ID, Service, Severity, Title, Detected At, Status
  - Click row → Navigate to incident details
  - Color-coded severity badges (🔴 Critical, 🟡 High, 🟢 Medium)
- **Trigger Investigation Button**: Opens modal to select service

#### 2. **Incident Details Page** (`/incidents/:id`)

**Executive Summary Card:**
```
┌─────────────────────────────────────────────────┐
│ 🔴 HIGH SEVERITY                                │
│ High Error Rate in core-athenamind Service      │
│                                                 │
│ Impact: Elevated HTTP error rate               │
│ User Impact: Users may experience failed reqs   │
│ Confidence: 60%                                 │
│ Detected: 2025-11-26 05:46:11                  │
└─────────────────────────────────────────────────┘
```

**Investigation Timeline (Agentic Loop):**
```
┌─────────────────────────────────────────────────┐
│ Investigation Steps                             │
│                                                 │
│ ✓ 📋 PLAN: Planning investigation strategy...  │
│ ✓ 🔍 ACT: Fetching observability data...       │
│   → Querying Prometheus (last 5m)...           │
│   ✓ Fetched 6 host + 9 OTLP metrics            │
│   → Querying Loki for error logs...            │
│   ✓ Found 8 error logs                         │
│ ✓ ✓ CHECK: Data quality sufficient             │
│ ✓ 🧠 ACT: Generating RCA with AI...            │
│ ✓ ✓ ACT: RCA generation complete               │
│                                                 │
│ Duration: 3.45s | Cost: $0.00 | Tokens: 2160   │
└─────────────────────────────────────────────────┘
```

**Root Cause Card:**
```
┌─────────────────────────────────────────────────┐
│ Root Cause Analysis                             │
│                                                 │
│ Primary Cause:                                  │
│ Elevated HTTP error rate due to unknown cause   │
│                                                 │
│ Evidence:                                       │
│ • 📊 Metric: http_error_rate_percent = 47.06%  │
│ • 📊 Metric: http_requests_total = 17 requests │
│                                                 │
│ Contributing Factors:                           │
│ • Unknown factors                               │
└─────────────────────────────────────────────────┘
```

**Remediation Actions:**
```
┌─────────────────────────────────────────────────┐
│ Immediate Actions                               │
│                                                 │
│ 1. Investigate recent code changes              │
│    Command: git log                             │
│    Time: 30m | Impact: Identify potential cause│
│                                                 │
│ 2. Check server logs for errors                │
│    Command: loki query                          │
│    Time: 15m | Impact: Find error messages     │
│                                                 │
│ Permanent Fixes                                 │
│ • [P1] Implement retry mechanism for failed reqs│
└─────────────────────────────────────────────────┘
```

**Observability Data Tabs:**

*Metrics Tab:*
```
HOST METRICS:
🟢 OK cpu_usage_percent: 14.03% (min:9.3, max:14.0, avg:10.6)
🟢 OK memory_usage_percent: 71.30% (min:71.3, max:72.1, avg:71.6)

OTLP METRICS:
🔴 CRITICAL http_error_rate_percent: 47.06% (min:47.1, max:47.1, avg:47.1)
🟢 OK http_latency_p95_ms: 287.50ms (min:287.5, max:287.5, avg:287.5)
```

*Logs Tab:*
```
ERROR (8 logs):
[2x] Request failed: GET /api/trending
[2x] HTTP 500: Database error
[2x] Database connection refused
```

*Traces Tab:*
```
ERROR TRACES:
- Operation: GET /api/posts
  Duration: 14ms, Service: core-athenamind
  Error: Database connection timeout
```

**Similar Past Incidents (RAG):**
```
┌─────────────────────────────────────────────────┐
│ Similar Past Incidents (RAG Learning)           │
│                                                 │
│ No similar incidents found                      │
│ (This will be the first learned incident)       │
└─────────────────────────────────────────────────┘
```

#### 3. **Live Investigation Page** (`/investigate`)
- Service dropdown selector
- "Start Investigation" button
- Real-time streaming of investigation steps (WebSocket or polling)
- Progress bar
- Auto-redirect to incident details when complete

---

### Color Scheme

**Severity Colors:**
- 🔴 Critical: `#EF4444` (red-500)
- 🟡 High: `#F59E0B` (amber-500)
- 🟠 Medium: `#F97316` (orange-500)
- 🟢 Low: `#10B981` (green-500)

**Status Colors:**
- 🔴 CRITICAL: `#DC2626` (red-600)
- 🟡 WARNING: `#FBBF24` (yellow-400)
- 🟢 OK: `#059669` (green-600)

**Step Icons:**
- 📋 PLAN: Planning phase
- 🔍 ACT: Action/data fetching
- ✓ CHECK: Validation
- 🔄 ADAPT: Retry/fallback
- 🧠 AI: LLM generation

---

### Tech Stack Recommendations

**Framework:** React + TypeScript + Vite  
**UI Library:** Tailwind CSS + shadcn/ui  
**State Management:** TanStack Query (React Query)  
**Routing:** React Router v6  
**Charts:** Recharts or Chart.js  
**Icons:** Lucide React  

---

### Sample API Integration (React)

```typescript
// hooks/useIncidents.ts
import { useQuery } from '@tanstack/react-query';

export const useIncidents = (filters?: {
  service?: string;
  severity?: string;
  status?: string;
}) => {
  return useQuery({
    queryKey: ['incidents', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters);
      const res = await fetch(`http://localhost:7474/api/incidents/?${params}`);
      return res.json();
    }
  });
};

export const useIncidentDetails = (incidentId: string) => {
  return useQuery({
    queryKey: ['incident', incidentId],
    queryFn: async () => {
      const res = await fetch(`http://localhost:7474/api/incidents/${incidentId}`);
      return res.json();
    }
  });
};

export const useTriggerInvestigation = () => {
  return useMutation({
    mutationFn: async (service: string) => {
      const res = await fetch('http://localhost:7474/api/rca/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ service })
      });
      return res.json();
    }
  });
};
```

---

### Key Features to Implement

1. **Real-time Investigation Tracking**: Poll `/api/incidents/{id}` every 2s during investigation
2. **Severity Badges**: Color-coded badges for visual hierarchy
3. **Expandable Sections**: Collapsible cards for observability data
4. **Copy to Clipboard**: For commands in remediation actions
5. **Search & Filter**: Filter incidents by service, severity, date range
6. **Dark Mode**: Toggle between light/dark themes
7. **Export Report**: Download incident report as PDF/JSON
8. **Keyword Highlighting**: Highlight matched keywords in RAG similar incidents

---

### Mobile Responsive

- Stack cards vertically on mobile
- Collapsible sidebar navigation
- Touch-friendly buttons (min 44px height)
- Horizontal scroll for tables

---

## 🚀 Quick Start

1. **Install dependencies:**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install @tanstack/react-query axios react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

2. **Configure API base URL:**
```typescript
// src/config.ts
export const API_BASE_URL = 'http://localhost:7474';
```

3. **Start building!**
```bash
npm run dev
```

---

## 📊 Data Flow

```
User Action → API Call → Backend Processing → Database/JSON Storage
     ↓
Frontend Poll/Fetch → Display Results → User Interaction
```

---

## 🎯 Priority Pages

1. **Dashboard** - Overview of all incidents
2. **Incident Details** - Full RCA report with observability data
3. **Live Investigation** - Trigger and watch investigation in real-time

---

**Happy Building! 🚀**
