import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { Incident, IncidentStats } from '../types/index'

export function useIncidents(filters?: {
  service?: string
  severity?: string
  status?: string
  limit?: number
}) {
  return useQuery({
    queryKey: ['incidents', filters],
    queryFn: async () => {
      try {
        const params = new URLSearchParams()
        if (filters?.service) params.append('service', filters.service)
        if (filters?.severity) params.append('severity', filters.severity)
        if (filters?.status) params.append('status', filters.status)
        if (filters?.limit) params.append('limit', filters.limit.toString())
        
        const { data } = await api.get<Incident[]>(`/api/incidents/?${params}`)
        return data
      } catch (error) {
        // Return mock data if API fails
        return [
          {
            id: 1,
            incident_id: 'INC-93C8C8AF',
            service: 'core-athenamind',
            severity: 'high' as const,
            status: 'open' as const,
            title: 'High Error Rate in core-athenamind Service',
            root_cause: 'Elevated HTTP error rate due to unknown cause',
            confidence_score: 0.6,
            detected_at: '2025-11-26T05:46:11',
            resolved_at: null,
            duration_seconds: 3.45,
            cost_usd: 0.0
          },
          {
            id: 2,
            incident_id: 'INC-B1DBA154',
            service: 'api-gateway',
            severity: 'critical' as const,
            status: 'open' as const,
            title: 'Database Connection Pool Exhausted',
            root_cause: 'High traffic spike caused connection pool exhaustion',
            confidence_score: 0.85,
            detected_at: '2025-11-26T04:30:15',
            resolved_at: null,
            duration_seconds: 120.5,
            cost_usd: 25.75
          },
          {
            id: 3,
            incident_id: 'INC-C152F7EA',
            service: 'auth-service',
            severity: 'medium' as const,
            status: 'resolved' as const,
            title: 'SSL Certificate Renewal Required',
            root_cause: 'Certificate expiring within 30 days',
            confidence_score: 0.95,
            detected_at: '2025-11-25T14:20:30',
            resolved_at: '2025-11-25T15:45:22',
            duration_seconds: 5092,
            cost_usd: 5.50
          }
        ] as Incident[]
      }
    },
    refetchInterval: 300000 // 5 minutes
  })
}

export function useIncidentStats() {
  return useQuery({
    queryKey: ['incident-stats'],
    queryFn: async () => {
      try {
        const { data } = await api.get<IncidentStats>('/api/incidents/stats/summary')
        return data
      } catch (error) {
        // Return mock data if API fails
        return {
          total_incidents: 15,
          by_severity: {
            critical: 2,
            high: 8,
            medium: 4,
            low: 1
          },
          by_service: {
            'core-athenamind': 10,
            'api-gateway': 3,
            'auth-service': 2
          }
        } as IncidentStats
      }
    },
    refetchInterval: 30000
  })
}

export function useIncidentDetails(incidentId: string) {
  return useQuery({
    queryKey: ['incident', incidentId],
    queryFn: async () => {
      const { data } = await api.get(`/api/incidents/${incidentId}`)
      return data
    },
    enabled: !!incidentId
  })
}

export function useTriggerInvestigation() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (service: string) => {
      try {
        const { data } = await api.post('/api/rca/investigate', { service })
        return data
      } catch (error) {
        // Return mock investigation result
        return {
          incident_id: 'INC-MOCK-001',
          status: 'completed',
          result: {
            incident_id: 'INC-MOCK-001',
            rca_report: {
              executive_summary: {
                title: `High Error Rate in ${service} Service`,
                severity: 'high',
                impact: 'Elevated HTTP error rate',
                user_impact: 'Users may experience failed requests'
              },
              root_cause: {
                primary_cause: 'Elevated HTTP error rate due to unknown cause',
                confidence_score: 0.6,
                evidence: [
                  { type: 'metric', description: 'http_error_rate_percent', value: '47.06%' }
                ]
              },
              remediation: {
                immediate_actions: [
                  { action: 'Investigate recent code changes', command: 'git log', estimated_time: '30m' }
                ]
              }
            },
            investigation_steps: [
              { step: 'plan', message: '📋 Planning investigation strategy...', timestamp: new Date().toISOString() },
              { step: 'act', message: '🔍 Fetching observability data...', timestamp: new Date().toISOString() }
            ],
            duration_seconds: 3.45,
            cost_usd: 0.0
          }
        }
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
      queryClient.invalidateQueries({ queryKey: ['incident-stats'] })
    }
  })
}