import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, MessageCircle, ChevronRight, Coins, X } from 'lucide-react'
import { HoverCard } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'
import { Avatar } from '@/components/ui/Avatar'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import client, { unwrap } from '@/api/client'
import { useAuth } from '@/auth/AuthContext'

/** 与后端 community/domain/Question.java 字段对齐 */
interface Question {
  id: number
  gameId?: number | null
  userId?: number | null
  title: string
  description?: string | null
  bountyPoints?: number
  status?: string
  acceptedAnswerId?: number | null
  createdAt?: string
}

interface GameOption {
  id: number
  name: string
}

const STATUS_LABEL: Record<string, string> = {
  OPEN: '讨论中',
  SOLVED: '已解决',
  CLOSED: '已关闭',
}

function formatTime(iso?: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const diffMin = Math.floor((Date.now() - d.getTime()) / 60000)
  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  const h = Math.floor(diffMin / 60)
  if (h < 24) return `${h} 小时前`
  const day = Math.floor(h / 24)
  if (day < 30) return `${day} 天前`
  return d.toLocaleDateString()
}

export default function QAPage() {
  const { user } = useAuth()
  const [draft, setDraft] = useState('')
  const [keyword, setKeyword] = useState('')
  const [items, setItems] = useState<Question[]>([])
  const [games, setGames] = useState<GameOption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 提问弹窗状态
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newGameId, setNewGameId] = useState<number | ''>('')
  const [newDesc, setNewDesc] = useState('')
  const [newBounty, setNewBounty] = useState<number>(0)
  const [submitting, setSubmitting] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    client
      .get('/questions')
      .then((r) => setItems(unwrap<Question[]>(r) ?? []))
      .catch((e: unknown) => {
        const err = e as { message?: string }
        setError(err.message ?? '加载问答列表失败，请稍后重试')
        setItems([])
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    load()
    client.get('/games').then((r) => {
      const gList = unwrap<GameOption[]>(r) ?? []
      setGames(gList)
    }).catch(() => {})
  }, [load])

  const filtered = keyword.trim()
    ? items.filter((it) =>
        (it.title ?? '').includes(keyword.trim()) ||
        (it.description ?? '').includes(keyword.trim()),
      )
    : items

  function submitSearch() {
    setKeyword(draft)
  }

  const handleOpenAskModal = () => {
    if (!user) {
      alert('请先登录后再发布提问')
      return
    }
    setIsModalOpen(true)
  }

  const handleSubmitQuestion = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim() || submitting) return
    setSubmitting(true)
    try {
      await client.post('/questions', {
        title: newTitle.trim(),
        gameId: newGameId || null,
        description: newDesc.trim() || null,
        bountyPoints: Number(newBounty) || 0,
        status: 'OPEN',
      })
      setIsModalOpen(false)
      setNewTitle('')
      setNewDesc('')
      setNewBounty(0)
      setNewGameId('')
      load()
    } catch {
      alert('发布提问失败，请检查输入或登录状态')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="pt-10 pb-20">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="text-3xl font-display font-semibold text-ink-900">社区问答</h1>
          <p className="mt-1 text-sm text-ink-500">有问题?提出来,大佬来答</p>
        </div>
        <Button variant="primary" onClick={handleOpenAskModal}>
          <Plus size={16} /> 提问
        </Button>
      </div>

      <div className="bg-surface rounded-2xl border border-ink-100 p-2 mb-6 flex items-center gap-2">
        <Input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') submitSearch() }}
          placeholder="搜索问题…回车确认"
          className="border-0 bg-transparent"
        />
        <Button size="sm" onClick={submitSearch}>搜索</Button>
      </div>

      {loading ? (
        <p className="text-ink-500 text-center py-12">加载中…</p>
      ) : error ? (
        <p className="text-danger-600 text-center py-12">{error}</p>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16">
          <MessageCircle size={36} className="mx-auto text-accent-300 mb-3" />
          <p className="text-ink-500">
            {keyword ? `没有匹配「${keyword}」的问题` : '还没有人提问，来做第一个提问的人'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((it) => (
            <Link key={it.id} to={`/qa/${it.id}`}>
              <HoverCard className="p-5 flex items-center gap-4">
                <Avatar size="md" rounded="2xl">?</Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                    <Tag size="sm" variant={it.status === 'SOLVED' ? 'soft' : 'outline'}>
                      {STATUS_LABEL[it.status ?? 'OPEN'] ?? it.status}
                    </Tag>
                    {(it.bountyPoints ?? 0) > 0 && (
                      <span className="inline-flex items-center gap-1 text-xs text-accent-700">
                        <Coins size={12} /> 悬赏 {it.bountyPoints}
                      </span>
                    )}
                    {it.createdAt && (
                      <span className="text-xs text-ink-500">{formatTime(it.createdAt)}</span>
                    )}
                  </div>
                  <h3 className="text-base font-medium text-ink-900 truncate">{it.title}</h3>
                  {it.description && (
                    <p className="mt-1.5 text-sm text-ink-500 line-clamp-2">{it.description}</p>
                  )}
                </div>
                <div className="hidden sm:flex items-center gap-2 text-xs text-ink-500 shrink-0">
                  {it.acceptedAnswerId && (
                    <span className="inline-flex items-center gap-1 text-accent-700 font-medium">
                      <MessageCircle size={12} /> 已采纳
                    </span>
                  )}
                  <ChevronRight size={14} className="mt-0.5" />
                </div>
              </HoverCard>
            </Link>
          ))}
        </div>
      )}

      {/* 提问弹窗 */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="bg-surface w-full max-w-lg rounded-3xl border border-ink-100 shadow-xl p-6 relative">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute right-5 top-5 text-ink-400 hover:text-ink-700"
            >
              <X size={18} />
            </button>

            <h2 className="text-xl font-display font-semibold text-ink-900 mb-4">发布新问题</h2>

            <form onSubmit={handleSubmitQuestion} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-ink-700 mb-1">
                  问题标题 <span className="text-red-500">*</span>
                </label>
                <Input
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="一句话清晰描述你的问题…"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-ink-700 mb-1">相关游戏</label>
                <select
                  value={newGameId}
                  onChange={(e) => setNewGameId(e.target.value ? Number(e.target.value) : '')}
                  className="w-full px-3 py-2 bg-canvas border border-ink-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-accent-400"
                >
                  <option value="">选择游戏（可选）</option>
                  {games.map((g) => (
                    <option key={g.id} value={g.id}>{g.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-ink-700 mb-1">详细描述</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="补充更多上下文，如遇到的关卡、配队情况或错误提示…"
                  rows={4}
                  className="w-full p-3 bg-canvas rounded-xl border border-ink-200 text-sm focus:outline-none focus:ring-2 focus:ring-accent-400"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-ink-700 mb-1">悬赏积分</label>
                <Input
                  type="number"
                  min="0"
                  value={newBounty}
                  onChange={(e) => setNewBounty(Math.max(0, parseInt(e.target.value) || 0))}
                  placeholder="0"
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <Button variant="ghost" type="button" onClick={() => setIsModalOpen(false)}>
                  取消
                </Button>
                <Button variant="primary" type="submit" disabled={submitting || !newTitle.trim()}>
                  {submitting ? '发布中…' : '确认发布'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}