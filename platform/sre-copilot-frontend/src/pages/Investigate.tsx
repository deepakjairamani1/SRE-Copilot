import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '../components/layout/Header'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useTriggerInvestigation } from '../hooks/useIncidents'
import { 
  Play, 
  Loader2, 
  CheckCircle2,
  AlertTriangle,
  Activity,
  Search,
  Brain,
  Target
} from 'lucide-react'

export default function Investigate() {
  const [selectedService, setSelectedService] = useState('core-athenamind')
  const [customService, setCustomService] = useState('')
  const navigate = useNavigate()
  
  const { mutate: triggerInvestigation, isPending, data, error } = useTriggerInvestigation()

  const availableServices = [
    'core-athenamind',
    'api-gateway',
    'auth-service',
    'payment-service',
    'notification-service'
  ]

  const handleInvestigate = () => {
    const serviceToInvestigate = selectedService === 'custom' ? customService : selectedService
    
    if (!serviceToInvestigate) {
      alert('Please enter a service name')
      return
    }

    triggerInvestigation(serviceToInvestigate, {
      onSuccess: (data) => {
        setTimeout(() => {
          navigate(`/incidents/${data.incident_id}`)
        }, 2000)
      }
    })
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-accent mb-6">
              <Search className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-text-primary mb-3">
              Trigger RCA Investigation
            </h1>
            <p className="text-text-secondary text-lg">
              Start an autonomous root cause analysis using AI-powered investigation
            </p>
          </div>

          {!isPending && !data && (
            <Card className="mb-6">
              <h2 className="text-2xl font-bold text-text-primary mb-6">
                Select Service to Investigate
              </h2>

              <div className="space-y-3 mb-6">
                {availableServices.map(service => (
                  <label
                    key={service}
                    className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all ${
                      selectedService === service
                        ? 'border-primary bg-primary/5'
                        : 'border-gray-200 hover:border-primary/50 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="service"
                      value={service}
                      checked={selectedService === service}
                      onChange={(e) => setSelectedService(e.target.value)}
                      className="w-5 h-5 text-primary"
                    />
                    <div className="flex-1">
                      <p className="font-semibold text-text-primary">{service}</p>
                      <p className="text-sm text-text-secondary">
                        Investigate observability data for this service
                      </p>
                    </div>
                    <Activity className="w-5 h-5 text-primary" />
                  </label>
                ))}

                <label
                  className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    selectedService === 'custom'
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:border-primary/50 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="service"
                    value="custom"
                    checked={selectedService === 'custom'}
                    onChange={(e) => setSelectedService(e.target.value)}
                    className="w-5 h-5 text-primary"
                  />
                  <div className="flex-1">
                    <p className="font-semibold text-text-primary mb-2">Custom Service</p>
                    <input
                      type="text"
                      placeholder="Enter service name..."
                      value={customService}
                      onChange={(e) => setCustomService(e.target.value)}
                      disabled={selectedService !== 'custom'}
                      className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
                    />
                  </div>
                </label>
              </div>

              <div className="p-4 bg-blue-50 rounded-xl border border-blue-200 mb-6">
                <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  What happens during investigation?
                </h3>
                <ul className="space-y-2 text-sm text-blue-800">
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold mt-0.5">1.</span>
                    <span><strong>Plan:</strong> AI analyzes the service and creates investigation strategy</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold mt-0.5">2.</span>
                    <span><strong>Act:</strong> Fetches metrics from Prometheus, logs from Loki, traces from Jaeger</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold mt-0.5">3.</span>
                    <span><strong>Check:</strong> Validates data quality and sufficiency</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold mt-0.5">4.</span>
                    <span><strong>Adapt:</strong> Generates comprehensive RCA report with remediation steps</span>
                  </li>
                </ul>
              </div>

              <Button
                onClick={handleInvestigate}
                size="lg"
                className="w-full text-lg"
              >
                <Play className="w-5 h-5" />
                Start Investigation
              </Button>
            </Card>
          )}

          {isPending && (
            <Card className="mb-6">
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-6 animate-pulse">
                  <Loader2 className="w-10 h-10 text-primary animate-spin" />
                </div>
                <h2 className="text-2xl font-bold text-text-primary mb-3">
                  Investigation in Progress...
                </h2>
                <p className="text-text-secondary mb-8">
                  AI is analyzing {selectedService === 'custom' ? customService : selectedService}
                </p>

                <div className="max-w-md mx-auto space-y-4">
                  <ProgressStep
                    icon="📋"
                    label="Planning investigation strategy"
                    active
                  />
                  <ProgressStep
                    icon="🔍"
                    label="Fetching observability data"
                    active
                  />
                  <ProgressStep
                    icon="✓"
                    label="Validating data quality"
                  />
                  <ProgressStep
                    icon="🧠"
                    label="Generating RCA report"
                  />
                </div>
              </div>
            </Card>
          )}

          {data && !isPending && (
            <Card className="mb-6">
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-success/10 mb-6">
                  <CheckCircle2 className="w-10 h-10 text-success" />
                </div>
                <h2 className="text-2xl font-bold text-text-primary mb-3">
                  Investigation Complete!
                </h2>
                <p className="text-text-secondary mb-6">
                  Incident <code className="px-2 py-1 bg-primary/10 text-primary rounded font-mono text-sm">
                    {data.incident_id}
                  </code> has been created
                </p>

                <div className="grid grid-cols-3 gap-4 max-w-md mx-auto mb-8">
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <p className="text-sm text-text-secondary mb-1">Duration</p>
                    <p className="text-lg font-bold text-text-primary">
                      {data.result?.duration_seconds?.toFixed(2)}s
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <p className="text-sm text-text-secondary mb-1">Cost</p>
                    <p className="text-lg font-bold text-text-primary">
                      ${data.result?.cost_usd?.toFixed(4)}
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-xl">
                    <p className="text-sm text-text-secondary mb-1">Confidence</p>
                    <p className="text-lg font-bold text-text-primary">
                      {(data.result?.rca_report?.root_cause?.confidence_score * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>

                <p className="text-sm text-text-secondary mb-4">
                  Redirecting to incident details...
                </p>
                
                <Button
                  onClick={() => navigate(`/incidents/${data.incident_id}`)}
                  size="lg"
                >
                  View Incident Details
                  <Target className="w-5 h-5" />
                </Button>
              </div>
            </Card>
          )}

          {error && (
            <Card className="mb-6 border-2 border-danger">
              <div className="text-center py-8">
                <AlertTriangle className="w-16 h-16 text-danger mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-text-primary mb-3">
                  Investigation Failed
                </h2>
                <p className="text-text-secondary mb-6">
                  {error.message || 'An error occurred during the investigation'}
                </p>
                <Button onClick={() => window.location.reload()}>
                  Try Again
                </Button>
              </div>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}

function ProgressStep({ icon, label, active = false }: { icon: string; label: string; active?: boolean }) {
  return (
    <div className={`flex items-center gap-4 p-4 rounded-xl transition-all ${
      active ? 'bg-primary/10 border-2 border-primary' : 'bg-gray-50 border-2 border-transparent'
    }`}>
      <span className="text-2xl">{icon}</span>
      <span className={`font-medium ${active ? 'text-primary' : 'text-text-secondary'}`}>
        {label}
      </span>
      {active && <Loader2 className="w-5 h-5 text-primary animate-spin ml-auto" />}
    </div>
  )
}
