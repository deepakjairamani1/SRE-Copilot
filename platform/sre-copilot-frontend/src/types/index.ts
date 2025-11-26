export interface Incident {
  id: string
  title: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'investigating' | 'resolved'
  createdAt: string
  updatedAt: string
  assignee?: string
  tags: string[]
}

export interface Metric {
  name: string
  value: number
  unit: string
  timestamp: string
  status: 'ok' | 'warning' | 'critical'
}

export interface Service {
  id: string
  name: string
  status: 'healthy' | 'degraded' | 'down'
  uptime: number
  responseTime: number
  errorRate: number
  lastCheck: string
}

export interface Alert {
  id: string
  title: string
  message: string
  severity: 'info' | 'warning' | 'error'
  timestamp: string
  acknowledged: boolean
}