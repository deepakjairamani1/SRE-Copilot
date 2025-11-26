export interface Incident {
  id: number
  incident_id: string
  service: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'resolved'
  title: string
  root_cause: string
  confidence_score: number
  detected_at: string
  resolved_at: string | null
  duration_seconds: number
  cost_usd: number
}

export interface InvestigationStep {
  step: 'plan' | 'act' | 'check' | 'adapt'
  message: string
  timestamp: string
}

export interface RCAReport {
  executive_summary: {
    title: string
    severity: string
    impact: string
    user_impact: string
  }
  root_cause: {
    primary_cause: string
    confidence_score: number
    evidence: Array<{
      type: string
      description: string
      value: string
    }>
  }
  remediation: {
    immediate_actions: Array<{
      action: string
      command: string
      estimated_time: string
    }>
  }
  timeline?: Array<{
    timestamp: string
    event: string
    source: string
  }>
}

export interface Metric {
  current: number
  min?: number
  max?: number
  avg?: number
  status: 'ok' | 'warning' | 'critical'
}

// Observability metrics interface
export interface ObservabilityMetrics {
  host_metrics: {
    cpu_usage_percent?: Metric
    memory_usage_percent?: Metric
    disk_io_read_bytes_per_sec?: Metric
    disk_io_write_bytes_per_sec?: Metric
    network_receive_bytes_per_sec?: Metric
    network_transmit_bytes_per_sec?: Metric
  }
  otlp_metrics: {
    http_requests_total?: Metric
    http_error_rate_percent?: Metric
    http_latency_p95_ms?: Metric
    http_latency_p99_ms?: Metric
    http_active_connections?: Metric
    db_query_duration_seconds?: Metric
    cache_hit_rate_percent?: Metric
    queue_depth_current?: Metric
    cpu_usage_percent?: Metric
  }
}

export interface IncidentStats {
  total_incidents: number
  by_severity: {
    critical: number
    high: number
    medium: number
    low: number
  }
  by_service: Record<string, number>
}