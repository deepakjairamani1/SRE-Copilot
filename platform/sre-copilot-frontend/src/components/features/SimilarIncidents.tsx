import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { 
  Brain, 
  TrendingUp, 
  Clock, 
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Zap
} from 'lucide-react'

interface SimilarIncident {
  incident_id: string
  similarity_score: number
  metadata: {
    service?: string
    severity?: string
    detected_at?: string
    title?: string
    primary_cause?: string
    keywords?: string[]
  }
}

interface SimilarIncidentsProps {
  similarIncidents?: SimilarIncident[]
  isLoading?: boolean
}

export function SimilarIncidents({ similarIncidents = [], isLoading = false }: SimilarIncidentsProps) {
  if (isLoading) {
    return (
      <Card className="mb-6">
        <div className="flex items-center gap-3 mb-6">
          <Brain className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">Similar Incidents (AI Semantic Analysis)</h2>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-24 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      </Card>
    )
  }

  if (similarIncidents.length === 0) {
    return (
      <Card className="mb-6">
        <div className="flex items-center gap-3 mb-6">
          <Brain className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">Similar Incidents (AI Semantic Analysis)</h2>
        </div>
        <div className="text-center py-8">
          <Brain className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600 mb-2">No similar incidents found</p>
          <p className="text-sm text-gray-500">
            This appears to be a novel incident pattern. The AI will learn from this for future analysis.
          </p>
        </div>
      </Card>
    )
  }

  return (
    <Card className="mb-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">Similar Incidents (AI Semantic Analysis)</h2>
        </div>
        <Badge variant="info" className="flex items-center gap-1">
          <Zap className="w-3 h-3" />
          {similarIncidents.length} Found
        </Badge>
      </div>

      <div className="mb-4 p-4 bg-purple-50 rounded-xl border border-purple-200">
        <div className="flex items-start gap-3">
          <TrendingUp className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-purple-900 mb-1">AI Semantic Matching</p>
            <p className="text-sm text-purple-800">
              These incidents were identified using Bedrock Titan embeddings with {Math.round(similarIncidents[0]?.similarity_score * 100 || 75)}%+ similarity threshold.
              The AI analyzed technical patterns, error signatures, and resolution approaches.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {similarIncidents.map((incident, index) => (
          <SimilarIncidentCard key={incident.incident_id} incident={incident} rank={index + 1} />
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Brain className="w-4 h-4" />
          <span>
            Semantic analysis helps identify patterns and successful resolution strategies from past incidents
          </span>
        </div>
      </div>
    </Card>
  )
}

function SimilarIncidentCard({ incident, rank }: { incident: SimilarIncident; rank: number }) {
  const similarity = Math.round(incident.similarity_score * 100)
  const metadata = incident.metadata

  const getSeverityColor = (severity?: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200'
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getSimilarityColor = (score: number) => {
    if (score >= 90) return 'text-green-700 bg-green-100'
    if (score >= 80) return 'text-blue-700 bg-blue-100'
    if (score >= 70) return 'text-purple-700 bg-purple-100'
    return 'text-gray-700 bg-gray-100'
  }

  return (
    <div className="relative p-5 rounded-xl border-2 border-gray-100 hover:border-purple-200 transition-all duration-200 hover:shadow-md">
      {/* Rank Badge */}
      <div className="absolute -top-2 -left-2 w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center text-sm font-bold">
        {rank}
      </div>

      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold text-gray-900 font-mono text-sm">
              {incident.incident_id}
            </h3>
            {metadata.severity && (
              <span className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(metadata.severity)}`}>
                {metadata.severity.toUpperCase()}
              </span>
            )}
          </div>
          
          {metadata.title && (
            <p className="text-gray-900 font-medium mb-2 line-clamp-2">
              {metadata.title}
            </p>
          )}
          
          {metadata.primary_cause && (
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">
              <span className="font-medium">Root Cause:</span> {metadata.primary_cause}
            </p>
          )}
        </div>

        <div className="text-right ml-4">
          <div className={`px-3 py-1 rounded-full text-sm font-bold ${getSimilarityColor(similarity)}`}>
            {similarity}% Match
          </div>
          {metadata.detected_at && (
            <div className="flex items-center gap-1 text-xs text-gray-500 mt-2">
              <Clock className="w-3 h-3" />
              <span>{new Date(metadata.detected_at).toLocaleDateString()}</span>
            </div>
          )}
        </div>
      </div>

      {/* Keywords */}
      {metadata.keywords && metadata.keywords.length > 0 && (
        <div className="mb-3">
          <p className="text-xs text-gray-600 mb-2 font-medium">Matching Keywords:</p>
          <div className="flex flex-wrap gap-1">
            {metadata.keywords.slice(0, 6).map((keyword, idx) => (
              <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded font-mono">
                {keyword}
              </span>
            ))}
            {metadata.keywords.length > 6 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                +{metadata.keywords.length - 6} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Service Info */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          {metadata.service && (
            <div className="flex items-center gap-1 text-gray-600">
              <span className="font-medium">Service:</span>
              <span className="font-mono bg-gray-100 px-2 py-1 rounded text-xs">
                {metadata.service}
              </span>
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-1 text-purple-600 hover:text-purple-700 cursor-pointer">
          <span className="text-xs font-medium">View Details</span>
          <ArrowRight className="w-3 h-3" />
        </div>
      </div>

      {/* Similarity Indicator */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Semantic Similarity</span>
          <div className="flex items-center gap-2">
            <div className="w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${
                  similarity >= 90 ? 'bg-green-500' :
                  similarity >= 80 ? 'bg-blue-500' :
                  similarity >= 70 ? 'bg-purple-500' : 'bg-gray-400'
                }`}
                style={{ width: `${similarity}%` }}
              />
            </div>
            <CheckCircle2 className="w-3 h-3 text-green-500" />
          </div>
        </div>
      </div>
    </div>
  )
}