import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import client, { unwrap } from '../api/client'

interface Guide {
  id: number
  title: string
  summary?: string
  tags: string[]
  difficulty?: string
  likeCount: number
  usefulCount: number
  status: string
  updatedAt: string
}

interface Game {
  id: number
  name: string
  alias?: string
  platform?: string
  category?: string
  currentVersion?: string
}

interface PageResult<T> {
  items: T[]
  nextCursor?: string | null
}

export default function GuideList() {
  const [keyword, setKeyword] = useState('')
  const [games, setGames] = useState<Game[]>([])
  const [guides, setGuides] = useState<Guide[]>([])
  const [loading, setLoading] = useState(false)

  async function load(query: string) {
    setLoading(true)
    try {
      const url = query
        ? `/guides/search?keyword=${encodeURIComponent(query)}`
        : '/guides?status=PUBLISHED&size=20'
      const resp = await client.get(url)
      const data = unwrap<PageResult<Guide>>(resp)
      setGuides(data.items)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    client.get('/games').then((r) => setGames(unwrap<Game[]>(r)))
    load('')
  }, [])

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>游戏库</h2>
      <div className="game-grid">
        {games.map((g) => (
          <Link key={g.id} to={`/games/${g.id}`} className="game-card">
            <span className="game-name">{g.name}</span>
            <span className="muted">
              {[g.category, g.platform].filter(Boolean).join(' · ')}
              {g.currentVersion ? ` · v${g.currentVersion}` : ''}
            </span>
          </Link>
        ))}
      </div>

      <h2 style={{ marginTop: 24 }}>最新攻略</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input
          className="input"
          style={{ flex: 1, marginBottom: 0 }}
          placeholder="搜索攻略标题 / 摘要…"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') load(keyword) }}
        />
        <button className="btn btn-primary" onClick={() => load(keyword)}>搜索</button>
      </div>

      {loading && <p className="muted">加载中…</p>}

      {guides.map((g) => (
        <div key={g.id} className="card">
          <Link to={`/guides/${g.id}`} style={{ fontSize: 17, fontWeight: 600 }}>{g.title}</Link>
          {g.summary && <p className="muted" style={{ margin: '8px 0' }}>{g.summary}</p>}
          <div>
            {g.tags?.map((t) => <span key={t} className="tag">{t}</span>)}
            {g.difficulty && <span className="tag" style={{ background: '#fef3c7', color: '#b45309' }}>{g.difficulty}</span>}
          </div>
          <p className="muted" style={{ marginTop: 8 }}>👍 {g.likeCount} · 有用 {g.usefulCount} · {new Date(g.updatedAt).toLocaleDateString()}</p>
        </div>
      ))}
    </div>
  )
}
