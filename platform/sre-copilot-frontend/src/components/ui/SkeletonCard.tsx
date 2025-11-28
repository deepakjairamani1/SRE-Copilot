import { cn } from '../../lib/utils'

interface SkeletonCardProps {
  className?: string
  lines?: number
}

export function SkeletonCard({ className, lines = 3 }: SkeletonCardProps) {
  return (
    <div className={cn('glass-card p-6', className)}>
      <div className="animate-pulse space-y-4">
        <div className="h-4 bg-gray-200 rounded w-3/4" />
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className="h-3 bg-gray-200 rounded" />
        ))}
      </div>
    </div>
  )
}
