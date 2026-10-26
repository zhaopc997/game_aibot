import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** 合并 className + 解决 Tailwind 冲突 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * 从 catch 到的任意值中安全提取错误信息。
 *
 * catch 的变量类型在 TS 中是 unknown（不能直接访问 .message），
 * 此前各页面写成 `catch (e: any)` 绕过检查，既丢类型安全又易漏空值。
 * 统一走这里，避免 any 扩散。
 *
 * 取值优先级：后端响应体 message → Error.message → 字符串本身 → 兜底文案
 */
export function errorMessage(e: unknown, fallback = '操作失败，请重试'): string {
  if (typeof e === 'object' && e !== null) {
    const err = e as {
      message?: unknown
      response?: { data?: { message?: unknown } }
    }
    const fromResp = err.response?.data?.message
    if (typeof fromResp === 'string' && fromResp) return fromResp
    if (typeof err.message === 'string' && err.message) return err.message
  }
  if (typeof e === 'string' && e) return e
  return fallback
}
