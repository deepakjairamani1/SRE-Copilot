export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:7474'

export const SEVERITY_CONFIG = {
  critical: {
    color: '#EF4444',
    bg: '#FEE2E2',
    label: 'Critical'
  },
  high: {
    color: '#F59E0B',
    bg: '#FEF3C7',
    label: 'High'
  },
  medium: {
    color: '#F97316',
    bg: '#FFEDD5',
    label: 'Medium'
  },
  low: {
    color: '#10B981',
    bg: '#D1FAE5',
    label: 'Low'
  }
}

export const STATUS_CONFIG = {
  ok: {
    color: '#10B981',
    label: 'OK'
  },
  warning: {
    color: '#F59E0B',
    label: 'Warning'
  },
  critical: {
    color: '#EF4444',
    label: 'Critical'
  }
}