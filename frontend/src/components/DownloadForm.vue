<script setup lang="ts">
import { ref, watch } from 'vue'
import { useDownload } from '@/composables/useDownload'
import VideoInfo from './VideoInfo.vue'
import FormatSelector from './FormatSelector.vue'
import ProgressBar from './ProgressBar.vue'
import AIAssistant from './AIAssistant.vue'
import type { MembershipStatusResponse } from '@/types'

defineProps<{
  authenticated: boolean
  membership: MembershipStatusResponse | null
  membershipLoading: boolean
  checkoutLoading: boolean
  paymentOpen: boolean
}>()

defineEmits<{
  (e: 'open-auth', mode: 'login' | 'register'): void
  (e: 'start-checkout'): void
}>()

const {
  url,
  videoInfo,
  status,
  progress,
  speed,
  error,
  loading,
  extractedUrl,
  getInfo,
  startDownload,
  downloadFile
} = useDownload()

// AI 自动分析触发计数器：每次成功获取视频信息后递增
const analyzeTrigger = ref(0)

// 是否已进入双栏模式（视频信息已加载）
const hasVideoInfo = ref(false)

const handleGetInfo = () => {
  getInfo()
}

// 监听 videoInfo：成功获取后进入双栏模式 + 自动触发 AI 分析
watch(
  () => videoInfo.value,
  (newInfo) => {
    if (newInfo && status.value === 'ready') {
      hasVideoInfo.value = true
      analyzeTrigger.value++
    }
  },
)

const handleDownload = (options: any) => {
  startDownload(options)
}
</script>

