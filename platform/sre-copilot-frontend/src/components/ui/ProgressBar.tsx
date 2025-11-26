import { motion } from 'framer-motion'
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
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-text-secondary mt-1 text-right">
          {progress}%
        </p>
      )}
    </div>
  )
}
