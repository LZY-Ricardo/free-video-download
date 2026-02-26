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
  startDownload
} = useDownload()

const handleGetInfo = () => {
  getInfo()
}

const handleDownload = (options: any) => {
  startDownload(options)
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-12">
    <!-- 标题 -->
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold text-primary mb-4">
        🎬 万能视频下载器
      </h1>
      <p class="text-lg text-gray-600">
        一键下载各大平台视频，快速、免费、简单
      </p>
    </div>

    <!-- URL 输入 -->
    <div class="mb-6">
      <div class="relative">
        <input
          v-model="url"
          type="text"
          placeholder="粘贴视频链接 (支持 YouTube、Bilibili 等)"
          class="w-full px-6 py-4 pr-40 text-base rounded-lg border border-gray-300 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 transition-all"
          @keyup.enter="handleGetInfo"
        />
        <button
          @click="handleGetInfo"
          :disabled="loading || !url"
          class="absolute right-2 top-2 px-6 py-2 bg-accent text-white rounded-md hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ loading && status === 'fetching' ? '获取中...' : '获取信息' }}
        </button>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
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
    />

    <!-- 支持平台 -->
    <div class="mt-16 text-center">
      <h3 class="text-lg font-semibold text-gray-700 mb-6">支持平台</h3>
      <div class="flex flex-wrap justify-center gap-4">
        <div class="px-6 py-3 bg-gray-100 rounded-lg">
          <span class="font-medium">YouTube</span>
        </div>
        <div class="px-6 py-3 bg-gray-100 rounded-lg">
          <span class="font-medium">Bilibili</span>
        </div>
        <div class="px-6 py-3 bg-gray-100 rounded-lg">
          <span class="font-medium">TikTok</span>
        </div>
        <div class="px-6 py-3 bg-gray-100 rounded-lg">
          <span class="font-medium">Instagram</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
input {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
