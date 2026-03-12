<script setup lang="ts">
import { ref, watch } from 'vue'
import { useDownload } from '@/composables/useDownload'
import VideoInfo from './VideoInfo.vue'
import FormatSelector from './FormatSelector.vue'
import ProgressBar from './ProgressBar.vue'
import AIAssistant from './AIAssistant.vue'

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
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-10">
    <!-- Hero Section：始终居中窄版 -->
    <div class="max-w-3xl mx-auto">
      <div class="text-center mb-8">
        <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
          万能视频下载器
        </h1>
        <p class="text-gray-500 text-sm sm:text-base">
          支持 YouTube、Bilibili、TikTok 等 100+ 平台
        </p>
      </div>

      <!-- URL 输入 -->
      <div class="mb-6">
        <div class="flex gap-3">
          <div class="flex-1 relative">
            <input
              v-model="url"
              type="text"
              placeholder="粘贴视频链接..."
              class="w-full px-5 py-3.5 border border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all text-gray-900"
              @keyup.enter="handleGetInfo"
            />
          </div>
          <button
            @click="handleGetInfo"
            :disabled="loading || !url"
            class="px-6 sm:px-8 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
          >
            {{ loading && status === 'fetching' ? '解析中...' : '解析视频' }}
          </button>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {{ error }}
        </div>

        <!-- URL提取提示 -->
        <div v-if="extractedUrl" class="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <span class="flex-1">已自动提取链接：{{ extractedUrl }}</span>
        </div>
      </div>
    </div>

    <!-- ========== 双栏内容区：解析成功后展示 ========== -->
    <div v-if="hasVideoInfo && videoInfo" class="grid grid-cols-1 lg:grid-cols-[2fr_3fr] gap-5 mt-2 items-start">

      <!-- ===== 左栏：视频信息 + 下载 ===== -->
      <div class="space-y-4 lg:row-span-1">
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

      <!-- ===== 右栏：AI 学习助手（固定最大高度 = 左栏高度，内容滚动） ===== -->
      <div class="min-w-0 lg:max-h-[calc(100vh-12rem)] lg:overflow-hidden">
        <AIAssistant :url="url" :analyze-trigger="analyzeTrigger" />
      </div>
    </div>

    <!-- ========== 底部平台展示 ========== -->
    <div class="mt-16 text-center" :class="{ 'max-w-3xl mx-auto': !hasVideoInfo }">
      <h3 class="text-sm font-medium text-gray-500 mb-5 uppercase tracking-wide">支持平台</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="px-5 py-3 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <span class="font-medium text-gray-700">YouTube</span>
        </div>
        <div class="px-5 py-3 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <span class="font-medium text-gray-700">Bilibili</span>
        </div>
        <div class="px-5 py-3 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <span class="font-medium text-gray-700">TikTok</span>
        </div>
        <div class="px-5 py-3 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
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
</style>
