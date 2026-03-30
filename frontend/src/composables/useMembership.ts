import { ref } from 'vue'

import apiClient from '@/api/client'
import type { CheckoutSessionResponse, MembershipStatusResponse } from '@/types'

const membership = ref<MembershipStatusResponse | null>(null)
const loading = ref(false)
const checkoutLoading = ref(false)
const error = ref<string | null>(null)

export function useMembership() {
  const fetchMembership = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.get<MembershipStatusResponse>('/membership/me')
      membership.value = response.data
      return response.data
    } catch (err: any) {
      if (err.response?.status === 401) {
        membership.value = null
        return null
      }
      error.value = err.response?.data?.detail || '获取会员状态失败'
      membership.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearMembership = () => {
    membership.value = null
    error.value = null
  }

  const createCheckoutSession = async () => {
    checkoutLoading.value = true
    error.value = null
    try {
      const response = await apiClient.post<CheckoutSessionResponse>('/billing/checkout-session')
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建支付会话失败'
      throw err
    } finally {
      checkoutLoading.value = false
    }
  }

  const completeMockCheckout = async (orderId: string) => {
    checkoutLoading.value = true
    error.value = null
    try {
      await apiClient.post(`/dev/mock-billing/complete-order/${encodeURIComponent(orderId)}`)
    } catch (err: any) {
      error.value = err.response?.data?.detail || '模拟支付失败'
      throw err
    } finally {
      checkoutLoading.value = false
    }
  }

  return {
    membership,
    loading,
    checkoutLoading,
    error,
    fetchMembership,
    clearMembership,
    createCheckoutSession,
    completeMockCheckout,
  }
}
