import { useState, useEffect } from 'react'
import client, { unwrap } from '../api/client'
import { useAuth } from '../auth/AuthContext'

interface Question {
  id: number
  title: string
  description?: string
  status: string
  createdAt: string
}

interface Answer {
  id: number
  content: string
  createdAt: string
}

export default function QA() {
  const { token } = useAuth()
  const [questions, setQuestions] = useState<Question[]>([])
  const [title, setTitle] = useState('')
  const [desc, setDesc] = useState('')
  const [active, setActive] = useState<Question | null>(null)
  const [answers, setAnswers] = useState<Answer[]>([])
  const [newAnswer, setNewAnswer] = useState('')

  function load() {
    client.get('/questions').then((r) => setQuestions(unwrap<Question[]>(r)))
  }

  useEffect(load, [])

  async function ask() {
    if (!title.trim()) return
    await client.post('/questions', { title, description: desc, gameId: 1 })
    setTitle(''); setDesc(''); load()
  }

  async function open(q: Question) {
    setActive(q)
    const r = await client.get(`/questions/${q.id}/answers`)
    setAnswers(unwrap<Answer[]>(r))
  }

  async function answer() {
    if (!active || !newAnswer.trim()) return
    await client.post(`/questions/${active.id}/answers`, { content: newAnswer })
    setNewAnswer(''); open(active)
  }

  return (
    <div>
      <h2>问答社区</h2>
      {token && (
        <div className="card">
          <input className="input" placeholder="问题标题" value={title} onChange={(e) => setTitle(e.target.value)} />
          <textarea className="input" placeholder="问题描述" value={desc} onChange={(e) => setDesc(e.target.value)} />
          <button className="btn btn-primary" onClick={ask}>发布问题</button>
        </div>
      )}

      {questions.map((q) => (
        <div key={q.id} className="card">
          <div onClick={() => open(q)} style={{ cursor: 'pointer' }}>
            <b>{q.title}</b>
            {q.description && <p className="muted">{q.description}</p>}
            <span className="tag">{q.status}</span>
          </div>
          {active?.id === q.id && (
            <div style={{ marginTop: 12, borderTop: '1px solid #eee', paddingTop: 12 }}>
              {answers.map((a) => (
                <p key={a.id} className="muted" style={{ background: '#f9fafb', padding: 8, borderRadius: 6 }}>{a.content}</p>
              ))}
              {token && (
                <div style={{ display: 'flex', gap: 8 }}>
                  <input className="input" placeholder="写回答…" value={newAnswer}
                         onChange={(e) => setNewAnswer(e.target.value)} style={{ marginBottom: 0 }} />
                  <button className="btn btn-primary" onClick={answer}>回答</button>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
