import axios from 'axios'

export const TOKEN_KEY = 'guide_access_token'
export const REFRESH_KEY = 'guide_refresh_token'

/** 会话失效事件名：refresh 失败时广播，AuthContext 订阅后统一登出，避免 UI 与 localStorage 不一致。 */
export const SESSION_EXPIRED_EVENT = 'auth:session-expired'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** 清除本地凭证并广播会话失效（供 AuthContext 同步登出）。 */
export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_KEY)
  window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT))
}

/**
 * 刷新中的单例 Promise。
 * 并发 401 时只发起一次 refresh，其余请求 await 同一次结果；
 * 否则 N 个并发 401 会触发 N 次 refresh，其中 N-1 次使用已被轮换的旧
 * refreshToken，导致连锁失败并误清凭证（GameDetailPage 首屏即有 9 个并发请求）。
 */
let refreshPromise: Promise<string> | null = null

function refreshAccessToken(): Promise<string> {
  if (refreshPromise) return refreshPromise

  refreshPromise = (async () => {
    const refresh = localStorage.getItem(REFRESH_KEY)
    if (!refresh) throw new Error('no refresh token')

    const { data } = await axios.post(`${client.defaults.baseURL}/auth/refresh`, {
      refreshToken: refresh,
    })
    const payload = data?.data ?? data
    if (!payload?.accessToken) throw new Error('invalid refresh response')

    localStorage.setItem(TOKEN_KEY, payload.accessToken)
    if (payload.refreshToken) {
      localStorage.setItem(REFRESH_KEY, payload.refreshToken)
    }
    return payload.accessToken as string
  })().finally(() => {
    // 无论成败都释放锁，避免一次失败永久卡死后续请求
    refreshPromise = null
  })

  return refreshPromise
}

client.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    const original = error.config as typeof error.config & { _retry?: boolean }

    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true
      try {
        const token = await refreshAccessToken()
        original.headers.Authorization = `Bearer ${token}`
        return client(original)
      } catch {
        clearSession()
      }
    }
    return Promise.reject(error)
  },
)

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export function unwrap<T>(resp: { data: ApiResponse<T> }): T {
  if (resp.data.code !== 0) {
    throw new Error(resp.data.message)
  }
  return resp.data.data
}

export default client