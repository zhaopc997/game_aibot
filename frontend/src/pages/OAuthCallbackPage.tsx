import { useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import client, { unwrap } from '@/api/client'
import { useAuth, type LoginResponse } from '@/auth/AuthContext'

export default function OAuthCallbackPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { adoptSession } = useAuth()
  const handled = useRef(false)

  useEffect(() => {
    // React 18 开发模式 StrictMode 会双调用 effect，用 ref 保证只处理一次
    if (handled.current) return
    const code = params.get('code')
    if (!code) {
      navigate('/login', { replace: true })
      return
    }
    handled.current = true

    const provider = params.get('provider') || 'github'
    client
      .post(`/auth/oauth/mock?provider=${provider}&code=${encodeURIComponent(code)}`)
      .then((resp) => {
        // 后端已直接下发 token 与用户，直接接管会话；
        // 不能用用户名+假密码再调登录接口（会失败且未 await）
        adoptSession(unwrap<LoginResponse>(resp))
        navigate('/', { replace: true })
      })
      .catch(() => navigate('/login', { replace: true }))
  }, [params, navigate, adoptSession])

  return <div className="min-h-screen grid place-items-center text-ink-500">处理登录回调…</div>
}