<template>
  <div class="download-shell max-w-7xl mx-auto px-4 sm:px-6" :class="hasVideoInfo ? 'py-3 sm:py-4' : 'py-7 sm:py-10'">
    <!-- Hero Section：compact 模式下收起标题，只保留输入框 -->
    <div :class="hasVideoInfo ? 'max-w-7xl mx-auto' : 'max-w-3xl mx-auto'">
      <!-- 大标题：compact 模式隐藏 -->
      <div v-if="!hasVideoInfo" class="text-center mb-7 sm:mb-8">
        <h1 class="text-2xl sm:text-4xl font-bold text-gray-900 mb-2">
          万能视频下载器
        </h1>
        <p class="text-gray-500 text-xs sm:text-base">
          支持 YouTube、Bilibili、TikTok 等 100+ 平台
        </p>
      </div>

      <!-- URL 输入 -->
      <div :class="hasVideoInfo ? 'mb-3' : 'mb-6'">
        <div class="hero-input-wrap flex flex-col sm:flex-row gap-2">
          <div class="flex-1 relative">
            <input
              v-model="url"
              type="text"
              placeholder="粘贴视频链接..."
              :class="[
                'vg-input w-full rounded-lg focus:outline-none',
                hasVideoInfo ? 'px-4 py-2 text-sm' : 'px-5 py-3.5',
              ]"
              @keyup.enter="handleGetInfo"
            />
          </div>
          <button
            @click="handleGetInfo"
            :disabled="loading || !url"
            :class="[
              'vg-btn-primary w-full sm:w-auto font-medium rounded-lg whitespace-nowrap',
              hasVideoInfo ? 'px-4 py-2 text-sm' : 'px-6 sm:px-8',
            ]"
          >
            {{ loading && status === 'fetching' ? '解析中...' : '解析视频' }}
          </button>
        </div>
        <p v-if="!hasVideoInfo" class="hero-helper mt-2 text-xs text-slate-500">
          支持公开可访问视频链接，解析与下载完成后服务器自动清理临时文件
        </p>

        <!-- 错误提示 -->
        <div v-if="error" class="vg-alert vg-alert-error mt-2 p-2.5 text-sm whitespace-pre-line">
          {{ error }}
        </div>

        <!-- URL提取提示 -->
        <div v-if="extractedUrl" class="vg-alert vg-alert-success mt-2 p-2.5 text-sm flex items-center gap-2">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <span class="flex-1 truncate">已自动提取链接：{{ extractedUrl }}</span>
        </div>
      </div>
    </div>

    <!-- ========== 双栏内容区：解析成功后展示 ========== -->
    <div v-if="hasVideoInfo && videoInfo" class="grid grid-cols-1 lg:grid-cols-[2fr_3fr] gap-4">

      <!-- ===== 左栏：视频信息 + 下载 ===== -->
      <div class="flex flex-col gap-3">
        <!-- 视频信息 -->
        <VideoInfo v-if="status === 'ready'" :info="videoInfo" compact />

        <!-- 特殊提示信息（如抖音提示） -->
        <div v-if="status === 'ready' && videoInfo.error" class="p-4 bg-blue-50 border border-blue-200 rounded-xl">
          <div class="flex items-start gap-2.5">
            <svg class="w-5 h-5 text-blue-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div class="flex-1">
              <h4 class="text-sm font-semibold text-blue-900 mb-1">平台提示</h4>
              <p class="text-sm text-blue-700 whitespace-pre-line">{{ videoInfo.error }}</p>
            </div>
          </div>
        </div>

        <!-- 格式选择器 -->
        <FormatSelector
          v-if="status === 'ready' && !videoInfo.error"
          :formats="videoInfo.formats"
          compact
          @download="handleDownload"
        />

        <!-- 进度条 -->
        <ProgressBar
          v-if="status === 'downloading' || status === 'completed'"
          :progress="progress"
          :speed="speed"
          :status="status"
          compact
          @download-file="downloadFile"
        />
      </div>

        <!-- ===== 右栏：AI 学习助手 ===== -->
        <div class="min-w-0 self-start">
          <AIAssistant
            :url="url"
            :analyze-trigger="analyzeTrigger"
            :authenticated="authenticated"
            :membership="membership"
            :membership-loading="membershipLoading"
            :checkout-loading="checkoutLoading"
            :payment-open="paymentOpen"
            @open-auth="$emit('open-auth', $event)"
            @start-checkout="$emit('start-checkout')"
          />
        </div>
      </div>

    <!-- ========== 底部平台展示：compact 模式隐藏 ========== -->
    <div v-if="!hasVideoInfo" class="mt-12 sm:mt-16 text-center max-w-3xl mx-auto">
      <h3 class="text-sm font-medium text-gray-500 mb-5 uppercase tracking-wide">支持平台</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="platform-mini-card vg-card-soft px-5 py-3 rounded-lg">
          <span class="font-medium text-gray-700">YouTube</span>
        </div>
        <div class="platform-mini-card vg-card-soft px-5 py-3 rounded-lg">
          <span class="font-medium text-gray-700">Bilibili</span>
        </div>
        <div class="platform-mini-card vg-card-soft px-5 py-3 rounded-lg">
          <span class="font-medium text-gray-700">TikTok</span>
        </div>
        <div class="platform-mini-card vg-card-soft px-5 py-3 rounded-lg">
          <span class="font-medium text-gray-700">Instagram</span>
        </div>
      </div>
      <p class="text-sm text-gray-400 mt-4">以及 100+ 其他视频平台</p>
    </div>
  </div>
</template>

<style scoped>
input::placeholder {
  color: #9ca3af;
}

.download-shell {
  position: relative;
}

.hero-helper {
  line-height: 1.5;
  padding-left: 0.25rem;
}

.hero-input-wrap {
  padding: 0.36rem;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
  backdrop-filter: saturate(145%) blur(10px);
  transition:
    box-shadow var(--vg-dur-mid) var(--vg-ease-standard),
    border-color var(--vg-dur-mid) var(--vg-ease-standard),
    background-color var(--vg-dur-mid) var(--vg-ease-standard);
}

@media (max-width: 640px) {
  .hero-input-wrap {
    padding: 0.44rem;
    border-radius: 13px;
  }

  .platform-mini-card {
    padding: 0.65rem 0.75rem;
  }

  .hero-helper {
    font-size: 0.72rem;
    padding-left: 0.1rem;
    padding-right: 0.1rem;
  }
}

.platform-mini-card {
  transition:
    border-color var(--vg-dur-mid) var(--vg-ease-standard),
    box-shadow var(--vg-dur-mid) var(--vg-ease-standard),
    transform var(--vg-dur-fast) var(--vg-ease-standard);
}

.platform-mini-card:hover {
  border-color: rgba(96, 165, 250, 0.44);
  box-shadow: 0 10px 22px rgba(30, 64, 175, 0.1);
  transform: translateY(-1px);
}
</style>
