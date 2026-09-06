import * as React from 'react'
import { cn } from '@/lib/utils'

type Props = React.HTMLAttributes<HTMLDivElement> & {
  size?: 'sm' | 'md' | 'lg'
  rounded?: 'full' | '2xl' | '3xl'
}

const sizes = {
  sm: 'h-7 w-7 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-14 w-14 text-base',
}
const rounds = {
  full: 'rounded-full',
  '2xl': 'rounded-2xl',
  '3xl': 'rounded-3xl',
}

/**
 * Avatar — 圆角方形(默认)或全圆。背景用 accent-50 + 文字 accent-700,
 * 没有图片时显示用户名首字符,有图片时显示 img。
 */
export function Avatar({
  className,
  size = 'md',
  rounded = '2xl',
  children,
  src,
  alt,
  ...props
}: Props & { src?: string; alt?: string }) {
  return (
    <div
      className={cn(
        'inline-flex items-center justify-center overflow-hidden font-semibold',
        'bg-accent-50 text-accent-700 select-none',
        sizes[size],
        rounds[rounded],
        className
      )}
      {...props}
    >
      {src ? (
        <img src={src} alt={alt ?? ''} className="h-full w-full object-cover" />
      ) : (
        children
      )}
    </div>
  )
}
