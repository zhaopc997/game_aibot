import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

interface GameCoverProps {
  /** 数据库 cover_url（可为外链）。为空时会按 gameId 探测本地素材。 */
  src?: string | null
  /** 游戏 id：用于探测 public/games/{id}.{png,jpg,jpeg,webp} */
  gameId?: number
  alt: string
  /** 无封面时的占位字符 */
  fallback?: string
  className?: string
  emojiClassName?: string
}

const LOCAL_EXTS = ['jpg', 'png', 'webp', 'jpeg', 'svg'] as const

/**
 * 依次探测本地素材路径。
 *
 * 素材约定见 `public/games/README.md`：文件名为 `<gameId>.{jpg,png,webp,jpeg,svg}`，
 * 需自行从开发商官方授权渠道获取。
 *
 * 返回 null 表示本地无素材（调用方应回退到 emoji 占位）。
 * 用 <img> 的 onError 逐个探测，而不是 fetch HEAD——避免额外网络往返与跨域问题。
 */
function probeLocalCandidates(gameId: number): string[] {
  return LOCAL_EXTS.map((ext) => `/games/${gameId}.${ext}`)
}

/**
 * 构建按优先级排列的候选路径：数据库外链优先，本地素材兜底。
 * 自动去重避免多次重复发起同一路径的 404 网络请求。
 */
function buildCandidates(src?: string | null, gameId?: number): string[] {
  const list: string[] = []
  if (src) list.push(src)
  if (gameId) list.push(...probeLocalCandidates(gameId))
  return Array.from(new Set(list))
}

/**
 * 游戏封面图（自动降级为 emoji 占位）。
 *
 * <p>不要用 `onError` + `innerHTML` 手动塞占位图：那会绕过 React 的虚拟 DOM，
 * React 卸载该节点时会抛
 * `NotFoundError: Failed to execute 'removeChild' on 'Node'`，
 * 进而中断整棵树的渲染，表现为点击跳转后整页白屏。
 *
 * <p>改为用 state 声明式切换，React 就能正确管理节点增删。
 */
export function GameCover({
  src,
  gameId,
  alt,
  fallback = '🎮',
  className,
  emojiClassName = 'text-5xl select-none',
}: GameCoverProps) {
  // 数据库有图就用数据库的，否则按 gameId 探测本地
  const [candidates, setCandidates] = useState<string[]>(() => buildCandidates(src, gameId))
  const [idx, setIdx] = useState(0)
  const [failed, setFailed] = useState(false)

  // src 变化时重置（例如从列表页点到详情页换了游戏）
  useEffect(() => {
    setCandidates(buildCandidates(src, gameId))
    setIdx(0)
    setFailed(false)
  }, [src, gameId])

  const current = candidates[idx]

  if (failed || !current) {
    return (
      <div
        className={cn(
          'grid place-items-center overflow-hidden bg-gradient-to-br from-ink-100/50 to-ink-50/30',
          className
        )}
      >
        <div className="flex flex-col items-center justify-center p-2 text-center select-none">
          <span className={emojiClassName}>{fallback}</span>
          {alt && <span className="mt-1 text-xs font-medium text-ink-500 line-clamp-1 max-w-[90%]">{alt}</span>}
        </div>
      </div>
    )
  }

  return (
    <img
      key={current}
      src={current}
      alt={alt}
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => {
        // 还有候选路径就试下一个；都没有则回退占位
        if (idx < candidates.length - 1) {
          setIdx((i) => i + 1)
        } else {
          setFailed(true)
        }
      }}
      className={cn('object-cover', className)}
    />
  )
}