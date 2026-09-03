import { useState, useEffect } from 'react'
import client, { unwrap } from '../api/client'
import { useAuth } from '../auth/AuthContext'

interface User {
  id: number
  username: string
  email: string
  status: string
  level: number
}

interface Review {
  id: number
  targetType: string
  targetId: number
  status: string
  riskLevel: string
}

interface Game {
  id: number
  name: string
  category?: string
  currentVersion?: string
}

export default function Admin() {
  const { user } = useAuth()
  const [tab, setTab] = useState<'users' | 'reviews' | 'games'>('users')
  const [users, setUsers] = useState<User[]>([])
  const [reviews, setReviews] = useState<Review[]>([])
  const [games, setGames] = useState<Game[]>([])
  const [newGame, setNewGame] = useState('')

  function loadUsers() {
    client.get('/admin/users?size=50').then((r) => setUsers(unwrap<{ items: User[] }>(r).items))
  }
  function loadReviews() {
    client.get('/reviews/queue').then((r) => setReviews(unwrap<Review[]>(r)))
  }
  function loadGames() {
    client.get('/games').then((r) => setGames(unwrap<Game[]>(r)))
  }

  useEffect(() => {
    if (tab === 'users') loadUsers()
    if (tab === 'reviews') loadReviews()
    if (tab === 'games') loadGames()
  }, [tab])

  async function toggleStatus(u: User) {
    const next = u.status === 'DISABLED' ? 'NORMAL' : 'DISABLED'
    await client.put(`/admin/users/${u.id}/status`, { status: next })
    loadUsers()
  }

  async function decide(r: Review, decision: string) {
    await client.post(`/reviews/${r.id}/decision`, { decision })
    loadReviews()
  }

  async function createGame() {
    if (!newGame.trim()) return
    await client.post('/games', { name: newGame, category: '未分类', currentVersion: '1.0' })
    setNewGame(''); loadGames()
  }

  if (!user?.roles.includes('ADMIN')) {
    return <p className="muted">无权限访问管理后台（需要 ADMIN 角色）</p>
  }

  return (
    <div>
      <h2>管理后台</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {(['users', 'reviews', 'games'] as const).map((t) => (
          <button key={t} className={tab === t ? 'btn btn-primary' : 'btn'} onClick={() => setTab(t)}>
            {t === 'users' ? '用户管理' : t === 'reviews' ? '审核队列' : '游戏管理'}
          </button>
        ))}
      </div>

      {tab === 'users' && (
        <div>
          {users.map((u) => (
            <div key={u.id} className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <b>{u.username}</b>
              <span className="muted">{u.email}</span>
              <span className="tag">{u.status}</span>
              <span style={{ flex: 1 }} />
              <button className="btn" onClick={() => toggleStatus(u)}>
                {u.status === 'DISABLED' ? '启用' : '封禁'}
              </button>
            </div>
          ))}
        </div>
      )}

      {tab === 'reviews' && (
        <div>
          {reviews.length === 0 && <p className="muted">审核队列为空</p>}
          {reviews.map((r) => (
            <div key={r.id} className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <b>{r.targetType}#{r.targetId}</b>
              <span className="tag">{r.riskLevel}</span>
              <span style={{ flex: 1 }} />
              <button className="btn" onClick={() => decide(r, 'PASSED')}>通过</button>
              <button className="btn" onClick={() => decide(r, 'REJECTED')}>拒绝</button>
            </div>
          ))}
        </div>
      )}

      {tab === 'games' && (
        <div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            <input className="input" placeholder="新游戏名称" value={newGame}
                   onChange={(e) => setNewGame(e.target.value)} style={{ marginBottom: 0, flex: 1 }} />
            <button className="btn btn-primary" onClick={createGame}>新增游戏</button>
          </div>
          {games.map((g) => (
            <div key={g.id} className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <b>{g.name}</b>
              <span className="muted">{g.category}</span>
              <span className="tag">v{g.currentVersion}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
