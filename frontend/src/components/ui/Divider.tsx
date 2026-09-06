import { cn } from '@/lib/utils'

/** 极简分隔线 */
export function Divider({ className }: { className?: string }) {
  return <hr className={cn('border-0 h-px bg-ink-100', className)} />
}
