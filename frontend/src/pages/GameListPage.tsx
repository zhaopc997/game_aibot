import { Link, useSearchParams } from 'react-router-dom'
import { Search, Filter } from 'lucide-react'
import { useState } from 'react'
import { HoverCard } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'
import { Input } from '@/components/ui/Input'

const GAMES = [
  { id: 1, name: '原神',         cover: '🎮', tag: '开放世界',  category: 'RPG' },
  { id: 2, name: '崩坏：星穹铁道', cover: '🚂', tag: '回合制',   category: 'RPG' },
  { id: 3, name: '黑神话：悟空',   cover: '🐵', tag: 'ARPG',     category: '动作' },
  { id: 4, name: '王者荣耀',       cover: '⚔️', tag: 'MOBA',     category: '竞技' },
  { id: 5, name: '塞尔达传说',     cover: '🗡️', tag: '动作',     category: '冒险' },
  { id: 6, name: '艾尔登法环',     cover: '💍', tag: '魂类',     category: '动作' },
  { id: 7, name: '幻兽帕鲁',       cover: '🐉', tag: '生存',     category: '生存' },
  { id: 8, name: 'CS2',            cover: '🔫', tag: 'FPS',     category: '竞技' },
  { id: 9, name: '英雄联盟',       cover: '🛡️', tag: 'MOBA',    category: '竞技' },
]

const CATEGORIES = ['全部', 'RPG', '动作', '竞技', '生存', '冒险']

export default function GameListPage() {
  const [params, setParams] = useSearchParams()
  const q = params.get('q') ?? ''
  const cat = params.get('cat') ?? '全部'
  const [draft, setDraft] = useState(q)

  const filtered = GAMES.filter(
    (g) => (cat === '全部' || g.category === cat) && g.name.includes(q)
  )

  return (
    <div className="pt-10 pb-20">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-semibold text-ink-900">游戏库</h1>
        <p className="mt-1 text-sm text-ink-500">探索 {GAMES.length} 款游戏,寻找你的下一段冒险</p>
      </div>

      {/* 搜索 + 筛选 */}
      <div className="flex flex-col md:flex-row gap-3 mb-8">
        <form
          onSubmit={(e) => { e.preventDefault(); setParams({ q: draft, cat }) }}
          className="flex-1 relative"
        >
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-300 pointer-events-none" />
          <Input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="搜索游戏名…"
            className="pl-10"
          />
        </form>
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin">
          <Filter size={14} className="text-ink-500 shrink-0" />
          {CATEGORIES.map((c) => (
            <button
              key={c}
              onClick={() => setParams({ q, cat: c })}
              className={`shrink-0 h-9 px-3.5 rounded-xl text-sm font-medium transition-all ${
                cat === c
                  ? 'bg-accent-500 text-white shadow-soft'
                  : 'bg-surface text-ink-700 border border-ink-100 hover:border-ink-300'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* 游戏网格 */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
        {filtered.map((g) => (
          <Link key={g.id} to={`/games/${g.id}`}>
            <HoverCard className="p-5">
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-accent-100 to-canvas grid place-items-center text-5xl mb-4">
                {g.cover}
              </div>
              <h3 className="text-base font-medium text-ink-900">{g.name}</h3>
              <div className="mt-2 flex items-center gap-1.5">
                <Tag size="sm">{g.tag}</Tag>
                <Tag size="sm" variant="outline">{g.category}</Tag>
              </div>
            </HoverCard>
          </Link>
        ))}
        {filtered.length === 0 && (
          <div className="col-span-full text-center py-16 text-ink-500">
            没找到符合条件的游戏
          </div>
        )}
      </div>
    </div>
  )
}
