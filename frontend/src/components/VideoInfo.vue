<script setup lang="ts">
import type { VideoInfo } from '@/types'

defineProps<{
  info: VideoInfo
}>()

// 获取有效的缩略图 URL
const getThumbnailUrl = (thumbnail: string | null, platform: string) => {
  // 调试日志
  console.log('Thumbnail check:', { thumbnail, platform })

  // 如果没有缩略图
  if (!thumbnail) {
    console.log('No thumbnail provided')
    return null
  }

  // 检查是否是透明图片
  if (thumbnail.includes('transparent.png') || thumbnail.includes('archive/transparent')) {
    console.log('Using placeholder for transparent image:', platform)
    return null
  }

  // 对于 Bilibili，由于防盗链，使用占位符
  if (platform === 'bilibili') {
    console.log('Using placeholder for bilibili (due to anti-hotlinking)')
    return null
  }

  console.log('Using real thumbnail')
  return thumbnail
}

// 获取平台图标
const getPlatformIcon = (platform: string) => {
  const icons = {
    'bilibili': '📺',
    'youtube': '▶️',
    'tiktok': '🎵',
    'instagram': '📸',
  }
  return icons[platform] || '🎬'
}

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
          v-if="getThumbnailUrl(info.thumbnail, info.platform)"
          :src="getThumbnailUrl(info.thumbnail, info.platform)"
          :alt="info.title"
          class="w-48 h-32 object-cover rounded-lg"
        />
        <div
          v-else
          class="w-48 h-32 rounded-lg flex flex-col items-center justify-center text-white"
          style="background: linear-gradient(to bottom right, #3B82F6, #8B5CF6);"
        >
          <span class="text-4xl mb-2">{{ getPlatformIcon(info.platform) }}</span>
          <span class="text-xs font-medium capitalize">{{ info.platform }}</span>
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
