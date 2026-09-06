import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

/**
 * Button — 日式极简,大圆角,3 个变体。
 * 通过 asChild 转为 Radix Slot 模式,可包 Link。
 */
const buttonVariants = cva(
  // 基础层
  'inline-flex items-center justify-center gap-2 font-medium ' +
    'transition-all duration-200 ease-soft ' +
    'focus-visible:outline-none focus-visible:shadow-glow ' +
    'disabled:pointer-events-none disabled:opacity-50 ' +
    'select-none',
  {
    variants: {
      variant: {
        primary:
          'bg-accent-500 text-white hover:bg-accent-600 active:scale-[0.98] ' +
          'shadow-soft hover:shadow-lift',
        ghost:
          'text-ink-700 hover:bg-ink-100 active:scale-[0.98]',
        outline:
          'border border-ink-100 bg-surface text-ink-700 ' +
          'hover:border-ink-300 hover:bg-canvas active:scale-[0.98]',
        soft:
          'bg-accent-50 text-accent-700 hover:bg-accent-100 active:scale-[0.98]',
      },
      size: {
        sm:  'h-9  px-3.5 text-sm rounded-xl',
        md:  'h-11 px-5 text-sm rounded-xl',
        lg:  'h-13 px-6 text-base rounded-2xl',  // 52px
        icon:'h-10 w-10 rounded-xl',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp
        className={cn(buttonVariants({ variant, size }), className)}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

/** IconButton — 方形按钮,只放图标 */
export const IconButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'ghost', ...props }, ref) => (
    <Button
      ref={ref}
      variant={variant}
      size="icon"
      className={cn('text-ink-700', className)}
      {...props}
    />
  )
)
IconButton.displayName = 'IconButton'

export { buttonVariants }
