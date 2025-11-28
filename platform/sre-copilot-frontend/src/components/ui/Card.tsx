import { cn } from '../../lib/utils'

interface CardProps {
  variant?: 'glass' | 'solid' | 'neumorphic'
  children: React.ReactNode
  className?: string
  style?: React.CSSProperties
  onClick?: () => void
}

export function Card({ variant = 'glass', className, children, style, onClick }: CardProps) {
  return (
    <div 
      className={cn(
        'rounded-2xl p-6 transition-all duration-300',
        variant === 'glass' && 'glass-card',
        variant === 'solid' && 'bg-white shadow-lg',
        variant === 'neumorphic' && 'bg-gray-100 shadow-[8px_8px_16px_#d1d9e6,-8px_-8px_16px_#ffffff]',
        className
      )}
      style={style}
      onClick={onClick}
    >
      {children}
    </div>
  )
}