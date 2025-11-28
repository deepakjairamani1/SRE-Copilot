import { Card } from '../ui/Card'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'
import { 
  Wrench, 
  Terminal, 
  Clock, 
  Copy,
  CheckCircle2,
  AlertCircle
} from 'lucide-react'
import { useState } from 'react'

interface Action {
  action: string
  command?: string
  estimated_time?: string
  impact?: string
  priority?: string
}

interface RemediationActionsProps {
  immediateActions?: Action[]
  permanentFixes?: Action[]
}

export function RemediationActions({ immediateActions = [], permanentFixes = [] }: RemediationActionsProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  const copyToClipboard = async (text: string, index: number) => {
    await navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
        <Wrench className="w-6 h-6 text-purple-600" />
        Remediation Actions
      </h2>

      {immediateActions.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <h3 className="font-semibold text-gray-900 text-lg">Immediate Actions</h3>
          </div>
          
          <div className="space-y-4">
            {immediateActions.map((action, index) => (
              <div key={index} className="p-5 rounded-xl bg-red-50 border-2 border-red-100">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-red-600 text-white text-sm font-bold">
                        {index + 1}
                      </span>
                      <h4 className="font-semibold text-gray-900">{action.action}</h4>
                    </div>
                    
                    {action.command && (
                      <div className="relative group">
                        <div className="flex items-center gap-2 p-3 bg-gray-900 rounded-lg font-mono text-sm text-green-400 mt-2">
                          <Terminal className="w-4 h-4 flex-shrink-0" />
                          <code className="flex-1">{action.command}</code>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={() => copyToClipboard(action.command!, index)}
                          >
                            {copiedIndex === index ? (
                              <CheckCircle2 className="w-4 h-4 text-green-500" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-4 text-sm mt-3">
                  {action.estimated_time && (
                    <div className="flex items-center gap-1 text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span>~{action.estimated_time}</span>
                    </div>
                  )}
                  {action.impact && (
                    <Badge variant="warning">
                      Impact: {action.impact}
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {permanentFixes.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold text-gray-900 text-lg">Permanent Fixes</h3>
          </div>
          
          <div className="space-y-3">
            {permanentFixes.map((fix, index) => (
              <div key={index} className="flex items-start gap-3 p-4 rounded-xl bg-green-50 border border-green-200">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-green-600 text-white text-sm font-bold flex-shrink-0">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{fix.action}</p>
                  {fix.priority && (
                    <Badge variant="high" className="mt-2">
                      {fix.priority}
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {immediateActions.length === 0 && permanentFixes.length === 0 && (
        <div className="text-center py-8 text-gray-600">
          <Wrench className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No remediation actions available</p>
        </div>
      )}
    </Card>
  )
}