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

interface SSEEventMessage {
  event: string
  data: any
}

export type TranscriptFormat = 'srt' | 'vtt' | 'txt'

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
  const downloadingTranscriptFormat = ref<TranscriptFormat | null>(null)

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
    chatHistory.value.push({
      question: currentQuestion,
      answer: '',
      citations: [],
    })
    const chatIndex = chatHistory.value.length - 1
    question.value = ''

    try {
      await streamQuestionAnswer(analysisResult.value.analysis_id, currentQuestion, chatIndex)
    } catch (err: any) {
      analysisError.value = err?.message || err.response?.data?.detail || 'AI 问答失败'
      const turn = chatHistory.value[chatIndex]
      if (turn && !turn.answer.trim()) {
        chatHistory.value.splice(chatIndex, 1)
      }
    } finally {
      asking.value = false
    }
  }

  const streamQuestionAnswer = async (analysisId: string, q: string, chatIndex: number) => {
    const response = await fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        analysis_id: analysisId,
        question: q,
      }),
    })

    if (!response.ok) {
      throw new Error(await readResponseError(response))
    }

    if (!response.body) {
      await fetchAnswerWithoutStream(analysisId, q, chatIndex)
      return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) {
        break
      }

      buffer += decoder.decode(value, { stream: true })
      buffer = buffer.replace(/\r\n/g, '\n')

      let boundary = buffer.indexOf('\n\n')
      while (boundary !== -1) {
        const rawEvent = buffer.slice(0, boundary).trim()
        buffer = buffer.slice(boundary + 2)
        if (rawEvent) {
          applyStreamEvent(rawEvent, chatIndex)
        }
        boundary = buffer.indexOf('\n\n')
      }
    }

    buffer += decoder.decode()
    const tail = buffer.trim()
    if (tail) {
      applyStreamEvent(tail, chatIndex)
    }
  }

  const applyStreamEvent = (rawEvent: string, chatIndex: number) => {
    const event = parseSSEEvent(rawEvent)
    if (!event) {
      return
    }

    const turn = chatHistory.value[chatIndex]
    if (!turn) {
      return
    }

    if (event.event === 'delta') {
      const delta = event.data?.delta
      if (typeof delta === 'string') {
        turn.answer += delta
      }
      return
    }

    if (event.event === 'start' || event.event === 'done') {
      const citations = event.data?.citations
      if (Array.isArray(citations)) {
        turn.citations = citations
      }
      return
    }

    if (event.event === 'error') {
      throw new Error(event.data?.message || 'AI 问答失败')
    }
  }

  const parseSSEEvent = (rawEvent: string): SSEEventMessage | null => {
    if (!rawEvent.trim()) {
      return null
    }

    const lines = rawEvent.split('\n')
    let eventName = 'message'
    const dataLines: string[] = []

    for (const line of lines) {
      if (line.startsWith('event:')) {
        eventName = line.slice(6).trim()
        continue
      }
      if (line.startsWith('data:')) {
        dataLines.push(line.slice(5).trim())
      }
    }

    if (!dataLines.length) {
      return { event: eventName, data: {} }
    }

    const dataText = dataLines.join('\n')
    try {
      return {
        event: eventName,
        data: JSON.parse(dataText),
      }
    } catch {
      return {
        event: eventName,
        data: { raw: dataText },
      }
    }
  }

  const fetchAnswerWithoutStream = async (analysisId: string, q: string, chatIndex: number) => {
    const response = await apiClient.post<VideoChatResponse>('/ai/chat', {
      analysis_id: analysisId,
      question: q,
    })
    const turn = chatHistory.value[chatIndex]
    if (!turn) {
      return
    }
    turn.answer = response.data.answer || ''
    turn.citations = response.data.citations || []
  }

  const readResponseError = async (response: Response): Promise<string> => {
    const contentType = response.headers.get('content-type') || ''
    try {
      if (contentType.includes('application/json')) {
        const payload = await response.json()
        return payload?.detail || payload?.message || `AI 问答失败（HTTP ${response.status}）`
      }
      const text = await response.text()
      return text || `AI 问答失败（HTTP ${response.status}）`
    } catch {
      return `AI 问答失败（HTTP ${response.status}）`
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
    downloadingTranscriptFormat.value = null
  }

  const downloadTranscript = async (format: TranscriptFormat) => {
    const analysisId = analysisResult.value?.analysis_id
    if (!analysisId) {
      analysisError.value = '请先完成视频分析'
      return
    }

    downloadingTranscriptFormat.value = format
    analysisError.value = null

    try {
      const response = await fetch(
        `/api/ai/transcript/download/${encodeURIComponent(analysisId)}?format=${encodeURIComponent(format)}`,
      )
      if (!response.ok) {
        throw new Error(await readResponseError(response))
      }

      const blob = await response.blob()
      const contentDisposition = response.headers.get('content-disposition')
      const fallbackName = `transcript-${analysisId.slice(0, 8)}.${format}`
      const filename = parseDownloadFilename(contentDisposition) || fallbackName

      const objectUrl = window.URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = objectUrl
      anchor.download = filename
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      window.URL.revokeObjectURL(objectUrl)
    } catch (err: any) {
      analysisError.value = err?.message || '字幕下载失败'
    } finally {
      downloadingTranscriptFormat.value = null
    }
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

  const parseDownloadFilename = (contentDisposition: string | null): string | null => {
    if (!contentDisposition) {
      return null
    }

    const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i)
    if (utf8Match?.[1]) {
      try {
        return decodeURIComponent(utf8Match[1])
      } catch {
        return utf8Match[1]
      }
    }

    const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i)
    return filenameMatch?.[1] || null
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
    downloadingTranscriptFormat,
    analyzeVideo,
    askQuestion,
    downloadTranscript,
    resetAI,
  }
}
