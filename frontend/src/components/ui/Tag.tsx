import * as React from 'react'
import { cn } from '@/lib/utils'

/**
 * Tag — 攻略/游戏标签。
 * 两种风格:solid 强调色 / outline 描边
 */
type Props = React.HTMLAttributes<HTMLSpanElement> & {
  variant?: 'solid' | 'outline' | 'soft'
  size?: 'sm' | 'md'
}

export function Tag({
  className,
  variant = 'soft',
  size = 'sm',
  children,
  ...props
}: Props) {
  const base =
    'inline-flex items-center font-medium rounded-full whitespace-nowrap ' +
    'transition-colors duration-200'
  const variants = {
    solid:   'bg-accent-500 text-white',
    soft:    'bg-accent-50 text-accent-700 hover:bg-accent-100',
    outline: 'border border-ink-100 text-ink-700 hover:border-ink-300',
  }
  const sizes = {
    sm: 'h-6 px-2.5 text-xs',
    md: 'h-7 px-3 text-sm',
  }
  return (
    <span className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {children}
    </span>
  )
}
