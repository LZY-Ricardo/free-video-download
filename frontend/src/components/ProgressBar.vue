<script setup lang="ts">
defineProps<{
  progress: number
  speed: string
  status: string
}>()
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
    <!-- 进度标题 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div v-if="status === 'downloading'" class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
          <svg class="w-5 h-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <div v-else class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>

        <div>
          <h3 class="font-semibold text-gray-900">
            {{ status === 'downloading' ? '正在下载' : '下载完成' }}
          </h3>
          <p class="text-sm text-gray-500">{{ speed }}</p>
        </div>
      </div>

      <div class="text-2xl font-semibold text-gray-900">
        {{ progress.toFixed(1) }}%
      </div>
    </div>

    <!-- 进度条 -->
    <div class="mb-4">
      <div class="h-2.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-300 ease-out"
          :class="status === 'completed' ? 'bg-green-500' : 'bg-blue-500'"
          :style="{ width: `${progress}%` }"
        />
      </div>
    </div>

    <!-- 下载完成后的下载按钮 -->
    <div v-if="status === 'completed'" class="flex gap-3">
      <button
        @click="$emit('download-file')"
        class="flex-1 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
        </svg>
        下载到本地
      </button>
    </div>
  </div>
</template>
