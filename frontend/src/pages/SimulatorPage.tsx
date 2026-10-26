import { useCallback, useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, Calculator, Sparkles } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import client, { unwrap } from '@/api/client'

interface BuildSimulator {
  id: number
  gameId: number
  name: string
  config?: Record<string, unknown>
}

interface CalcResult {
  simulator: string
  attack: number
  critRate: number
  critDmg: number
  power: number
  bonusCount: number
}

export default function SimulatorPage() {
  const { id } = useParams<{ id: string }>()
  const gameId = Number(id)

  const [sims, setSims] = useState<BuildSimulator[]>([])
  const [activeId, setActiveId] = useState<number | null>(null)
  const [attack, setAttack] = useState('')
  const [critRate, setCritRate] = useState('')
  const [critDmg, setCritDmg] = useState('')
  const [bonusCount, setBonusCount] = useState('0')
  const [result, setResult] = useState<CalcResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [calculating, setCalculating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    if (!Number.isFinite(gameId) || gameId <= 0) {
      setError('缺少有效的游戏 ID')
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    client
      .get(`/tools/simulators?gameId=${gameId}`)
      .then((r) => {
        const data = unwrap<BuildSimulator[]>(r) ?? []
        setSims(data)
        setActiveId(data.length > 0 ? data[0].id : null)
      })
      .catch((e: unknown) => {
        const err = e as { message?: string }
        setError(err.message ?? '加载配装器失败，请稍后重试')
        setSims([])
      })
      .finally(() => setLoading(false))
  }, [gameId])

  useEffect(load, [load])

  async function calculate() {
    if (activeId == null) return
    setCalculating(true)
    setError(null)
    const n = (v: string) => (v.trim() === '' ? 0 : Number(v))
    try {
      const resp = await client.post(`/tools/simulators/${activeId}/calculate`, {
        attributes: {
          '攻击': n(attack),
          '暴击率': n(critRate),
          '暴击伤害': n(critDmg),
        },
        bonuses: Array.from({ length: Math.max(0, Math.floor(n(bonusCount))) }, (_, i) => `bonus_${i + 1}`),
      })
      setResult(unwrap<CalcResult>(resp))
    } catch (e) {
      const err = e as { message?: string }
      setError(err.message ?? '计算失败，请检查输入')
    } finally {
      setCalculating(false)
    }
  }

  return (
    <div className="pt-8 pb-20 max-w-3xl">
      <Link to={`/games/${gameId}`} className="inline-flex items-center gap-1 text-sm text-ink-500 hover:text-ink-700 mb-6">
        <ChevronLeft size={14} /> 返回游戏
      </Link>
      <h1 className="text-3xl font-display font-semibold text-ink-900 mb-6">Build 模拟器</h1>

      {loading ? (
        <p className="text-ink-500 text-center py-12">加载中…</p>
      ) : sims.length === 0 ? (
        <Card>
          <CardBody className="text-center py-16">
            <Calculator size={40} className="mx-auto text-accent-300 mb-3" />
            <p className="text-ink-500">{error ?? '该游戏暂无可用的配装模拟器'}</p>
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-6">
          {sims.length > 1 && (
            <div className="flex items-center gap-2 overflow-x-auto scrollbar-thin">
              {sims.map((s) => (
                <button
                  key={s.id}
                  onClick={() => { setActiveId(s.id); setResult(null) }}
                  className={`shrink-0 h-9 px-3.5 rounded-xl text-sm font-medium transition-all ${
                    activeId === s.id
                      ? 'bg-accent-500 text-white'
                      : 'bg-surface text-ink-700 border border-ink-100 hover:border-ink-300'
                  }`}
                >{s.name}</button>
              ))}
            </div>
          )}

          <Card>
            <CardBody>
              <h2 className="text-base font-medium text-ink-900 mb-4">输入属性</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-ink-700 mb-1.5">攻击</label>
                  <Input value={attack} onChange={(e) => setAttack(e.target.value)} placeholder="例如 1200" />
                </div>
                <div>
                  <label className="block text-sm text-ink-700 mb-1.5">暴击率 (%)</label>
                  <Input value={critRate} onChange={(e) => setCritRate(e.target.value)} placeholder="例如 45" />
                </div>
                <div>
                  <label className="block text-sm text-ink-700 mb-1.5">暴击伤害 (%)</label>
                  <Input value={critDmg} onChange={(e) => setCritDmg(e.target.value)} placeholder="例如 90" />
                </div>
                <div>
                  <label className="block text-sm text-ink-700 mb-1.5">加成词条数</label>
                  <Input value={bonusCount} onChange={(e) => setBonusCount(e.target.value)} placeholder="例如 4" />
                </div>
              </div>

              {error && <p className="mt-4 text-danger-600 text-sm">{error}</p>}

              <Button variant="primary" className="mt-6" disabled={calculating} onClick={calculate}>
                <Sparkles size={14} /> {calculating ? '计算中…' : '开始计算'}
              </Button>
            </CardBody>
          </Card>

          {result && (
            <Card>
              <CardBody>
                <h2 className="text-base font-medium text-ink-900 mb-4">计算结果</h2>
                <dl className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  <div>
                    <dt className="text-xs text-ink-500 mb-1">战力</dt>
                    <dd className="text-2xl font-display font-semibold text-accent-600">{result.power}</dd>
                  </div>
                  {[
                    ['攻击', result.attack],
                    ['暴击率', `${result.critRate}%`],
                    ['暴击伤害', `${result.critDmg}%`],
                    ['加成词条', result.bonusCount],
                  ].map(([k, v]) => (
                    <div key={k as string}>
                      <dt className="text-xs text-ink-500 mb-1">{k}</dt>
                      <dd className="text-lg text-ink-900">{v}</dd>
                    </div>
                  ))}
                </dl>
              </CardBody>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}