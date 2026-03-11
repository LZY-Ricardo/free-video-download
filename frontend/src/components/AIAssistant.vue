<script setup lang="ts">
import { computed, ref } from 'vue'
import MarkdownIt from 'markdown-it'

import { useVideoAI } from '@/composables/useVideoAI'
import MindMapTree from './MindMapTree.vue'

const props = defineProps<{
  url: string
}>()

const {
  analyzing,
  analysisError,
  analysisResult,
  analysisStage,
  analysisProgress,
  asking,
  question,
  chatHistory,
  analyzeVideo,
  askQuestion,
} = useVideoAI()

const activeTab = ref<'summary' | 'transcript' | 'mindmap' | 'qa'>('summary')

const transcriptCount = computed(() => analysisResult.value?.transcript?.length || 0)

const tabItems = [
  { key: 'summary', label: '总结摘要' },
  { key: 'transcript', label: '字幕文本' },
  { key: 'mindmap', label: '思维导图' },
  { key: 'qa', label: 'AI 问答' },
] as const

const onAnalyze = () => {
  analyzeVideo(props.url)
}

const onAsk = () => {
  askQuestion()
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
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-xl p-5 mb-6">
    <div class="flex items-center justify-between gap-3 mb-4">
      <div class="min-w-0">
        <h3 class="text-lg font-semibold text-gray-900 truncate">AI 学习助手</h3>
        <p class="text-sm text-gray-500 mt-1">
          总结、字幕、脑图、问答一体化（支持本地离线转写）
        </p>
      </div>
      <button
        @click="onAnalyze"
        :disabled="!url || analyzing"
        class="px-4 py-2 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors shrink-0"
      >
        {{ analyzing ? '分析中...' : 'AI 分析视频' }}
      </button>
    </div>

    <div v-if="analysisError" class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
      {{ analysisError }}
    </div>

    <div v-if="analyzing" class="mb-4 rounded-lg border border-blue-200 bg-blue-50 p-3">
      <div class="flex items-center justify-between text-xs text-blue-700 mb-2">
        <span>{{ analysisStage }}</span>
        <span>{{ analysisProgress.toFixed(0) }}%</span>
      </div>
      <div class="h-2 rounded-full bg-blue-100 overflow-hidden">
        <div
          class="h-full bg-blue-500 transition-all duration-300"
          :style="{ width: `${analysisProgress}%` }"
        ></div>
      </div>
    </div>

    <div v-if="analysisResult" class="rounded-xl border border-gray-200 overflow-hidden">
      <div class="bg-gray-50 border-b border-gray-200 px-3 pt-2">
        <div class="flex items-center gap-1 overflow-x-auto">
          <button
            v-for="tab in tabItems"
            :key="tab.key"
            @click="activeTab = tab.key"
            :class="[
              'px-3 py-2 text-sm border-b-2 whitespace-nowrap transition-colors',
              activeTab === tab.key
                ? 'text-blue-600 border-blue-600 font-medium'
                : 'text-gray-500 border-transparent hover:text-gray-700',
            ]"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="p-4 h-[460px] overflow-y-auto bg-white">
        <template v-if="activeTab === 'summary'">
          <div class="space-y-4">
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
          <div class="space-y-1">
            <div
              v-for="(segment, idx) in analysisResult.transcript"
              :key="`seg-${idx}`"
              class="grid grid-cols-[64px_1fr] gap-3 py-2 border-b border-gray-100"
            >
              <div class="text-xs text-blue-600 font-medium pt-0.5">{{ segment.timestamp }}</div>
              <div class="text-sm text-gray-700 leading-6">{{ segment.text }}</div>
            </div>
          </div>
        </template>

        <template v-else-if="activeTab === 'mindmap'">
          <MindMapTree :node="analysisResult.mind_map" />
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
