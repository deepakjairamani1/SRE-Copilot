import { Card } from './Card'
import { cn } from '../../lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  trend?: {
    value: number
    direction: 'up' | 'down' | 'neutral'
  }
  color?: string
}

export function StatCard({ title, value, icon, trend, color = '#6366F1' }: StatCardProps) {
  const TrendIcon = trend?.direction === 'up' ? TrendingUp : trend?.direction === 'down' ? TrendingDown : Minus
  
  return (
    <Card className="hover:scale-105 transition-transform cursor-pointer">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-gray-600 text-sm font-medium mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          
          {trend && (
            <div className={cn(
              'flex items-center gap-1 mt-2 text-sm font-medium',
              trend.direction === 'up' && 'text-green-600',
              trend.direction === 'down' && 'text-red-600',
              trend.direction === 'neutral' && 'text-gray-600'
            )}>
              <TrendIcon className="w-4 h-4" />
              <span>{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>
        
        <div 
          className="p-3 rounded-xl"
          style={{ backgroundColor: `${color}20` }}
        >
          <div style={{ color }}>{icon}</div>
        </div>
      </div>
    </Card>
  )
}