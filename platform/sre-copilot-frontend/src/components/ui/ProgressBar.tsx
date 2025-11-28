import { cn } from '../../lib/utils'

interface ProgressBarProps {
  progress: number
  className?: string
  color?: string
  showLabel?: boolean
}

export function ProgressBar({ 
  progress, 
  className, 
  color = '#6366F1',
  showLabel = false 
}: ProgressBarProps) {
  return (
    <div className={cn('w-full', className)}>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{ backgroundColor: color, width: `${progress}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-gray-600 mt-1 text-right">
          {progress}%
        </p>
      )}
    </div>
  )
}
