import { Link, useParams } from 'react-router-dom'
import { Heart, Map as MapIcon, Calculator, Sparkles, ChevronLeft } from 'lucide-react'
import { Tag } from '@/components/ui/Tag'
import { Button } from '@/components/ui/Button'
import { HoverCard } from '@/components/ui/Card'

/* mock — 真实场景由 /api/v1/games/{id} + /guides?gameId= 取 */
const MOCK = {
  id: 1, name: '原神', cover: '🎮', version: '4.2',
  currentVersion: '4.2.0',
  releaseDate: '2026-08-15',
  category: '开放世界 RPG',
  platform: ['PC', 'PS5', 'iOS', 'Android'],
  description: '在七元素的幻想世界中,展开属于你的冒险。',
}

const GUIDES = [
  { id: 101, title: '4.2 钟离圣遗物毕业指南',     tag: '配装', likes: 234 },
  { id: 102, title: '原神 4.2 全角色强度榜',     tag: '榜单', likes: 567 },
  { id: 103, title: '须弥 3.0 探索度速刷路线',   tag: '探索', likes: 312 },
  { id: 104, title: '原神武器池抽取策略',       tag: '抽卡', likes: 189 },
]

export default function GameDetailPage() {
  const { id } = useParams()
  return (
    <div className="pt-8 pb-20 space-y-10">
      {/* 面包屑 */}
      <Link to="/games" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700">
        <ChevronLeft size={14} /> 返回游戏库
      </Link>

      {/* Hero */}
      <section className="rounded-4xl bg-gradient-to-br from-accent-50 to-canvas border border-ink-100/40 p-8 md:p-12 relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 h-60 w-60 rounded-full bg-accent-200/40 blur-3xl" />
        <div className="relative grid md:grid-cols-[auto_1fr] gap-8 items-center">
          <div className="h-40 w-40 md:h-48 md:w-48 rounded-3xl bg-surface shadow-soft grid place-items-center text-7xl">
            {MOCK.cover}
          </div>
          <div>
            <h1 className="text-3xl md:text-4xl font-display font-semibold text-ink-900">
              {MOCK.name}
              <span className="ml-3 text-base font-sans font-normal text-ink-500">v{MOCK.currentVersion}</span>
            </h1>
            <div className="mt-3 flex items-center gap-2 flex-wrap">
              <Tag>{MOCK.category}</Tag>
              {MOCK.platform.map((p) => <Tag key={p} variant="outline">{p}</Tag>)}
            </div>
            <p className="mt-4 text-ink-700 max-w-2xl">{MOCK.description}</p>
            <div className="mt-6 flex items-center gap-2 flex-wrap">
              <Button variant="primary" size="md">
                <Heart size={16} /> 收藏
              </Button>
              <Link to={`/games/${id}/maps`}>
                <Button variant="outline"><MapIcon size={16} /> 互动地图</Button>
              </Link>
              <Link to={`/games/${id}/simulators`}>
                <Button variant="outline"><Calculator size={16} /> 模拟器</Button>
              </Link>
              <Link to="/ai">
                <Button variant="soft">
                  <Sparkles size={16} /> AI 帮帮我
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Tabs (简化版,真实版用 Radix Tabs) */}
      <section>
        <div className="flex items-center gap-1 border-b border-ink-100 mb-6">
          {['攻略', '资讯', '百科', '讨论'].map((t, i) => (
            <button
              key={t}
              className={`px-4 h-11 text-sm font-medium border-b-2 transition-colors ${
                i === 0
                  ? 'border-accent-500 text-accent-700'
                  : 'border-transparent text-ink-500 hover:text-ink-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          {GUIDES.map((g) => (
            <Link key={g.id} to={`/guides/${g.id}`}>
              <HoverCard className="flex items-center gap-4 p-4">
                <div className="h-16 w-20 rounded-2xl bg-gradient-to-br from-accent-100 to-canvas grid place-items-center text-3xl shrink-0">
                  📖
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Tag size="sm">{g.tag}</Tag>
                    <span className="text-xs text-ink-500">{MOCK.name}</span>
                  </div>
                  <h3 className="text-base font-medium text-ink-900 truncate group-hover:text-accent-700">
                    {g.title}
                  </h3>
                </div>
                <div className="hidden sm:flex items-center gap-1 text-xs text-ink-500 shrink-0">
                  <Heart size={12} className="text-accent-500 fill-accent-500" /> {g.likes}
                </div>
              </HoverCard>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
