import { Link } from 'react-router-dom'
import { Search, Sparkles, Flame, TrendingUp, ArrowRight, Star } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { HoverCard } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'
import { GameCover } from '@/components/GameCover'
import client, { unwrap } from '@/api/client'

interface Game {
  id: number
  name: string
  coverUrl?: string | null
  category?: string
  currentVersion?: string
}

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

const FALLBACK_HOT_GAMES: Game[] = [
  { id: 2, name: '原神', category: '开放世界', currentVersion: '5.0' },
  { id: 8, name: '崩坏：星穹铁道', category: '回合制 RPG', currentVersion: '2.7' },
  { id: 4, name: '黑神话：悟空', category: 'ARPG', currentVersion: '1.0' },
  { id: 6, name: '英雄联盟', category: 'MOBA', currentVersion: '14.19' },
  { id: 3, name: '塞尔达传说：王国之泪', category: '动作冒险', currentVersion: '1.2' },
  { id: 1, name: '艾尔登法环', category: '魂系 RPG', currentVersion: '1.10' },
]

const FALLBACK_FEATURED: Guide[] = [
  {
    id: 1,
    title: '4.2 钟离圣遗物毕业指南：从入门到精通',
    summary: '钟离在 4.2 版本依旧是顶级辅助，本文从圣遗物选择、词条优先级到配队，系统讲解钟离的培养路线与深渊实战细节。',
    tags: ['配装', '原神', '辅助'],
    difficulty: 'NORMAL',
    likeCount: 512,
    usefulCount: 468,
    updatedAt: new Date().toISOString(),
  },
  {
    id: 2,
    title: '黑神话：悟空全 Boss 打法与禁字决高爆发构筑',
    summary: '汇总核心首领的招式拆解、克制策略与硬直窗口，搭配重击蓄力与高暴击仙丹分配，助你畅快通关。',
    tags: ['Boss', '黑神话', 'Build'],
    difficulty: 'HARD',
    likeCount: 680,
    usefulCount: 590,
    updatedAt: new Date().toISOString(),
  },
  {
    id: 3,
    title: '星穹铁道：新版本角色抽取与遗器养成优先级',
    summary: '新版本角色配队思路详解，针对主C、辅助不同定位的遗器主副词条推荐，平民零氪必看攻略。',
    tags: ['抽卡', '星穹铁道', '攻略'],
    difficulty: 'EASY',
    likeCount: 410,
    usefulCount: 375,
    updatedAt: new Date().toISOString(),
  },
  {
    id: 4,
    title: '艾尔登法环：新手开荒职业推荐与前期神兵获取',
    summary: '面向刚入坑玩家的无痛开荒指南，开局加点推荐、关键道具与漂流墓地神兵获取路线完整整理。',
    tags: ['开荒', '艾尔登法环', '新手'],
    difficulty: 'EASY',
    likeCount: 320,
    usefulCount: 280,
    updatedAt: new Date().toISOString(),
  },
]

