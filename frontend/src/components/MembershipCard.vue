<script setup lang="ts">
import type { MembershipStatusResponse } from '@/types'

const props = withDefaults(defineProps<{
  authenticated: boolean
  membership: MembershipStatusResponse | null
  loading?: boolean
  checkoutLoading?: boolean
}>(), {
  loading: false,
  checkoutLoading: false,
})

const emit = defineEmits<{
  (e: 'open-auth', mode: 'login' | 'register'): void
  (e: 'checkout'): void
}>()

const openLogin = () => emit('open-auth', 'login')
const openRegister = () => emit('open-auth', 'register')
const startCheckout = () => emit('checkout')
</script>

<template>
  <div class="rounded-xl border border-blue-100 bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-5">
    <div class="flex items-start justify-between gap-4">
      <div>
        <p class="text-xs font-semibold tracking-wide text-blue-600 uppercase">VidGrab AI VIP</p>
        <h4 class="text-lg font-semibold text-gray-900 mt-1">
          解锁视频总结、字幕整理、脑图导出和 AI 问答
        </h4>
        <p class="text-sm text-gray-600 mt-2 leading-6">
          会员价格固定为 19.9 CNY / 30 天。下载功能继续免费，只有 AI 学习助手需要会员。
        </p>
      </div>
      <span class="shrink-0 rounded-full bg-white px-3 py-1 text-xs font-medium text-blue-700 border border-blue-100">
        {{ authenticated && membership?.is_member ? '已开通' : '会员专享' }}
      </span>
    </div>

    <div class="mt-4 grid gap-2 text-sm text-gray-700 sm:grid-cols-2">
      <div class="rounded-lg bg-white/80 border border-white px-3 py-2">AI 视频总结摘要</div>
      <div class="rounded-lg bg-white/80 border border-white px-3 py-2">字幕导出（SRT / VTT / TXT）</div>
      <div class="rounded-lg bg-white/80 border border-white px-3 py-2">思维导图浏览与导出</div>
      <div class="rounded-lg bg-white/80 border border-white px-3 py-2">视频内容流式问答</div>
    </div>

    <div v-if="loading" class="mt-4 text-sm text-gray-500">
      正在加载会员状态...
    </div>

    <div v-else-if="authenticated && membership?.is_member" class="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
      当前会员有效，剩余 {{ membership.remaining_days }} 天。
      <span v-if="membership.expires_at">到期时间：{{ membership.expires_at }}</span>
    </div>

    <div v-else-if="authenticated" class="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
      当前账号未开通会员，购买后立即解锁所有 AI 学习能力。
    </div>

    <div class="mt-5 flex flex-wrap gap-3">
      <template v-if="!authenticated">
        <button
          class="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
          @click="openLogin"
        >
          登录后购买
        </button>
        <button
          class="px-4 py-2 rounded-lg border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          @click="openRegister"
        >
          注册账号
        </button>
      </template>

      <button
        v-else
        class="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        :disabled="checkoutLoading"
        @click="startCheckout"
      >
        {{ checkoutLoading ? '跳转支付中...' : membership?.is_member ? '续费会员' : '立即开通会员' }}
      </button>
    </div>
  </div>
</template>
