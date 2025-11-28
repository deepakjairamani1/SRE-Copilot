import { useState, useEffect } from 'react';
import { Header } from '../components/layout/Header';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { Activity, Database, FileText, GitBranch, Clock, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';

export default function ObservabilityDashboard() {
  const [timeRange, setTimeRange] = useState('5m');
  const [metrics, setMetrics] = useState<any>(null);
  const [logs, setLogs] = useState<any>(null);
  const [traces, setTraces] = useState<any>(null);
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'metrics' | 'logs' | 'traces'>('overview');

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      console.log('Fetching data for time range:', timeRange);
      const [metricsRes, logsRes, tracesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/observability/metrics`),
        fetch(`${API_BASE_URL}/api/observability/logs?time_range=${timeRange}`),
        fetch(`${API_BASE_URL}/api/observability/traces?time_range=${timeRange}`)
      ]);

      const [metricsData, logsData, tracesData] = await Promise.all([
        metricsRes.json(),
        logsRes.json(),
        tracesRes.json()
      ]);

      const logs = logsData.logs || {};
      const traces = tracesData.traces || {};
      const errorCount = logs.error_logs?.length || 0;
      const criticalCount = logs.critical_logs?.length || 0;
      const slowCount = traces.slow_traces?.length || 0;
      
      let healthScore = 100;
      healthScore -= Math.min(errorCount * 2, 30);
      healthScore -= Math.min(criticalCount * 5, 40);
      healthScore -= Math.min(slowCount * 3, 20);
      healthScore = Math.max(healthScore, 0);

      setOverview({
        health_score: healthScore,
        metrics_status: metricsData.error ? 'error' : 'ok',
        logs_status: logsData.error ? 'error' : 'ok',
        traces_status: tracesData.error ? 'error' : 'ok',
        error_count: errorCount,
        critical_count: criticalCount,
        slow_trace_count: slowCount,
        timestamp: new Date().toISOString()
      });

      setMetrics(metricsData);
      setLogs({
        logs: logsData.logs || {},
        statistics: {
          error_count: errorCount,
          critical_count: criticalCount,
          warning_count: logs.warning_logs?.length || 0,
          info_count: logs.info_logs?.length || 0
        }
      });
      setTraces({
        error_traces: traces.error_traces || [],
        slow_traces: traces.slow_traces || [],
        recent_traces: traces.recent_traces || [],
        summary: tracesData.trace_summary || {}
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-600';
    if (score >= 60) return 'from-yellow-500 to-orange-600';
    return 'from-red-500 to-rose-600';
  };

  if (loading && !overview) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Observability Dashboard</h1>
            <p className="text-gray-600 text-lg">Real-time metrics, logs, and traces</p>
          </div>
          <div className="flex gap-4 items-center">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 rounded-xl bg-white shadow-sm hover:border-blue-500 transition-colors disabled:opacity-50"
            >
              <option value="1m">Last 1 minute</option>
              <option value="5m">Last 5 minutes</option>
              <option value="15m">Last 15 minutes</option>
            </select>
            <button
              onClick={fetchDashboardData}
              disabled={loading}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? <LoadingSpinner size="sm" /> : null}
              Refresh
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8 glass-card p-2 rounded-xl inline-flex">
          {['overview', 'metrics', 'logs', 'traces'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-6 py-3 font-medium capitalize rounded-lg transition-all ${
                activeTab === tab
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-600 hover:bg-white/50'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && overview && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <Card className="col-span-1 lg:col-span-2">
                <div className="text-center py-8">
                  <div className="flex items-center justify-center gap-2 mb-4">
                    <Activity className="w-6 h-6 text-blue-600" />
                    <h2 className="text-xl font-semibold text-gray-900">System Health Score</h2>
                  </div>
                  <div className={`text-7xl font-bold bg-gradient-to-r ${getHealthColor(overview.health_score)} bg-clip-text text-transparent mb-2`}>
                    {overview.health_score}%
                  </div>
                  <div className="flex items-center justify-center gap-2 text-gray-600">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">{new Date(overview.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </Card>

              <StatCard
                icon={<FileText className="w-6 h-6" />}
                title="Error Logs"
                value={overview.error_count}
                color="from-red-500 to-rose-600"
              />
              <StatCard
                icon={<AlertCircle className="w-6 h-6" />}
                title="Critical Logs"
                value={overview.critical_count}
                color="from-orange-500 to-red-600"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatusCard
                title="Metrics"
                status={overview.metrics_status}
                icon={<Database className="w-5 h-5" />}
              />
              <StatusCard
                title="Logs"
                status={overview.logs_status}
                icon={<FileText className="w-5 h-5" />}
              />
              <StatusCard
                title="Traces"
                status={overview.traces_status}
                icon={<GitBranch className="w-5 h-5" />}
              />
            </div>
          </div>
        )}

        {/* Metrics Tab */}
        {activeTab === 'metrics' && metrics && (
          <div className="space-y-6">
            <Card>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Host Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(metrics.host_metrics || {}).map(([name, data]: [string, any]) => (
                  <MetricCard key={name} name={name} data={data} />
                ))}
              </div>
            </Card>

            <Card>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Application Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(metrics.otlp_metrics || {}).map(([name, data]: [string, any]) => (
                  <MetricCard key={name} name={name} data={data} />
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && logs && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <LogStatCard title="Errors" count={logs.statistics.error_count} color="red" />
              <LogStatCard title="Critical" count={logs.statistics.critical_count} color="orange" />
              <LogStatCard title="Warnings" count={logs.statistics.warning_count} color="yellow" />
              <LogStatCard title="Info" count={logs.statistics.info_count} color="blue" />
            </div>

            {['error_logs', 'critical_logs', 'warning_logs', 'info_logs'].map((level) => {
              const logList = logs.logs[level] || [];
              if (logList.length === 0) return null;

              return (
                <Card key={level}>
                  <h2 className="text-xl font-bold text-gray-900 mb-4 capitalize">{level.replace('_logs', ' Logs')}</h2>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {logList.slice(0, 50).map((log: any, idx: number) => (
                      <div key={idx} className="p-3 bg-gray-50 rounded-lg text-sm font-mono hover:bg-gray-100 transition-colors">
                        <span className="text-gray-500">{log.timestamp}</span> {log.message}
                      </div>
                    ))}
                  </div>
                </Card>
              );
            })}
          </div>
        )}

        {/* Traces Tab */}
        {activeTab === 'traces' && traces && (
          <div className="space-y-6">
            <Card>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Trace Summary</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <TraceStatCard title="Total" value={traces.summary?.total_traces || 0} />
                <TraceStatCard title="P50 Latency" value={`${traces.summary?.p50_latency_ms?.toFixed(0) || 0}ms`} color="green" />
                <TraceStatCard title="P95 Latency" value={`${traces.summary?.p95_latency_ms?.toFixed(0) || 0}ms`} color="yellow" />
                <TraceStatCard title="P99 Latency" value={`${traces.summary?.p99_latency_ms?.toFixed(0) || 0}ms`} color="red" />
              </div>
            </Card>

            {traces.recent_traces?.length > 0 && (
              <Card>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Traces with Spans</h2>
                <div className="space-y-4">
                  {traces.recent_traces.slice(0, 5).map((trace: any, idx: number) => (
                    <div key={idx} className="border border-gray-200 rounded-xl p-4 hover:border-blue-500 hover:shadow-lg transition-all">
                      <div className="flex justify-between items-start mb-3 pb-3 border-b">
                        <div>
                          <div className="font-semibold text-lg text-gray-900">{trace.root_operation}</div>
                          <div className="text-xs text-gray-500 mt-1">Trace ID: {trace.trace_id}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-blue-600">{trace.duration_ms?.toFixed(2)}ms</div>
                          <div className="text-xs text-gray-500">{trace.spans?.length || 0} spans</div>
                        </div>
                      </div>
                      {trace.spans && trace.spans.length > 0 && (
                        <div className="space-y-1">
                          {trace.spans.map((span: any, spanIdx: number) => (
                            <div key={spanIdx} className="flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg hover:bg-blue-50 transition-colors">
                              <div className="flex-1">
                                <div className="font-medium text-sm">{span.operation_name}</div>
                                {span.service && <div className="text-xs text-gray-500">Service: {span.service}</div>}
                              </div>
                              <div className="font-mono text-sm font-semibold text-gray-900">{span.duration_ms?.toFixed(2)}ms</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({ icon, title, value, color }: any) {
  return (
    <Card className="text-center">
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${color} flex items-center justify-center text-white mx-auto mb-3`}>
        {icon}
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-sm text-gray-600">{title}</div>
    </Card>
  );
}

