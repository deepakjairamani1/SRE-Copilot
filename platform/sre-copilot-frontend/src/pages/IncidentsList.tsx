import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Header } from '../components/layout/Header'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useIncidents, useIncidentStats } from '../hooks/useIncidents'
import { 
  Search, 
  Filter, 
  Download,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  AlertCircle,
  CheckCircle2
} from 'lucide-react'
import { formatDate } from '../lib/utils'
import { SEVERITY_CONFIG } from '../config'
import type { Incident } from '../types'

type SortField = 'detected_at' | 'severity' | 'confidence_score'
type SortOrder = 'asc' | 'desc'

export default function IncidentsList() {
  const [searchQuery, setSearchQuery] = useState('')
  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [serviceFilter, setServiceFilter] = useState<string>('')
  const [sortField, setSortField] = useState<SortField>('detected_at')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [showFilters, setShowFilters] = useState(false)

  const { data: incidents, isLoading } = useIncidents({
    severity: severityFilter || undefined,
    status: statusFilter || undefined,
    service: serviceFilter || undefined,
    limit: 100
  })

  const { data: stats } = useIncidentStats()

  const filteredIncidents = incidents?.filter(incident => {
    const matchesSearch = searchQuery === '' || 
      incident.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      incident.incident_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      incident.service.toLowerCase().includes(searchQuery.toLowerCase())
    
    return matchesSearch
  }).sort((a, b) => {
    let aVal: any = a[sortField]
    let bVal: any = b[sortField]

    if (sortField === 'detected_at') {
      aVal = new Date(aVal).getTime()
      bVal = new Date(bVal).getTime()
    }

    if (sortField === 'severity') {
      const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
      aVal = severityOrder[a.severity]
      bVal = severityOrder[b.severity]
    }

    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const exportToCSV = () => {
    if (!filteredIncidents) return
    
    const headers = ['Incident ID', 'Service', 'Severity', 'Status', 'Title', 'Detected At', 'Confidence']
    const rows = filteredIncidents.map(i => [
      i.incident_id,
      i.service,
      i.severity,
      i.status,
      i.title,
      i.detected_at,
      `${(i.confidence_score * 100).toFixed(0)}%`
    ])
    
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `incidents-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-text-primary mb-2">
              All Incidents
            </h1>
            <p className="text-text-secondary text-lg">
              {filteredIncidents?.length || 0} incidents found
            </p>
          </div>
          
          <Button onClick={exportToCSV} variant="secondary">
            <Download className="w-4 h-4" />
            Export CSV
          </Button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <StatBox
            label="Total"
            value={stats?.total_incidents || 0}
            active={!severityFilter && !statusFilter}
            onClick={() => {
              setSeverityFilter('')
              setStatusFilter('')
            }}
          />
          <StatBox
            label="Critical"
            value={stats?.by_severity.critical || 0}
            color="#EF4444"
            active={severityFilter === 'critical'}
            onClick={() => setSeverityFilter(severityFilter === 'critical' ? '' : 'critical')}
          />
          <StatBox
            label="High"
            value={stats?.by_severity.high || 0}
            color="#F59E0B"
            active={severityFilter === 'high'}
            onClick={() => setSeverityFilter(severityFilter === 'high' ? '' : 'high')}
          />
          <StatBox
            label="Medium"
            value={stats?.by_severity.medium || 0}
            color="#F97316"
            active={severityFilter === 'medium'}
            onClick={() => setSeverityFilter(severityFilter === 'medium' ? '' : 'medium')}
          />
          <StatBox
            label="Low"
            value={stats?.by_severity.low || 0}
            color="#10B981"
            active={severityFilter === 'low'}
            onClick={() => setSeverityFilter(severityFilter === 'low' ? '' : 'low')}
          />
        </div>

        <Card className="mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
              <input
                type="text"
                placeholder="Search incidents by ID, title, or service..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              />
            </div>

            <Button
              variant="ghost"
              onClick={() => setShowFilters(!showFilters)}
              className="md:w-auto"
            >
              <Filter className="w-4 h-4" />
              Filters
              {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </Button>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Status
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"
                >
                  <option value="">All Statuses</option>
                  <option value="open">Open</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Service
                </label>
                <select
                  value={serviceFilter}
                  onChange={(e) => setServiceFilter(e.target.value)}
                  className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"
                >
                  <option value="">All Services</option>
                  {Object.keys(stats?.by_service || {}).map(service => (
                    <option key={service} value={service}>{service}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-end">
                <Button
                  variant="ghost"
                  onClick={() => {
                    setSeverityFilter('')
                    setStatusFilter('')
                    setServiceFilter('')
                    setSearchQuery('')
                  }}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          )}
        </Card>

        <Card className="overflow-hidden">
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="h-20 bg-gray-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : filteredIncidents && filteredIncidents.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left px-4 py-4 text-sm font-semibold text-text-secondary">
                      Incident ID
                    </th>
                    <th className="text-left px-4 py-4 text-sm font-semibold text-text-secondary">
                      Service
                    </th>
                    <th 
                      className="text-left px-4 py-4 text-sm font-semibold text-text-secondary cursor-pointer hover:text-primary transition-colors"
                      onClick={() => handleSort('severity')}
                    >
                      <div className="flex items-center gap-2">
                        Severity
                        {sortField === 'severity' && (
                          sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </div>
                    </th>
                    <th className="text-left px-4 py-4 text-sm font-semibold text-text-secondary">
                      Status
                    </th>
                    <th className="text-left px-4 py-4 text-sm font-semibold text-text-secondary">
                      Title
                    </th>
                    <th 
                      className="text-left px-4 py-4 text-sm font-semibold text-text-secondary cursor-pointer hover:text-primary transition-colors"
                      onClick={() => handleSort('detected_at')}
                    >
                      <div className="flex items-center gap-2">
                        Detected At
                        {sortField === 'detected_at' && (
                          sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </div>
                    </th>
                    <th 
                      className="text-left px-4 py-4 text-sm font-semibold text-text-secondary cursor-pointer hover:text-primary transition-colors"
                      onClick={() => handleSort('confidence_score')}
                    >
                      <div className="flex items-center gap-2">
                        Confidence
                        {sortField === 'confidence_score' && (
                          sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        )}
                      </div>
                    </th>
                    <th className="text-right px-4 py-4 text-sm font-semibold text-text-secondary">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredIncidents.map((incident) => (
                    <IncidentRow key={incident.id} incident={incident} />
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <AlertCircle className="w-16 h-16 text-text-secondary mx-auto mb-4 opacity-30" />
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                No incidents found
              </h3>
              <p className="text-text-secondary">
                Try adjusting your filters or search query
              </p>
            </div>
          )}
        </Card>
      </main>
    </div>
  )
}

interface StatBoxProps {
  label: string
  value: number
  color?: string
  active?: boolean
  onClick?: () => void
}

function StatBox({ label, value, color = '#6366F1', active, onClick }: StatBoxProps) {
  return (
    <button
      onClick={onClick}
      className="p-4 rounded-xl transition-all glass-card hover:shadow-lg hover:scale-105"
      style={active ? { backgroundColor: color, color: 'white' } : {}}
    >
      <p className={`text-sm font-medium mb-1 ${active ? 'text-white' : 'text-text-secondary'}`}>
        {label}
      </p>
      <p className={`text-2xl font-bold ${active ? 'text-white' : 'text-text-primary'}`}>
        {value}
      </p>
    </button>
  )
}

function IncidentRow({ incident }: { incident: Incident }) {
  const severityConfig = SEVERITY_CONFIG[incident.severity]
  
  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
      <td className="px-4 py-4">
        <code className="text-sm font-mono text-primary bg-primary/10 px-2 py-1 rounded">
          {incident.incident_id}
        </code>
      </td>
      <td className="px-4 py-4">
        <span className="text-sm text-text-primary font-medium">
          {incident.service}
        </span>
      </td>
      <td className="px-4 py-4">
        <Badge variant={incident.severity}>
          {severityConfig.label}
        </Badge>
      </td>
      <td className="px-4 py-4">
        {incident.status === 'open' ? (
          <Badge variant="warning" withDot>
            Open
          </Badge>
        ) : (
          <Badge variant="ok">
            <CheckCircle2 className="w-3 h-3" />
            Resolved
          </Badge>
        )}
      </td>
      <td className="px-4 py-4 max-w-md">
        <p className="text-sm text-text-primary font-medium line-clamp-2">
          {incident.title}
        </p>
      </td>
      <td className="px-4 py-4">
        <span className="text-sm text-text-secondary">
          {formatDate(incident.detected_at)}
        </span>
      </td>
      <td className="px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden flex-shrink-0">
            <div 
              className="h-full transition-all duration-300"
              style={{ 
                width: `${(incident.confidence_score || 0) * 100}%`,
                background: `linear-gradient(to right, #6366F1, #8B5CF6)`
              }}
            />
          </div>
          <span className="text-sm font-medium text-text-primary whitespace-nowrap">
            {((incident.confidence_score || 0) * 100).toFixed(0)}%
          </span>
        </div>
      </td>
      <td className="px-4 py-4 text-right">
        <Link to={`/incidents/${incident.incident_id}`}>
          <Button size="sm" variant="ghost">
            View
            <ExternalLink className="w-3 h-3" />
          </Button>
        </Link>
      </td>
    </tr>
  )
}
