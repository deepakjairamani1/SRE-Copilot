import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Clock } from 'lucide-react'
import { formatDate } from '../../lib/utils'

interface TimelineEvent {
  timestamp: string
  event: string
  source: string
}

interface IncidentTimelineProps {
  timeline: TimelineEvent[]
}

export function IncidentTimeline({ timeline }: IncidentTimelineProps) {
  if (!timeline || timeline.length === 0) {
    return null
  }

  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
        <Clock className="w-6 h-6 text-blue-600" />
        Event Timeline
      </h2>

      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-600 to-purple-600" />

        <div className="space-y-6">
          {timeline.map((event, index) => (
            <div key={index} className="relative flex items-start gap-4 pl-10">
              <div className="absolute left-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-blue-600" />
              </div>

              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-sm font-semibold text-gray-900">
                    {formatDate(event.timestamp)}
                  </span>
                  <Badge variant="ok">
                    {event.source}
                  </Badge>
                </div>
                <p className="text-gray-600">{event.event}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}