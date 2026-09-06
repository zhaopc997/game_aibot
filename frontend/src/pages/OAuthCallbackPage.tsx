import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import client from '@/api/client'
import { useAuth } from '@/auth/AuthContext'

export default function OAuthCallbackPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuth()
  useEffect(() => {
    const code = params.get('code')
    if (!code) return
    client.post<{ data: { accessToken: string; refreshToken: string; user: any } }>(`/auth/oauth/mock?provider=github&code=${code}`)
      .then((r) => {
        const d = r.data.data
        // 直接写 token + 跳走(简化:复用旧 login 流程的 token 持久化)
        localStorage.setItem('guide_access_token', d.accessToken)
        localStorage.setItem('guide_refresh_token', d.refreshToken)
        login(d.user.username, 'oauth')
        navigate('/')
      })
      .catch(() => navigate('/login'))
  }, [])
  return <div className="min-h-screen grid place-items-center text-ink-500">处理登录回调…</div>
}
