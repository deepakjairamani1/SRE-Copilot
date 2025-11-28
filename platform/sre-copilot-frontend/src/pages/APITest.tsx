import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { useMetrics } from '../hooks/useMetrics'
import { useIncidents, useIncidentStats, useTriggerInvestigation } from '../hooks/useIncidents'
import { useLogs } from '../hooks/useLogs'
import { useTraces } from '../hooks/useTraces'
import { Loader2, AlertTriangle, Activity, Database } from 'lucide-react'

export function APITest() {
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useMetrics()
  const { data: incidents, isLoading: incidentsLoading } = useIncidents({ limit: 5 })
  const { data: stats, isLoading: statsLoading } = useIncidentStats()
  const { data: logs, isLoading: logsLoading } = useLogs('5m')
  const { data: traces, isLoading: tracesLoading } = useTraces()
  const triggerInvestigation = useTriggerInvestigation()

  const handleTriggerInvestigation = () => {
    triggerInvestigation.mutate('user-service')
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">API Integration Test</h1>
          <p className="text-gray-600">Testing React Query hooks with SRE Copilot backend</p>
        </div>

        {/* Metrics */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Observability Metrics</h2>
            {metricsLoading && <Loader2 className="w-5 h-5 animate-spin" />}
          </div>
          
          {metricsError ? (
            <div className="text-red-600">Error: {metricsError.message}</div>
          ) : metricsLoading ? (
            <div className="text-gray-600">Loading metrics...</div>
          ) : metrics ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-medium mb-2">Host Metrics</h3>
                <div className="space-y-2 text-sm">
                  {metrics.host_metrics.cpu_usage_percent && (
                    <div className="flex justify-between">
                      <span>CPU Usage:</span>
                      <Badge variant={metrics.host_metrics.cpu_usage_percent.status === 'ok' ? 'ok' : 'warning'}>
                        {metrics.host_metrics.cpu_usage_percent.current}%
                      </Badge>
                    </div>
                  )}
                  {metrics.host_metrics.memory_usage_percent && (
                    <div className="flex justify-between">
                      <span>Memory Usage:</span>
                      <Badge variant={metrics.host_metrics.memory_usage_percent.status === 'ok' ? 'ok' : 'warning'}>
                        {metrics.host_metrics.memory_usage_percent.current}%
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
              
              <div>
                <h3 className="font-medium mb-2">OTLP Metrics</h3>
                <div className="space-y-2 text-sm">
                  {metrics.otlp_metrics.http_requests_total && (
                    <div className="flex justify-between">
                      <span>HTTP Requests:</span>
                      <span>{metrics.otlp_metrics.http_requests_total.current}</span>
                    </div>
                  )}
                  {metrics.otlp_metrics.http_error_rate_percent && (
                    <div className="flex justify-between">
                      <span>Error Rate:</span>
                      <Badge variant={metrics.otlp_metrics.http_error_rate_percent.status === 'ok' ? 'ok' : 'critical'}>
                        {metrics.otlp_metrics.http_error_rate_percent.current}%
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-600">No metrics data</div>
          )}
        </Card>

        {/* Incident Stats */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Incident Statistics</h2>
            {statsLoading && <Loader2 className="w-5 h-5 animate-spin" />}
          </div>
          
          {stats ? (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{stats.total_incidents}</div>
                <div className="text-sm text-gray-600">Total</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{stats.by_severity.critical}</div>
                <div className="text-sm text-gray-600">Critical</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{stats.by_severity.high}</div>
                <div className="text-sm text-gray-600">High</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{stats.by_severity.medium}</div>
                <div className="text-sm text-gray-600">Medium</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{stats.by_severity.low}</div>
                <div className="text-sm text-gray-600">Low</div>
              </div>
            </div>
          ) : (
            <div className="text-gray-600">Loading stats...</div>
          )}
        </Card>

        {/* Recent Incidents */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Incidents</h2>
            {incidentsLoading && <Loader2 className="w-5 h-5 animate-spin" />}
          </div>
          
          {incidents && incidents.length > 0 ? (
            <div className="space-y-3">
              {incidents.map((incident) => (
                <div key={incident.id} className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    <div>
                      <p className="font-medium text-gray-900">{incident.title}</p>
                      <p className="text-sm text-gray-600">{incident.service} • {incident.detected_at}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={incident.severity as any}>{incident.severity}</Badge>
                    <Badge variant={incident.status === 'open' ? 'warning' : 'ok'}>{incident.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-600">No incidents found</div>
          )}
        </Card>

        {/* API Actions */}
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">API Actions</h2>
          <div className="flex gap-4">
            <Button 
              variant="primary" 
              onClick={handleTriggerInvestigation}
              loading={triggerInvestigation.isPending}
            >
              <Database className="w-4 h-4" />
              Trigger Investigation
            </Button>
          </div>
          
          {triggerInvestigation.isSuccess && (
            <div className="mt-4 p-3 bg-green-100 text-green-800 rounded-lg">
              Investigation triggered successfully!
            </div>
          )}
          
          {triggerInvestigation.isError && (
            <div className="mt-4 p-3 bg-red-100 text-red-800 rounded-lg">
              Error: {triggerInvestigation.error?.message}
            </div>
          )}
        </Card>

        {/* Logs */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Logs</h2>
            {logsLoading && <Loader2 className="w-5 h-5 animate-spin" />}
          </div>
          
          {logs ? (
            <div className="space-y-4">
              {logs.logs?.error_logs && logs.logs.error_logs.length > 0 && (
                <div>
                  <h3 className="font-medium text-red-600 mb-2">Error Logs ({logs.logs.error_logs.length})</h3>
                  <div className="space-y-1">
                    {logs.logs.error_logs.slice(0, 3).map((log: any, i: number) => (
                      <div key={i} className="text-sm text-gray-700 bg-red-50 p-2 rounded">
                        {typeof log === 'string' ? log : log.message || JSON.stringify(log)}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {logs.logs?.critical_logs && logs.logs.critical_logs.length > 0 && (
                <div>
                  <h3 className="font-medium text-red-800 mb-2">Critical Logs ({logs.logs.critical_logs.length})</h3>
                  <div className="space-y-1">
                    {logs.logs.critical_logs.slice(0, 3).map((log: any, i: number) => (
                      <div key={i} className="text-sm text-gray-700 bg-red-100 p-2 rounded">
                        {typeof log === 'string' ? log : log.message || JSON.stringify(log)}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {logs.logs?.warning_logs && logs.logs.warning_logs.length > 0 && (
                <div>
                  <h3 className="font-medium text-yellow-600 mb-2">Warning Logs ({logs.logs.warning_logs.length})</h3>
                  <div className="space-y-1">
                    {logs.logs.warning_logs.slice(0, 3).map((log: any, i: number) => (
                      <div key={i} className="text-sm text-gray-700 bg-yellow-50 p-2 rounded">
                        {typeof log === 'string' ? log : log.message || JSON.stringify(log)}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-600">Loading logs...</div>
          )}
        </Card>

        {/* Traces */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Traces</h2>
            {tracesLoading && <Loader2 className="w-5 h-5 animate-spin" />}
          </div>
          
          {traces ? (
            <div className="space-y-4">
              {traces.traces?.error_traces && traces.traces.error_traces.length > 0 && (
                <div>
                  <h3 className="font-medium text-red-600 mb-2">Error Traces</h3>
                  <div className="space-y-2">
                    {traces.traces.error_traces.map((trace: any, i: number) => (
                      <div key={i} className="bg-red-50 p-3 rounded">
                        <div className="font-medium text-sm">{trace.operation}</div>
                        <div className="text-xs text-gray-600">Duration: {trace.duration} | Service: {trace.service}</div>
                        {trace.error && <div className="text-xs text-red-600 mt-1">Error: {trace.error}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {traces.traces?.slow_traces && traces.traces.slow_traces.length > 0 && (
                <div>
                  <h3 className="font-medium text-yellow-600 mb-2">Slow Traces</h3>
                  <div className="space-y-2">
                    {traces.traces.slow_traces.map((trace: any, i: number) => (
                      <div key={i} className="bg-yellow-50 p-3 rounded">
                        <div className="font-medium text-sm">{trace.operation}</div>
                        <div className="text-xs text-gray-600">Duration: {trace.duration} | Service: {trace.service}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-600">Loading traces...</div>
          )}
        </Card>

        {/* Connection Status */}
        <Card>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Connection Status</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              <span>Metrics:</span>
              <Badge variant={metricsError ? 'critical' : 'ok'} withDot>
                {metricsError ? 'Error' : 'Connected'}
              </Badge>
            </div>
            
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              <span>Incidents:</span>
              <Badge variant="ok" withDot>Connected</Badge>
            </div>
            
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              <span>Logs:</span>
              <Badge variant={logsLoading ? 'warning' : 'ok'} withDot>
                {logsLoading ? 'Loading' : 'Connected'}
              </Badge>
            </div>
            
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              <span>Traces:</span>
              <Badge variant={tracesLoading ? 'warning' : 'ok'} withDot>
                {tracesLoading ? 'Loading' : 'Connected'}
              </Badge>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}