export default function HomePage() {
  const navigate = useNavigate()
  const [hotGames, setHotGames] = useState<Game[]>(FALLBACK_HOT_GAMES)
  const [featured, setFeatured] = useState<Guide[]>(FALLBACK_FEATURED)

  useEffect(() => {
    // 独立获取热门游戏（即便精选攻略接口暂无数据或异常，也不影响热门游戏展示）
    client.get('/games')
      .then((g) => {
        const games = unwrap<Game[]>(g)
        if (Array.isArray(games) && games.length > 0) {
          setHotGames(games.slice(0, 6))
        }
      })
      .catch((err) => {
        console.warn('[HomePage] 热门游戏加载异常，已启用内置精选列表:', err)
      })

    // 独立获取精选攻略
    client.get('/guides?status=PUBLISHED&size=6')
      .then((gl) => {
        const res = unwrap<PageResult<Guide>>(gl)
        if (res?.items && Array.isArray(res.items) && res.items.length > 0) {
          setFeatured(res.items)
        }
      })
      .catch((err) => {
        console.warn('[HomePage] 本周精选攻略加载异常，已启用内置精选列表:', err)
      })
  }, [])

  return (
    <div className="space-y-16 pb-20">
      {/* HERO */}
      <section className="pt-8">
        <div className="relative overflow-hidden rounded-4xl bg-gradient-to-br from-accent-50 via-canvas to-accent-50 p-10 md:p-16 border border-ink-100/40">
          {/* 装饰光斑 */}
          <div className="absolute -top-20 -right-20 h-72 w-72 rounded-full bg-accent-200/40 blur-3xl pointer-events-none" />
          <div className="absolute -bottom-20 -left-20 h-72 w-72 rounded-full bg-accent-100/60 blur-3xl pointer-events-none" />

          <div className="relative max-w-2xl">
            <span className="inline-flex items-center gap-1.5 px-3 h-7 rounded-full bg-accent-100 text-accent-700 text-xs font-medium mb-5">
              <Sparkles size={13} /> 100+ 游戏 · AI 智能问答
            </span>
            <h1 className="text-4xl md:text-5xl font-display font-semibold text-ink-900 leading-tight tracking-tight">
              找游戏 · <br className="md:hidden" />
              <span className="text-accent-500">更聪明</span>。
            </h1>
            <p className="mt-5 text-base md:text-lg text-ink-500 max-w-lg leading-relaxed">
              海量游戏攻略、实时社区问答、专属 AI 助手。
              <br />
              让我们帮你把"卡关"变成"通关"。
            </p>

            {/* 大搜索 */}
            <form
              onSubmit={(e) => {
                e.preventDefault()
                const v = new FormData(e.currentTarget).get('q')?.toString().trim()
                if (v) navigate(`/games?q=${encodeURIComponent(v)}`)
              }}
              className="mt-8 flex items-center gap-2 max-w-xl bg-surface rounded-2xl shadow-soft p-1.5"
            >
              <div className="flex-1 flex items-center gap-2 px-4">
                <Search size={18} className="text-ink-300" />
                <input
                  name="q"
                  placeholder="搜索游戏、攻略、问答…"
                  className="flex-1 h-12 bg-transparent text-sm placeholder:text-ink-300 focus:outline-none"
                />
              </div>
              <Button type="submit" size="lg">搜索</Button>
            </form>

            <div className="mt-5 flex items-center gap-2 flex-wrap">
              <span className="text-xs text-ink-500">热门:</span>
              {['原神 4.2', '黑神话 攻略', '星穹铁道', '王者 S37'].map((q) => (
                <button
                  key={q}
                  onClick={() => navigate(`/games?q=${encodeURIComponent(q)}`)}
                  className="text-xs px-2.5 h-6 rounded-full bg-surface/70 text-ink-700 hover:bg-accent-50 hover:text-accent-700 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 热门游戏 - 横向滚动 */}
      <section>
        <div className="flex items-end justify-between mb-6">
          <div>
            <h2 className="text-2xl font-display font-semibold text-ink-900 flex items-center gap-2">
              <Flame size={20} className="text-accent-500" /> 热门游戏
            </h2>
            <p className="mt-1 text-sm text-ink-500">本周玩家活跃度 Top 6</p>
          </div>
          <Link
            to="/games"
            className="text-sm text-ink-700 hover:text-accent-700 inline-flex items-center gap-1 transition-colors"
          >
            查看全部 <ArrowRight size={14} />
          </Link>
        </div>

        <div className="-mx-4 px-4 overflow-x-auto scrollbar-thin">
          <div className="flex gap-4 pb-2">
            {hotGames.map((g) => (
              <Link
                key={g.id}
                to={`/games/${g.id}`}
                className="group shrink-0 w-44"
              >
                <div className="aspect-[3/4] rounded-3xl bg-gradient-to-br from-accent-100 to-canvas border border-ink-100/40 grid place-items-center overflow-hidden shadow-soft transition-all duration-300 group-hover:shadow-lift group-hover:-translate-y-1">
                  <GameCover
                    src={g.coverUrl}
                    gameId={g.id}
                    alt={g.name}
                    className="h-full w-full"
                    emojiClassName="text-6xl select-none"
                  />
                </div>
                <div className="mt-3 px-1">
                  <div className="text-sm font-medium text-ink-900 truncate">{g.name}</div>
                  {g.category && <div className="mt-0.5 text-xs text-ink-500">{g.category}</div>}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* 本周精选攻略 - 双列卡片 */}
      <section>
        <div className="flex items-end justify-between mb-6">
          <div>
            <h2 className="text-2xl font-display font-semibold text-ink-900 flex items-center gap-2">
              <TrendingUp size={20} className="text-accent-500" /> 本周精选
            </h2>
            <p className="mt-1 text-sm text-ink-500">编辑精心挑选的高质量攻略</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {featured.map((it) => (
            <Link key={it.id} to={`/guides/${it.id}`}>
              <HoverCard className="overflow-hidden">
                <div className="grid grid-cols-[120px_1fr] gap-5 p-5">
                  <div className="aspect-[3/4] rounded-2xl bg-gradient-to-br from-accent-100 to-canvas grid place-items-center text-5xl">
                    📖
                  </div>
                  <div className="flex flex-col py-1">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      {it.tags?.slice(0, 2).map((t) => <Tag key={t} size="sm">{t}</Tag>)}
                      {it.difficulty && <span className="text-xs text-ink-500">{it.difficulty}</span>}
                    </div>
                    <h3 className="text-base font-display font-semibold text-ink-900 leading-snug line-clamp-2 group-hover:text-accent-700">
                      {it.title}
                    </h3>
                    {it.summary && <p className="mt-2 text-sm text-ink-500 line-clamp-2 flex-1">{it.summary}</p>}
                    <div className="mt-3 flex items-center gap-4 text-xs text-ink-500">
                      <span className="inline-flex items-center gap-1">
                        <Star size={12} className="text-accent-500 fill-accent-500" /> {it.likeCount}
                      </span>
                      <span className="inline-flex items-center gap-1">
                        👍 {it.usefulCount}
                      </span>
                    </div>
                  </div>
                </div>
              </HoverCard>
            </Link>
          ))}
        </div>
      </section>

      {/* AI 助手 CTA */}
      <section>
        <div className="rounded-4xl bg-gradient-to-br from-accent-500 to-accent-600 p-10 md:p-14 text-white relative overflow-hidden">
          <div className="absolute -right-10 -top-10 h-60 w-60 rounded-full bg-white/10 blur-2xl" />
          <div className="relative max-w-2xl">
            <span className="inline-flex items-center gap-1.5 px-3 h-7 rounded-full bg-white/20 text-white text-xs font-medium mb-4">
              <Sparkles size={13} /> AI Copilot
            </span>
            <h2 className="text-3xl font-display font-semibold leading-tight">
              卡关了?问问 AI 助手
            </h2>
            <p className="mt-3 text-white/80 max-w-lg">
              基于 RAG 检索 + 工具调用,直接给你当下版本最准的攻略答案。
            </p>
            <Link to="/ai" className="inline-block mt-6">
              <Button size="lg" className="bg-white text-accent-700 hover:bg-canvas">
                立即对话 <ArrowRight size={16} />
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
