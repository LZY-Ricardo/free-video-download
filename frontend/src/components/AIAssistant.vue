<script setup lang="ts">
import { computed, ref } from 'vue'

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
                <p class="text-sm text-gray-700 mt-2 whitespace-pre-line leading-6">{{ item.answer }}</p>
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
