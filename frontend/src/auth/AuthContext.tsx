import { createContext, useCallback, useContext, useEffect, useState, ReactNode } from 'react'
import client, { unwrap, TOKEN_KEY, REFRESH_KEY, SESSION_EXPIRED_EVENT } from '../api/client'

interface User {
  id: number
  username: string
  email: string
  avatar?: string
  bio?: string
  level: number
  exp: number
  roles: string[]
}

/** 登录/注册/OAuth 三种入口共用的会话响应体。 */
export interface LoginResponse {
  accessToken: string
  refreshToken: string
  expiresIn: number
  user: User
}

interface AuthContextValue {
  token: string | null
  user: User | null
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  /** 直接接管后端下发的 token+user（OAuth 回调用），不经过登录接口。 */
  adoptSession: (resp: LoginResponse) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
    setToken(null)
    setUser(null)
  }, [])

  // token 变化后拉取当前用户；失败视为凭证失效，登出避免"假登录态"
  useEffect(() => {
    if (!token) {
      setUser(null)
      return
    }
    let cancelled = false
    client
      .get('/users/me')
      .then((resp) => {
        if (!cancelled) setUser(unwrap<User>(resp))
      })
      .catch(() => {
        if (!cancelled) logout()
      })
    return () => {
      cancelled = true
    }
  }, [token, logout])

  // axios 层 refresh 失败时广播 SESSION_EXPIRED_EVENT，此处同步登出，
  // 否则 localStorage 已清空但 token state 仍是旧值，路由守卫会误判为已登录
  useEffect(() => {
    window.addEventListener(SESSION_EXPIRED_EVENT, logout)
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, logout)
  }, [logout])

  function persist(resp: LoginResponse) {
    localStorage.setItem(TOKEN_KEY, resp.accessToken)
    localStorage.setItem(REFRESH_KEY, resp.refreshToken)
    setToken(resp.accessToken)
    setUser(resp.user)
  }

  /** OAuth 回调等场景：后端已直接下发 token 与用户，无需再走登录接口。 */
  function adoptSession(resp: LoginResponse) {
    persist(resp)
  }

  async function login(username: string, password: string) {
    const resp = await client.post('/auth/login', { username, password })
    persist(unwrap<LoginResponse>(resp))
  }

  async function register(username: string, email: string, password: string) {
    const resp = await client.post('/auth/register', { username, email, password })
    persist(unwrap<LoginResponse>(resp))
  }

  return (
    <AuthContext.Provider value={{ token, user, login, register, adoptSession, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
