import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30秒超时
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default apiClient
