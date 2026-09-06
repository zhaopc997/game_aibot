import * as React from 'react'
import { cn } from '@/lib/utils'

/** Input — xl 圆角 + glow focus,与 Button 风格统一 */
export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input
      ref={ref}
      type={type}
      className={cn(
        'h-11 w-full px-4 text-sm rounded-xl bg-surface',
        'border border-ink-100 text-ink-900 placeholder:text-ink-300',
        'transition-all duration-200 ease-soft',
        'focus:outline-none focus:border-accent-500 focus:shadow-glow',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
      {...props}
    />
  )
)
Input.displayName = 'Input'

/** 大尺寸搜索框(hero / AI 对话用) */
export const LargeInput = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        'h-14 w-full px-5 text-base rounded-2xl bg-surface',
        'border border-ink-100 text-ink-900 placeholder:text-ink-300',
        'transition-all duration-200 ease-soft',
        'focus:outline-none focus:border-accent-500 focus:shadow-glow',
        className
      )}
      {...props}
    />
  )
)
LargeInput.displayName = 'LargeInput'
