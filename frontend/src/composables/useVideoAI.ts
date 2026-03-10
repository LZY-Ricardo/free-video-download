import { ref } from 'vue'

import apiClient from '@/api/client'
import type {
  AnalyzeStartResponse,
  AnalyzeTaskStatusResponse,
  VideoAnalysisResponse,
  VideoChatResponse,
} from '@/types'

export interface ChatTurn {
  question: string
  answer: string
  citations: { timestamp: string; text: string }[]
}

export function useVideoAI() {
  const analyzing = ref(false)
  const analysisError = ref<string | null>(null)
  const analysisResult = ref<VideoAnalysisResponse | null>(null)
  const analysisStage = ref('待开始')
  const analysisProgress = ref(0)
  const analysisTaskId = ref<string | null>(null)
  const pollTimer = ref<number | null>(null)

  const asking = ref(false)
  const question = ref('')
  const chatHistory = ref<ChatTurn[]>([])

  const analyzeVideo = async (url: string) => {
    if (!url) {
      analysisError.value = '请先输入视频链接'
      return
    }

    analyzing.value = true
    analysisError.value = null
    analysisResult.value = null
    chatHistory.value = []
    analysisStage.value = '创建任务中'
    analysisProgress.value = 0
    analysisTaskId.value = null

    try {
      const response = await apiClient.post<AnalyzeStartResponse>('/ai/analyze/start', { url })
      analysisTaskId.value = response.data.task_id
      analysisStage.value = '任务已创建'
      analysisProgress.value = 2
      await pollAnalyzeStatus(response.data.task_id)
    } catch (err: any) {
      analysisError.value = err.response?.data?.detail || 'AI 分析失败'
      stopPolling()
      analyzing.value = false
    } finally {
      if (!analyzing.value) {
        stopPolling()
      }
    }
  }

  const askQuestion = async () => {
    if (!analysisResult.value?.analysis_id) {
      analysisError.value = '请先完成视频分析'
      return
    }
    if (!question.value.trim()) {
      return
    }

    asking.value = true
    analysisError.value = null

    const currentQuestion = question.value.trim()
    try {
      const response = await apiClient.post<VideoChatResponse>('/ai/chat', {
        analysis_id: analysisResult.value.analysis_id,
        question: currentQuestion,
      })
      chatHistory.value.push({
        question: currentQuestion,
        answer: response.data.answer,
        citations: response.data.citations || [],
      })
      question.value = ''
    } catch (err: any) {
      analysisError.value = err.response?.data?.detail || 'AI 问答失败'
    } finally {
      asking.value = false
    }
  }

  const resetAI = () => {
    stopPolling()
    analyzing.value = false
    analysisError.value = null
    analysisResult.value = null
    analysisStage.value = '待开始'
    analysisProgress.value = 0
    analysisTaskId.value = null
    asking.value = false
    question.value = ''
    chatHistory.value = []
  }

  const pollAnalyzeStatus = async (taskId: string) => {
    stopPolling()

    await fetchAnalyzeStatus(taskId)
    if (!analyzing.value) {
      return
    }

    pollTimer.value = window.setInterval(async () => {
      await fetchAnalyzeStatus(taskId)
    }, 1200)
  }

  const fetchAnalyzeStatus = async (taskId: string) => {
    try {
      const response = await apiClient.get<AnalyzeTaskStatusResponse>(`/ai/analyze/status/${taskId}`)
      const task = response.data
      analysisStage.value = task.stage || '处理中'
      analysisProgress.value = Number.isFinite(task.progress) ? task.progress : 0

      if (task.status === 'completed') {
        analysisResult.value = task.result || null
        analyzing.value = false
        stopPolling()
      } else if (task.status === 'failed') {
        analysisError.value = task.error || 'AI 分析失败'
        analyzing.value = false
        stopPolling()
      } else {
        analyzing.value = true
      }
    } catch (err: any) {
      analysisError.value = err.response?.data?.detail || '获取分析状态失败'
      analyzing.value = false
      stopPolling()
    }
  }

  const stopPolling = () => {
    if (pollTimer.value !== null) {
      window.clearInterval(pollTimer.value)
      pollTimer.value = null
    }
  }

  return {
    analyzing,
    analysisError,
    analysisResult,
    analysisStage,
    analysisProgress,
    analysisTaskId,
    asking,
    question,
    chatHistory,
    analyzeVideo,
    askQuestion,
    resetAI,
  }
}
