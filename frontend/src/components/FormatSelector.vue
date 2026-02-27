<script setup lang="ts">
import type { Format } from '@/types'
import { ref } from 'vue'

defineProps<{
  formats: Format[]
}>()

const emit = defineEmits<{
  download: [options: { format: string; quality: string }]
}>()

const selectedFormat = ref('mp4')
const selectedQuality = ref('1080p')

const formatOptions = [
  { value: 'mp4', label: 'MP4', desc: '视频+音频' },
  { value: 'mp3', label: 'MP3', desc: '仅音频' },
  { value: 'webm', label: 'WebM', desc: '高清视频' }
]

const qualities = ['4K', '2K', '1080p', '720p', '480p', '360p']

const handleDownload = () => {
  emit('download', {
    format: selectedFormat.value,
    quality: selectedQuality.value
  })
}
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
    <h3 class="text-base font-semibold text-gray-900 mb-5">选择下载格式</h3>

    <!-- 格式选择 -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-3">文件格式</label>
      <div class="grid grid-cols-3 gap-3">
        <button
          v-for="option in formatOptions"
          :key="option.value"
          @click="selectedFormat = option.value"
          :class="[
            'p-4 rounded-lg border-2 text-left transition-all',
            selectedFormat === option.value
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          ]"
        >
          <div class="text-base font-semibold" :class="selectedFormat === option.value ? 'text-blue-700' : 'text-gray-700'">
            {{ option.label }}
          </div>
          <div class="text-xs text-gray-500 mt-1">{{ option.desc }}</div>
        </button>
      </div>
    </div>

    <!-- 质量选择（仅视频格式） -->
    <div v-if="selectedFormat !== 'mp3'" class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-3">视频质量</label>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="quality in qualities"
          :key="quality"
          @click="selectedQuality = quality"
          :class="[
            'px-4 py-2 rounded-lg border-2 transition-all text-sm font-medium',
            selectedQuality === quality
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
          ]"
        >
          {{ quality }}
        </button>
      </div>
    </div>

    <!-- 下载按钮 -->
    <button
      @click="handleDownload"
      class="w-full py-3.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
      </svg>
      开始下载
    </button>
  </div>
</template>
