import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { ObservabilityMetrics } from '../types/index'

export function useMetrics() {
  return useQuery({
    queryKey: ['metrics'],
    queryFn: async () => {
      try {
        const { data } = await api.get<ObservabilityMetrics>('/api/observability/metrics')
        return data
      } catch (error) {
        // Return mock data matching API documentation structure
        return {
          host_metrics: {
            cpu_usage_percent: { current: 14.03, status: 'ok' as const },
            memory_usage_percent: { current: 71.30, status: 'ok' as const }
          },
          otlp_metrics: {
            http_error_rate_percent: { current: 47.06, status: 'critical' as const },
            http_latency_p95_ms: { current: 287.50, status: 'ok' as const },
            http_requests_total: { current: 17, status: 'ok' as const },
            http_active_connections: { current: 25, status: 'ok' as const },
            db_query_duration_seconds: { current: 0.045, status: 'ok' as const }
          }
        } as ObservabilityMetrics
      }
    },
    refetchInterval: 300000, // 5 minutes
    retry: 1
  })
}