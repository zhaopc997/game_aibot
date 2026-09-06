import { Link } from 'react-router-dom'
import { Search, Sparkles, Flame, TrendingUp, ArrowRight, Star } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { HoverCard } from '@/components/ui/Card'
import { Tag } from '@/components/ui/Tag'

/* ───── mock 数据(后端就绪后换成 API) ───── */
const HOT_GAMES = [
  { id: 1, name: '原神',         cover: '🎮', players: '2.3M', tag: '开放世界' },
  { id: 2, name: '崩坏：星穹铁道', cover: '🚂', players: '1.5M', tag: '回合制' },
  { id: 3, name: '黑神话：悟空',   cover: '🐵', players: '1.1M', tag: 'ARPG' },
  { id: 4, name: '王者荣耀',       cover: '⚔️', players: '5.0M', tag: 'MOBA' },
  { id: 5, name: '塞尔达传说',     cover: '🗡️', players: '850K', tag: '动作' },
  { id: 6, name: '艾尔登法环',     cover: '💍', players: '720K', tag: '魂类' },
]

const FEATURED = [
  {
    id: 101,
    title: '4.2 钟离圣遗物毕业指南：从入门到精通',
    game: '原神',
    summary: '钟离在 4.2 版本依旧是顶级辅助,本文从圣遗物选择、词条优先级到配队,系统讲解钟离的培养路线...',
    cover: '🏔️',
    likes: 234, comments: 18, tag: '配装',
  },
  {
    id: 102,
    title: '黑神话：悟空全 Boss 打法合集',
    game: '黑神话：悟空',
    summary: '汇总 86 个 Boss 的招式拆解、克制策略与硬直窗口,配 4K 视频演示,看完就能上手...',
    cover: '🐉',
    likes: 412, comments: 56, tag: 'Boss',
  },
  {
    id: 103,
    title: '星穹铁道：3.0 新角色抽取优先级',
    game: '崩坏：星穹铁道',
    summary: '新版本三位新角色,谁最值得抽?本文从队伍适配、光锥、性价比三个维度分析...',
    cover: '✨',
    likes: 189, comments: 32, tag: '抽卡',
  },
  {
    id: 104,
    title: '王者荣耀：S37 赛季上分英雄榜',
    game: '王者荣耀',
    summary: '基于 10 万场对局数据,盘点新赛季最强上分英雄与禁用技巧...',
    cover: '🛡️',
    likes: 156, comments: 24, tag: '上分',
  },
]

/* ───── 页面 ───── */
export default function HomePage() {
  const navigate = useNavigate()
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
            {HOT_GAMES.map((g) => (
              <Link
                key={g.id}
                to={`/games/${g.id}`}
                className="group shrink-0 w-44"
              >
                <div className="aspect-[3/4] rounded-3xl bg-gradient-to-br from-accent-100 to-canvas border border-ink-100/40 grid place-items-center text-6xl shadow-soft transition-all duration-300 group-hover:shadow-lift group-hover:-translate-y-1">
                  {g.cover}
                </div>
                <div className="mt-3 px-1">
                  <div className="text-sm font-medium text-ink-900 truncate">{g.name}</div>
                  <div className="mt-0.5 text-xs text-ink-500 flex items-center gap-1.5">
                    <span>{g.players} 玩家</span>
                    <span className="text-ink-100">·</span>
                    <span className="text-accent-700">{g.tag}</span>
                  </div>
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
          {FEATURED.map((it) => (
            <Link key={it.id} to={`/guides/${it.id}`}>
              <HoverCard className="overflow-hidden">
                <div className="grid grid-cols-[120px_1fr] gap-5 p-5">
                  {/* 缩略图 */}
                  <div className="aspect-[3/4] rounded-2xl bg-gradient-to-br from-accent-100 to-canvas grid place-items-center text-5xl">
                    {it.cover}
                  </div>
                  {/* 文字 */}
                  <div className="flex flex-col py-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Tag size="sm">{it.tag}</Tag>
                      <span className="text-xs text-ink-500">{it.game}</span>
                    </div>
                    <h3 className="text-base font-display font-semibold text-ink-900 leading-snug line-clamp-2 group-hover:text-accent-700">
                      {it.title}
                    </h3>
                    <p className="mt-2 text-sm text-ink-500 line-clamp-2 flex-1">
                      {it.summary}
                    </p>
                    <div className="mt-3 flex items-center gap-4 text-xs text-ink-500">
                      <span className="inline-flex items-center gap-1">
                        <Star size={12} className="text-accent-500 fill-accent-500" /> {it.likes}
                      </span>
                      <span>💬 {it.comments}</span>
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
