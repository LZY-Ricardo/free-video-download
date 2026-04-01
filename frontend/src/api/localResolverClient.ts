import axios from 'axios'

const localResolverBase =
  (import.meta.env.VITE_LOCAL_RESOLVER_BASE_URL as string | undefined)?.trim() ||
  'http://127.0.0.1:61337/api'

const localResolverClient = axios.create({
  baseURL: localResolverBase,
  timeout: 60000,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const LOCAL_RESOLVER_BASE = localResolverBase
export default localResolverClient

