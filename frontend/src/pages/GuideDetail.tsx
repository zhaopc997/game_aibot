import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import client, { unwrap } from '../api/client'

interface Step {
  step_id: number
  title: string
  description?: string
  conditions?: string[]
  tools?: string[]
  images?: string[]
}

interface Guide {
  id: number
  title: string
  summary?: string
  tags: string[]
  difficulty?: string
  status: string
  content: { steps: Step[] }
  likeCount: number
  usefulCount: number
  verifyCount: number
}

export default function GuideDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [guide, setGuide] = useState<Guide | null>(null)

  useEffect(() => {
    client.get(`/guides/${id}`)
      .then((resp) => setGuide(unwrap<Guide>(resp)))
      .catch(() => navigate('/'))
  }, [id, navigate])

  if (!guide) return <p className="muted">加载中…</p>

  return (
    <div>
      <h1>{guide.title}</h1>
      <p className="muted">{guide.summary}</p>
      <div style={{ marginBottom: 16 }}>
        {guide.tags?.map((t) => <span key={t} className="tag">{t}</span>)}
        {guide.difficulty && <span className="tag">{guide.difficulty}</span>}
      </div>

      <div className="card">
        <h3>步骤</h3>
        {guide.content?.steps?.map((s, i) => (
          <div key={s.step_id} style={{ padding: '8px 0', borderBottom: '1px solid #eee' }}>
            <b>Step {i + 1}：{s.title}</b>
            {s.description && <p className="muted">{s.description}</p>}
            {s.conditions?.length ? (
              <p className="muted">前置条件：{s.conditions.join('，')}</p>
            ) : null}
            {s.tools?.length ? (
              <p className="muted">工具：{s.tools.join('、')}</p>
            ) : null}
          </div>
        ))}
      </div>

      <p className="muted">
        👍 {guide.likeCount} · 有用 {guide.usefulCount} · 已验证 {guide.verifyCount}
      </p>
    </div>
  )
}
