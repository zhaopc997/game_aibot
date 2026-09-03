import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import client, { unwrap } from '../api/client'

interface Simulator {
  id: number
  name: string
  config: Record<string, unknown>
}

export default function SimulatorPage() {
  const { id } = useParams()
  const [sim, setSim] = useState<Simulator | null>(null)
  const [attack, setAttack] = useState(100)
  const [critRate, setCritRate] = useState(20)
  const [critDmg, setCritDmg] = useState(150)
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    client.get(`/tools/simulators/${id}`).then((r) => setSim(unwrap<Simulator>(r)))
  }, [id])

  async function calculate() {
    const r = await client.post(`/tools/simulators/${id}/calculate`, {
      attributes: { 攻击: attack, 暴击率: critRate, 暴击伤害: critDmg },
      bonuses: [{ type: '套装' }],
    })
    setResult(unwrap<Record<string, unknown>>(r))
  }

  return (
    <div style={{ maxWidth: 560 }}>
      <h2>{sim?.name || 'Build 模拟器'}</h2>
      <div className="card">
        <label className="muted">攻击力</label>
        <input className="input" type="number" value={attack} onChange={(e) => setAttack(+e.target.value)} />
        <label className="muted">暴击率（%）</label>
        <input className="input" type="number" value={critRate} onChange={(e) => setCritRate(+e.target.value)} />
        <label className="muted">暴击伤害（%）</label>
        <input className="input" type="number" value={critDmg} onChange={(e) => setCritDmg(+e.target.value)} />
        <button className="btn btn-primary btn-block" onClick={calculate}>计算战力</button>
      </div>
      {result && (
        <div className="card">
          <h3>计算结果</h3>
          <p>攻击：{String(result.attack)}</p>
          <p>暴击率：{String(result.critRate)}%</p>
          <p>暴击伤害：{String(result.critDmg)}%</p>
          <p style={{ fontSize: 20 }}>综合战力：<b>{String(result.power)}</b></p>
        </div>
      )}
    </div>
  )
}
