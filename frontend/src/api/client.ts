import axios from 'axios'

const customApiBase = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim()
const defaultApiBase = import.meta.env.DEV
  ? '/api'
  : 'https://api.vidgrab.sunandyu.top/api'

const apiClient = axios.create({
  baseURL: customApiBase || defaultApiBase,
  timeout: 30000, // 30秒超时
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default apiClient
