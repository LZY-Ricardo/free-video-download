<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import AuthModal from './components/AuthModal.vue'
import DownloadForm from './components/DownloadForm.vue'
import { useAuth } from './composables/useAuth'
import { useMembership } from './composables/useMembership'

const authModalOpen = ref(false)
const authModalMode = ref<'login' | 'register'>('login')
const notice = ref<string | null>(null)
const mockCheckoutOrderId = ref<string | null>(null)

const {
  authenticated,
  currentUser,
  loading: authLoading,
  logout,
  fetchCurrentUser,
} = useAuth()

const {
  membership,
  loading: membershipLoading,
  checkoutLoading,
  fetchMembership,
  clearMembership,
  createCheckoutSession,
  completeMockCheckout,
  error: membershipError,
} = useMembership()

const memberSummary = computed(() => {
  if (!membership.value?.is_member) {
    return '未开通会员'
  }
  return `会员剩余 ${membership.value.remaining_days} 天`
})

const currentEmailLabel = computed(() => currentUser.value?.email || '未登录')

const setNotice = (message: string | null) => {
  notice.value = message
}

const replaceCurrentSearch = (entries: Record<string, string | null>) => {
  const url = new URL(window.location.href)
  Object.entries(entries).forEach(([key, value]) => {
    if (value === null) {
      url.searchParams.delete(key)
    } else {
      url.searchParams.set(key, value)
    }
  })
  const search = url.searchParams.toString()
  const nextUrl = `${url.pathname}${search ? `?${search}` : ''}${url.hash}`
  window.history.replaceState({}, '', nextUrl)
}

const refreshSession = async () => {
  await fetchCurrentUser()
  if (authenticated.value) {
    await fetchMembership()
  } else {
    clearMembership()
  }
}

const pollMembershipAfterBilling = async () => {
  for (let index = 0; index < 3; index += 1) {
    await fetchMembership()
    if (membership.value?.is_member) {
      return
    }
    await new Promise((resolve) => window.setTimeout(resolve, 1000))
  }
}

const syncUrlState = async () => {
  const params = new URLSearchParams(window.location.search)
  const mockOrderId = params.get('mock_checkout_order_id')
  const billingResult = params.get('billing')

  if (mockOrderId) {
    mockCheckoutOrderId.value = mockOrderId
  }

  if (billingResult === 'success') {
    setNotice('支付已提交，正在同步会员状态...')
    await pollMembershipAfterBilling()
    replaceCurrentSearch({
      billing: null,
      session_id: null,
    })
    if (membership.value?.is_member) {
      setNotice('会员已开通，AI 学习助手已解锁')
    }
  } else if (billingResult === 'cancel') {
    setNotice('已取消支付')
    replaceCurrentSearch({
      billing: null,
      session_id: null,
    })
  }
}

const openAuthModal = (mode: 'login' | 'register') => {
  authModalMode.value = mode
  authModalOpen.value = true
}

const closeAuthModal = () => {
  authModalOpen.value = false
}

const handleLoginSuccess = async () => {
  await refreshSession()
  closeAuthModal()
  setNotice('登录成功')
}

const handleLogout = async () => {
  try {
    await logout()
    clearMembership()
    setNotice('已退出登录')
  } catch {
    setNotice('退出登录失败，请稍后重试')
  }
}

const handleStartCheckout = async () => {
  if (!authenticated.value) {
    openAuthModal('login')
    return
  }

  try {
    const session = await createCheckoutSession()
    window.location.href = session.checkout_url
  } catch {
    setNotice(membershipError.value || '创建支付会话失败')
  }
}

const handleMockCheckoutSuccess = async () => {
  if (!mockCheckoutOrderId.value) {
    return
  }

  try {
    await completeMockCheckout(mockCheckoutOrderId.value)
    await fetchMembership()
    mockCheckoutOrderId.value = null
    replaceCurrentSearch({
      mock_checkout_order_id: null,
    })
    setNotice('模拟支付成功，会员已开通')
  } catch {
    setNotice(membershipError.value || '模拟支付失败')
  }
}

const handleMockCheckoutCancel = () => {
  mockCheckoutOrderId.value = null
  replaceCurrentSearch({
    mock_checkout_order_id: null,
  })
  setNotice('已取消模拟支付')
}

onMounted(async () => {
  await refreshSession()
  await syncUrlState()
})
</script>

