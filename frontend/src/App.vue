<script setup lang="ts">
import { onMounted, ref } from 'vue'

import AuthModal from './components/AuthModal.vue'
import DownloadForm from './components/DownloadForm.vue'
import UserMenu from './components/UserMenu.vue'
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

let noticeTimer: ReturnType<typeof setTimeout> | null = null

const setNotice = (message: string | null) => {
  if (noticeTimer) clearTimeout(noticeTimer)
  notice.value = message
  if (message) {
    noticeTimer = setTimeout(() => {
      notice.value = null
      noticeTimer = null
    }, 3000)
  }
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

  const verifyResult = params.get('verify')
  if (verifyResult === 'success') {
    setNotice('邮箱验证成功，请登录账号')
    replaceCurrentSearch({ verify: null })
  } else if (verifyResult === 'failed') {
    setNotice('验证链接已过期或无效，请重新注册')
    replaceCurrentSearch({ verify: null })
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
  <div id="app" class="app-shell flex flex-col min-h-screen">
    <!-- 顶部导航 -->
    <nav class="top-nav border-b border-white/40">
      <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <!-- 左侧 Logo 和品牌 -->
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-3">
            <!-- Logo: 蓝色圆形背景 + 白色播放图标 -->
            <div class="brand-logo w-9 h-9 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </div>
            <!-- 品牌名称 -->
            <span class="text-lg font-bold text-gray-900">VidGrab</span>
          </div>
          <!-- 标签 -->
          <span class="brand-pill px-2.5 py-1 text-xs font-medium rounded-md">
            万能视频下载
          </span>
        </div>

        <!-- 中间导航链接 -->
        <div class="flex items-center gap-8">
          <a href="#features" class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">功能特性</a>
          <a href="#pricing" class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">套餐价格</a>
          <a href="#platforms" class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">支持平台</a>
        </div>

        <!-- 右侧账号与会员入口 -->
        <div class="flex items-center gap-3">
          <template v-if="authenticated">
            <UserMenu
              :user="currentUser"
              :membership="membership"
              :checkout-loading="checkoutLoading"
              @start-checkout="handleStartCheckout"
              @logout="handleLogout"
            />
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
              class="vg-btn-soft flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm"
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

    <div v-if="notice" class="notice-bar border-b border-blue-100/70 bg-blue-50/80">
      <div class="max-w-6xl mx-auto px-6 py-3 text-sm text-blue-700">
        {{ notice }}
      </div>
    </div>

    <div v-if="mockCheckoutOrderId" class="mock-bar border-b border-amber-100/80 bg-amber-50/85">
      <div class="max-w-6xl mx-auto px-6 py-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-sm font-semibold text-amber-800">当前处于本地 mock 支付模式</p>
          <p class="text-sm text-amber-700 mt-1">
            订单 {{ mockCheckoutOrderId }} 已创建。你可以直接模拟成功或取消支付，不需要访问外网。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <button
            class="vg-btn-primary px-4 py-2 rounded-lg text-sm font-medium"
            :disabled="checkoutLoading"
            @click="handleMockCheckoutSuccess"
          >
            {{ checkoutLoading ? '处理中...' : '模拟支付成功' }}
          </button>
          <button
            class="vg-btn-ghost px-4 py-2 rounded-lg text-sm font-medium"
            @click="handleMockCheckoutCancel"
          >
            取消模拟支付
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容 -->
    <main class="main-stage relative flex-1">
      <DownloadForm
        :authenticated="authenticated"
        :membership="membership"
        :membership-loading="membershipLoading"
        :checkout-loading="checkoutLoading"
        @open-auth="openAuthModal"
        @start-checkout="handleStartCheckout"
      />
    </main>

    <!-- 功能特性区块 -->
    <section id="features" class="section-soft border-t border-white/60">
      <div class="max-w-4xl mx-auto px-6 py-14 md:py-16">
        <div class="text-center mb-10">
          <h2 class="section-title text-2xl font-bold text-gray-900">功能特性</h2>
          <p class="section-subtitle text-sm text-gray-500 mt-2">简单三步，完成下载与 AI 分析</p>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div class="feature-card rounded-2xl border border-gray-200 bg-white p-6">
            <div class="icon-tile icon-tile-blue w-10 h-10 rounded-xl flex items-center justify-center mb-4">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            </div>
            <h3 class="text-base font-semibold text-gray-900 mb-2">视频下载</h3>
            <p class="text-sm text-gray-600 leading-6">粘贴链接即可解析，支持 MP4 / MP3 / WebM 等格式，多清晰度自由选择，实时进度显示。</p>
          </div>
          <div class="feature-card rounded-2xl border border-gray-200 bg-white p-6">
            <div class="icon-tile icon-tile-purple w-10 h-10 rounded-xl flex items-center justify-center mb-4">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m1.636 6.364l.707-.707M12 21v-1m-6.364-1.636l.707-.707"/></svg>
            </div>
            <h3 class="text-base font-semibold text-gray-900 mb-2">AI 视频总结</h3>
            <p class="text-sm text-gray-600 leading-6">自动生成摘要、章节要点和思维导图，字幕支持 SRT / VTT / TXT 导出，AI 问答流式回答。</p>
          </div>
          <div class="feature-card rounded-2xl border border-gray-200 bg-white p-6">
            <div class="icon-tile icon-tile-emerald w-10 h-10 rounded-xl flex items-center justify-center mb-4">
              <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            </div>
            <h3 class="text-base font-semibold text-gray-900 mb-2">安全可靠</h3>
            <p class="text-sm text-gray-600 leading-6">文件下载后服务器立即清理，不留存任何用户数据，邮箱验证保障账号安全。</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 支持平台区块 -->
    <section id="platforms" class="section-plain border-t border-white/70">
      <div class="max-w-4xl mx-auto px-6 py-14 md:py-16">
        <div class="text-center mb-10">
          <h2 class="section-title text-2xl font-bold text-gray-900">支持平台</h2>
          <p class="section-subtitle text-sm text-gray-500 mt-2">基于 yt-dlp，支持全球 1000+ 视频网站</p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 sm:gap-4">
          <div v-for="platform in ['YouTube', 'Bilibili', 'TikTok', 'Instagram', 'Twitter / X', 'Facebook', 'Vimeo', '更多 1000+ 平台']" :key="platform"
            class="platform-chip rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm font-medium text-gray-700 text-center transition-colors">
            {{ platform }}
          </div>
        </div>
      </div>
    </section>

    <!-- 套餐价格区块 -->
    <section id="pricing" class="section-plain border-t border-white/70">
      <div class="max-w-4xl mx-auto px-6 py-14 md:py-16">
        <div class="text-center mb-10">
          <h2 class="section-title text-2xl font-bold text-gray-900">套餐价格</h2>
          <p class="pricing-subtitle text-sm text-gray-500 mt-2">下载功能永久免费，AI 学习助手开通 VIP 后无限使用</p>
        </div>

        <div class="pricing-grid grid md:grid-cols-2 gap-6">
          <!-- 免费版 -->
          <div class="plan-card plan-free rounded-2xl border border-gray-200 bg-gray-50 p-6 flex flex-col">
            <div class="mb-4">
              <span class="text-xs font-semibold tracking-wide text-gray-500 uppercase">免费版</span>
              <div class="mt-2 flex items-end gap-1">
                <span class="text-3xl font-bold text-gray-900">¥0</span>
                <span class="text-sm text-gray-500 mb-1">永久免费</span>
              </div>
              <p class="plan-hint mt-2 text-xs text-gray-500">适合轻量下载与日常临时使用</p>
            </div>
            <ul class="space-y-3 text-sm flex-1">
              <li class="flex items-center gap-2 text-gray-700">
                <svg class="w-4 h-4 text-emerald-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                视频下载（无限次）
              </li>
              <li class="flex items-center gap-2 text-gray-700">
                <svg class="w-4 h-4 text-emerald-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                支持 100+ 平台（YouTube / Bilibili / TikTok 等）
              </li>
              <li class="flex items-center gap-2 text-gray-700">
                <svg class="w-4 h-4 text-emerald-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                多格式 / 多清晰度选择
              </li>
              <li class="flex items-center gap-2 text-gray-400">
                <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                AI 视频总结（每日限 2 次）
              </li>
              <li class="flex items-center gap-2 text-gray-400">
                <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                字幕导出（SRT / VTT / TXT）
              </li>
              <li class="flex items-center gap-2 text-gray-400">
                <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                思维导图浏览与导出
              </li>
              <li class="flex items-center gap-2 text-gray-400">
                <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                AI 流式问答（无限次）
              </li>
            </ul>
            <div class="mt-6">
              <button
                class="plan-btn-secondary w-full rounded-lg border border-gray-300 bg-white py-2.5 text-sm font-medium text-gray-700 transition-colors"
                @click="openAuthModal('register')"
              >
                免费注册
              </button>
            </div>
          </div>

          <!-- VIP 版 -->
          <div class="plan-card plan-vip rounded-2xl border-2 border-blue-500 p-6 relative flex flex-col">
            <span class="plan-badge absolute z-10 -top-3 left-1/2 -translate-x-1/2 rounded-full px-4 py-1 text-xs font-semibold text-white">推荐</span>
            <div class="mb-4">
              <span class="text-xs font-semibold tracking-wide text-blue-600 uppercase">VIP 会员</span>
              <div class="plan-price-row mt-2 flex items-end gap-1">
                <span class="plan-price-main text-3xl font-bold text-gray-900">¥19.9</span>
                <span class="text-sm text-gray-500 mb-1">/ 30天</span>
              </div>
              <div class="value-chips mt-3">
                <span class="value-chip">不限 AI 总结</span>
                <span class="value-chip">字幕导出</span>
                <span class="value-chip">思维导图</span>
              </div>
            </div>
            <ul class="space-y-3 text-sm flex-1">
              <li class="flex items-center gap-2 text-gray-700">
                <svg class="w-4 h-4 text-blue-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                免费版全部功能
              </li>
              <li class="flex items-center gap-2 text-gray-700">
                <svg class="w-4 h-4 text-blue-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                AI 视频总结（无限次）
              </li>
              <li class="flex items-center gap-2 text-gray-700">
                <svg class="w-4 h-4 text-blue-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                字幕导出（SRT / VTT / TXT）
              </li>
              <li class="flex items-center gap-2 text-gray-700">
                <svg class="w-4 h-4 text-blue-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                思维导图浏览与高清导出（PNG / SVG）
              </li>
              <li class="flex items-center gap-2 text-gray-700">
                <svg class="w-4 h-4 text-blue-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                AI 流式问答（无限次）
              </li>
              <li class="flex items-center gap-2 text-gray-700">
                <svg class="w-4 h-4 text-blue-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                优先客服支持
              </li>
            </ul>
            <div class="mt-6">
              <button
                class="plan-btn-primary w-full rounded-lg py-2.5 text-sm font-medium text-white transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                :disabled="checkoutLoading"
                @click="handleStartCheckout"
              >
                {{ checkoutLoading ? '跳转支付中...' : authenticated ? (membership?.is_member ? '续费会员' : '立即开通') : '登录后开通' }}
              </button>
              <p class="plan-note mt-2 text-center text-xs text-blue-700/80">开通后立即解锁 AI 学习助手全部能力</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="section-plain border-t border-white/60">
      <div class="max-w-6xl mx-auto px-6 py-8">
        <div class="grid gap-4 md:grid-cols-3 mb-8">
          <section class="footer-card rounded-2xl border border-gray-100 bg-gray-50 p-5">
            <h2 class="footer-title text-base font-semibold text-gray-900 mb-2">视频下载与字幕整理</h2>
            <p class="footer-desc text-sm leading-6 text-gray-600">
              用 VidGrab 解析公开视频链接后，可以继续完成下载、字幕导出和音频保存，适合课程复盘与素材归档。
            </p>
          </section>
          <section class="footer-card rounded-2xl border border-gray-100 bg-gray-50 p-5">
            <h2 class="footer-title text-base font-semibold text-gray-900 mb-2">AI 视频总结</h2>
            <p class="footer-desc text-sm leading-6 text-gray-600">
              AI 学习助手会输出总览、章节要点、思维导图和流式问答，把长视频转换成更容易复盘的知识结构。
            </p>
          </section>
          <section class="footer-card rounded-2xl border border-gray-100 bg-gray-50 p-5">
            <h2 class="footer-title text-base font-semibold text-gray-900 mb-2">探索双语 SEO 与 GEO 页面</h2>
            <p class="footer-desc text-sm leading-6 text-gray-600">
              你也可以从平台页、功能页、答案中心和 FAQ 页面快速进入对应场景，查看更多关于 VidGrab 的能力说明。
            </p>
            <div class="mt-3 flex flex-wrap gap-3 text-sm">
              <a href="/zh/" class="footer-link text-blue-600 transition-colors">中文入口</a>
              <a href="/en/" class="footer-link text-blue-600 transition-colors">English Hub</a>
              <a href="/zh/answers/" class="footer-link text-blue-600 transition-colors">中文答案中心</a>
              <a href="/en/answers/" class="footer-link text-blue-600 transition-colors">English Answers</a>
              <a href="/zh/faq" class="footer-link text-blue-600 transition-colors">常见问题</a>
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
            <a href="#" class="footer-link hover:text-gray-900 transition-colors">用户协议</a>
            <a href="#" class="footer-link hover:text-gray-900 transition-colors">隐私政策</a>
            <a href="#" class="footer-link hover:text-gray-900 transition-colors">联系我们</a>
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

.app-shell {
  background: transparent;
}

.top-nav {
  position: sticky;
  top: 0;
  z-index: 30;
  backdrop-filter: saturate(140%) blur(12px);
  background: rgba(255, 255, 255, 0.72);
}

.brand-logo {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 65%, #1d4ed8 100%);
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.28);
}

.brand-pill {
  background: rgba(239, 246, 255, 0.86);
  color: #46607c;
  border: 1px solid rgba(147, 197, 253, 0.44);
}

.notice-bar,
.mock-bar {
  backdrop-filter: blur(8px);
}

.main-stage {
  background: transparent;
}

.section-soft {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.4), rgba(241, 245, 249, 0.62));
}

