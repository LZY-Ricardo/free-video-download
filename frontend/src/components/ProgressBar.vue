<script setup lang="ts">
defineProps<{
  progress: number
  speed: string
  status: string
}>()
</script>

<template>
  <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6 shadow-sm">
    <div class="mb-4">
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm font-medium text-gray-700">下载进度</span>
        <span class="text-sm font-semibold text-accent">{{ progress.toFixed(1) }}%</span>
      </div>

      <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          class="h-full bg-accent transition-all duration-300 ease-out"
          :style="{ width: `${progress}%` }"
        />
      </div>
    </div>

    <div class="flex justify-between items-center text-sm text-gray-600">
      <span>速度: {{ speed }}</span>
      <span v-if="status === 'completed'" class="text-green-600 font-medium">
        ✓ 下载完成
      </span>
      <span v-else-if="status === 'downloading'" class="text-blue-600">
        下载中...
      </span>
    </div>

    <!-- 下载完成后的下载按钮 -->
    <div v-if="status === 'completed'" class="mt-4">
      <button
        @click="$emit('download-file')"
        class="w-full py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
      >
        📥 下载文件到本地
      </button>
    </div>
  </div>
</template>