<template>
  <div id="app" class="flex flex-col min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <nav class="bg-white border-b border-gray-100">
      <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <!-- 左侧 Logo 和品牌 -->
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-3">
            <!-- Logo: 蓝色圆形背景 + 白色播放图标 -->
            <div class="w-9 h-9 rounded-full flex items-center justify-center" style="background-color: #3B82F6;">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </div>
            <!-- 品牌名称 -->
            <span class="text-lg font-bold text-gray-900">VidGrab</span>
          </div>
          <!-- 标签 -->
          <span class="px-2.5 py-1 text-xs font-medium rounded-md" style="background-color: #F3F4F6; color: #6B7280;">
            万能视频下载
          </span>
        </div>

        <!-- 中间导航链接 -->
        <div class="flex items-center gap-8">
          <a href="#" class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">功能特性</a>
          <a href="#" class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">套餐价格</a>
          <a href="#" class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">支持平台</a>
        </div>

        <!-- 右侧账号与会员入口 -->
        <div class="flex items-center gap-3">
          <template v-if="authenticated">
            <div class="hidden md:flex flex-col items-end">
              <span class="text-xs text-gray-500">{{ currentEmailLabel }}</span>
              <span class="text-xs font-medium" :class="membership?.is_member ? 'text-emerald-600' : 'text-amber-600'">
                {{ memberSummary }}
              </span>
            </div>
            <button
              class="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors hover:opacity-80 disabled:opacity-60 disabled:cursor-not-allowed"
              style="background-color: #EFF6FF; color: #1D4ED8;"
              :disabled="checkoutLoading"
              @click="handleStartCheckout"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              {{ checkoutLoading ? '处理中...' : membership?.is_member ? '续费 VIP' : '开通 VIP' }}
            </button>
            <button
              class="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors"
              @click="handleLogout"
            >
              退出
            </button>
          </template>
          <template v-else>
            <button
              class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              :disabled="authLoading"
              @click="openAuthModal('login')"
            >
              登录
            </button>
            <button
              class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              :disabled="authLoading"
              @click="openAuthModal('register')"
            >
              注册
            </button>
            <button
              class="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors hover:opacity-80"
              style="background-color: #EFF6FF; color: #1D4ED8;"
              @click="openAuthModal('login')"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              开通 VIP
            </button>
          </template>
        </div>
      </div>
    </nav>

    <div v-if="notice" class="border-b border-blue-100 bg-blue-50">
      <div class="max-w-6xl mx-auto px-6 py-3 text-sm text-blue-700">
        {{ notice }}
      </div>
    </div>

    <div v-if="mockCheckoutOrderId" class="border-b border-amber-100 bg-amber-50">
      <div class="max-w-6xl mx-auto px-6 py-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-sm font-semibold text-amber-800">当前处于本地 mock 支付模式</p>
          <p class="text-sm text-amber-700 mt-1">
            订单 {{ mockCheckoutOrderId }} 已创建。你可以直接模拟成功或取消支付，不需要访问外网。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <button
            class="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            :disabled="checkoutLoading"
            @click="handleMockCheckoutSuccess"
          >
            {{ checkoutLoading ? '处理中...' : '模拟支付成功' }}
          </button>
          <button
            class="px-4 py-2 rounded-lg border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
            @click="handleMockCheckoutCancel"
          >
            取消模拟支付
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容 -->
    <main class="relative flex-1">
      <DownloadForm
        :authenticated="authenticated"
        :membership="membership"
        :membership-loading="membershipLoading"
        :checkout-loading="checkoutLoading"
        @open-auth="openAuthModal"
        @start-checkout="handleStartCheckout"
      />
    </main>

    <!-- 底部 -->
    <footer class="bg-white border-t border-gray-100">
      <div class="max-w-6xl mx-auto px-6 py-8">
        <div class="grid gap-4 md:grid-cols-3 mb-8">
          <section class="rounded-2xl border border-gray-100 bg-gray-50 p-5">
            <h2 class="text-base font-semibold text-gray-900 mb-2">视频下载与字幕整理</h2>
            <p class="text-sm leading-6 text-gray-600">
              用 VidGrab 解析公开视频链接后，可以继续完成下载、字幕导出和音频保存，适合课程复盘与素材归档。
            </p>
          </section>
          <section class="rounded-2xl border border-gray-100 bg-gray-50 p-5">
            <h2 class="text-base font-semibold text-gray-900 mb-2">AI 视频总结</h2>
            <p class="text-sm leading-6 text-gray-600">
              AI 学习助手会输出总览、章节要点、思维导图和流式问答，把长视频转换成更容易复盘的知识结构。
            </p>
          </section>
          <section class="rounded-2xl border border-gray-100 bg-gray-50 p-5">
            <h2 class="text-base font-semibold text-gray-900 mb-2">探索双语 SEO 与 GEO 页面</h2>
            <p class="text-sm leading-6 text-gray-600">
              你也可以从平台页、功能页、答案中心和 FAQ 页面快速进入对应场景，查看更多关于 VidGrab 的能力说明。
            </p>
            <div class="mt-3 flex flex-wrap gap-3 text-sm">
              <a href="/zh/" class="text-blue-600 hover:text-blue-700 transition-colors">中文入口</a>
              <a href="/en/" class="text-blue-600 hover:text-blue-700 transition-colors">English Hub</a>
              <a href="/zh/answers/" class="text-blue-600 hover:text-blue-700 transition-colors">中文答案中心</a>
              <a href="/en/answers/" class="text-blue-600 hover:text-blue-700 transition-colors">English Answers</a>
              <a href="/zh/faq" class="text-blue-600 hover:text-blue-700 transition-colors">常见问题</a>
            </div>
          </section>
        </div>
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <!-- 版权信息 -->
          <div class="text-sm text-gray-500">
            © 2026 VidGrab. 仅供学习使用，请遵守相关法律法规
          </div>
          <!-- 右侧链接 -->
          <div class="flex items-center gap-6 text-sm text-gray-500">
            <a href="#" class="hover:text-gray-900 transition-colors">用户协议</a>
            <a href="#" class="hover:text-gray-900 transition-colors">隐私政策</a>
            <a href="#" class="hover:text-gray-900 transition-colors">联系我们</a>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-50 text-center text-xs text-gray-400">
          基于 yt-dlp 开源项目构建
        </div>
      </div>
    </footer>

    <AuthModal
      :open="authModalOpen"
      :mode="authModalMode"
      @close="closeAuthModal"
      @login-success="handleLoginSuccess"
    />
  </div>
</template>

<style scoped>
nav a {
  text-decoration: none;
}
</style>