.section-plain {
  background: rgba(255, 255, 255, 0.72);
}

.feature-card,
.footer-card,
.plan-card,
.platform-chip {
  transition:
    border-color var(--vg-dur-mid) var(--vg-ease-standard),
    box-shadow var(--vg-dur-mid) var(--vg-ease-standard),
    transform var(--vg-dur-fast) var(--vg-ease-standard),
    background-color var(--vg-dur-mid) var(--vg-ease-standard);
}

.feature-card,
.footer-card {
  background: rgba(255, 255, 255, 0.78);
  border-color: rgba(148, 163, 184, 0.24);
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
  backdrop-filter: blur(8px);
}

.feature-card:hover,
.footer-card:hover {
  transform: translateY(-2px);
  border-color: rgba(96, 165, 250, 0.34);
  box-shadow: 0 18px 34px rgba(30, 64, 175, 0.1);
}

.icon-tile {
  border: 1px solid rgba(255, 255, 255, 0.66);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.64);
}

.icon-tile-blue {
  background: linear-gradient(145deg, rgba(219, 234, 254, 0.95), rgba(191, 219, 254, 0.7));
}

.icon-tile-purple {
  background: linear-gradient(145deg, rgba(233, 213, 255, 0.94), rgba(221, 214, 254, 0.68));
}

