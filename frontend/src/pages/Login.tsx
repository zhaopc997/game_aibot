import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function Login() {
  const { login, oauthMock } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    try {
      await login(username, password)
      navigate('/')
    } catch (err: any) {
      setError(err?.response?.data?.message || '登录失败')
    }
  }

  return (
    <div className="card form-card">
      <h2 style={{ marginTop: 0 }}>登录</h2>
      {error && <p style={{ color: '#dc2626' }}>{error}</p>}
      <form onSubmit={submit}>
        <input className="input" placeholder="用户名" value={username}
               onChange={(e) => setUsername(e.target.value)} />
        <input className="input" type="password" placeholder="密码" value={password}
               onChange={(e) => setPassword(e.target.value)} />
        <button className="btn btn-primary btn-block" type="submit">登录</button>
      </form>
      <div style={{ textAlign: 'center', margin: '16px 0', color: '#6b7280' }}>— 或 —</div>
      <button className="btn btn-block" style={{ marginBottom: 8 }} onClick={() => oauthMock('github')}>
        GitHub 模拟登录
      </button>
      <button className="btn btn-block" onClick={() => oauthMock('wechat')}>
        微信模拟登录
      </button>
      <p className="muted" style={{ textAlign: 'center' }}>
        还没有账号？<Link to="/register">立即注册</Link>
      </p>
    </div>
  )
}
