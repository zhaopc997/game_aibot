import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell, CheckCheck } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import client, { unwrap } from '@/api/client'

interface Notification {
  id: number
  type: string
  title: string
  content?: string
  relatedType?: string | null
  relatedId?: number | null
  isRead: boolean
  createdAt?: string
}

function formatTime(iso?: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const diffMs = Date.now() - d.getTime()
  const min = Math.floor(diffMs / 60000)
  if (min < 1) return '刚刚'
  if (min < 60) return `${min} 分钟前`
  const hour = Math.floor(min / 60)
  if (hour < 24) return `${hour} 小时前`
  const day = Math.floor(hour / 24)
  if (day < 30) return `${day} 天前`
  return d.toLocaleDateString()
}

export default function NotificationsPage() {
  const navigate = useNavigate()
  const [items, setItems] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [marking, setMarking] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    client
      .get('/notifications')
      .then((r) => setItems(unwrap<Notification[]>(r) ?? []))
      .catch((e: unknown) => {
        const err = e as { response?: { status?: number }; message?: string }
        if (err.response?.status === 401 || err.response?.status === 403) {
          setError('请先登录后查看通知')
        } else {
          setError(err.message ?? '加载通知失败，请稍后重试')
        }
        setItems([])
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(load, [load])

  async function markAllRead() {
    setMarking(true)
    try {
      await client.post('/notifications/read')
      setItems((prev) => prev.map((n) => ({ ...n, isRead: true })))
    } catch {
      // 失败时保持原状，用户可重试
    } finally {
      setMarking(false)
    }
  }

  const unread = items.filter((n) => !n.isRead).length

  return (
    <div className="pt-10 pb-20 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-display font-semibold text-ink-900">通知</h1>
          {unread > 0 && <p className="mt-1 text-sm text-ink-500">{unread} 条未读</p>}
        </div>
        {items.length > 0 && unread > 0 && (
          <Button variant="outline" size="sm" disabled={marking} onClick={markAllRead}>
            <CheckCheck size={14} /> 全部标为已读
          </Button>
        )}
      </div>

      {loading ? (
        <p className="text-ink-500 text-center py-12">加载中…</p>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-danger-600 mb-4">{error}</p>
          <Button variant="outline" size="sm" onClick={() => navigate('/login')}>去登录</Button>
        </div>
      ) : items.length === 0 ? (
        <Card><CardBody className="text-center text-ink-500 py-12">暂无通知</CardBody></Card>
      ) : (
        <Card>
          <CardBody className="p-0">
            {items.map((n, i) => (
              <div
                key={n.id}
                className={`flex items-start gap-4 p-5 ${i < items.length - 1 ? 'border-b border-ink-100' : ''} ${n.isRead ? '' : 'bg-accent-50/30'}`}
              >
                <div className="h-10 w-10 rounded-2xl bg-accent-50 text-accent-500 grid place-items-center shrink-0">
                  <Bell size={16} />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-ink-900 flex items-center gap-2">
                    {n.title}
                    {!n.isRead && <span className="h-1.5 w-1.5 rounded-full bg-accent-500 shrink-0" />}
                  </h3>
                  {n.content && <p className="mt-1 text-sm text-ink-500">{n.content}</p>}
                  <p className="mt-1.5 text-xs text-ink-300">{formatTime(n.createdAt)}</p>
                </div>
              </div>
            ))}
          </CardBody>
        </Card>
      )}
    </div>
  )
}