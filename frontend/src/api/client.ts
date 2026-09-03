import axios from 'axios'

export const TOKEN_KEY = 'guide_access_token'
export const REFRESH_KEY = 'guide_refresh_token'

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

client.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem(REFRESH_KEY)
      if (refresh) {
        try {
          const { data } = await axios.post('/api/v1/auth/refresh', { refreshToken: refresh })
          localStorage.setItem(TOKEN_KEY, data.data.accessToken)
          localStorage.setItem(REFRESH_KEY, data.data.refreshToken)
          original.headers.Authorization = `Bearer ${data.data.accessToken}`
          return client(original)
        } catch {
          localStorage.removeItem(TOKEN_KEY)
          localStorage.removeItem(REFRESH_KEY)
        }
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