.icon-tile-emerald {
  background: linear-gradient(145deg, rgba(209, 250, 229, 0.95), rgba(167, 243, 208, 0.65));
}

.platform-chip {
  background: rgba(248, 250, 252, 0.8);
  border-color: rgba(148, 163, 184, 0.24);
}

.platform-chip:hover {
  background: rgba(239, 246, 255, 0.95);
  border-color: rgba(96, 165, 250, 0.45);
  transform: translateY(-1px);
}

.plan-card {
  backdrop-filter: blur(10px);
  height: 100%;
}

.plan-free {
  background: rgba(248, 250, 252, 0.78);
  border-color: rgba(148, 163, 184, 0.28);
  box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
}

.plan-vip {
  background:
    radial-gradient(680px 180px at 80% -30%, rgba(59, 130, 246, 0.14), transparent 65%),
    linear-gradient(155deg, rgba(239, 246, 255, 0.96), rgba(255, 255, 255, 0.92) 56%, rgba(238, 242, 255, 0.9));
  border-color: rgba(59, 130, 246, 0.6);
  box-shadow: 0 18px 36px rgba(37, 99, 235, 0.16);
}

.plan-vip::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 12%, rgba(255, 255, 255, 0.44) 42%, transparent 78%);
  opacity: 0.45;
  pointer-events: none;
}

