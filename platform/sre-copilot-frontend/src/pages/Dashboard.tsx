import { Header } from '../components/layout/Header'
import { Card } from '../components/ui/Card'
import { StatCard } from '../components/ui/StatCard'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { MetricChart } from '../components/features/MetricChart'
import { useMetrics } from '../hooks/useMetrics'
import { useIncidents, useIncidentStats } from '../hooks/useIncidents'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Cpu,
  HardDrive,
  Network,
  Zap,
  ChevronRight
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { formatDate } from '../lib/utils'
import { SEVERITY_CONFIG } from '../config'

export default function Dashboard() {
  const { data: metrics, isLoading: metricsLoading } = useMetrics()
  const { data: incidents, isLoading: incidentsLoading } = useIncidents({ limit: 5 })
  const { data: stats } = useIncidentStats()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">System Monitoring</h1>
          <p className="text-gray-600 text-lg">Real-time observability and incident tracking</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Incidents"
            value={stats?.total_incidents || 0}
            icon={<Activity className="w-6 h-6" />}
            color="#6366F1"
            trend={{ value: 12, direction: 'down' }}
          />
          <StatCard
            title="Critical"
            value={stats?.by_severity.critical || 0}
            icon={<AlertTriangle className="w-6 h-6" />}
            color="#EF4444"
            trend={{ value: 25, direction: 'up' }}
          />
          <StatCard
            title="High Priority"
            value={stats?.by_severity.high || 0}
            icon={<Clock className="w-6 h-6" />}
            color="#F59E0B"
          />
          <StatCard
            title="Resolved Today"
            value={0}
            icon={<CheckCircle className="w-6 h-6" />}
            color="#10B981"
            trend={{ value: 8, direction: 'up' }}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Host Metrics</h2>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-sm text-gray-600">Live</span>
              </div>
            </div>

            {metricsLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <MetricRow
                  icon={<Cpu className="w-5 h-5" />}
                  label="CPU Usage"
                  value={`${metrics?.host_metrics.cpu_usage_percent?.current.toFixed(1) || 0}%`}
                  status={metrics?.host_metrics.cpu_usage_percent?.status || 'ok'}
                  details={`avg: ${metrics?.host_metrics.cpu_usage_percent?.avg?.toFixed(1) || 0}%`}
                />
                <MetricRow
                  icon={<HardDrive className="w-5 h-5" />}
                  label="Memory Usage"
                  value={`${metrics?.host_metrics.memory_usage_percent?.current.toFixed(1) || 0}%`}
                  status={metrics?.host_metrics.memory_usage_percent?.status || 'ok'}
                  details={`avg: ${metrics?.host_metrics.memory_usage_percent?.avg?.toFixed(1) || 0}%`}
                />
                <MetricRow
                  icon={<Network className="w-5 h-5" />}
                  label="Network RX"
                  value={`${(metrics?.host_metrics.network_receive_bytes_per_sec?.current || 0).toFixed(0)} B/s`}
                  status={metrics?.host_metrics.network_receive_bytes_per_sec?.status || 'ok'}
                />
              </div>
            )}
          </Card>

          <Card>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Application Metrics</h2>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-sm text-gray-600">Live</span>
              </div>
            </div>

            {metricsLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <MetricRow
                  icon={<AlertTriangle className="w-5 h-5" />}
                  label="Error Rate"
                  value={`${metrics?.otlp_metrics.http_error_rate_percent?.current.toFixed(2) || 0}%`}
                  status={metrics?.otlp_metrics.http_error_rate_percent?.status || 'ok'}
                  critical={metrics?.otlp_metrics.http_error_rate_percent?.status === 'critical'}
                />
                <MetricRow
                  icon={<Zap className="w-5 h-5" />}
                  label="P95 Latency"
                  value={`${metrics?.otlp_metrics.http_latency_p95_ms?.current.toFixed(1) || 0}ms`}
                  status={metrics?.otlp_metrics.http_latency_p95_ms?.status || 'ok'}
                />
                <MetricRow
                  icon={<Activity className="w-5 h-5" />}
                  label="Total Requests"
                  value={metrics?.otlp_metrics.http_requests_total?.current.toFixed(0) || '0'}
                  status="ok"
                />
                {metrics?.otlp_metrics.http_active_connections && (
                  <MetricRow
                    icon={<Network className="w-5 h-5" />}
                    label="Active Connections"
                    value={metrics.otlp_metrics.http_active_connections.current.toFixed(0)}
                    status={metrics.otlp_metrics.http_active_connections.status}
                  />
                )}
                {metrics?.otlp_metrics.db_query_duration_seconds && (
                  <MetricRow
                    icon={<HardDrive className="w-5 h-5" />}
                    label="DB Query Time"
                    value={`${(metrics.otlp_metrics.db_query_duration_seconds.current * 1000).toFixed(1)}ms`}
                    status={metrics.otlp_metrics.db_query_duration_seconds.status}
                  />
                )}
              </div>
            )}
          </Card>
        </div>

        {/* Metric Trends */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Metric Trends</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <MetricChart
              title="CPU Usage"
              data={[]}
              color="#6366F1"
              unit="%"
            />
            <MetricChart
              title="Memory Usage"
              data={[]}
              color="#8B5CF6"
              unit="%"
            />
            <MetricChart
              title="HTTP Latency (P95)"
              data={[]}
              color="#F59E0B"
              unit="ms"
              type="line"
            />
          </div>
        </div>

        <Card>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Incidents</h2>
            <Link to="/incidents">
              <Button variant="ghost" size="sm">
                View All
                <ChevronRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>

          {incidentsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-20 bg-gray-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : incidents && incidents.length > 0 ? (
            <div className="space-y-3">
              {incidents.map(incident => (
                <Link 
                  key={incident.id} 
                  to={`/incidents/${incident.incident_id}`}
                  className="block"
                >
                  <div className="p-4 rounded-xl border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all cursor-pointer">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Badge variant={incident.severity as any} withDot>
                            {SEVERITY_CONFIG[incident.severity].label}
                          </Badge>
                          <span className="text-sm text-gray-600">{incident.incident_id}</span>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-1">{incident.title}</h3>
                        <p className="text-sm text-gray-600 line-clamp-1">{incident.root_cause}</p>
                      </div>
                      <div className="text-right text-sm text-gray-600">
                        <div>{formatDate(incident.detected_at)}</div>
                        <div className="mt-1">Confidence: {(incident.confidence_score * 100).toFixed(0)}%</div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4 opacity-50" />
              <p className="text-gray-600 text-lg">No incidents detected</p>
              <p className="text-gray-500 text-sm mt-1">System is running smoothly</p>
            </div>
          )}
        </Card>
      </main>
    </div>
  )
}

interface MetricRowProps {
  icon: React.ReactNode
  label: string
  value: string
  status: 'ok' | 'warning' | 'critical'
  details?: string
  critical?: boolean
}

function MetricRow({ icon, label, value, status, details, critical }: MetricRowProps) {
  const statusColors = {
    ok: 'text-green-600 bg-green-50',
    warning: 'text-yellow-600 bg-yellow-50',
    critical: 'text-red-600 bg-red-50'
  }

  return (
    <div className={`flex items-center justify-between p-4 rounded-xl ${critical ? 'bg-red-50 border-2 border-red-200' : 'bg-gray-50'}`}>
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${statusColors[status]}`}>
          {icon}
        </div>
        <div>
          <p className="font-medium text-gray-900">{label}</p>
          {details && <p className="text-xs text-gray-600">{details}</p>}
        </div>
      </div>
      <div className="text-right">
        <p className="text-xl font-bold text-gray-900">{value}</p>
        <Badge variant={status} className="mt-1">
          {status.toUpperCase()}
        </Badge>
      </div>
    </div>
  )
}