import { cn } from '../../lib/utils'
import { motion } from 'framer-motion'

interface CardProps {
  variant?: 'glass' | 'solid' | 'neumorphic'
  children: React.ReactNode
  hoverable?: boolean
  className?: string
  onClick?: () => void
  id?: string
  style?: React.CSSProperties
}

export function Card({ variant = 'glass', className, children, hoverable = false, onClick, id, style }: CardProps) {
  const baseClassName = cn(
    'rounded-2xl p-6 transition-all duration-300',
    variant === 'glass' && 'glass-card',
    variant === 'solid' && 'bg-white shadow-lg',
    variant === 'neumorphic' && 'bg-gray-100 shadow-[8px_8px_16px_#d1d9e6,-8px_-8px_16px_#ffffff]',
    hoverable && 'cursor-pointer',
    className
  )
  
  if (hoverable) {
    return (
      <motion.div
        className={baseClassName}
        whileHover={{ scale: 1.02, y: -4 }}
        whileTap={{ scale: 0.98 }}
        onClick={onClick}
        id={id}
        style={style}
      >
        {children}
      </motion.div>
    )
  }
  
  return (
    <div className={baseClassName} onClick={onClick} id={id} style={style}>
      {children}
    </div>
  )
}