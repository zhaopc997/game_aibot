import { useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { TOKEN_KEY, REFRESH_KEY } from '../api/client'

export default function OAuthCallback() {
  const [params] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const access = params.get('accessToken')
    const refresh = params.get('refreshToken')
    if (access) {
      localStorage.setItem(TOKEN_KEY, access)
      if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
      navigate('/')
    } else {
      navigate('/login')
    }
  }, [params, navigate])

  return <p className="muted" style={{ textAlign: 'center', marginTop: 60 }}>登录处理中…</p>
}
