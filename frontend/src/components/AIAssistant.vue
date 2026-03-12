<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import MarkdownIt from 'markdown-it'

import { useVideoAI, type TranscriptFormat } from '@/composables/useVideoAI'
import MindMapTree from './MindMapTree.vue'

type MindMapExportFormat = 'png' | 'svg'

interface MindMapExporter {
  downloadPng: (filenameBase?: string, scale?: number) => Promise<void>
  downloadSvg: (filenameBase?: string) => void
}

const props = withDefaults(defineProps<{
  url: string
  analyzeTrigger?: number
}>(), {
  analyzeTrigger: 0,
})

const {
  analyzing,
  analysisError,
  analysisResult,
  analysisStage,
  analysisProgress,
  streamingOverview,
  streamingTitle,
  asking,
  question,
  chatHistory,
  downloadingTranscriptFormat,
  analyzeVideo,
  askQuestion,
  downloadTranscript,
} = useVideoAI()

const activeTab = ref<'summary' | 'transcript' | 'mindmap' | 'qa'>('summary')
const mindMapFullscreen = ref(false)
const downloadingMindMapFormat = ref<MindMapExportFormat | null>(null)
const mindMapRef = ref<MindMapExporter | null>(null)
const fullscreenMindMapRef = ref<MindMapExporter | null>(null)

const transcriptCount = computed(() => analysisResult.value?.transcript?.length || 0)

const tabItems = [
  { key: 'summary', label: '总结摘要' },
  { key: 'transcript', label: '字幕文本' },
  { key: 'mindmap', label: '思维导图' },
  { key: 'qa', label: 'AI 问答' },
] as const

const transcriptDownloadOptions: { key: TranscriptFormat; label: string }[] = [
  { key: 'srt', label: '下载 SRT' },
  { key: 'vtt', label: '下载 VTT' },
  { key: 'txt', label: '下载 TXT' },
]

// 分析中或已有结果时都展示 Tab 结构
const showTabs = computed(() => analyzing.value || !!analysisResult.value)

const tabContentClass = computed(() => {
  if (activeTab.value === 'mindmap') {
    return 'p-0 flex-1 min-h-0 overflow-hidden bg-slate-50'
  }
  return 'p-4 flex-1 min-h-0 overflow-y-auto bg-white'
})

const onAnalyze = () => {
  analyzeVideo(props.url)
}

// 监听外部触发信号：自动开始分析
// immediate: true 确保组件首次挂载时若 trigger 已 > 0 也能自动触发
watch(
  () => props.analyzeTrigger,
  (newVal) => {
    if (newVal > 0 && props.url && !analyzing.value) {
      onAnalyze()
    }
  },
  { immediate: true },
)

const onAsk = () => {
  askQuestion()
}

const onDownloadTranscript = async (format: TranscriptFormat) => {
  await downloadTranscript(format)
}

const openMindMapFullscreen = async () => {
  mindMapFullscreen.value = true
  await nextTick()
}

const closeMindMapFullscreen = () => {
  mindMapFullscreen.value = false
}

const sanitizeFilename = (value: string) => value.replace(/[<>:"/\\|?*]+/g, '_').trim()

const getMindMapFileBase = () => {
  const title = analysisResult.value?.video_title || 'mind-map'
  const safeTitle = sanitizeFilename(title)
  return `${safeTitle || 'mind-map'}-mindmap`
}

const resolveMindMapExporter = (): MindMapExporter | null => {
  if (mindMapFullscreen.value) {
    return fullscreenMindMapRef.value || mindMapRef.value
  }
  return mindMapRef.value || fullscreenMindMapRef.value
}

const downloadMindMap = async (format: MindMapExportFormat) => {
  const exporter = resolveMindMapExporter()
  if (!analysisResult.value || !exporter) {
    analysisError.value = '导图尚未就绪，请先完成视频分析'
    return
  }

  downloadingMindMapFormat.value = format
  try {
    const filenameBase = getMindMapFileBase()
    if (format === 'png') {
      await exporter.downloadPng(filenameBase, 3)
    } else {
      exporter.downloadSvg(filenameBase)
    }
  } catch (error: any) {
    analysisError.value = error?.message || '思维导图下载失败'
  } finally {
    downloadingMindMapFormat.value = null
  }
}

const onDownloadMindMapPng = async () => {
  await downloadMindMap('png')
}

const onDownloadMindMapSvg = async () => {
  await downloadMindMap('svg')
}

const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  typographer: false,
})

const defaultRenderLink =
  markdown.renderer.rules.link_open ??
  ((tokens: any, idx: number, options: any, _env: any, self: any) => self.renderToken(tokens, idx, options))

