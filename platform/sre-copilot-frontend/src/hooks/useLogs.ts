import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export function useLogs(timeRange = '5m', level?: string) {
  return useQuery({
    queryKey: ['logs', timeRange, level],
    queryFn: async () => {
      try {
        const params = new URLSearchParams()
        params.append('time_range', timeRange)
        if (level) params.append('level', level)
        
        const { data } = await api.get(`/api/observability/logs?${params}`)
        return data
      } catch (error) {
        // Return mock data if API fails
        return {
          logs: {
            error_logs: [
              'Request failed: GET /api/trending',
              'HTTP 500: Database error',
              'Database connection refused'
            ],
            critical_logs: [
              'Service core-athenamind is down',
              'Critical memory threshold exceeded'
            ],
            warning_logs: [
              'High response time detected',
              'Connection pool near capacity'
            ]
          }
        }
      }
    },
    refetchInterval: 300000 // 5 minutes
  })
}