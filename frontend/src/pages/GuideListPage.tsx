import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Search, Heart, Filter } from 'lucide-react'
import { HoverCard } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

const GUIDES = [
  { id: 101, title: '4.2 钟离圣遗物毕业指南',  game: '原神',         tag: '配装', likes: 234, summary: '系统讲解钟离的培养路线,从入门到精通...' },
  { id: 102, title: '全 Boss 打法合集',         game: '黑神话：悟空', tag: 'Boss', likes: 412, summary: '86 个 Boss 的招式拆解与克制策略...' },
  { id: 103, title: '3.0 抽卡优先级',           game: '星穹铁道',     tag: '抽卡', likes: 189, summary: '从队伍适配、光锥、性价比三个维度分析...' },
  { id: 104, title: 'S37 上分英雄榜',           game: '王者荣耀',     tag: '上分', likes: 156, summary: '10 万场对局数据盘点,新赛季最强英雄...' },
  { id: 105, title: '原神武器池抽取策略',       game: '原神',         tag: '抽卡', likes: 234, summary: '概率模型 + 期望值计算,理性抽卡...' },
  { id: 106, title: '魂系开荒保姆级教程',       game: '艾尔登法环',   tag: '开荒', likes: 321, summary: '从职业选择到一周目通关,完整路线图...' },
]

const TYPES = ['全部', '配装', 'Boss', '抽卡', '上分', '开荒']

export default function GuideListPage() {
  const [params, setParams] = useSearchParams()
  const t = params.get('type') ?? '全部'
  const [q, setQ] = useState('')

  const filtered = GUIDES.filter(
    (g) => (t === '全部' || g.tag === t) && (g.title.includes(q) || g.game.includes(q))
  )

  return (
    <div className="pt-10 pb-20">
      <div className="mb-8">
        <h1 className="text-3xl font-display font-semibold text-ink-900">攻略库</h1>
        <p className="mt-1 text-sm text-ink-500">{GUIDES.length} 篇精选攻略,带版本号、带来源</p>
      </div>

      <div className="flex flex-col md:flex-row gap-3 mb-8">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-300" />
          <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="搜索攻略…" className="pl-10" />
        </div>
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin">
          <Filter size={14} className="text-ink-500 shrink-0" />
          {TYPES.map((c) => (
            <button
              key={c}
              onClick={() => setParams({ type: c })}
              className={`shrink-0 h-9 px-3.5 rounded-xl text-sm font-medium transition-all ${
                t === c ? 'bg-accent-500 text-white' : 'bg-surface text-ink-700 border border-ink-100 hover:border-ink-300'
              }`}
            >{c}</button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filtered.map((g) => (
          <Link key={g.id} to={`/guides/${g.id}`}>
            <HoverCard className="p-5">
              <div className="flex items-center gap-2 mb-3">
                <Tag size="sm">{g.tag}</Tag>
                <span className="text-xs text-ink-500">{g.game}</span>
              </div>
              <h3 className="text-base font-medium text-ink-900 leading-snug">{g.title}</h3>
              <p className="mt-2 text-sm text-ink-500 line-clamp-2">{g.summary}</p>
              <div className="mt-4 flex items-center justify-between text-xs text-ink-500">
                <span className="inline-flex items-center gap-1">
                  <Heart size={12} className="text-accent-500 fill-accent-500" /> {g.likes}
                </span>
                <Button variant="ghost" size="sm">阅读 →</Button>
              </div>
            </HoverCard>
          </Link>
        ))}
      </div>
    </div>
  )
}
