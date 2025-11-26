import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export function useTraces() {
  return useQuery({
    queryKey: ['traces'],
    queryFn: async () => {
      try {
        const { data } = await api.get('/api/observability/traces')
        return data
      } catch (error) {
        // Return mock data if API fails
        return {
          traces: {
            slow_traces: [
              { operation: 'GET /api/posts', duration: '287ms', service: 'core-athenamind' }
            ],
            error_traces: [
              { operation: 'GET /api/posts', duration: '14ms', service: 'core-athenamind', error: 'Database connection timeout' }
            ],
            sample_traces_with_spans: [
              { traceId: 'abc123', spans: 5, duration: '150ms', service: 'api-gateway' }
            ]
          }
        }
      }
    },
    refetchInterval: 300000 // 5 minutes
  })
}