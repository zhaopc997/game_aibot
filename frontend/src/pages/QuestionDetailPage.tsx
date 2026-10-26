import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, MessageCircle, CheckCircle2, Coins, Send, User } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Tag } from '@/components/ui/Tag'
import { Card, CardBody } from '@/components/ui/Card'
import { Avatar } from '@/components/ui/Avatar'
import client, { unwrap } from '@/api/client'
import { useAuth } from '@/auth/AuthContext'

interface Question {
  id: number
  gameId?: number | null
  userId: number
  title: string
  description?: string | null
  bountyPoints?: number
  status: string
  acceptedAnswerId?: number | null
  createdAt?: string
}

interface Answer {
  id: number
  questionId: number
  userId: number
  content: string
  isAccepted?: boolean
  createdAt: string
}

interface Game {
  id: number
  name: string
}

function formatTime(iso?: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleString()
}

export default function QuestionDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const [question, setQuestion] = useState<Question | null>(null)
  const [answers, setAnswers] = useState<Answer[]>([])
  const [game, setGame] = useState<Game | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [answerContent, setAnswerContent] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const loadData = useCallback(() => {
    if (!id) return
    setLoading(true)
    Promise.all([
      client.get(`/questions/${id}`).then((r) => unwrap<Question>(r)),
      client.get(`/questions/${id}/answers`).then((r) => unwrap<Answer[]>(r) ?? []),
    ])
      .then(([q, ansList]) => {
        setQuestion(q)
        setAnswers(ansList)
        if (q.gameId) {
          client.get(`/games/${q.gameId}`)
            .then((gr) => setGame(unwrap<Game>(gr)))
            .catch(() => {})
        }
      })
      .catch(() => setError('问答不存在或已删除'))
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleSendAnswer = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!answerContent.trim() || submitting || !id) return
    setSubmitting(true)
    try {
      await client.post(`/questions/${id}/answers`, {
        content: answerContent.trim(),
      })
      setAnswerContent('')
      loadData()
    } catch {
      alert('提交回答失败，请确认是否已登录')
    } finally {
      setSubmitting(false)
    }
  }

  const handleAccept = async (answerId: number) => {
    if (!id) return
    if (!confirm('确定采纳此回答为最佳答案吗？')) return
    try {
      await client.post(`/questions/${id}/accept-answer`, null, {
        params: { answerId },
      })
      loadData()
    } catch {
      alert('采纳失败，仅提问者可采纳答案')
    }
  }

  if (loading) return <div className="pt-20 text-center text-ink-500">加载中…</div>
  if (error || !question) return <div className="pt-20 text-center text-ink-500">{error || '加载失败'}</div>

  const isAuthor = user && user.id === question.userId
  const isSolved = question.status === 'SOLVED' || !!question.acceptedAnswerId

  return (
    <div className="pt-8 pb-20 max-w-3xl mx-auto">
      <Link to="/qa" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-6">
        <ChevronLeft size={14} /> 返回问答社区
      </Link>

      {/* 问题头 */}
      <Card className="mb-8">
        <CardBody className="p-6">
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <Tag variant={isSolved ? 'outline' : 'soft'} className={isSolved ? 'border-accent-400 text-accent-700 bg-accent-50' : ''}>
              {isSolved ? '已解决' : '讨论中'}
            </Tag>
            {game && <Tag variant="outline">{game.name}</Tag>}
            {(question.bountyPoints ?? 0) > 0 && (
              <span className="inline-flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full font-medium">
                <Coins size={12} /> 悬赏 {question.bountyPoints} 积分
              </span>
            )}
            <span className="text-xs text-ink-400 ml-auto">{formatTime(question.createdAt)}</span>
          </div>

          <h1 className="text-2xl md:text-3xl font-display font-semibold text-ink-900 leading-snug">
            {question.title}
          </h1>

          {question.description && (
            <div className="mt-4 text-ink-700 text-sm leading-relaxed whitespace-pre-wrap bg-surface/50 p-4 rounded-xl border border-ink-100/60">
              {question.description}
            </div>
          )}

          <div className="mt-4 pt-4 border-t border-ink-100/40 flex items-center gap-2 text-xs text-ink-500">
            <Avatar size="sm"><User size={14} /></Avatar>
            <span>提问者 (UID: {question.userId})</span>
          </div>
        </CardBody>
      </Card>

      {/* 回答列表 */}
      <div className="mb-8">
        <h2 className="text-xl font-display font-semibold text-ink-900 mb-4 flex items-center gap-2">
          <MessageCircle size={20} className="text-accent-500" />
          全部回答 ({answers.length})
        </h2>

        {answers.length === 0 ? (
          <Card>
            <CardBody className="text-center text-ink-500 py-12">
              暂无回答，来发布第一个回答吧！
            </CardBody>
          </Card>
        ) : (
          <div className="space-y-4">
            {answers.map((ans) => {
              const isThisAccepted = question.acceptedAnswerId === ans.id
              return (
                <Card
                  key={ans.id}
                  className={`border transition-all ${
                    isThisAccepted ? 'border-accent-400 bg-accent-50/20 shadow-soft' : 'border-ink-100'
                  }`}
                >
                  <CardBody className="p-5">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <Avatar size="sm"><User size={14} /></Avatar>
                        <span className="text-xs font-medium text-ink-700">用户 {ans.userId}</span>
                        <span className="text-xs text-ink-400">· {formatTime(ans.createdAt)}</span>
                      </div>

                      {isThisAccepted && (
                        <span className="inline-flex items-center gap-1 text-xs text-accent-700 bg-accent-100/70 font-medium px-2.5 py-0.5 rounded-full">
                          <CheckCircle2 size={13} /> 最佳答案
                        </span>
                      )}

                      {isAuthor && !isSolved && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleAccept(ans.id)}
                          className="text-xs text-accent-600 hover:bg-accent-50"
                        >
                          采纳该回答
                        </Button>
                      )}
                    </div>

                    <div className="text-sm text-ink-800 leading-relaxed whitespace-pre-wrap">
                      {ans.content}
                    </div>
                  </CardBody>
                </Card>
              )
            })}
          </div>
        )}
      </div>

      {/* 回答输入框 */}
      <Card>
        <CardBody className="p-5">
          <h3 className="text-base font-medium text-ink-900 mb-3">撰写我的回答</h3>
          <form onSubmit={handleSendAnswer} className="space-y-3">
            <textarea
              value={answerContent}
              onChange={(e) => setAnswerContent(e.target.value)}
              placeholder="请详细描述你的解答思路或游戏心得…"
              rows={4}
              className="w-full p-3 rounded-xl border border-ink-200 text-sm focus:outline-none focus:ring-2 focus:ring-accent-400"
              disabled={submitting}
            />
            <div className="flex justify-end">
              <Button type="submit" disabled={submitting || !answerContent.trim()}>
                <Send size={15} /> 提交回答
              </Button>
            </div>
          </form>
        </CardBody>
      </Card>
    </div>
  )
}
