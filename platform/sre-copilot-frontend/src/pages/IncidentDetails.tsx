import { useParams, Link } from 'react-router-dom'
import { Header } from '../components/layout/Header'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { RemediationActions } from '../components/features/RemediationActions'
import { IncidentTimeline } from '../components/features/IncidentTimeline'
import { useIncidentDetails } from '../hooks/useIncidents'
import { 
  ArrowLeft, 
  Clock, 
  Target, 
  AlertTriangle,
  CheckCircle2,
  Brain,
  Activity,
  TrendingUp,
  Users,
  Server,
  Lightbulb,
  Shield,
  Code,
  Bell,
  BookOpen
} from 'lucide-react'
import { formatDate, formatDuration, formatCost } from '../lib/utils'
import { SEVERITY_CONFIG } from '../config'

export default function IncidentDetails() {
  const { incident_id } = useParams<{ incident_id: string }>()
  const { data: incident, isLoading } = useIncidentDetails(incident_id!)

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <Header />
        <main className="container mx-auto px-6 py-8">
          <div className="space-y-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-48 bg-gray-100 rounded-2xl animate-pulse" />
            ))}
          </div>
        </main>
      </div>
    )
  }

  if (!incident) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <Header />
        <main className="container mx-auto px-6 py-8">
          <Card className="text-center py-12">
            <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Incident Not Found</h2>
            <p className="text-gray-600 mb-6">
              The incident you're looking for doesn't exist or has been removed.
            </p>
            <Link to="/">
              <Button>Return to Dashboard</Button>
            </Link>
          </Card>
        </main>
      </div>
    )
  }

  const severityConfig = SEVERITY_CONFIG[incident.severity]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <Link to="/" className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>

        {/* Executive Summary */}
        <Card className="mb-6 border-l-4" style={{ borderLeftColor: severityConfig.color }}>
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <Badge variant={incident.severity as any} withDot>
                  {severityConfig.label.toUpperCase()}
                </Badge>
                <span className="text-sm text-gray-600 font-mono">{incident.incident_id}</span>
                <Badge variant={incident.status === 'open' ? 'warning' : 'ok'}>
                  {incident.status.toUpperCase()}
                </Badge>
              </div>
              
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {incident.rca_report?.executive_summary?.title || incident.title}
              </h1>
              
              <p className="text-gray-600 text-lg mb-4">
                {incident.rca_report?.executive_summary?.impact}
              </p>
              
              {incident.rca_report?.executive_summary?.user_impact && (
                <div className="flex items-start gap-2 p-4 bg-amber-50 rounded-xl border border-amber-200">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-amber-900 mb-1">User Impact</p>
                    <p className="text-amber-800">{incident.rca_report.executive_summary.user_impact}</p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="text-right ml-6">
              <div className="flex items-center gap-2 text-gray-600 mb-2">
                <Clock className="w-4 h-4" />
                <span className="text-sm">Detected</span>
              </div>
              <p className="font-semibold text-gray-900">{formatDate(incident.detected_at)}</p>
              
              {incident.resolved_at && (
                <>
                  <div className="flex items-center gap-2 text-gray-600 mt-4 mb-2">
                    <CheckCircle2 className="w-4 h-4" />
                    <span className="text-sm">Resolved</span>
                  </div>
                  <p className="font-semibold text-gray-900">{formatDate(incident.resolved_at)}</p>
                </>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
            <MetricItem 
              label="Confidence Score" 
              value={`${(incident.confidence_score * 100).toFixed(0)}%`}
              icon={<Target className="w-4 h-4" />}
            />
            <MetricItem 
              label="Service" 
              value={incident.service}
              icon={<Activity className="w-4 h-4" />}
            />
            <MetricItem 
              label="Investigation Time" 
              value={formatDuration(incident.duration_seconds)}
              icon={<Clock className="w-4 h-4" />}
            />
            <MetricItem 
              label="AI Cost" 
              value={formatCost(incident.cost_usd)}
              icon={<Brain className="w-4 h-4" />}
            />
          </div>
        </Card>

        {/* Investigation Timeline */}
        <Card className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Activity className="w-6 h-6 text-blue-600" />
            Investigation Timeline (Agentic Loop)
          </h2>

          <div className="space-y-3">
            {incident.investigation_steps?.map((step: any, index: number) => (
              <InvestigationStep
                key={index}
                step={step.step}
                message={step.message}
                timestamp={step.timestamp}
                isLast={index === incident.investigation_steps.length - 1}
              />
            ))}
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between text-sm">
            <div className="flex items-center gap-6">
              <span className="text-gray-600">
                Duration: <span className="font-semibold text-gray-900">{formatDuration(incident.duration_seconds)}</span>
              </span>
              <span className="text-gray-600">
                Cost: <span className="font-semibold text-gray-900">{formatCost(incident.cost_usd)}</span>
              </span>
              <span className="text-gray-600">
                Tokens: <span className="font-semibold text-gray-900">{incident.tokens_used?.toLocaleString()}</span>
              </span>
            </div>
            <Badge variant="ok">Completed</Badge>
          </div>
        </Card>

        {/* Root Cause Analysis */}
        {incident.rca_report?.root_cause && (
          <Card className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <Target className="w-6 h-6 text-red-600" />
              Root Cause Analysis
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Primary Cause</h3>
                <p className="text-gray-600 text-lg">{incident.rca_report.root_cause.primary_cause}</p>
              </div>

              {incident.rca_report.root_cause.evidence && incident.rca_report.root_cause.evidence.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Evidence</h3>
                  <div className="space-y-2">
                    {incident.rca_report.root_cause.evidence.map((evidence: any, index: number) => (
                      <div key={index} className="flex items-start gap-3 p-4 bg-gray-50 rounded-xl">
                        <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                          <TrendingUp className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-gray-900">{evidence.description}</span>
                            <span className="font-mono text-sm font-bold text-red-600">{evidence.value}</span>
                          </div>
                          <span className="text-xs text-gray-600 uppercase">{evidence.type}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Remediation Actions */}
        {incident.rca_report?.remediation && (
          <div className="mb-6">
            <RemediationActions
              immediateActions={incident.rca_report.remediation.immediate_actions}
              permanentFixes={incident.rca_report.remediation.permanent_fixes}
            />
          </div>
        )}

        {/* Timeline */}
        {incident.rca_report?.timeline && incident.rca_report.timeline.length > 0 && (
          <IncidentTimeline timeline={incident.rca_report.timeline} />
        )}

        {/* Technical Details */}
        {incident.rca_report?.technical_details && (
          <Card className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <Server className="w-6 h-6 text-purple-600" />
              Technical Details
            </h2>

            {incident.rca_report.technical_details.affected_components && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">Affected Components</h3>
                <div className="flex flex-wrap gap-2">
                  {incident.rca_report.technical_details.affected_components.map((comp: any, idx: number) => (
                    <div key={idx} className="px-4 py-2 bg-red-50 border border-red-200 rounded-lg">
                      <span className="font-medium text-red-900">{comp.component}</span>
                      <span className="text-sm text-red-700 ml-2">({comp.status})</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {incident.rca_report.technical_details.metrics_snapshot && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Metrics Snapshot</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(incident.rca_report.technical_details.metrics_snapshot).map(([key, value]: [string, any]) => (
                    <div key={key} className="p-4 bg-gray-50 rounded-xl">
                      <p className="text-xs text-gray-600 mb-1">{key.replace(/_/g, ' ').toUpperCase()}</p>
                      <p className="text-lg font-bold text-gray-900">{typeof value === 'number' ? value.toFixed(2) : value}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        )}

        {/* Impact Assessment */}
        {incident.rca_report?.impact_assessment && (
          <Card className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <Users className="w-6 h-6 text-orange-600" />
              Impact Assessment
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 bg-orange-50 rounded-xl border border-orange-200">
                <p className="text-sm text-orange-700 mb-1">Severity</p>
                <p className="text-2xl font-bold text-orange-900 capitalize">{incident.rca_report.impact_assessment.severity}</p>
              </div>
              <div className="p-4 bg-orange-50 rounded-xl border border-orange-200">
                <p className="text-sm text-orange-700 mb-1">Users Affected</p>
                <p className="text-2xl font-bold text-orange-900">{incident.rca_report.impact_assessment.users_affected}</p>
              </div>
            </div>
          </Card>
        )}

        {/* Contributing Factors */}
        {incident.rca_report?.root_cause?.contributing_factors && incident.rca_report.root_cause.contributing_factors.length > 0 && (
          <Card className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
              Contributing Factors
            </h2>
            <div className="space-y-2">
              {incident.rca_report.root_cause.contributing_factors.map((factor: string, idx: number) => (
                <div key={idx} className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <span className="text-yellow-600 font-bold">{idx + 1}.</span>
                  <p className="text-yellow-900">{factor}</p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Potential Causes */}
        {incident.rca_report?.potential_causes && incident.rca_report.potential_causes.length > 0 && (
          <Card className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <Lightbulb className="w-6 h-6 text-yellow-600" />
              Potential Causes
            </h2>
            <div className="space-y-3">
              {incident.rca_report.potential_causes.map((cause: any, idx: number) => (
                <div key={idx} className="p-4 bg-gray-50 rounded-xl border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{cause.hypothesis}</h3>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-yellow-500 to-orange-500"
                          style={{ width: `${cause.probability * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-bold text-gray-900">{(cause.probability * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {cause.evidence.map((ev: string, i: number) => (
                      <span key={i} className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">{ev}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Prevention */}
        {incident.rca_report?.prevention && (
          <Card className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
              <Shield className="w-6 h-6 text-green-600" />
              Prevention Measures
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {incident.rca_report.prevention.code_changes && incident.rca_report.prevention.code_changes.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Code className="w-5 h-5 text-blue-600" />
                    Code Changes
                  </h3>
                  <div className="space-y-2">
                    {incident.rca_report.prevention.code_changes.map((change: string, idx: number) => (
                      <div key={idx} className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <p className="text-sm text-blue-900">{change}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {incident.rca_report.prevention.monitoring_enhancements && incident.rca_report.prevention.monitoring_enhancements.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Bell className="w-5 h-5 text-purple-600" />
                    Monitoring Enhancements
                  </h3>
                  <div className="space-y-2">
                    {incident.rca_report.prevention.monitoring_enhancements.map((enhancement: string, idx: number) => (
                      <div key={idx} className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                        <p className="text-sm text-purple-900">{enhancement}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Confidence & Learning */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Confidence */}
          {incident.rca_report?.confidence && (
            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-3">
                <Target className="w-5 h-5 text-blue-600" />
                Confidence Analysis
              </h2>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600 mb-2">Overall Score</p>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                        style={{ width: `${(incident.rca_report.confidence.overall_score || 0) * 100}%` }}
                      />
                    </div>
                    <span className="text-lg font-bold text-gray-900">{((incident.rca_report.confidence.overall_score || 0) * 100).toFixed(0)}%</span>
                  </div>
                </div>
                {incident.rca_report.confidence.uncertainties && incident.rca_report.confidence.uncertainties.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-600 mb-2">Uncertainties</p>
                    <div className="flex flex-wrap gap-2">
                      {incident.rca_report.confidence.uncertainties.map((u: string, i: number) => (
                        <span key={i} className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded">{u}</span>
                      ))}
                    </div>
                  </div>
                )}
                {incident.rca_report.confidence.recommendation && (
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-sm text-blue-900">{incident.rca_report.confidence.recommendation}</p>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Learning Metadata */}
          {incident.rca_report?.learning_metadata && (
            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-3">
                <BookOpen className="w-5 h-5 text-green-600" />
                Learning Metadata
              </h2>
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Worth Learning:</span>
                  <Badge variant={incident.rca_report.learning_metadata.worth_learning ? 'ok' : 'warning'}>
                    {incident.rca_report.learning_metadata.worth_learning ? 'Yes' : 'No'}
                  </Badge>
                </div>
                {incident.rca_report.learning_metadata.reason && (
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Reason</p>
                    <p className="text-sm text-gray-900">{incident.rca_report.learning_metadata.reason}</p>
                  </div>
                )}
                {incident.rca_report.learning_metadata.keywords && incident.rca_report.learning_metadata.keywords.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-600 mb-2">Keywords</p>
                    <div className="flex flex-wrap gap-2">
                      {incident.rca_report.learning_metadata.keywords.map((keyword: string, i: number) => (
                        <span key={i} className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded font-mono">{keyword}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}

function MetricItem({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-2 text-gray-600 text-sm mb-1">
        {icon}
        <span>{label}</span>
      </div>
      <p className="font-semibold text-gray-900">{value}</p>
    </div>
  )
}

function InvestigationStep({ step, message, timestamp, isLast }: { 
  step: string
  message: string
  timestamp: string
  isLast: boolean
}) {
  const stepConfig: Record<string, { icon: string; color: string; label: string }> = {
    plan: { icon: '📋', color: '#6366F1', label: 'PLAN' },
    act: { icon: '🔍', color: '#8B5CF6', label: 'ACT' },
    check: { icon: '✓', color: '#10B981', label: 'CHECK' },
    adapt: { icon: '🔄', color: '#F59E0B', label: 'ADAPT' }
  }

  const config = stepConfig[step] || stepConfig.act

  return (
    <div className="relative flex items-start gap-4">
      {!isLast && (
        <div className="absolute left-5 top-12 w-0.5 h-full bg-gray-200" />
      )}
      
      <div 
        className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0 relative z-10"
        style={{ backgroundColor: `${config.color}20` }}
      >
        {config.icon}
      </div>

      <div className="flex-1 pb-6">
        <div className="flex items-center gap-3 mb-1">
          <span className="font-bold text-sm" style={{ color: config.color }}>
            {config.label}
          </span>
          <span className="text-xs text-gray-600">
            {new Date(timestamp).toLocaleTimeString()}
          </span>
        </div>
        <p className="text-gray-900">{message}</p>
      </div>
    </div>
  )
}