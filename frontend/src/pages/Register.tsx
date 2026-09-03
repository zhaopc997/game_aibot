import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')

  function set(key: string, value: string) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    try {
      await register(form.username, form.email, form.password)
      navigate('/')
    } catch (err: any) {
      setError(err?.response?.data?.message || '注册失败')
    }
  }

  return (
    <div className="card form-card">
      <h2 style={{ marginTop: 0 }}>注册</h2>
      {error && <p style={{ color: '#dc2626' }}>{error}</p>}
      <form onSubmit={submit}>
        <input className="input" placeholder="用户名（≥3字符）" value={form.username}
               onChange={(e) => set('username', e.target.value)} />
        <input className="input" type="email" placeholder="邮箱" value={form.email}
               onChange={(e) => set('email', e.target.value)} />
        <input className="input" type="password" placeholder="密码（≥6位）" value={form.password}
               onChange={(e) => set('password', e.target.value)} />
        <button className="btn btn-primary btn-block" type="submit">注册</button>
      </form>
      <p className="muted" style={{ textAlign: 'center' }}>
        已有账号？<Link to="/login">去登录</Link>
      </p>
    </div>
  )
}
