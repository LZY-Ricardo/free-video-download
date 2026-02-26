import { ref, computed } from 'vue'
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

  // 获取视频信息
  const getInfo = async () => {
    if (!url.value) {
      error.value = '请输入视频链接'
      return
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
      pollStatus(taskId.value)
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
      } catch (err) {
        error.value = '获取状态失败'
        status.value = 'error'
        loading.value = false
        clearInterval(interval)
      }
    }, 1000) // 每秒更新一次
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
    getInfo,
    startDownload,
    downloadFile,
    reset
  }
}
