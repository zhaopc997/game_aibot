import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, Check, X, AlertTriangle } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Tag } from '@/components/ui/Tag'
import client, { unwrap } from '@/api/client'

interface ReviewItem {
  reviewId: number | null
  targetType: string
  targetId: number
  title?: string | null
  status: string
  riskLevel: string
  reason?: string | null
  createdAt?: string | null
}

export default function ReviewAdminPage() {
  const [items, setItems] = useState<ReviewItem[]>([])
  const [loading, setLoading] = useState(true)
  // 403(非审核员)不能显示成"暂无待审核内容"，否则运营会以为队列已清空
  const [error, setError] = useState<string | null>(null)

  function load() {
    setLoading(true)
    setError(null)
    client
      .get('/reviews/queue')
      .then((r) => setItems(unwrap<ReviewItem[]>(r) ?? []))
      .catch((e: unknown) => {
        const err = e as { response?: { status?: number }; message?: string }
        if (err.response?.status === 403) {
          setError('无权访问：当前账号不是审核员或管理员')
        } else if (err.response?.status === 401) {
          setError('登录已失效，请重新登录')
        } else {
          setError(err.message ?? '加载审核队列失败，请稍后重试')
        }
        setItems([])
      })
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  async function decide(item: ReviewItem, decision: string) {
    if (item.reviewId != null) {
      await client.post(`/reviews/${item.reviewId}/decision`, { decision })
    } else {
      await client.post(`/reviews/guides/${item.targetId}/decision`, { decision })
    }
    load()
  }

  const statusLabel: Record<string, string> = {
    DRAFT: '草稿', PENDING_REVIEW: '待审核', PENDING: '待审核',
    NEED_HUMAN: '待人工', REJECTED: '已拒绝', PASSED: '已通过', PUBLISHED: '已发布',
  }

  return (
    <div className="pt-10 pb-20 max-w-3xl">
      <Link to="/admin" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-4">
        <ChevronLeft size={14} /> 返回管理后台
      </Link>
      <h1 className="text-2xl font-display font-semibold text-ink-900 mb-1">内容审核</h1>
      <p className="text-sm text-ink-500 mb-6">含已进审核队列 + 待审草稿攻略（爬虫/AI 入库）</p>

      {loading ? <p className="text-ink-500">加载中…</p> : error ? (
        <Card><CardBody className="text-center text-danger-600 py-10">{error}</CardBody></Card>
      ) : items.length === 0 ? (
        <Card><CardBody className="text-center text-ink-500 py-10">暂无待审核内容</CardBody></Card>
      ) : items.map((r) => (
        <Card key={r.reviewId ?? `g-${r.targetId}`} className="mb-4">
          <CardBody>
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Tag size="sm">{r.targetType}</Tag>
              <span className="text-xs text-ink-500">#{r.targetId}</span>
              {r.riskLevel === 'HIGH' && (
                <Tag size="sm" variant="solid"><AlertTriangle size={11} className="inline mr-0.5" />高风险</Tag>
              )}
              <Tag size="sm" variant="outline">{statusLabel[r.status] || r.status}</Tag>
              <span className="text-xs text-ink-500 ml-auto">{r.createdAt ? new Date(r.createdAt).toLocaleString() : ''}</span>
            </div>
            <h3 className="text-base font-medium text-ink-900 mb-3">{r.title || `${r.targetType} #${r.targetId}`}</h3>
            {r.reason && <p className="text-sm text-ink-500 mb-3">{r.reason}</p>}
            <div className="flex gap-2">
              <Button size="sm" onClick={() => decide(r, 'PASSED')}><Check size={14} /> 通过</Button>
              <Button size="sm" variant="outline" onClick={() => decide(r, 'REJECTED')}><X size={14} /> 拒绝</Button>
            </div>
          </CardBody>
        </Card>
      ))}
    </div>
  )
}