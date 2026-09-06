import { useEffect, useRef, useState } from 'react'
import { Send, Sparkles, User as UserIcon, Bot, ChevronDown } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Avatar } from '@/components/ui/Avatar'
import client from '@/api/client'

/* ─── 与后端 V2 架构对接的最小交互 ─── */
type Role = 'user' | 'assistant' | 'system'

interface Message {
  id: string
  role: Role
  content: string
  plan?: Array<{ stepId: number; tool: string; status: string; durationMs: number }>
  sources?: Array<{ guideId: number; title: string; version: string; url: string }>
  loading?: boolean
}

const STARTERS = [
  '原神 4.2 钟离圣遗物怎么刷?',
  '黑神话 悟空 二郎神怎么打?',
  '星穹铁道 新手池要不要抽?',
]

export default function AIChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text: string) => {
    if (!text.trim() || sending) return
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
    }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setSending(true)

    // 加载占位
    const aiId = crypto.randomUUID()
    setMessages((m) => [...m, { id: aiId, role: 'assistant', content: '', loading: true }])

    try {
      const res = await client.post('/api/v1/agent/chat', {
        message: text,
        stream: false,
      })
      const data = res.data?.data
      setMessages((m) =>
        m.map((x) =>
          x.id === aiId
            ? {
                ...x,
                content: data?.answer ?? '抱歉,我没理解。',
                plan: data?.plan,
                sources: data?.sources,
                loading: false,
              }
            : x
        )
      )
    } catch (e) {
      setMessages((m) =>
        m.map((x) =>
          x.id === aiId
            ? { ...x, content: '❌ 调用失败,请检查后端是否运行。', loading: false }
            : x
        )
      )
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="pt-8 pb-20">
      <div className="max-w-3xl mx-auto h-[calc(100vh-180px)] flex flex-col">
        {/* 标题 */}
        <div className="mb-6">
          <h1 className="text-3xl font-display font-semibold text-ink-900 flex items-center gap-2">
            <Sparkles size={24} className="text-accent-500" /> AI 助手
          </h1>
          <p className="mt-1 text-sm text-ink-500">基于 RAG 检索 + 工具调用,给你的答案带版本号、带来源。</p>
        </div>

        {/* 消息区 */}
        <div className="flex-1 overflow-y-auto bg-surface rounded-3xl border border-ink-100/40 p-5 space-y-4 scrollbar-thin">
          {messages.length === 0 && (
            <div className="text-center py-10">
              <div className="inline-grid place-items-center h-14 w-14 rounded-2xl bg-accent-50 text-accent-500 mb-4">
                <Sparkles size={24} />
              </div>
              <h3 className="text-base font-medium text-ink-900">开始你的第一个问题</h3>
              <p className="text-sm text-ink-500 mt-1">试试下面这些,或者直接输入</p>
              <div className="mt-5 flex flex-wrap gap-2 justify-center">
                {STARTERS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="text-sm px-3.5 h-9 rounded-full bg-accent-50 text-accent-700 hover:bg-accent-100 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              {m.role === 'user' ? (
                <Avatar size="md"><UserIcon size={16} /></Avatar>
              ) : (
                <div className="h-10 w-10 rounded-2xl bg-accent-500 text-white grid place-items-center shrink-0">
                  <Bot size={18} />
                </div>
              )}

              <div className={`flex-1 max-w-[80%] ${m.role === 'user' ? 'text-right' : ''}`}>
                <Card className={`inline-block p-4 ${
                  m.role === 'user'
                    ? 'bg-accent-500 text-white border-transparent'
                    : 'bg-canvas'
                }`}>
                  {m.loading ? (
                    <div className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-accent-300 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="h-2 w-2 rounded-full bg-accent-300 animate-bounce" style={{ animationDelay: '120ms' }} />
                      <span className="h-2 w-2 rounded-full bg-accent-300 animate-bounce" style={{ animationDelay: '240ms' }} />
                    </div>
                  ) : (
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{m.content}</p>
                  )}
                </Card>

                {/* Plan 展开 */}
                {m.plan && m.plan.length > 0 && (
                  <details className="mt-2 text-left">
                    <summary className="text-xs text-ink-500 cursor-pointer inline-flex items-center gap-1 hover:text-ink-700">
                      <ChevronDown size={12} /> 查看工具调用 ({m.plan.length} 步)
                    </summary>
                    <div className="mt-2 space-y-1.5">
                      {m.plan.map((p) => (
                        <div key={p.stepId} className="text-xs text-ink-500 flex items-center gap-2">
                          <span className={`h-1.5 w-1.5 rounded-full ${p.status === 'SUCCESS' ? 'bg-accent-500' : 'bg-red-400'}`} />
                          <span className="font-mono text-ink-700">{p.tool}</span>
                          <span>·</span>
                          <span>{p.status}</span>
                          <span>·</span>
                          <span>{p.durationMs}ms</span>
                        </div>
                      ))}
                    </div>
                  </details>
                )}

                {/* 来源 */}
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-2 text-left flex flex-wrap gap-1.5">
                    {m.sources.map((s) => (
                      <a
                        key={s.guideId}
                        href={s.url}
                        className="text-xs px-2.5 h-6 inline-flex items-center rounded-full bg-canvas text-ink-700 hover:bg-accent-50 hover:text-accent-700 border border-ink-100"
                      >
                        📖 {s.title} · v{s.version}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* 输入区 */}
        <form
          onSubmit={(e) => { e.preventDefault(); send(input) }}
          className="mt-4 bg-surface rounded-2xl border border-ink-100 shadow-soft p-2 flex items-center gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="问问 AI…(Enter 发送)"
            className="flex-1 h-12 px-4 bg-transparent text-sm placeholder:text-ink-300 focus:outline-none"
            disabled={sending}
          />
          <Button type="submit" disabled={sending || !input.trim()}>
            <Send size={16} /> 发送
          </Button>
        </form>
      </div>
    </div>
  )
}
