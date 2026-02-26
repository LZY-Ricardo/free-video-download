<script setup lang="ts">
import type { VideoInfo } from '@/types'

defineProps<{
  info: VideoInfo
}>()

const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  }
  return num.toString()
}
</script>

<template>
  <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6 shadow-sm">
    <div class="flex gap-6">
      <!-- 缩略图 -->
      <div class="flex-shrink-0">
        <img
          v-if="info.thumbnail"
          :src="info.thumbnail"
          :alt="info.title"
          class="w-48 h-32 object-cover rounded-lg"
        />
        <div v-else class="w-48 h-32 bg-gray-200 rounded-lg flex items-center justify-center">
          <span class="text-gray-400">无缩略图</span>
        </div>
      </div>

      <!-- 视频信息 -->
      <div class="flex-1">
        <h3 class="text-xl font-semibold text-primary mb-2 line-clamp-2">
          {{ info.title }}
        </h3>

        <div class="flex flex-wrap gap-4 text-sm text-gray-600">
          <span v-if="info.duration" class="flex items-center gap-1">
            ⏱️ {{ formatDuration(info.duration) }}
          </span>
          <span v-if="info.uploader" class="flex items-center gap-1">
            👤 {{ info.uploader }}
          </span>
          <span v-if="info.view_count" class="flex items-center gap-1">
            👁️ {{ formatNumber(info.view_count) }} 次观看
          </span>
        </div>

        <div class="mt-3">
          <span class="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
            {{ info.platform }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
