<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Format {
  format_id: string
  ext: string
  quality: string
  filesize_display?: string
  resolution?: string
  fps_display?: string
  filesize_mb?: number
}

const props = withDefaults(defineProps<{
  formats: Format[]
  compact?: boolean
}>(), {
  compact: false,
})

const emit = defineEmits<{
  download: [options: { format: string; quality: string }]
}>()

// 选中的格式 ID
const selectedFormatId = ref<string>('')

// 从可用格式中选择一个推荐格式
const recommendedFormat = computed(() => {
  if (!props.formats || props.formats.length === 0) return null

  // 优先选择 1080p，如果没有则选择最高质量
  let format = props.formats.find(f => f.quality === '1080p')
  if (!format) {
    // 按质量排序，选择最高的
    const sorted = [...props.formats].sort((a, b) => {
      const aHeight = parseInt(a.quality) || 0
      const bHeight = parseInt(b.quality) || 0
      return bHeight - aHeight
    })
    format = sorted[0]
  }

  return format
})

// 当推荐格式变化时，自动选中
watch(() => recommendedFormat.value, (newFormat) => {
  if (newFormat && !selectedFormatId.value) {
    selectedFormatId.value = newFormat.format_id
  }
}, { immediate: true })

// 当前选中的格式
const selectedFormat = computed(() => {
  return props.formats.find(f => f.format_id === selectedFormatId.value) || recommendedFormat.value
})

const handleDownload = () => {
  if (!selectedFormat.value) return

  // 从 quality 中提取数字（如 "1080p" -> "1080"）
  const quality = selectedFormat.value.quality.replace('p', '')

  emit('download', {
    format: selectedFormat.value.ext,
    quality: quality
  })
}

// 获取推荐标签
const isRecommended = (format: Format) => {
  return recommendedFormat.value?.format_id === format.format_id
}
</script>

<template>
  <div :class="compact ? 'bg-white border border-gray-200 rounded-xl p-4' : 'bg-white border border-gray-200 rounded-xl p-6 mb-6'">
    <h3 :class="compact ? 'text-sm font-semibold text-gray-900 mb-1' : 'text-base font-semibold text-gray-900 mb-2'">选择下载格式</h3>
    <p :class="compact ? 'text-xs text-gray-500 mb-3' : 'text-sm text-gray-500 mb-5'">选择最适合您需求的格式和质量</p>

    <!-- 格式列表 -->
    <div :class="compact ? 'space-y-2 mb-3 max-h-[240px] overflow-y-auto pr-1' : 'space-y-3 mb-6'">
      <div
        v-for="format in formats"
        :key="format.format_id"
        @click="selectedFormatId = format.format_id"
        :class="[
          'rounded-lg border-2 cursor-pointer transition-all',
          compact ? 'px-3 py-2.5' : 'p-4',
          selectedFormatId === format.format_id
            ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500/20'
            : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
        ]"
      >
        <div class="flex items-center justify-between gap-3">
          <!-- 左侧：主要信息 -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <!-- 推荐标签 -->
              <span
                v-if="isRecommended(format)"
                class="shrink-0 inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700"
              >
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.738 1.948-2.93a2 2 0 002.026-1.977l-2.8-2.034a1 1 0 00-.95-.69h-3.462c-.969 0-1.371-1.24-.588-1.81l2.8-2.034a1 1 0 00.364-1.118L9.05 2.927z" />
                </svg>
                推荐
              </span>

              <!-- 格式名称和质量 -->
              <span :class="compact ? 'text-sm font-semibold text-gray-900' : 'text-base font-semibold text-gray-900'">
                {{ format.ext.toUpperCase() }} · {{ format.quality }}
              </span>
            </div>

            <!-- 详细信息 -->
            <div :class="['flex flex-wrap items-center gap-x-3 gap-y-0.5 text-gray-500', compact ? 'text-xs mt-1' : 'text-sm mt-2']">
              <span>{{ format.resolution }}</span>
              <span>{{ format.fps_display || '未知 FPS' }}</span>
              <span class="font-medium text-gray-700">{{ format.filesize_display || '未知大小' }}</span>
            </div>
          </div>

          <!-- 右侧：选中指示器 -->
          <div class="shrink-0">
            <div
              :class="[
                'w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all',
                selectedFormatId === format.format_id
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300'
              ]"
            >
              <svg
                v-if="selectedFormatId === format.format_id"
                class="w-2.5 h-2.5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 下载按钮 -->
    <button
      @click="handleDownload"
      :disabled="!selectedFormat"
      :class="[
        'w-full bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2',
        compact ? 'py-2.5 text-sm' : 'py-3.5'
      ]"
    >
      <svg :class="compact ? 'w-4 h-4' : 'w-5 h-5'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
      </svg>
      开始下载
    </button>
  </div>
</template>
