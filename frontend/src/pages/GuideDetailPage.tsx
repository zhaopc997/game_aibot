import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Heart, Bookmark, Share2, ChevronLeft, Sparkles, MapPin } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Tag } from '@/components/ui/Tag'
import { Card, CardBody } from '@/components/ui/Card'
import client, { unwrap } from '@/api/client'

interface Guide {
  id: number
  gameId: number
  versionId?: number | null
  title: string
  authorId: number
  type: string
  difficulty?: string
  tags: string[]
  summary?: string
  content: {
    steps?: Array<{
      step_id: number
      title: string
      description?: string
      conditions?: string[]
      tools?: string[]
      images?: string[]
    }>
  }
  status: string
  likeCount: number
  usefulCount: number
  updatedAt: string
}

interface Game {
  id: number
  name: string
  currentVersion?: string
}

export default function GuideDetailPage() {
  const { id } = useParams()
  const [guide, setGuide] = useState<Guide | null>(null)
  const [game, setGame] = useState<Game | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [liked, setLiked] = useState(false)
  const [likeCount, setLikeCount] = useState(0)
  const [favorited, setFavorited] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    client.get(`/guides/${id}`)
      .then((r) => {
        const g = unwrap<Guide>(r)
        setGuide(g)
        setLikeCount(g.likeCount || 0)
        if (g.gameId) {
          return client.get(`/games/${g.gameId}`).then((gr) => setGame(unwrap<Game>(gr)))
        }
      })
      .catch(() => setError('攻略不存在或已删除'))
      .finally(() => setLoading(false))
  }, [id])

  const toggleLike = async () => {
    if (!guide) return
    try {
      const res = await client.post('/likes', null, {
        params: { targetType: 'guide', targetId: guide.id }
      })
      const data = unwrap<{ liked: boolean; count: number }>(res)
      setLiked(data.liked)
      setLikeCount(data.count)
    } catch {
      alert('请先登录后再进行点赞操作')
    }
  }

  const toggleFavorite = async () => {
    if (!guide) return
    try {
      const res = await client.post('/favorites', null, {
        params: { targetType: 'guide', targetId: guide.id }
      })
      const data = unwrap<{ favorited: boolean }>(res)
      setFavorited(data.favorited)
    } catch {
      alert('请先登录后再进行收藏操作')
    }
  }

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) return <div className="pt-20 text-center text-ink-500">加载中…</div>
  if (error || !guide) return <div className="pt-20 text-center text-ink-500">{error || '加载失败'}</div>

  const steps = guide.content?.steps ?? []
  const difficultyLabel: Record<string, string> = { EASY: '简单', NORMAL: '普通', HARD: '困难' }

  return (
    <article className="pt-8 pb-20 max-w-3xl mx-auto">
      <Link to={`/games/${guide.gameId}`} className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-6">
        <ChevronLeft size={14} /> 返回 {game?.name || '游戏'}
      </Link>

      <header className="mb-8">
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          {guide.tags?.map((t) => <Tag key={t}>{t}</Tag>)}
          {guide.difficulty && <Tag variant="outline">{difficultyLabel[guide.difficulty] || guide.difficulty}</Tag>}
          {game && (
            <>
              <span className="text-ink-100">·</span>
              <span className="text-sm text-ink-500">{game.name}</span>
            </>
          )}
          {game?.currentVersion && (
            <>
              <span className="text-ink-100">·</span>
              <span className="text-sm text-ink-500">v{game.currentVersion}</span>
            </>
          )}
        </div>
        <h1 className="text-3xl md:text-4xl font-display font-semibold text-ink-900 leading-tight">
          {guide.title}
        </h1>
        {guide.summary && <p className="mt-3 text-ink-500">{guide.summary}</p>}
        <p className="mt-2 text-xs text-ink-400">更新于 {new Date(guide.updatedAt).toLocaleDateString()}</p>
      </header>

      <div className="flex items-center gap-2 mb-10 flex-wrap">
        <Button
          variant={liked ? "primary" : "outline"}
          size="sm"
          onClick={toggleLike}
          className={liked ? "bg-red-500 hover:bg-red-600 text-white border-transparent" : ""}
        >
          <Heart size={14} className={liked ? "fill-white" : ""} /> 有用 ({likeCount})
        </Button>
        <Button
          variant={favorited ? "primary" : "outline"}
          size="sm"
          onClick={toggleFavorite}
          className={favorited ? "bg-amber-500 hover:bg-amber-600 text-white border-transparent" : ""}
        >
          <Bookmark size={14} className={favorited ? "fill-white" : ""} /> {favorited ? '已收藏' : '收藏'}
        </Button>
        <Button variant="ghost" size="sm" onClick={handleShare}>
          <Share2 size={14} /> {copied ? '已复制链接！' : '分享'}
        </Button>
        <Link to="/ai" className="ml-auto">
          <Button variant="soft" size="sm"><Sparkles size={14} /> AI 帮帮我</Button>
        </Link>
      </div>

      {steps.length === 0 ? (
        <Card><CardBody className="text-center text-ink-500 py-10">本篇攻略暂无内容</CardBody></Card>
      ) : (
        <div className="space-y-5">
          {steps.map((s, i) => (
            <Card key={s.step_id ?? i}>
              <CardBody>
                <h3 className="text-lg font-display font-semibold text-ink-900 mb-2 flex items-center gap-2">
                  <span className="inline-flex items-center gap-1.5 text-accent-700">
                    <MapPin size={16} className="text-accent-500" /> 第 {s.step_id} 步
                  </span>
                  {s.title}
                </h3>
                {s.description && <p className="text-ink-700 leading-relaxed">{s.description}</p>}
                {s.conditions && s.conditions.length > 0 && (
                  <div className="mt-3 flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-ink-500">条件:</span>
                    {s.conditions.map((c, idx) => <Tag key={idx} size="sm" variant="outline">{c}</Tag>)}
                  </div>
                )}
                {s.tools && s.tools.length > 0 && (
                  <div className="mt-2 flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-ink-500">道具:</span>
                    {s.tools.map((t, idx) => <Tag key={idx} size="sm">{t}</Tag>)}
                  </div>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      <Card className="mt-12">
        <CardBody>
          <h3 className="text-lg font-display font-semibold text-ink-900 mb-3 flex items-center gap-2">
            <Sparkles size={18} className="text-accent-500" /> AI 助手推荐
          </h3>
          <p className="text-sm text-ink-500 mb-4">想看更多当前版本的攻略?问问 AI 助手。</p>
          <Link to="/ai">
            <Button variant="primary" size="sm">问问 AI →</Button>
          </Link>
        </CardBody>
      </Card>
    </article>
  )
}