function StatusCard({ title, status, icon }: any) {
  const statusConfig = {
    ok: { color: 'from-green-500 to-emerald-600', label: 'Healthy' },
    error: { color: 'from-red-500 to-rose-600', label: 'Error' }
  };
  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.ok;

  return (
    <Card>
      <div className="flex items-center gap-3">
        <div className={`p-3 rounded-xl bg-gradient-to-r ${config.color} text-white`}>
          {icon}
        </div>
        <div>
          <div className="text-sm text-gray-600">{title}</div>
          <div className="text-lg font-bold text-gray-900">{config.label}</div>
        </div>
      </div>
    </Card>
  );
}

function MetricCard({ name, data }: any) {
  const statusColors = {
    ok: 'from-green-500 to-emerald-600',
    warning: 'from-yellow-500 to-orange-600',
    critical: 'from-red-500 to-rose-600'
  };

  return (
    <div className="p-4 border border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-lg transition-all">
      <div className="flex items-center gap-2 mb-3">
        <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${statusColors[data.status as keyof typeof statusColors]}`}></div>
        <h3 className="font-medium text-sm text-gray-900">{name.replace(/_/g, ' ')}</h3>
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-2">
        {data.current?.toFixed(2)} <span className="text-sm text-gray-600">{data.unit}</span>
      </div>
      <div className="text-xs text-gray-600">
        Min: {data.min?.toFixed(1)} | Max: {data.max?.toFixed(1)} | Avg: {data.avg?.toFixed(1)}
      </div>
    </div>
  );
}

function LogStatCard({ title, count, color }: any) {
  const colors = {
    red: 'from-red-500 to-rose-600',
    orange: 'from-orange-500 to-red-600',
    yellow: 'from-yellow-500 to-orange-600',
    blue: 'from-blue-500 to-purple-600'
  };

  return (
    <Card className="text-center">
      <div className={`text-4xl font-bold bg-gradient-to-r ${colors[color as keyof typeof colors]} bg-clip-text text-transparent mb-2`}>
        {count}
      </div>
      <div className="text-sm text-gray-600">{title}</div>
    </Card>
  );
}

function TraceStatCard({ title, value, color }: any) {
  const colors = {
    green: 'from-green-500 to-emerald-600',
    yellow: 'from-yellow-500 to-orange-600',
    red: 'from-red-500 to-rose-600'
  };

  return (
    <Card className="text-center">
      <div className={`text-3xl font-bold ${color ? `bg-gradient-to-r ${colors[color as keyof typeof colors]} bg-clip-text text-transparent` : 'text-gray-900'} mb-2`}>
        {value}
      </div>
      <div className="text-sm text-gray-600">{title}</div>
    </Card>
  );
}
