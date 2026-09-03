import { useState, useEffect } from 'react'
import client, { unwrap } from '../api/client'
import { useAuth } from '../auth/AuthContext'

interface Notification {
  id: number
  type: string
  title: string
  content?: string
  isRead: boolean
  createdAt: string
}

export default function Notifications() {
  const { token } = useAuth()
  const [items, setItems] = useState<Notification[]>([])

  useEffect(() => {
    if (!token) return
    client.get('/notifications').then((r) => setItems(unwrap<Notification[]>(r)))
  }, [token])

  async function markRead() {
    await client.post('/notifications/read')
    setItems(items.map((n) => ({ ...n, isRead: true })))
  }

  return (
    <div style={{ maxWidth: 640 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <h2>通知中心</h2>
        {token && <button className="btn" onClick={markRead}>全部已读</button>}
      </div>
      {!token && <p className="muted">请先登录查看通知</p>}
      {items.map((n) => (
        <div key={n.id} className="card" style={{ opacity: n.isRead ? 0.7 : 1 }}>
          <b>{n.title}</b> <span className="tag">{n.type}</span>
          {n.content && <p className="muted" style={{ margin: '6px 0' }}>{n.content}</p>}
          <p className="muted" style={{ margin: 0 }}>{new Date(n.createdAt).toLocaleString()}</p>
        </div>
      ))}
      {token && items.length === 0 && <p className="muted">暂无通知</p>}
    </div>
  )
}