.plan-vip:hover {
  transform: translateY(-2px);
  box-shadow: 0 24px 42px rgba(37, 99, 235, 0.2);
}

.plan-price-row {
  align-items: baseline;
}

.plan-price-main {
  letter-spacing: -0.02em;
  color: #0f172a;
}

.plan-badge {
  background: linear-gradient(135deg, #2563eb, #1e40af);
  box-shadow: 0 8px 18px rgba(37, 99, 235, 0.3);
}

.plan-btn-secondary {
  border-color: rgba(148, 163, 184, 0.46);
  background: rgba(255, 255, 255, 0.95);
  transition:
    background-color var(--vg-dur-mid) var(--vg-ease-standard),
    border-color var(--vg-dur-mid) var(--vg-ease-standard),
    transform var(--vg-dur-fast) var(--vg-ease-standard);
}

.plan-btn-secondary:hover {
  background: rgba(248, 250, 252, 0.95);
}

.plan-btn-secondary:active {
  transform: translateY(0);
}

.plan-btn-primary {
  background: linear-gradient(135deg, #2563eb, #1d4ed8 62%, #1e40af);
  box-shadow: 0 14px 24px rgba(37, 99, 235, 0.3);
  transition:
    transform var(--vg-dur-fast) var(--vg-ease-standard),
    filter var(--vg-dur-fast) var(--vg-ease-standard),
    box-shadow var(--vg-dur-mid) var(--vg-ease-standard);
}

.plan-btn-primary:hover {
  filter: brightness(1.03);
  transform: translateY(-1px);
}

.plan-btn-primary:active {
  transform: translateY(0);
}

.plan-note {
  font-weight: 500;
}

.plan-hint {
  line-height: 1.45;
}

.pricing-subtitle {
  color: #64748b;
  line-height: 1.5;
}

.value-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.value-chip {
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  color: #1d4ed8;
  background: rgba(219, 234, 254, 0.74);
  border: 1px solid rgba(147, 197, 253, 0.52);
}

.footer-title {
  color: #0f172a;
}

.footer-desc {
  color: #475569;
}

.footer-link:hover {
  color: #1d4ed8;
}

.section-title {
  letter-spacing: -0.01em;
}

.section-subtitle {
  color: #64748b;
  line-height: 1.5;
}

@media (min-width: 768px) {
  .pricing-grid {
    gap: 1.75rem;
  }
}

@media (max-width: 768px) {
  .top-nav .max-w-6xl {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .top-nav .flex.items-center.gap-8 {
    display: none;
  }

  .top-nav .brand-pill {
    display: none;
  }

  .section-title {
    font-size: 1.42rem;
  }
}
</style>
