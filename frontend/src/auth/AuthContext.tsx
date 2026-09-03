import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import client, { unwrap, TOKEN_KEY, REFRESH_KEY } from '../api/client'

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

interface LoginResponse {
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
  oauthMock: (provider: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    if (token) {
      client.get('/users/me')
        .then((resp) => setUser(unwrap<User>(resp)))
        .catch(() => logout())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  function persist(resp: LoginResponse) {
    localStorage.setItem(TOKEN_KEY, resp.accessToken)
    localStorage.setItem(REFRESH_KEY, resp.refreshToken)
    setToken(resp.accessToken)
    setUser(resp.user)
  }

  async function login(username: string, password: string) {
    const resp = await client.post('/auth/login', { username, password })
    persist(unwrap<LoginResponse>(resp))
  }

  async function register(username: string, email: string, password: string) {
    const resp = await client.post('/auth/register', { username, email, password })
    persist(unwrap<LoginResponse>(resp))
  }

  async function oauthMock(provider: string) {
    const resp = await client.post(`/auth/oauth/mock?provider=${provider}&code=demo-${Date.now()}`)
    persist(unwrap<LoginResponse>(resp))
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, login, register, oauthMock, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
