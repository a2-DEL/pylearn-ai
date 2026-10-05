import axios from 'axios'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'pylearn_token'

const http = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// 请求拦截：注入 JWT
http.interceptors.request.use((config: any) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers = config.headers || {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (resp: any) => {
    const body = resp.data
    if (body && typeof body.code === 'number' && body.code !== 0) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return (body && 'data' in body ? body.data : body) as any
  },
  (err: any) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
    }
    const msg = err?.response?.data?.message || err?.message || '网络错误'
    ElMessage.error(msg)
    return Promise.reject(err)
  },
)

export default http