markdown.renderer.rules.link_open = (tokens: any, idx: number, options: any, env: any, self: any) => {
  tokens[idx]?.attrSet('target', '_blank')
  tokens[idx]?.attrSet('rel', 'noopener noreferrer nofollow')
  return defaultRenderLink(tokens, idx, options, env, self)
}

const renderAnswerMarkdown = (content: string): string => {
  return markdown.render(content || '')
}

const onWindowKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && mindMapFullscreen.value) {
    closeMindMapFullscreen()
  }
}

watch(mindMapFullscreen, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  window.addEventListener('keydown', onWindowKeyDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onWindowKeyDown)
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-xl p-4 h-full flex flex-col max-h-[calc(100vh-12rem)] overflow-hidden">
    <div class="flex items-center justify-between gap-3 mb-3">
      <div class="flex items-center gap-2 min-w-0">
        <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shrink-0">
          <svg class="w-3.5 h-3.5 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <div class="min-w-0">
          <h3 class="text-base font-semibold text-gray-900 truncate">AI 学习助手</h3>
          <p class="text-xs text-gray-400">总结 · 字幕 · 脑图 · 问答</p>
        </div>
      </div>
      <button
        @click="onAnalyze"
        :disabled="!url || analyzing"
        class="px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors shrink-0"
        :class="analyzing
          ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
          : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400'"
      >
        {{ analyzing ? '分析中...' : analysisResult ? '重新分析' : 'AI 分析视频' }}
      </button>
    </div>

    <div v-if="analysisError" class="mb-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
      {{ analysisError }}
    </div>

    <div v-if="showTabs" class="rounded-xl border border-gray-200 overflow-hidden flex-1 flex flex-col min-h-0">
      <!-- 分析中：顶部细进度条 -->
      <div v-if="analyzing" class="h-1 bg-blue-100 overflow-hidden shrink-0">
        <div class="h-full bg-blue-500 transition-all duration-500 ease-out" :style="{ width: `${analysisProgress}%` }"></div>
      </div>

      <!-- Tab 导航 -->
      <div class="bg-gray-50 border-b border-gray-200 px-3 pt-2 shrink-0">
        <div class="flex items-center gap-1 overflow-x-auto">
          <button
            v-for="tab in tabItems"
            :key="tab.key"
            @click="activeTab = tab.key"
            :disabled="analyzing && tab.key !== 'summary'"
            :class="[
              'px-3 py-2 text-sm border-b-2 whitespace-nowrap transition-colors',
              activeTab === tab.key
                ? 'text-blue-600 border-blue-600 font-medium'
                : 'text-gray-500 border-transparent hover:text-gray-700',
              analyzing && tab.key !== 'summary' ? 'opacity-40 cursor-not-allowed' : '',
            ]"
          >
            {{ tab.label }}
          </button>
          <!-- 分析中状态提示 -->
          <span v-if="analyzing" class="ml-auto text-xs text-blue-500 flex items-center gap-1.5 shrink-0 pr-1">
            <svg class="w-3 h-3 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ analysisStage }}
          </span>
        </div>
      </div>

      <!-- Tab 内容区 -->
      <div :class="tabContentClass">
        <template v-if="activeTab === 'summary'">
          <!-- === 分析中，尚无流式内容：骨架屏 === -->
          <div v-if="analyzing && !streamingOverview" class="space-y-4 animate-pulse">
            <!-- 视频标题骨架 -->
            <div class="rounded-lg border border-gray-200 bg-gray-50 p-3">
              <div class="h-3 w-16 bg-gray-200 rounded mb-2"></div>
              <div class="h-4 w-3/4 bg-gray-200 rounded mb-2"></div>
              <div class="h-3 w-1/3 bg-gray-200 rounded"></div>
            </div>
            <!-- 总览骨架 -->
            <div class="rounded-lg border border-blue-200 bg-blue-50/60 p-3">
              <div class="h-4 w-12 bg-blue-200 rounded mb-3"></div>
              <div class="space-y-2">
                <div class="h-3 w-full bg-blue-200/60 rounded"></div>
                <div class="h-3 w-5/6 bg-blue-200/60 rounded"></div>
                <div class="h-3 w-4/6 bg-blue-200/60 rounded"></div>
              </div>
            </div>
            <!-- 核心要点骨架 -->
            <div class="rounded-lg border border-gray-200 p-3">
              <div class="h-4 w-20 bg-gray-200 rounded mb-3"></div>
              <div class="space-y-2">
                <div class="h-3 w-full bg-gray-100 rounded"></div>
                <div class="h-3 w-5/6 bg-gray-100 rounded"></div>
                <div class="h-3 w-4/6 bg-gray-100 rounded"></div>
              </div>
            </div>
            <!-- 章节结构骨架 -->
            <div class="rounded-lg border border-gray-200 p-3">
              <div class="h-4 w-20 bg-gray-200 rounded mb-3"></div>
              <div class="space-y-2">
                <div class="rounded-md border border-gray-100 bg-gray-50 p-2.5">
                  <div class="h-3 w-20 bg-gray-200 rounded mb-1.5"></div>
                  <div class="h-3.5 w-2/3 bg-gray-200 rounded mb-1.5"></div>
                  <div class="h-3 w-full bg-gray-100 rounded"></div>
                </div>
                <div class="rounded-md border border-gray-100 bg-gray-50 p-2.5">
                  <div class="h-3 w-20 bg-gray-200 rounded mb-1.5"></div>
                  <div class="h-3.5 w-1/2 bg-gray-200 rounded mb-1.5"></div>
                  <div class="h-3 w-5/6 bg-gray-100 rounded"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- === 分析中，流式摘要输出中 === -->
          <div v-else-if="analyzing && streamingOverview" class="space-y-4">
            <!-- 视频标题 -->
            <div v-if="streamingTitle" class="rounded-lg border border-gray-200 bg-gray-50 p-3">
              <p class="text-xs text-gray-500 mb-1">视频标题</p>
              <p class="text-sm text-gray-900 font-medium">{{ streamingTitle }}</p>
            </div>
            <div v-else class="rounded-lg border border-gray-200 bg-gray-50 p-3 animate-pulse">
              <div class="h-3 w-16 bg-gray-200 rounded mb-2"></div>
              <div class="h-4 w-3/4 bg-gray-200 rounded"></div>
            </div>

            <!-- 流式总览：逐字输出 + 光标闪烁 -->
            <div class="rounded-lg border border-blue-200 bg-blue-50 p-3">
              <p class="text-sm font-semibold text-blue-900 mb-2">总览</p>
              <p class="text-sm text-blue-800 leading-6">
                {{ streamingOverview }}<span class="inline-block w-0.5 h-4 bg-blue-600 animate-pulse ml-0.5 align-text-bottom"></span>
              </p>
            </div>

            <!-- 核心要点骨架 -->
            <div class="rounded-lg border border-gray-200 p-3 animate-pulse">
              <div class="h-4 w-20 bg-gray-200 rounded mb-3"></div>
              <div class="space-y-2">
                <div class="h-3 w-full bg-gray-100 rounded"></div>
                <div class="h-3 w-5/6 bg-gray-100 rounded"></div>
                <div class="h-3 w-4/6 bg-gray-100 rounded"></div>
              </div>
            </div>

            <!-- 章节结构骨架 -->
            <div class="rounded-lg border border-gray-200 p-3 animate-pulse">
              <div class="h-4 w-20 bg-gray-200 rounded mb-3"></div>
              <div class="space-y-2">
                <div class="rounded-md border border-gray-100 bg-gray-50 p-2.5">
                  <div class="h-3 w-20 bg-gray-200 rounded mb-1.5"></div>
                  <div class="h-3.5 w-2/3 bg-gray-200 rounded"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- === 分析完成：真实内容 === -->
          <div v-else-if="analysisResult" class="space-y-4">
            <div class="rounded-lg border border-gray-200 bg-gray-50 p-3">
              <p class="text-xs text-gray-500 mb-1">视频标题</p>
              <p class="text-sm text-gray-900 font-medium">{{ analysisResult.video_title }}</p>
              <p class="text-xs text-gray-500 mt-1">
                转录语言：{{ analysisResult.transcript_language || '未知' }} · 片段：{{ transcriptCount }}
              </p>
            </div>

            <div class="rounded-lg border border-blue-200 bg-blue-50 p-3">
              <p class="text-sm font-semibold text-blue-900 mb-2">总览</p>
              <p class="text-sm text-blue-800 leading-6">{{ analysisResult.summary.overview }}</p>
            </div>

            <div class="rounded-lg border border-gray-200 p-3">
              <p class="text-sm font-semibold text-gray-900 mb-2">核心要点</p>
              <ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
                <li v-for="(item, idx) in analysisResult.summary.key_points" :key="`kp-${idx}`">
                  {{ item }}
                </li>
              </ul>
            </div>

            <div class="rounded-lg border border-gray-200 p-3">
              <p class="text-sm font-semibold text-gray-900 mb-2">章节结构</p>
              <div class="space-y-2">
                <div
                  v-for="(section, idx) in analysisResult.summary.sections"
                  :key="`section-${idx}`"
                  class="rounded-md border border-gray-100 bg-gray-50 p-2.5"
                >
                  <p class="text-xs text-blue-600 font-medium">{{ section.start }}</p>
                  <p class="text-sm text-gray-900 font-medium mt-0.5">{{ section.title }}</p>
                  <p class="text-sm text-gray-600 mt-1">{{ section.summary }}</p>
                </div>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="activeTab === 'transcript'">
          <div v-if="analysisResult" class="h-full flex flex-col">
            <div class="flex items-center justify-between gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3 mb-3">
              <div>
                <p class="text-sm font-medium text-gray-800">字幕片段：{{ transcriptCount }}</p>
                <p class="text-xs text-gray-500 mt-0.5">支持单独下载字幕文件</p>
              </div>
              <div class="flex items-center gap-2">
                <button
                  v-for="option in transcriptDownloadOptions"
                  :key="option.key"
                  @click="onDownloadTranscript(option.key)"
                  :disabled="downloadingTranscriptFormat !== null"
                  class="px-3 py-1.5 rounded-md text-xs font-medium border border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100 disabled:bg-gray-100 disabled:border-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {{
                    downloadingTranscriptFormat === option.key
                      ? `${option.key.toUpperCase()} 下载中...`
                      : option.label
                  }}
                </button>
              </div>
            </div>

            <div class="flex-1 overflow-y-auto pr-1">
              <div v-if="analysisResult.transcript.length" class="space-y-1">
                <div
                  v-for="(segment, idx) in analysisResult.transcript"
                  :key="`seg-${idx}`"
                  class="grid grid-cols-[64px_1fr] gap-3 py-2 border-b border-gray-100"
                >
                  <div class="text-xs text-blue-600 font-medium pt-0.5">{{ segment.timestamp }}</div>
                  <div class="text-sm text-gray-700 leading-6">{{ segment.text }}</div>
                </div>
              </div>
              <div v-else class="text-sm text-gray-500 py-8 text-center">暂无字幕内容</div>
            </div>
          </div>
          <div v-else class="flex items-center justify-center h-full text-sm text-gray-400">分析完成后展示字幕</div>
        </template>

        <template v-else-if="activeTab === 'mindmap'">
          <div v-if="analysisResult" class="h-full flex flex-col">
            <div class="flex items-center justify-between gap-3 px-4 py-3 bg-white border-b border-slate-200">
              <div>
                <p class="text-sm font-medium text-slate-800">思维导图浏览与导出</p>
                <p class="text-xs text-slate-500 mt-0.5">支持全屏查看、高清 PNG、SVG 下载</p>
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click="openMindMapFullscreen"
                  class="px-3 py-1.5 rounded-md text-xs font-medium border border-slate-300 text-slate-700 bg-white hover:bg-slate-100 transition-colors"
                >
                  全屏查看
                </button>
                <button
                  @click="onDownloadMindMapPng"
                  :disabled="downloadingMindMapFormat !== null"
                  class="px-3 py-1.5 rounded-md text-xs font-medium border border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100 disabled:bg-gray-100 disabled:border-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {{ downloadingMindMapFormat === 'png' ? 'PNG 生成中...' : '下载高清 PNG' }}
                </button>
                <button
                  @click="onDownloadMindMapSvg"
                  :disabled="downloadingMindMapFormat !== null"
                  class="px-3 py-1.5 rounded-md text-xs font-medium border border-emerald-200 text-emerald-700 bg-emerald-50 hover:bg-emerald-100 disabled:bg-gray-100 disabled:border-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {{ downloadingMindMapFormat === 'svg' ? 'SVG 导出中...' : '下载 SVG' }}
                </button>
              </div>
            </div>
            <div class="flex-1 p-3 min-h-0">
              <MindMapTree ref="mindMapRef" :node="analysisResult.mind_map" />
            </div>
          </div>
          <div v-else class="flex items-center justify-center h-full text-sm text-gray-400">分析完成后展示思维导图</div>
        </template>

        <template v-else>
          <div class="h-full flex flex-col">
            <div class="flex gap-2 mb-3">
              <input
                v-model="question"
                type="text"
                placeholder="输入问题，例如：这个项目主要做了什么？"
                class="flex-1 rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                @keyup.enter="onAsk"
              />
              <button
                @click="onAsk"
                :disabled="asking || !question.trim()"
                class="px-4 py-2.5 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {{ asking ? '回答中...' : '发送' }}
              </button>
            </div>

            <div class="flex-1 overflow-y-auto space-y-3">
              <div
                v-for="(item, idx) in chatHistory"
                :key="`chat-${idx}`"
                class="rounded-lg border border-gray-100 bg-gray-50 p-3"
              >
                <p class="text-sm font-medium text-blue-700">问：{{ item.question }}</p>
                <div
                  class="ai-markdown text-sm text-gray-700 mt-2 leading-6"
                  v-html="renderAnswerMarkdown(item.answer)"
                ></div>
                <div v-if="item.citations?.length" class="mt-2">
                  <p class="text-xs text-gray-500 mb-1">引用片段</p>
                  <div
                    v-for="(citation, cidx) in item.citations"
                    :key="`citation-${idx}-${cidx}`"
                    class="text-xs text-gray-600 leading-5"
                  >
                    <span class="text-blue-600 font-medium">[{{ citation.timestamp }}]</span>
                    {{ citation.text }}
                  </div>
                </div>
              </div>

              <div v-if="!chatHistory.length" class="text-sm text-gray-500 py-8 text-center">
                你可以问：这个视频的核心观点是什么？有哪些可执行步骤？
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <div
      v-if="mindMapFullscreen && analysisResult"
      class="fixed inset-0 z-[1200] bg-slate-900/70 backdrop-blur-sm p-3 sm:p-6"
      @click.self="closeMindMapFullscreen"
    >
      <div class="mx-auto h-full w-full max-w-[1700px] bg-white border border-slate-200 rounded-xl shadow-2xl flex flex-col">
        <div class="flex items-center justify-between gap-4 px-4 py-3 border-b border-slate-200">
          <div class="min-w-0">
            <h4 class="text-sm sm:text-base font-semibold text-slate-900 truncate">
              {{ analysisResult.video_title }} · 思维导图
            </h4>
            <p class="text-xs text-slate-500 mt-0.5">按 Esc 可退出全屏</p>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button
              @click="onDownloadMindMapPng"
              :disabled="downloadingMindMapFormat !== null"
              class="px-3 py-1.5 rounded-md text-xs font-medium border border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100 disabled:bg-gray-100 disabled:border-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {{ downloadingMindMapFormat === 'png' ? 'PNG 生成中...' : '下载高清 PNG' }}
            </button>
            <button
              @click="onDownloadMindMapSvg"
              :disabled="downloadingMindMapFormat !== null"
              class="px-3 py-1.5 rounded-md text-xs font-medium border border-emerald-200 text-emerald-700 bg-emerald-50 hover:bg-emerald-100 disabled:bg-gray-100 disabled:border-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {{ downloadingMindMapFormat === 'svg' ? 'SVG 导出中...' : '下载 SVG' }}
            </button>
            <button
              @click="closeMindMapFullscreen"
              class="px-3 py-1.5 rounded-md text-xs font-medium border border-slate-300 text-slate-700 bg-white hover:bg-slate-100 transition-colors"
            >
              关闭
            </button>
          </div>
        </div>
        <div class="flex-1 p-3 sm:p-4 min-h-0">
          <MindMapTree ref="fullscreenMindMapRef" :node="analysisResult.mind_map" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.ai-markdown :deep(p) {
  margin: 0 0 0.55rem;
}

