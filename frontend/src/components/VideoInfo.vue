<script setup lang="ts">
import { computed } from 'vue'

import type { VideoInfo } from '@/types'

const props = withDefaults(defineProps<{
  info: VideoInfo
  compact?: boolean
}>(), {
  compact: false,
})

// 获取有效的缩略图 URL（通过代理）
const getThumbnailUrl = (thumbnail: string | null | undefined, platform: string) => {
  if (!thumbnail) {
    return null
  }

  // 检查是否是透明图片
  if (thumbnail.includes('transparent.png') || thumbnail.includes('archive/transparent')) {
    return null
  }

  // 使用后端图片代理
  const encodedUrl = encodeURIComponent(thumbnail)
  return `/api/proxy/image?url=${encodedUrl}&platform=${platform}`
}

// 获取平台图标
const getPlatformIcon = (platform: string) => {
  const icons: Record<string, string> = {
    'bilibili': '📺',
    'youtube': '▶️',
    'tiktok': '🎵',
    'instagram': '📸',
  }
  return icons[platform] || '🎬'
}

// 获取平台颜色
const getPlatformColor = (platform: string) => {
  const colors: Record<string, string> = {
    'bilibili': 'bg-pink-100 text-pink-700',
    'youtube': 'bg-red-100 text-red-700',
    'tiktok': 'bg-gray-100 text-gray-700',
    'instagram': 'bg-purple-100 text-purple-700',
  }
  return colors[platform] || 'bg-blue-100 text-blue-700'
}

const thumbnailProxyUrl = computed(() => getThumbnailUrl(props.info.thumbnail, props.info.platform))

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
  <div :class="compact ? 'bg-white border border-gray-200 rounded-xl p-4' : 'bg-white border border-gray-200 rounded-xl p-6 mb-6'">
    <div :class="compact ? 'flex flex-col gap-3' : 'flex flex-col md:flex-row gap-5'">
      <!-- 缩略图 -->
      <div :class="compact ? 'shrink-0' : 'shrink-0 mx-auto md:mx-0'">
        <div v-if="thumbnailProxyUrl" :class="compact ? 'w-full overflow-hidden rounded-lg' : 'w-full md:w-64 overflow-hidden rounded-lg'">
          <img
            :src="thumbnailProxyUrl"
            :alt="info.title"
            class="w-full aspect-video object-cover"
          />
        </div>
        <div
          v-else
          :class="[
            'aspect-video rounded-lg flex flex-col items-center justify-center',
            compact ? 'w-full' : 'w-full md:w-64',
            getPlatformColor(info.platform)
          ]"
        >
          <span class="text-4xl mb-1">{{ getPlatformIcon(info.platform) }}</span>
          <span class="text-xs font-medium capitalize">{{ info.platform }}</span>
        </div>
      </div>

      <!-- 视频信息 -->
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-2 mb-2">
          <h3 :class="compact ? 'text-sm font-semibold text-gray-900 line-clamp-2 flex-1' : 'text-lg font-semibold text-gray-900 line-clamp-2 flex-1'">
            {{ info.title }}
          </h3>
          <!-- 平台标签 -->
          <span
            class="shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium capitalize"
            :class="getPlatformColor(info.platform)"
          >
            <span>{{ getPlatformIcon(info.platform) }}</span>
            {{ info.platform }}
          </span>
        </div>

        <p v-if="info.uploader" :class="['text-gray-500 flex items-center gap-1.5', compact ? 'text-xs mb-2' : 'text-sm mb-3']">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
          {{ info.uploader }}
        </p>

        <!-- 视频统计 -->
        <div :class="['flex flex-wrap gap-4 text-gray-500', compact ? 'text-xs' : 'text-sm']">
          <span v-if="info.duration" class="flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            {{ formatDuration(info.duration) }}
          </span>
          <span v-if="info.view_count" class="flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
            {{ formatNumber(info.view_count) }} 次观看
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
