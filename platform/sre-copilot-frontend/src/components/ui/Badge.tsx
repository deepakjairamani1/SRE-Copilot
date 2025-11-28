import { cn } from '../../lib/utils'

interface BadgeProps {
  variant: 'critical' | 'high' | 'medium' | 'low' | 'ok' | 'warning'
  children: React.ReactNode
  withDot?: boolean
  className?: string
}

export function Badge({ variant, children, withDot = false, className }: BadgeProps) {
  const colors = {
    critical: 'bg-red-100 text-red-700 border-red-200',
    high: 'bg-amber-100 text-amber-700 border-amber-200',
    medium: 'bg-orange-100 text-orange-700 border-orange-200',
    low: 'bg-green-100 text-green-700 border-green-200',
    ok: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    warning: 'bg-yellow-100 text-yellow-700 border-yellow-200'
  }
  
  const dotColors = {
    critical: 'bg-red-500',
    high: 'bg-amber-500',
    medium: 'bg-orange-500',
    low: 'bg-green-500',
    ok: 'bg-emerald-500',
    warning: 'bg-yellow-500'
  }

  return (
    <span className={cn('status-badge border', colors[variant], className)}>
      {withDot && (
        <span className={cn('pulse-dot', dotColors[variant])}>
          <span className={cn('absolute inline-flex h-full w-full rounded-full', dotColors[variant])} />
        </span>
      )}
      {children}
    </span>
  )
}