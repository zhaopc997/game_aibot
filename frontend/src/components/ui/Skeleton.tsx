import { cn } from '@/lib/utils'

/** Skeleton — 加载占位,极简脉冲动画 */
type Props = React.HTMLAttributes<HTMLDivElement> & {
  rounded?: 'xl' | '2xl' | '3xl' | 'full'
}

export function Skeleton({ className, rounded = '2xl', ...props }: Props) {
  const r = { xl: 'rounded-xl', '2xl': 'rounded-2xl', '3xl': 'rounded-3xl', full: 'rounded-full' }[rounded]
  return (
    <div
      className={cn('animate-pulse bg-ink-100/60', r, className)}
      {...props}
    />
  )
}
