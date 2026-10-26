import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, Ban, CheckCircle2 } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Tag } from '@/components/ui/Tag'
import { Input } from '@/components/ui/Input'
import client, { unwrap } from '@/api/client'

interface User {
  id: number
  username: string
  email: string
  status: string
  level: number
  exp: number
  createdAt: string
}

interface PageResult<T> { items: T[]; nextCursor?: string | null }

export default function UserAdminPage() {
  const [items, setItems] = useState<User[]>([])
  const [page, setPage] = useState(0)
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(true)
  // 区分"加载失败"与"确实没有数据"：否则 403 会被显示成"无匹配用户"，误导运营
  const [error, setError] = useState<string | null>(null)

  const PAGE_SIZE = 20

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    client
      .get(`/admin/users?page=${page}&size=${PAGE_SIZE}`)
      .then((r) => {
        if (!cancelled) setItems(unwrap<PageResult<User>>(r).items ?? [])
      })
      .catch((e: unknown) => {
        if (cancelled) return
        const err = e as { response?: { status?: number }; message?: string }
        if (err.response?.status === 403) {
          setError('无权访问：当前账号不是管理员')
        } else if (err.response?.status === 401) {
          setError('登录已失效，请重新登录')
        } else {
          setError(err.message ?? '加载用户列表失败，请稍后重试')
        }
        setItems([])
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [page])

  async function toggle(u: User) {
    const next = u.status === 'DISABLED' ? 'NORMAL' : 'DISABLED'
    await client.put(`/admin/users/${u.id}/status`, { status: next })
    setPage(0)
    // 重新拉取当前页
    client
      .get(`/admin/users?page=${page}&size=${PAGE_SIZE}`)
      .then((r) => setItems(unwrap<PageResult<User>>(r).items ?? []))
      .catch(() => undefined)
  }

  const filtered = items.filter((u) => u.username.includes(keyword) || u.email.includes(keyword))

  return (
    <div className="pt-10 pb-20 max-w-3xl">
      <Link to="/admin" className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-4">
        <ChevronLeft size={14} /> 返回管理后台
      </Link>
      <h1 className="text-2xl font-display font-semibold text-ink-900 mb-4">用户管理</h1>
      <div className="mb-5">
        <Input placeholder="按用户名 / 邮箱筛选…" value={keyword} onChange={(e) => setKeyword(e.target.value)} />
      </div>

      {loading ? <p className="text-ink-500">加载中…</p> : error ? (
        <p className="text-danger-600 text-center py-8">{error}</p>
      ) : (
        <div className="space-y-3">
          {filtered.map((u) => (
            <Card key={u.id}>
              <CardBody className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-2xl bg-accent-50 grid place-items-center text-accent-700 font-semibold">
                  {u.username[0]?.toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-ink-900">{u.username}</span>
                    <Tag size="sm" variant={u.status === 'NORMAL' ? 'soft' : 'solid'}>{u.status}</Tag>
                  </div>
                  <p className="text-xs text-ink-500 truncate">{u.email} · Lv.{u.level} · 注册于 {new Date(u.createdAt).toLocaleDateString()}</p>
                </div>
                <Button size="sm" variant={u.status === 'NORMAL' ? 'outline' : 'primary'} onClick={() => toggle(u)}>
                  {u.status === 'NORMAL' ? <><Ban size={13} /> 禁用</> : <><CheckCircle2 size={13} /> 启用</>}
                </Button>
              </CardBody>
            </Card>
          ))}
          {filtered.length === 0 && (
            <p className="text-ink-500 text-center py-8">
              {keyword ? `本页没有匹配「${keyword}」的用户，请翻页或清空筛选` : '暂无用户'}
            </p>
          )}
        </div>
      )}

      <div className="flex items-center justify-center gap-4 mt-6">
        <Button size="sm" variant="outline" disabled={page === 0} onClick={() => setPage(page - 1)}>上一页</Button>
        <span className="text-sm text-ink-500">第 {page + 1} 页</span>
        <Button size="sm" variant="outline" disabled={items.length < 20} onClick={() => setPage(page + 1)}>下一页</Button>
      </div>
    </div>
  )
}
