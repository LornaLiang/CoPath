import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload?.code === 200) {
      return payload.data
    }
    return Promise.reject(new Error(payload?.message || '请求失败'))
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '网络请求失败'
    return Promise.reject(new Error(message))
  },
)

export default api
