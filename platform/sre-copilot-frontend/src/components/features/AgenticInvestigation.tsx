import { useState, useEffect } from 'react'
import { Card } from '../ui/Card'
import { 
  Search, 
  Database, 
  FileText, 
  Activity, 
  Brain, 
  CheckCircle2,
  Loader2,
  ArrowRight,
  Zap,
  Target,
  Shield,
  BookOpen
} from 'lucide-react'

interface AgentStep {
  id: string
  name: string
  icon: React.ReactNode
  description: string
  status: 'pending' | 'active' | 'completed' | 'error'
  duration?: number
  details?: string[]
  data?: any
}

interface AgenticInvestigationProps {
  isActive: boolean
  serviceName: string
  onComplete?: (result: any) => void
  apiCompleted?: boolean
  apiData?: any
}

export function AgenticInvestigation({ isActive, serviceName, onComplete, apiCompleted = false, apiData }: AgenticInvestigationProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [steps, setSteps] = useState<AgentStep[]>([
    {
      id: 'monitoring',
      name: 'Monitoring Agent',
      icon: <Search className="w-5 h-5" />,
      description: 'Detecting anomalies and gathering initial context',
      status: 'pending',
      details: []
    },
    {
      id: 'orchestrator',
      name: 'Orchestrator Agent',
      icon: <Target className="w-5 h-5" />,
      description: 'Coordinating investigation strategy and resource allocation',
      status: 'pending',
      details: []
    },
    {
      id: 'diagnostic-prometheus',
      name: 'Diagnostic Agent - Metrics',
      icon: <Database className="w-5 h-5" />,
      description: 'Querying Prometheus for performance metrics and trends',
      status: 'pending',
      details: []
    },
    {
      id: 'diagnostic-loki',
      name: 'Diagnostic Agent - Logs',
      icon: <FileText className="w-5 h-5" />,
      description: 'Analyzing Loki logs for error patterns and anomalies',
      status: 'pending',
      details: []
    },
    {
      id: 'diagnostic-jaeger',
      name: 'Diagnostic Agent - Traces',
      icon: <Activity className="w-5 h-5" />,
      description: 'Examining Jaeger traces for latency and dependency issues',
      status: 'pending',
      details: []
    },
    {
      id: 'compliance',
      name: 'Compliance Agent',
      icon: <Shield className="w-5 h-5" />,
      description: 'Validating findings against policies and regulations',
      status: 'pending',
      details: []
    },
    {
      id: 'learning',
      name: 'Learning Agent',
      icon: <BookOpen className="w-5 h-5" />,
      description: 'Correlating with historical incidents and generating insights',
      status: 'pending',
      details: []
    },
    {
      id: 'rca-generation',
      name: 'RCA Generation',
      icon: <Brain className="w-5 h-5" />,
      description: 'Synthesizing findings into comprehensive root cause analysis',
      status: 'pending',
      details: []
    }
  ])

  const agentDetails = {
    monitoring: [
      'Scanning service health metrics',
      'Detecting anomaly patterns using ML models',
      'Correlating with business impact metrics',
      'Generating P1 alert with context'
    ],
    orchestrator: [
      'Assessing incident severity and business impact',
      'Allocating diagnostic agents based on service type',
      'Setting investigation priorities and SLA targets',
      'Coordinating parallel data collection'
    ],
    'diagnostic-prometheus': [
      'Executing PromQL queries for CPU, memory, disk I/O',
      'Analyzing request rate and error rate trends',
      'Checking service dependency health',
      'Identifying performance bottlenecks'
    ],
    'diagnostic-loki': [
      'Parsing application logs for error patterns',
      'Searching for exception stack traces',
      'Analyzing log volume and frequency changes',
      'Extracting relevant error messages'
    ],
    'diagnostic-jaeger': [
      'Tracing request flows across microservices',
      'Measuring span durations and identifying slow operations',
      'Analyzing dependency call patterns',
      'Detecting timeout and connection issues'
    ],
    compliance: [
      'Validating against SLA thresholds',
      'Checking compliance with incident response policies',
      'Ensuring data privacy and security requirements',
      'Approving remediation recommendations'
    ],
    learning: [
      'Searching knowledge base for similar incidents',
      'Analyzing historical resolution patterns',
      'Updating ML models with new data points',
      'Generating confidence scores for hypotheses'
    ],
    'rca-generation': [
      'Correlating findings across all data sources',
      'Ranking root cause hypotheses by evidence',
      'Generating remediation recommendations',
      'Creating comprehensive incident report'
    ]
  }

  useEffect(() => {
    if (!isActive) return

    const interval = setInterval(() => {
      setSteps(prevSteps => {
        const newSteps = [...prevSteps]
        
        // Find current active step
        const activeIndex = newSteps.findIndex(step => step.status === 'active')
        
        if (activeIndex !== -1) {
          // Complete current step
          newSteps[activeIndex] = {
            ...newSteps[activeIndex],
            status: 'completed',
            duration: Math.random() * 3 + 1, // 1-4 seconds
            details: agentDetails[newSteps[activeIndex].id as keyof typeof agentDetails] || []
          }
          
          // Start next step
          if (activeIndex + 1 < newSteps.length) {
            newSteps[activeIndex + 1] = {
              ...newSteps[activeIndex + 1],
              status: 'active'
            }
            setCurrentStep(activeIndex + 1)
          } else {
            // All steps completed
            setTimeout(() => {
              onComplete?.({
                incident_id: `INC-${Date.now()}`,
                duration: 18.5,
                confidence: 0.92,
                status: 'completed'
              })
            }, 1000)
          }
        } else if (currentStep === 0) {
          // Start first step
          newSteps[0] = { ...newSteps[0], status: 'active' }
        }
        
        return newSteps
      })
    }, 2500) // Each step takes ~2.5 seconds

    return () => clearInterval(interval)
  }, [isActive, currentStep, onComplete])

  if (!isActive) return null

  const completedSteps = steps.filter(step => step.status === 'completed').length
  const totalSteps = steps.length
  const progress = (completedSteps / totalSteps) * 100

  return (
    <Card className="mb-6">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-text-primary mb-2">
              Agentic Investigation in Progress
            </h2>
            <p className="text-text-secondary">
              AI agents are autonomously investigating <span className="font-semibold text-primary">{serviceName}</span>
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-primary">{Math.round(progress)}%</div>
            <div className="text-sm text-text-secondary">Complete</div>
          </div>
        </div>

        {/* Colorful Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-3 mb-8 overflow-hidden">
          <div 
            className="h-3 rounded-full transition-all duration-500 ease-out relative"
            style={{ 
              width: `${progress}%`,
              background: `linear-gradient(90deg, 
                #e74c3c 0%, 
                #f39c12 20%, 
                #f1c40f 40%, 
                #2ecc71 60%, 
                #3498db 80%, 
                #9b59b6 100%
              )`
            }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse" />
          </div>
        </div>

        {/* Agent Steps */}
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={step.id} className="relative">
              {/* Colorful Connection Line */}
              {index < steps.length - 1 && (
                <div className={`absolute left-6 top-12 w-0.5 h-16 transition-all duration-500 ${
                  step.status === 'completed' 
                    ? 'bg-gradient-to-b from-green-400 to-blue-400' 
                    : step.status === 'active'
                    ? 'bg-gradient-to-b from-blue-400 to-purple-400 animate-pulse'
                    : 'bg-gray-200'
                }`} />
              )}
              
              <div className={`flex items-start gap-4 p-4 rounded-xl transition-all duration-300 relative overflow-hidden ${
                step.status === 'active' 
                  ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-400 shadow-lg' 
                  : step.status === 'completed'
                  ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-400'
                  : 'bg-gray-50 border-2 border-transparent'
              }`}>
                {/* Animated background for active step */}
                {step.status === 'active' && (
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-blue-400/10 animate-pulse" />
                )}
                {/* Colorful Agent Icon */}
                <div className={`flex items-center justify-center w-12 h-12 rounded-full transition-all relative z-10 ${
                  step.status === 'active'
                    ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg'
                    : step.status === 'completed'
                    ? 'bg-gradient-to-br from-green-500 to-emerald-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  {step.status === 'active' && (
                    <div className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 animate-ping opacity-75" />
                  )}
                  <div className="relative z-10">
                    {step.status === 'completed' ? (
                      <CheckCircle2 className="w-6 h-6" />
                    ) : step.status === 'active' ? (
                      <Loader2 className="w-6 h-6 animate-spin" />
                    ) : (
                      step.icon
                    )}
                  </div>
                </div>

                {/* Agent Details */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className={`font-semibold relative z-10 ${
                      step.status === 'active' ? 'text-blue-700' : 'text-text-primary'
                    }`}>
                      {step.name}
                    </h3>
                    {step.status === 'active' && (
                      <div className="flex items-center gap-1 text-blue-600 relative z-10">
                        <Zap className="w-4 h-4 animate-bounce" />
                        <span className="text-sm font-medium animate-pulse">Active</span>
                      </div>
                    )}
                    {step.duration && (
                      <span className="text-sm text-text-secondary">
                        {step.duration.toFixed(1)}s
                      </span>
                    )}
                  </div>
                  
                  <p className="text-text-secondary mb-3">{step.description}</p>
                  
                  {/* Real-time Details */}
                  {(step.status === 'active' || step.status === 'completed') && step.details && (
                    <div className="space-y-2">
                      {step.details.map((detail, idx) => (
                        <div key={idx} className={`flex items-center gap-2 text-sm transition-all duration-300 relative z-10 ${
                          step.status === 'active' && idx === step.details!.length - 1
                            ? 'text-blue-700 font-medium'
                            : 'text-text-secondary'
                        }`}>
                          <ArrowRight className="w-3 h-3" />
                          <span>{detail}</span>
                          {step.status === 'active' && idx === step.details!.length - 1 && (
                            <Loader2 className="w-3 h-3 animate-spin ml-1 text-blue-600" />
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Status Messages */}
        {apiCompleted && completedSteps < totalSteps && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
            <div className="flex items-center gap-2 text-yellow-700">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="font-medium">API investigation complete - finalizing agent analysis...</span>
            </div>
          </div>
        )}
        
        {completedSteps === totalSteps && !apiCompleted && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
            <div className="flex items-center gap-2 text-blue-700">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="font-medium">Agent analysis complete - waiting for API response...</span>
            </div>
          </div>
        )}

        {/* Colorful Live Stats */}
        <div className="mt-8 grid grid-cols-4 gap-4">
          <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-8 h-8 bg-blue-200 rounded-full -mr-4 -mt-4 opacity-50" />
            <div className="text-sm text-blue-600 mb-1 font-medium">Agents Active</div>
            <div className="text-2xl font-bold text-blue-700">
              {steps.filter(s => s.status === 'active').length}
            </div>
          </div>
          <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-8 h-8 bg-green-200 rounded-full -mr-4 -mt-4 opacity-50" />
            <div className="text-sm text-green-600 mb-1 font-medium">Completed</div>
            <div className="text-2xl font-bold text-green-700">{completedSteps}</div>
          </div>
          <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-8 h-8 bg-purple-200 rounded-full -mr-4 -mt-4 opacity-50" />
            <div className="text-sm text-purple-600 mb-1 font-medium">Data Sources</div>
            <div className="text-2xl font-bold text-purple-700">3</div>
          </div>
          <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl border border-orange-200 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-8 h-8 bg-orange-200 rounded-full -mr-4 -mt-4 opacity-50" />
            <div className="text-sm text-orange-600 mb-1 font-medium">Status</div>
            <div className="text-lg font-bold text-orange-700">
              {apiCompleted && completedSteps === totalSteps ? 'Ready' : 'Running'}
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}