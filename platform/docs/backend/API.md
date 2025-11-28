# Backend API Documentation

Complete API reference for the Albeyla backend service.

## Base URL

```
http://localhost:7474
```

## Table of Contents

- [Health Check](#health-check)
- [Metrics API](#metrics-api)
- [Incidents API](#incidents-api)
- [Logs API](#logs-api)
- [Traces API](#traces-api)
- [RCA Investigation API](#rca-investigation-api)

---

## Health Check

### GET /health

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200` - Service is healthy

---

## Metrics API

### GET /api/metrics

Fetch current observability metrics from Prometheus.

**Query Parameters:**
None

**Response:**
```json
{
  "host_metrics": {
    "cpu_usage_percent": {
      "current": 45.2,
      "avg": 42.1,
      "min": 38.5,
      "max": 52.3,
      "status": "ok"
    },
    "memory_usage_percent": {
      "current": 68.5,
      "avg": 65.2,
      "min": 60.1,
      "max": 72.8,
      "status": "warning"
    },
    "disk_read_bytes_per_sec": {
      "current": 19114.03,
      "status": "ok"
    },
    "disk_write_bytes_per_sec": {
      "current": 1616500.78,
      "status": "ok"
    },
    "network_receive_bytes_per_sec": {
      "current": 3962.47,
      "status": "ok"
    },
    "network_transmit_bytes_per_sec": {
      "current": 4273.72,
      "status": "ok"
    }
  },
  "otlp_metrics": {
    "http_error_rate_percent": {
      "current": 2.5,
      "status": "ok"
    },
    "http_latency_p95_ms": {
      "current": 125.3,
      "status": "ok"
    },
    "http_requests_total": {
      "current": 15234,
      "status": "ok"
    },
    "http_active_connections": {
      "current": 42,
      "status": "ok"
    },
    "db_query_duration_seconds": {
      "current": 0.023,
      "status": "ok"
    }
  }
}
```

**Status Values:**
- `ok` - Metric is within normal range
- `warning` - Metric is elevated but not critical
- `critical` - Metric requires immediate attention

**Status Codes:**
- `200` - Success
- `500` - Prometheus connection error

---

## Incidents API

### GET /api/incidents

Fetch list of incidents with optional filtering.

**Query Parameters:**
- `severity` (optional): `critical`, `high`, `medium`, `low`
- `status` (optional): `open`, `resolved`
- `service` (optional): Service name
- `limit` (optional): Number of results (default: 50)

**Example:**
```
GET /api/incidents?severity=critical&status=open&limit=10
```

**Response:**
```json
[
  {
    "id": 1,
    "incident_id": "INC-ABC123",
    "service": "core-athenamind",
    "severity": "critical",
    "status": "open",
    "title": "Database Connection Refused",
    "root_cause": "database connection refused",
    "confidence_score": 0.92,
    "detected_at": "2024-01-15T10:30:00Z",
    "resolved_at": null,
    "duration_seconds": 45.2,
    "cost_usd": 0.0234,
    "tokens_used": 12500
  }
]
```

**Status Codes:**
- `200` - Success
- `400` - Invalid query parameters

---

### GET /api/incidents/stats

Get incident statistics.

**Response:**
```json
{
  "total_incidents": 42,
  "by_severity": {
    "critical": 5,
    "high": 12,
    "medium": 18,
    "low": 7
  },
  "by_service": {
    "core-athenamind": 15,
    "api-gateway": 10,
    "auth-service": 8,
    "payment-service": 5,
    "notification-service": 4
  },
  "by_status": {
    "open": 8,
    "resolved": 34
  }
}
```

**Status Codes:**
- `200` - Success

---

### GET /api/incidents/{incident_id}

Get detailed incident information including RCA report.

**Path Parameters:**
- `incident_id`: Incident identifier (e.g., "INC-ABC123")

**Response:**
```json
{
  "id": 1,
  "incident_id": "INC-ABC123",
  "service": "core-athenamind",
  "severity": "high",
  "status": "open",
  "title": "Database Connection Refused",
  "root_cause": "database connection refused",
  "confidence_score": 0.9,
  "detected_at": "2024-01-15T10:30:00Z",
  "resolved_at": null,
  "duration_seconds": 45.2,
  "cost_usd": 0.0234,
  "tokens_used": 12500,
  "investigation_steps": [
    {
      "step": "plan",
      "message": "Analyzing service metrics and creating investigation strategy",
      "timestamp": "2024-01-15T10:30:05Z"
    },
    {
      "step": "act",
      "message": "Fetching metrics from Prometheus, logs from Loki, traces from Jaeger",
      "timestamp": "2024-01-15T10:30:15Z"
    },
    {
      "step": "check",
      "message": "Validating data quality and sufficiency",
      "timestamp": "2024-01-15T10:30:25Z"
    },
    {
      "step": "adapt",
      "message": "Generating comprehensive RCA report",
      "timestamp": "2024-01-15T10:30:35Z"
    }
  ],
  "rca_report": {
    "executive_summary": {
      "title": "Database Connection Refused",
      "severity": "high",
      "impact": "core-athenamind service is experiencing errors due to database connection issues",
      "user_impact": "users are unable to retrieve trending posts, resulting in a degraded user experience"
    },
    "timeline": [
      {
        "timestamp": "17:40:43",
        "event": "Anomaly detected - investigate observability data",
        "source": "prometheus"
      },
      {
        "timestamp": "17:40:43",
        "event": "ERROR: Request failed: GET /api/trending",
        "source": "loki"
      },
      {
        "timestamp": "17:40:43",
        "event": "ERROR TRACES: Operation unknown, Duration: 32ms, Service: unknown, Error: True",
        "source": "jaeger"
      }
    ],
    "root_cause": {
      "primary_cause": "database connection refused",
      "contributing_factors": [
        "psycopg2.OperationalError",
        "connection to server at localhost (127.0.0.1), port 5432 failed"
      ],
      "evidence": [
        {
          "type": "log",
          "description": "ERROR: Request failed: GET /api/trending",
          "value": "Database error"
        },
        {
          "type": "metric",
          "description": "http_error_rate_percent",
          "value": "13.89 percent"
        },
        {
          "type": "trace",
          "description": "ERROR TRACES: Operation unknown, Duration: 32ms, Service: unknown, Error: True",
          "value": "true"
        }
      ],
      "confidence_score": 0.9,
      "similar_to_past_incident": null
    },
    "technical_details": {
      "affected_components": [
        {
          "component": "core-athenamind",
          "status": "degraded"
        }
      ],
      "metrics_snapshot": {
        "cpu_usage_percent": 8.93,
        "memory_usage_percent": 48.49,
        "disk_read_bytes_per_sec": 19114.03,
        "disk_write_bytes_per_sec": 1616500.78,
        "network_receive_bytes_per_sec": 3962.47,
        "network_transmit_bytes_per_sec": 4273.72,
        "http_error_rate_percent": 13.89
      }
    },
    "impact_assessment": {
      "severity": "high",
      "users_affected": "estimated 1000+ users"
    },
    "remediation": {
      "immediate_actions": [
        {
          "action": "restart database service",
          "command": "sudo service postgresql restart",
          "estimated_time": "1m",
          "expected_impact": "resolves database connection issues"
        }
      ],
      "permanent_fixes": [
        {
          "fix": "implement database connection pooling and retry mechanism",
          "priority": "P0"
        }
      ]
    },
    "prevention": {
      "code_changes": [
        "add database connection timeout and retry logic"
      ],
      "monitoring_enhancements": [
        "add alert for database connection errors"
      ]
    },
    "potential_causes": [
      {
        "hypothesis": "database server is down or not accepting connections",
        "probability": 0.8,
        "evidence": [
          "connection refused error",
          "database server logs"
        ]
      },
      {
        "hypothesis": "database credentials are incorrect",
        "probability": 0.2,
        "evidence": [
          "database connection logs"
        ]
      }
    ],
    "confidence": {
      "overall_score": 0.9,
      "uncertainties": [
        "database server status",
        "database credentials"
      ],
      "recommendation": "investigate database server status and credentials"
    },
    "learning_metadata": {
      "worth_learning": true,
      "reason": "novel issue with clear root cause and actionable fix",
      "keywords": [
        "database-connection",
        "connection-refused",
        "http-error",
        "postgresql",
        "retry-mechanism"
      ]
    }
  },
  "observability_data": {
    "prometheus": {
      "host_metrics": {},
      "otlp_metrics": {}
    },
    "loki": {
      "logs": {
        "error_logs": [],
        "critical_logs": [],
        "warning_logs": []
      }
    },
    "jaeger": {
      "traces": {
        "error_traces": [],
        "slow_traces": [],
        "sample_traces_with_spans": []
      }
    }
  }
}
```

**Status Codes:**
- `200` - Success
- `404` - Incident not found

---

## Logs API

### GET /api/logs

Fetch recent logs from Loki.

**Query Parameters:**
- `service` (optional): Filter by service name
- `level` (optional): `error`, `critical`, `warning`
- `limit` (optional): Number of results (default: 100)

**Response:**
```json
{
  "logs": {
    "error_logs": [
      {
        "timestamp": "2024-01-15T10:30:00Z",
        "message": "ERROR: Request failed: GET /api/trending",
        "service": "core-athenamind",
        "level": "error"
      }
    ],
    "critical_logs": [
      {
        "timestamp": "2024-01-15T10:29:55Z",
        "message": "CRITICAL: Database connection pool exhausted",
        "service": "core-athenamind",
        "level": "critical"
      }
    ],
    "warning_logs": [
      {
        "timestamp": "2024-01-15T10:29:50Z",
        "message": "WARNING: High memory usage detected",
        "service": "core-athenamind",
        "level": "warning"
      }
    ]
  }
}
```

**Status Codes:**
- `200` - Success
- `500` - Loki connection error

---

## Traces API

### GET /api/traces

Fetch recent traces from Jaeger.

**Query Parameters:**
- `service` (optional): Filter by service name
- `limit` (optional): Number of results (default: 50)

**Response:**
```json
{
  "traces": {
    "error_traces": [
      {
        "trace_id": "abc123def456",
        "operation_name": "GET /api/trending",
        "service": "core-athenamind",
        "duration_ms": 32,
        "error": true,
        "error_message": "Database connection refused"
      }
    ],
    "slow_traces": [
      {
        "trace_id": "xyz789uvw012",
        "operation_name": "POST /api/posts",
        "service": "core-athenamind",
        "duration_ms": 2500,
        "error": false
      }
    ],
    "sample_traces_with_spans": [
      {
        "trace_id": "mno345pqr678",
        "operation_name": "GET /api/users",
        "service": "api-gateway",
        "duration_ms": 125,
        "spans": [
          {
            "span_id": "span1",
            "operation_name": "auth.verify",
            "duration_ms": 15
          },
          {
            "span_id": "span2",
            "operation_name": "db.query",
            "duration_ms": 85
          },
          {
            "span_id": "span3",
            "operation_name": "cache.get",
            "duration_ms": 5
          }
        ]
      }
    ]
  }
}
```

**Status Codes:**
- `200` - Success
- `500` - Jaeger connection error

---

## RCA Investigation API

### POST /api/rca/investigate

Trigger a new autonomous RCA investigation for a service.

**Request Body:**
```json
{
  "service": "core-athenamind"
}
```

**Response:**
```json
{
  "status": "success",
  "incident_id": "INC-ABC123",
  "message": "Investigation completed successfully",
  "result": {
    "incident_id": "INC-ABC123",
    "service": "core-athenamind",
    "severity": "high",
    "confidence_score": 0.92,
    "duration_seconds": 45.2,
    "cost_usd": 0.0234,
    "tokens_used": 12500,
    "rca_report": {
      "executive_summary": {},
      "root_cause": {},
      "remediation": {},
      "prevention": {}
    }
  }
}
```

**Investigation Process:**

1. **Plan Phase**
   - Analyzes service name
   - Creates investigation strategy
   - Determines data sources to query

2. **Act Phase**
   - Fetches metrics from Prometheus
   - Retrieves logs from Loki
   - Collects traces from Jaeger
   - Gathers observability data

3. **Check Phase**
   - Validates data quality
   - Checks data sufficiency
   - Identifies anomalies
   - Determines if more data is needed

4. **Adapt Phase**
   - Analyzes all collected data
   - Uses AWS Bedrock (Claude 3.5 Sonnet) for RCA
   - Generates comprehensive report
   - Provides remediation steps
   - Calculates confidence score

**Status Codes:**
- `200` - Investigation completed successfully
- `400` - Invalid service name
- `500` - Investigation failed (AI error, data fetch error, etc.)

**Error Response:**
```json
{
  "status": "error",
  "message": "Failed to fetch metrics from Prometheus",
  "error_details": "Connection timeout"
}
```

---

## Data Models

### Incident Model

```python
class Incident(BaseModel):
    id: int
    incident_id: str
    service: str
    severity: Literal["critical", "high", "medium", "low"]
    status: Literal["open", "resolved"]
    title: str
    root_cause: str
    confidence_score: float
    detected_at: datetime
    resolved_at: Optional[datetime]
    duration_seconds: float
    cost_usd: float
    tokens_used: int
    investigation_steps: List[InvestigationStep]
    rca_report: RCAReport
    observability_data: dict
```

### InvestigationStep Model

```python
class InvestigationStep(BaseModel):
    step: Literal["plan", "act", "check", "adapt"]
    message: str
    timestamp: datetime
```

### RCAReport Model

```python
class RCAReport(BaseModel):
    executive_summary: ExecutiveSummary
    timeline: List[TimelineEvent]
    root_cause: RootCause
    technical_details: TechnicalDetails
    impact_assessment: ImpactAssessment
    remediation: Remediation
    prevention: Prevention
    potential_causes: List[PotentialCause]
    confidence: Confidence
    learning_metadata: LearningMetadata
```

---

## Environment Variables

```bash
# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Observability Services
PROMETHEUS_URL=http://prometheus:9090
LOKI_URL=http://loki:3100
JAEGER_URL=http://jaeger:16686

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# API Configuration
API_PORT=8000
LOG_LEVEL=INFO
```

---

## Error Handling

All API endpoints follow consistent error response format:

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

**Common Error Codes:**
- `INVALID_REQUEST` - Invalid request parameters
- `NOT_FOUND` - Resource not found
- `SERVICE_UNAVAILABLE` - External service unavailable
- `AI_ERROR` - AWS Bedrock error
- `DATABASE_ERROR` - Database connection error
- `INTERNAL_ERROR` - Unexpected server error

---

## Rate Limiting

- **Default:** 100 requests per minute per IP
- **Investigation endpoint:** 10 requests per minute per IP
- **Headers:**
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when limit resets

---

## Authentication

Currently, the API does not require authentication (MVP version).

**Future:** Will implement JWT-based authentication with API keys.

---

## Caching

- **Metrics:** Cached for 30 seconds in Redis
- **Incidents list:** Cached for 1 minute
- **Incident details:** Cached for 5 minutes
- **Logs/Traces:** Not cached (real-time data)

---

## Best Practices

1. **Always handle errors** - Check status codes and error responses
2. **Use query parameters** for filtering to reduce data transfer
3. **Poll responsibly** - Don't poll faster than 5-second intervals
4. **Cache responses** on the client side when appropriate
5. **Use incident_id** for unique identification, not database id
6. **Check confidence_score** before acting on RCA recommendations
7. **Monitor rate limits** to avoid throttling
8. **Validate service names** before triggering investigations
9. **Handle timeouts** - Investigation can take 30-60 seconds
10. **Log errors** for debugging and monitoring
