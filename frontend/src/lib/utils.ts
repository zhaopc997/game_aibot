import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** 合并 className + 解决 Tailwind 冲突 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