.ai-markdown :deep(p:last-child) {
  margin-bottom: 0;
}

.ai-markdown :deep(ul),
.ai-markdown :deep(ol) {
  margin: 0.4rem 0 0.7rem 1.15rem;
  padding: 0;
}

.ai-markdown :deep(li) {
  margin: 0.2rem 0;
}

.ai-markdown :deep(strong) {
  font-weight: 700;
  color: #1f2937;
}

.ai-markdown :deep(code) {
  background: #e5e7eb;
  color: #1e3a8a;
  border-radius: 5px;
  padding: 1px 6px;
  font-size: 0.82em;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
    'Courier New', monospace;
}

.ai-markdown :deep(pre) {
  margin: 0.6rem 0;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.7rem 0.85rem;
  background: #f8fafc;
  overflow-x: auto;
}

.ai-markdown :deep(pre code) {
  background: transparent;
  border-radius: 0;
  padding: 0;
  color: #0f172a;
}

.ai-markdown :deep(blockquote) {
  margin: 0.55rem 0;
  border-left: 3px solid #93c5fd;
  padding: 0.2rem 0 0.2rem 0.7rem;
  color: #475569;
}

.ai-markdown :deep(a) {
  color: #2563eb;
  text-decoration: underline;
  text-underline-offset: 2px;
}
</style>
