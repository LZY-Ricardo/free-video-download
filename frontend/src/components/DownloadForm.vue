<script setup lang="ts">
import { useDownload } from '@/composables/useDownload'
import VideoInfo from './VideoInfo.vue'
import FormatSelector from './FormatSelector.vue'
import ProgressBar from './ProgressBar.vue'

const {
  url,
  videoInfo,
  status,
  progress,
  speed,
  error,
  loading,
  getInfo,
  startDownload,
  downloadFile
} = useDownload()

const handleGetInfo = () => {
  getInfo()
}

const handleDownload = (options: any) => {
  startDownload(options)
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-16">
    <!-- Hero Section -->
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold text-gray-900 mb-3">
        万能视频下载器
      </h1>
      <p class="text-gray-500">
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
            class="w-full px-5 py-4 border border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all text-gray-900"
            @keyup.enter="handleGetInfo"
          />
        </div>
        <button
          @click="handleGetInfo"
          :disabled="loading || !url"
          class="px-8 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
        >
          {{ loading && status === 'fetching' ? '获取中' : '获取视频' }}
        </button>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mt-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
        {{ error }}
      </div>
    </div>

    <!-- 视频信息 -->
    <VideoInfo v-if="videoInfo && status === 'ready'" :info="videoInfo" />

    <!-- 格式选择器 -->
    <FormatSelector
      v-if="videoInfo && status === 'ready'"
      :formats="videoInfo.formats"
      @download="handleDownload"
    />

    <!-- 进度条 -->
    <ProgressBar
      v-if="status === 'downloading' || status === 'completed'"
      :progress="progress"
      :speed="speed"
      :status="status"
      @download-file="downloadFile"
    />

    <!-- 支持平台 -->
    <div class="mt-20 text-center">
      <h3 class="text-sm font-medium text-gray-500 mb-6 uppercase tracking-wide">支持平台</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="px-6 py-4 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <span class="font-medium text-gray-700">YouTube</span>
        </div>
        <div class="px-6 py-4 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <span class="font-medium text-gray-700">Bilibili</span>
        </div>
        <div class="px-6 py-4 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <span class="font-medium text-gray-700">TikTok</span>
        </div>
        <div class="px-6 py-4 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
          <span class="font-medium text-gray-700">Instagram</span>
        </div>
      </div>
      <p class="text-sm text-gray-400 mt-6">以及 100+ 其他视频平台</p>
    </div>
  </div>
</template>

<style scoped>
input::placeholder {
  color: #9ca3af;
}
</style>
