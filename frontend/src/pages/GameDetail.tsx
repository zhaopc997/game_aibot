import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import client, { unwrap } from '../api/client'

interface Game {
  id: number
  name: string
  category?: string
  platform?: string
  description?: string
  currentVersion?: string
}

interface Guide {
  id: number
  title: string
  summary?: string
  tags: string[]
  difficulty?: string
}

interface PageResult<T> {
  items: T[]
  nextCursor?: string | null
}

export default function GameDetail() {
  const { id } = useParams()
  const [game, setGame] = useState<Game | null>(null)
  const [guides, setGuides] = useState<Guide[]>([])

  useEffect(() => {
    client.get(`/games/${id}`).then((r) => setGame(unwrap<Game>(r)))
    client.get(`/guides?gameId=${id}&status=PUBLISHED&size=20`).then((r) => {
      setGuides(unwrap<PageResult<Guide>>(r).items)
    })
  }, [id])

  if (!game) return <p className="muted">加载中…</p>

  return (
    <div>
      <h1>{game.name}</h1>
      <p className="muted">
        {game.category} · {game.platform} · 当前版本 {game.currentVersion}
      </p>
      {game.description && <p>{game.description}</p>}

      <div style={{ display: 'flex', gap: 8, margin: '16px 0' }}>
        <Link className="btn" to={`/games/${id}/maps`}>互动地图</Link>
        <Link className="btn" to={`/games/${id}/simulators`}>Build 模拟器</Link>
        <Link className="btn" to={`/guides/new?gameId=${id}`}>写攻略</Link>
      </div>

      <h3>攻略列表</h3>
      {guides.map((g) => (
        <div key={g.id} className="card">
          <Link to={`/guides/${g.id}`} style={{ fontWeight: 600 }}>{g.title}</Link>
          {g.summary && <p className="muted" style={{ margin: '6px 0' }}>{g.summary}</p>}
          <div>
            {g.tags?.map((t) => <span key={t} className="tag">{t}</span>)}
            {g.difficulty && <span className="tag">{g.difficulty}</span>}
          </div>
        </div>
      ))}
      {guides.length === 0 && <p className="muted">暂无攻略</p>}
    </div>
  )
}
