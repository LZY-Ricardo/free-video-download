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
  { value: 'mp4', label: 'MP4 (视频+音频)' },
  { value: 'mp3', label: 'MP3 (仅音频)' },
  { value: 'webm', label: 'WebM (视频)' }
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
  <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6 shadow-sm">
    <h3 class="text-lg font-semibold text-primary mb-4">选择下载格式</h3>

    <!-- 格式选择 -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-3">文件格式</label>
      <div class="flex flex-wrap gap-3">
        <button
          v-for="option in formatOptions"
          :key="option.value"
          @click="selectedFormat = option.value"
          :class="[
            'px-6 py-3 rounded-lg border-2 transition-all',
            selectedFormat === option.value
              ? 'border-accent bg-blue-50 text-accent'
              : 'border-gray-300 text-gray-700 hover:border-gray-400'
          ]"
        >
          {{ option.label }}
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
            'px-4 py-2 rounded-lg border-2 transition-all',
            selectedQuality === quality
              ? 'border-accent bg-blue-50 text-accent'
              : 'border-gray-300 text-gray-700 hover:border-gray-400'
          ]"
        >
          {{ quality }}
        </button>
      </div>
    </div>

    <!-- 下载按钮 -->
    <button
      @click="handleDownload"
      class="w-full py-4 bg-accent text-white text-lg font-semibold rounded-lg hover:bg-accent-hover transition-colors flex items-center justify-center gap-2"
    >
      <span>🎥</span>
      <span>开始下载</span>
    </button>
  </div>
</template>
