import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import client, { unwrap } from '../api/client'

interface Step {
  step_id: number
  title: string
  description: string
  conditions: string[]
  tools: string[]
}

export default function GuideEditor() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const gameId = Number(params.get('gameId') || 1)

  const [title, setTitle] = useState('')
  const [summary, setSummary] = useState('')
  const [difficulty, setDifficulty] = useState('EASY')
  const [tagsText, setTagsText] = useState('')
  const [steps, setSteps] = useState<Step[]>([])
  const [error, setError] = useState('')

  function addStep() {
    setSteps([...steps, { step_id: steps.length + 1, title: '', description: '', conditions: [], tools: [] }])
  }

  function updateStep(i: number, patch: Partial<Step>) {
    setSteps(steps.map((s, idx) => (idx === i ? { ...s, ...patch } : s)))
  }

  function removeStep(i: number) {
    setSteps(steps.filter((_, idx) => idx !== i))
  }

  async function submit() {
    if (!title.trim()) { setError('请填写标题'); return }
    const tags = tagsText.split(/[，,]/).map((t) => t.trim()).filter(Boolean)
    try {
      const content = { schema_version: '1.0', steps: steps.map((s, i) => ({ ...s, step_id: i + 1 })) }
      const resp = await client.post('/guides', {
        gameId, title, summary, difficulty, tags,
        content,
      })
      const guide = unwrap<{ id: number }>(resp)
      navigate(`/guides/${guide.id}`)
    } catch (err: any) {
      setError(err?.response?.data?.message || '保存失败')
    }
  }

  return (
    <div style={{ maxWidth: 720 }}>
      <h2>编写攻略</h2>
      {error && <p style={{ color: '#dc2626' }}>{error}</p>}
      <input className="input" placeholder="标题" value={title} onChange={(e) => setTitle(e.target.value)} />
      <textarea className="input" placeholder="摘要" value={summary} onChange={(e) => setSummary(e.target.value)} />
      <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        <select className="input" style={{ width: 200, marginBottom: 0 }} value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}>
          <option value="EASY">简单</option>
          <option value="NORMAL">普通</option>
          <option value="HARD">困难</option>
          <option value="EXPERT">专家</option>
        </select>
        <input className="input" style={{ flex: 1, marginBottom: 0 }} placeholder="标签（逗号分隔）"
               value={tagsText} onChange={(e) => setTagsText(e.target.value)} />
      </div>

      <h3>步骤</h3>
      {steps.map((s, i) => (
        <div key={i} className="card">
          <div style={{ display: 'flex', gap: 8 }}>
            <input className="input" placeholder={`步骤 ${i + 1} 标题`} value={s.title}
                   onChange={(e) => updateStep(i, { title: e.target.value })} />
            <button className="btn" onClick={() => removeStep(i)}>删除</button>
          </div>
          <textarea className="input" placeholder="详细描述" value={s.description}
                    onChange={(e) => updateStep(i, { description: e.target.value })} />
          <input className="input" placeholder="前置条件（逗号分隔）" value={s.conditions.join(',')}
                 onChange={(e) => updateStep(i, { conditions: e.target.value.split(/[，,]/).map((x) => x.trim()).filter(Boolean) })} />
          <input className="input" placeholder="工具（逗号分隔）" value={s.tools.join(',')}
                 onChange={(e) => updateStep(i, { tools: e.target.value.split(/[，,]/).map((x) => x.trim()).filter(Boolean) })} />
        </div>
      ))}
      <button className="btn" onClick={addStep} style={{ marginRight: 8 }}>+ 添加步骤</button>
      <button className="btn btn-primary" onClick={submit}>保存（草稿）</button>
    </div>
  )
}
