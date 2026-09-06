import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, MessageCircle, ChevronRight } from 'lucide-react'
import { HoverCard } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'
import { Avatar } from '@/components/ui/Avatar'
import { Button } from '@/components/ui/Button'

const QUESTIONS = [
  { id: 1, title: '4.2 钟离值不值得抽?', author: '冒险家小K', answers: 12, views: 234, tag: '抽卡', time: '2 小时前' },
  { id: 2, title: '原神须弥探索度怎么刷最快?', author: '萌新上路', answers: 8,  views: 189, tag: '探索', time: '5 小时前' },
  { id: 3, title: '黑神话 第四章卡关了,有什么技巧?', author: '打不过的悟空', answers: 23, views: 567, tag: 'Boss', time: '1 天前' },
]

export default function QAPage() {
  const [q, setQ] = useState('')
  return (
    <div className="pt-10 pb-20">
      <div className="flex items-end justify-between mb-6">
        <div>
          <h1 className="text-3xl font-display font-semibold text-ink-900">社区问答</h1>
          <p className="mt-1 text-sm text-ink-500">有问题?提出来,大佬来答</p>
        </div>
        <Button variant="primary"><Plus size={16} /> 提问</Button>
      </div>

      <div className="bg-surface rounded-2xl border border-ink-100 p-2 mb-6 flex items-center gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="搜索问题…"
          className="flex-1 h-10 px-3 bg-transparent text-sm placeholder:text-ink-300 focus:outline-none"
        />
        <Button size="sm">搜索</Button>
      </div>

      <div className="space-y-3">
        {QUESTIONS.map((it) => (
          <Link key={it.id} to="#">
            <HoverCard className="p-5 flex items-center gap-4">
              <Avatar size="md" rounded="2xl">{it.author[0]}</Avatar>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5">
                  <Tag size="sm">{it.tag}</Tag>
                  <span className="text-xs text-ink-500">{it.time}</span>
                </div>
                <h3 className="text-base font-medium text-ink-900 truncate">{it.title}</h3>
                <div className="mt-2 text-xs text-ink-500">
                  {it.author} · {it.views} 浏览
                </div>
              </div>
              <div className="hidden sm:flex flex-col items-end text-xs text-ink-500 shrink-0">
                <span className="inline-flex items-center gap-1 text-accent-700 font-medium">
                  <MessageCircle size={12} /> {it.answers} 回答
                </span>
                <ChevronRight size={14} className="mt-1" />
              </div>
            </HoverCard>
          </Link>
        ))}
      </div>
    </div>
  )
}
