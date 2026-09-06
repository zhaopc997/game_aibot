import * as React from 'react'
import { cn } from '@/lib/utils'

/**
 * Card — 大圆角基础卡(2xl=20px)。
 * 组合方式:Card > CardHeader / CardBody / CardFooter。
 */
export const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'bg-surface rounded-2xl shadow-soft border border-ink-100/40',
        'transition-all duration-300 ease-soft',
        className
      )}
      {...props}
    />
  )
)
Card.displayName = 'Card'

/** 可悬浮上浮的卡(列表项/卡片网格用) */
export const HoverCard = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'group bg-surface rounded-2xl shadow-soft border border-ink-100/40',
        'transition-all duration-300 ease-soft',
        'hover:shadow-lift hover:-translate-y-0.5 hover:border-ink-100',
        className
      )}
      {...props}
    />
  )
)
HoverCard.displayName = 'HoverCard'

export const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 pb-3', className)} {...props} />
  )
)
CardHeader.displayName = 'CardHeader'

export const CardBody = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6', className)} {...props} />
  )
)
CardBody.displayName = 'CardBody'

export const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 pt-3 flex items-center', className)} {...props} />
  )
)
CardFooter.displayName = 'CardFooter'
