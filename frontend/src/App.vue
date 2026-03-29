<script setup lang="ts">
import DownloadForm from './components/DownloadForm.vue'
</script>

<template>
  <div id="app" class="flex flex-col min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <nav class="bg-white border-b border-gray-100">
      <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <!-- 左侧 Logo 和品牌 -->
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-3">
            <!-- Logo: 蓝色圆形背景 + 白色播放图标 -->
            <div class="w-9 h-9 rounded-full flex items-center justify-center" style="background-color: #3B82F6;">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </div>
            <!-- 品牌名称 -->
            <span class="text-lg font-bold text-gray-900">VidGrab</span>
          </div>
          <!-- 标签 -->
          <span class="px-2.5 py-1 text-xs font-medium rounded-md" style="background-color: #F3F4F6; color: #6B7280;">
            万能视频下载
          </span>
        </div>

        <!-- 中间导航链接 -->
        <div class="flex items-center gap-8">
          <a href="#" class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">功能特性</a>
          <a href="#" class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">套餐价格</a>
          <a href="#" class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">支持平台</a>
        </div>

        <!-- 右侧 VIP 按钮 -->
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-colors hover:opacity-80" style="background-color: #EFF6FF; color: #1D4ED8;">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
          开通 VIP
        </button>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="relative flex-1">
      <DownloadForm />
    </main>

    <!-- 底部 -->
    <footer class="bg-white border-t border-gray-100">
      <div class="max-w-6xl mx-auto px-6 py-8">
        <div class="grid gap-4 md:grid-cols-3 mb-8">
          <section class="rounded-2xl border border-gray-100 bg-gray-50 p-5">
            <h2 class="text-base font-semibold text-gray-900 mb-2">视频下载与字幕整理</h2>
            <p class="text-sm leading-6 text-gray-600">
              用 VidGrab 解析公开视频链接后，可以继续完成下载、字幕导出和音频保存，适合课程复盘与素材归档。
            </p>
          </section>
          <section class="rounded-2xl border border-gray-100 bg-gray-50 p-5">
            <h2 class="text-base font-semibold text-gray-900 mb-2">AI 视频总结</h2>
            <p class="text-sm leading-6 text-gray-600">
              AI 学习助手会输出总览、章节要点、思维导图和流式问答，把长视频转换成更容易复盘的知识结构。
            </p>
          </section>
          <section class="rounded-2xl border border-gray-100 bg-gray-50 p-5">
            <h2 class="text-base font-semibold text-gray-900 mb-2">探索双语 SEO 页面</h2>
            <p class="text-sm leading-6 text-gray-600">
              你也可以从平台页、功能页和 FAQ 页面快速进入对应场景，查看更多关于 VidGrab 的能力说明。
            </p>
            <div class="mt-3 flex flex-wrap gap-3 text-sm">
              <a href="/zh/" class="text-blue-600 hover:text-blue-700 transition-colors">中文入口</a>
              <a href="/en/" class="text-blue-600 hover:text-blue-700 transition-colors">English Hub</a>
              <a href="/zh/faq" class="text-blue-600 hover:text-blue-700 transition-colors">常见问题</a>
            </div>
          </section>
        </div>
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <!-- 版权信息 -->
          <div class="text-sm text-gray-500">
            © 2026 VidGrab. 仅供学习使用，请遵守相关法律法规
          </div>
          <!-- 右侧链接 -->
          <div class="flex items-center gap-6 text-sm text-gray-500">
            <a href="#" class="hover:text-gray-900 transition-colors">用户协议</a>
            <a href="#" class="hover:text-gray-900 transition-colors">隐私政策</a>
            <a href="#" class="hover:text-gray-900 transition-colors">联系我们</a>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-50 text-center text-xs text-gray-400">
          基于 yt-dlp 开源项目构建
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
nav a {
  text-decoration: none;
}
</style>
