import { computed, ref } from 'vue'

import apiClient from '@/api/client'
import type {
  CurrentUserResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  UserProfile,
} from '@/types'

const currentUser = ref<UserProfile | null>(null)
const loading = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)
const registerMessage = ref<string | null>(null)
const debugVerifyUrl = ref<string | null>(null)

const authenticated = computed(() => !!currentUser.value)

export function useAuth() {
  const fetchCurrentUser = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get<CurrentUserResponse>('/auth/me')
      currentUser.value = response.data.authenticated ? response.data.user || null : null
      return currentUser.value
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取登录状态失败'
      currentUser.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  const register = async (payload: RegisterRequest) => {
    submitting.value = true
    error.value = null
    registerMessage.value = null
    debugVerifyUrl.value = null

    try {
      const response = await apiClient.post<RegisterResponse>('/auth/register', payload)
      registerMessage.value = response.data.message
      debugVerifyUrl.value = response.data.debug_verify_url || null
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '注册失败'
      throw err
    } finally {
      submitting.value = false
    }
  }

  const login = async (payload: LoginRequest) => {
    submitting.value = true
    error.value = null
    try {
      const response = await apiClient.post<LoginResponse>('/auth/login', payload)
      currentUser.value = response.data.user
      return response.data.user
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登录失败'
      throw err
    } finally {
      submitting.value = false
    }
  }

  const logout = async () => {
    submitting.value = true
    error.value = null
    try {
      await apiClient.post('/auth/logout')
      currentUser.value = null
      registerMessage.value = null
      debugVerifyUrl.value = null
    } catch (err: any) {
      error.value = err.response?.data?.detail || '退出登录失败'
      throw err
    } finally {
      submitting.value = false
    }
  }

  const clearFeedback = () => {
    error.value = null
    registerMessage.value = null
    debugVerifyUrl.value = null
  }

  return {
    currentUser,
    authenticated,
    loading,
    submitting,
    error,
    registerMessage,
    debugVerifyUrl,
    fetchCurrentUser,
    register,
    login,
    logout,
    clearFeedback,
  }
}
