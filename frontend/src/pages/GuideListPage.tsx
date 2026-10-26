import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Search, Heart, Filter, ChevronLeft, ChevronRight } from 'lucide-react'
import { HoverCard } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import client, { unwrap } from '@/api/client'

interface Guide {
  id: number
  title: string
  summary?: string
  tags: string[]
  difficulty?: string
  likeCount: number
  usefulCount: number
  updatedAt: string
}

interface PageResult<T> { items: T[]; nextCursor?: string | null }

const PAGE_SIZE = 20

/** 从攻略 tags 中取第一个作为分类标签（后端 tags 为字符串数组）。 */
function primaryTag(g: Guide): string {
  return g.tags?.[0] ?? '攻略'
}

export default function GuideListPage() {
  const [params, setParams] = useSearchParams()
  const t = params.get('type') ?? '全部'
  const [q, setQ] = useState('')
  const [keyword, setKeyword] = useState('')
  const [items, setItems] = useState<Guide[]>([])
  const [page, setPage] = useState(0)
  const [hasNext, setHasNext] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    const search = new URLSearchParams({ page: String(page), size: String(PAGE_SIZE) })
    if (keyword) search.set('keyword', keyword)
    if (t !== '全部') search.set('tag', t)
    client
      .get(`/guides/search?${search.toString()}`)
      .then((r) => {
        const data = unwrap<PageResult<Guide>>(r)
        setItems(data.items ?? [])
        setHasNext(Boolean(data.nextCursor))
      })
      .catch((e: unknown) => {
        const err = e as { message?: string }
        setError(err.message ?? '加载攻略失败，请稍后重试')
        setItems([])
      })
      .finally(() => setLoading(false))
  }, [page, keyword, t])

  useEffect(load, [load])

  // 分类候选来自已加载数据的标签并集；搜索/筛选时会动态变化
  const tagOptions = useMemo(() => {
    const set = new Set<string>()
    for (const g of items) for (const tg of g.tags ?? []) set.add(tg)
    return Array.from(set).slice(0, 12)
  }, [items])

  function pickType(c: string) {
    setPage(0)
    setParams(c === '全部' ? {} : { type: c })
  }

  function submitSearch() {
    setPage(0)
    setKeyword(q.trim())
  }

  return (
    <div className="pt-10 pb-20">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-semibold text-ink-900">攻略库</h1>
        <p className="mt-1 text-sm text-ink-500">
          {loading ? '加载中…' : `${items.length} 篇攻略，带版本号、带来源`}
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-3 mb-6">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-300" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') submitSearch() }}
            placeholder="搜索攻略…回车确认"
            className="pl-10"
          />
        </div>
        <Button variant="outline" size="sm" onClick={submitSearch}>搜索</Button>
      </div>

      {/* 分类筛选：标签来自后端真实数据的并集，避免写死与实际内容脱节 */}
      <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin mb-8">
        <Filter size={14} className="text-ink-500 shrink-0" />
        <button
          onClick={() => pickType('全部')}
          className={`shrink-0 h-9 px-3.5 rounded-xl text-sm font-medium transition-all ${
            t === '全部' ? 'bg-accent-500 text-white' : 'bg-surface text-ink-700 border border-ink-100 hover:border-ink-300'
          }`}
        >全部</button>
        {tagOptions.map((c) => (
          <button
            key={c}
            onClick={() => pickType(c)}
            className={`shrink-0 h-9 px-3.5 rounded-xl text-sm font-medium transition-all ${
              t === c ? 'bg-accent-500 text-white' : 'bg-surface text-ink-700 border border-ink-100 hover:border-ink-300'
            }`}
          >{c}</button>
        ))}
      </div>

      {error ? (
        <p className="text-danger-600 text-center py-12">{error}</p>
      ) : loading ? (
        <p className="text-ink-500 text-center py-12">加载中…</p>
      ) : items.length === 0 ? (
        <p className="text-ink-500 text-center py-12">
          {keyword || t !== '全部' ? '没有符合条件的攻略，换个关键词试试' : '暂无攻略'}
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {items.map((g) => (
            <Link key={g.id} to={`/guides/${g.id}`}>
              <HoverCard className="p-5">
                <div className="flex items-center gap-2 mb-3 flex-wrap">
                  <Tag size="sm">{primaryTag(g)}</Tag>
                  {g.tags?.slice(1, 3).map((tg) => (
                    <Tag key={tg} size="sm" variant="outline">{tg}</Tag>
                  ))}
                  {g.difficulty && (
                    <Tag size="sm" variant="soft">{g.difficulty}</Tag>
                  )}
                </div>
                <h3 className="text-base font-medium text-ink-900 leading-snug">{g.title}</h3>
                <p className="mt-2 text-sm text-ink-500 line-clamp-2">
                  {g.summary || '暂无摘要'}
                </p>
                <div className="mt-4 flex items-center justify-between text-xs text-ink-500">
                  <span className="inline-flex items-center gap-1">
                    <Heart size={12} className="text-accent-500 fill-accent-500" /> {g.likeCount}
                  </span>
                  <span>更新于 {new Date(g.updatedAt).toLocaleDateString()}</span>
                </div>
              </HoverCard>
            </Link>
          ))}
        </div>
      )}

      <div className="flex items-center justify-center gap-4 mt-8">
        <Button
          size="sm"
          variant="outline"
          disabled={page === 0 || loading}
          onClick={() => setPage((p) => Math.max(0, p - 1))}
        >
          <ChevronLeft size={14} /> 上一页
        </Button>
        <span className="text-sm text-ink-500">第 {page + 1} 页</span>
        <Button
          size="sm"
          variant="outline"
          disabled={!hasNext || loading}
          onClick={() => setPage((p) => p + 1)}
        >
          下一页 <ChevronRight size={14} />
        </Button>
      </div>
    </div>
  )
}