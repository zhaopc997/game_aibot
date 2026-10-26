import { Link, useNavigate } from 'react-router-dom'
import { ChevronLeft, Loader2, Send, Bookmark } from 'lucide-react'
import { errorMessage } from '@/lib/utils'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardBody } from '@/components/ui/Card'
import client, { unwrap } from '@/api/client'

interface Game {
  id: number
  name: string
}

export default function GuideEditorPage() {
  const navigate = useNavigate()
  const [games, setGames] = useState<Game[]>([])
  const [gameId, setGameId] = useState<number | ''>('')
  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [tags, setTags] = useState('')
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    client.get('/games')
      .then((res) => {
        const list = unwrap<Game[]>(res)
        setGames(list)
        if (list.length > 0) setGameId(list[0].id)
      })
      .catch((err) => {
        console.error('获取游戏列表失败', err)
      })
  }, [])

  const handleSubmit = async (submitForReview: boolean) => {
    if (!title.trim()) {
      setErrorMsg('请输入攻略标题')
      return
    }
    if (!gameId) {
      setErrorMsg('请选择所属游戏')
      return
    }
    if (!content.trim()) {
      setErrorMsg('请输入攻略内容')
      return
    }
    setErrorMsg('')
    setSubmitting(true)

    try {
      const tagList = tags.split(/[,，\s]+/).filter(Boolean)
      const payload = {
        gameId: Number(gameId),
        title: title.trim(),
        summary: summary.trim() || title.trim(),
        content: {
          steps: [
            {
              step_id: 1,
              title: title.trim(),
              description: content.trim(),
            },
          ],
        },
        tags: tagList.length > 0 ? tagList : ['新手攻略'],
        difficulty: 'NORMAL',
        type: 'MANUAL',
        status: 'DRAFT',
      }

      const res = await client.post('/guides', payload)
      const guide = unwrap<{ id: number }>(res)

      if (submitForReview && guide?.id) {
        await client.post(`/guides/${guide.id}/submit-review`)
      }

      navigate(guide?.id ? `/guides/${guide.id}` : '/guides')
    } catch (err: unknown) {
      setErrorMsg(errorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="pt-8 pb-20 max-w-3xl mx-auto">
      <Link to="/guides" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-6">
        <ChevronLeft size={14} /> 取消
      </Link>
      <h1 className="text-3xl font-display font-semibold text-ink-900 mb-6">写新攻略</h1>

      {errorMsg && (
        <div className="mb-4 p-3.5 text-sm rounded-xl bg-red-50 text-red-700 border border-red-200">
          {errorMsg}
        </div>
      )}

      <Card>
        <CardBody className="space-y-4">
          <div>
            <label className="text-sm text-ink-700 mb-1.5 block">所属游戏</label>
            <select
              value={gameId}
              onChange={(e) => setGameId(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 text-sm rounded-xl bg-canvas border border-ink-100 text-ink-900 focus:outline-none focus:border-accent-500"
            >
              {games.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm text-ink-700 mb-1.5 block">标题</label>
            <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="给你的攻略起个吸睛的标题…" />
          </div>

          <div>
            <label className="text-sm text-ink-700 mb-1.5 block">摘要（可选）</label>
            <Input value={summary} onChange={(e) => setSummary(e.target.value)} placeholder="一句话概括这篇攻略的核心要点…" />
          </div>

          <div>
            <label className="text-sm text-ink-700 mb-1.5 block">标签（以空格或逗号分隔）</label>
            <Input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="例如：圣遗物 配队 萌新必看" />
          </div>

          <div>
            <label className="text-sm text-ink-700 mb-1.5 block">攻略正文内容</label>
            <textarea
              rows={12}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="支持 Markdown 格式，详细记录通关步骤、属性搭配、Boss 机制技巧…"
              className="w-full px-4 py-3 text-sm rounded-2xl bg-canvas border border-ink-100 placeholder:text-ink-300 focus:outline-none focus:border-accent-500 focus:shadow-glow transition-all resize-y text-ink-900"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <Button
              variant="ghost"
              disabled={submitting}
              onClick={() => handleSubmit(false)}
            >
              <Bookmark size={15} className="mr-1 inline" />
              {submitting ? '保存中…' : '保存草稿'}
            </Button>
            <Button
              variant="primary"
              disabled={submitting}
              onClick={() => handleSubmit(true)}
            >
              {submitting ? <Loader2 size={15} className="animate-spin mr-1 inline" /> : <Send size={15} className="mr-1 inline" />}
              {submitting ? '提交中…' : '提交审核'}
            </Button>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
