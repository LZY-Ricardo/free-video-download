<script setup lang="ts">
import DownloadForm from './components/DownloadForm.vue'
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <nav class="bg-white border-b border-gray-200">
      <div class="max-w-6xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-2xl">🎬</span>
            <span class="text-xl font-bold text-primary">万能视频下载器</span>
          </div>
          <div class="flex gap-6 text-sm text-gray-600">
            <a href="#" class="hover:text-accent transition-colors">功能</a>
            <a href="#" class="hover:text-accent transition-colors">关于</a>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main>
      <DownloadForm />
    </main>

    <!-- 底部 -->
    <footer class="bg-white border-t border-gray-200 mt-16">
      <div class="max-w-6xl mx-auto px-6 py-8 text-center text-sm text-gray-600">
        <p>© 2024 万能视频下载器. 仅供学习使用，请遵守相关法律法规。</p>
        <p class="mt-2">基于 yt-dlp 开源项目构建</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
nav a {
  text-decoration: none;
}
</style>
