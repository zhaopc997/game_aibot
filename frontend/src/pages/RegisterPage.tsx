import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Gamepad2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardBody } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/auth/AuthContext'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); setErr('')
    try {
      await register(form.username, form.email, form.password)
      navigate('/')
    } catch (e: any) {
      setErr(e?.response?.data?.message ?? e?.message ?? '注册失败')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-canvas grid place-items-center px-4">
      <Card className="w-full max-w-md">
        <CardBody>
          <div className="text-center mb-6">
            <div className="inline-grid place-items-center h-12 w-12 rounded-2xl bg-accent-500 text-white mb-3">
              <Gamepad2 size={22} />
            </div>
            <h1 className="text-2xl font-display font-semibold text-ink-900">加入 game_aibot</h1>
            <p className="mt-1 text-sm text-ink-500">10 秒创建账号,开始你的攻略之旅</p>
          </div>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="text-sm text-ink-700 mb-1.5 block">用户名</label>
              <Input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
            </div>
            <div>
              <label className="text-sm text-ink-700 mb-1.5 block">邮箱</label>
              <Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
            <div>
              <label className="text-sm text-ink-700 mb-1.5 block">密码</label>
              <Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            </div>
            {err && <p className="text-sm text-red-500">{err}</p>}
            <Button type="submit" className="w-full" disabled={loading}>{loading ? '注册中…' : '注册'}</Button>
            <p className="text-center text-sm text-ink-500">
              已有账号? <Link to="/login" className="text-accent-700 hover:underline">登录</Link>
            </p>
          </form>
        </CardBody>
      </Card>
    </div>
  )
}
