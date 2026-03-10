import { ref } from 'vue'
import type { VideoInfo, TaskStatus } from '@/types'
import apiClient from '@/api/client'

export function useDownload() {
  const url = ref('')
  const videoInfo = ref<VideoInfo | null>(null)
  const taskId = ref<string | null>(null)
  const status = ref<'idle' | 'fetching' | 'ready' | 'downloading' | 'completed' | 'error'>('idle')
  const progress = ref(0)
  const speed = ref('0KB/s')
  const error = ref<string | null>(null)
  const loading = ref(false)
  const extractedUrl = ref<string | null>(null) // 显示提取到的URL

  // 从分享文本中提取URL
  const extractUrl = (text: string): string => {
    // 匹配 http/https 开头的 URL
    const urlPattern = /(https?:\/\/[^\s\u4e00-\u9fa5]+)/g
    const match = text.match(urlPattern)
    return match ? match[0] : text
  }

  // 获取视频信息
  const getInfo = async () => {
    if (!url.value) {
      error.value = '请输入视频链接'
      return
    }

    // 尝试从分享文本中提取URL
    const originalInput = url.value
    const cleanUrl = extractUrl(url.value)

    // 如果提取到的URL和输入不同，说明从分享文本中提取了URL
    if (cleanUrl !== originalInput) {
      extractedUrl.value = cleanUrl
      url.value = cleanUrl
    } else {
      extractedUrl.value = null
    }

    loading.value = true
    status.value = 'fetching'
    error.value = null

    try {
      const response = await apiClient.post<VideoInfo>('/info', { url: url.value })
      videoInfo.value = response.data
      status.value = 'ready'
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取视频信息失败'
      status.value = 'error'
    } finally {
      loading.value = false
    }
  }

  // 开始下载
  const startDownload = async (options: { format?: string; quality?: string }) => {
    if (!url.value) return

    loading.value = true
    status.value = 'downloading'
    error.value = null
    progress.value = 0

    try {
      const response = await apiClient.post<any>('/download', {
        url: url.value,
        ...options
      })
      taskId.value = response.data.task_id

      // 轮询获取状态
      if (taskId.value) {
        pollStatus(taskId.value)
      } else {
        throw new Error('未获取到任务 ID')
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || '下载失败'
      status.value = 'error'
      loading.value = false
    }
  }

  // 轮询任务状态
  const pollStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await apiClient.get<TaskStatus>(`/download/status/${id}`)
        const taskStatus = response.data

        progress.value = taskStatus.progress
        speed.value = taskStatus.speed

        if (taskStatus.status === 'completed') {
          status.value = 'completed'
          loading.value = false
          clearInterval(interval)
        } else if (taskStatus.status === 'failed') {
          error.value = taskStatus.error || '下载失败'
          status.value = 'error'
          loading.value = false
          clearInterval(interval)
        }
      } catch (err: any) {
        // 如果是 404 错误（任务不存在），可能是下载已完成但任务被清理
        // 不应该认为是错误
        if (err.response?.status === 404) {
          // 检查是否已经有进度
          if (progress.value > 0) {
            status.value = 'completed'
            loading.value = false
            clearInterval(interval)
            return
          }
        }
        error.value = err.response?.data?.detail || '获取状态失败'
        status.value = 'error'
        loading.value = false
        clearInterval(interval)
      }
    }, 500) // 每0.5秒更新一次
  }

  // 下载文件
  const downloadFile = () => {
    if (!taskId.value) return
    window.open(`/api/download/file/${taskId.value}`, '_blank')
  }

  // 重置状态
  const reset = () => {
    url.value = ''
    videoInfo.value = null
    taskId.value = null
    status.value = 'idle'
    progress.value = 0
    speed.value = '0KB/s'
    error.value = null
    loading.value = false
  }

  return {
    url,
    videoInfo,
    status,
    progress,
    speed,
    error,
    loading,
    extractedUrl,
    getInfo,
    startDownload,
    downloadFile,
    reset
  }
}
