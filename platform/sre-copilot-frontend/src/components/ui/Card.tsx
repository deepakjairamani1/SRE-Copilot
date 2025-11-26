import { cn } from '../../lib/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'glass' | 'solid' | 'neumorphic'
  children: React.ReactNode
}

export function Card({ variant = 'glass', className, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-2xl p-6 transition-all duration-300',
        variant === 'glass' && 'glass-card',
        variant === 'solid' && 'bg-white shadow-lg',
        variant === 'neumorphic' && 'bg-gray-100 shadow-[8px_8px_16px_#d1d9e6,-8px_-8px_16px_#ffffff]',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}