import { onUnmounted, ref } from 'vue'
import type { VideoInfo, TaskStatus } from '@/types'
import apiClient from '@/api/client'
import localResolverClient, { LOCAL_RESOLVER_BASE } from '@/api/localResolverClient'
import { getDisplayProgress } from '@/utils/downloadProgress'

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
  const resolverMode = ref<'server' | 'local'>('server')
  let extractedUrlTimer: ReturnType<typeof setTimeout> | null = null

  const clearExtractedUrlTimer = () => {
    if (extractedUrlTimer) {
      clearTimeout(extractedUrlTimer)
      extractedUrlTimer = null
    }
  }

  const scheduleExtractedUrlAutoHide = () => {
    clearExtractedUrlTimer()
    extractedUrlTimer = setTimeout(() => {
      extractedUrl.value = null
      extractedUrlTimer = null
    }, 5000)
  }

  // 从分享文本中提取URL
  const extractUrl = (text: string): string => {
    // 匹配 http/https 开头的 URL
    const urlPattern = /(https?:\/\/[^\s\u4e00-\u9fa5]+)/g
    const match = text.match(urlPattern)
    return match ? match[0] : text
  }

  const isBilibiliUrl = (input: string): boolean => {
    const text = (input || '').toLowerCase()
    return text.includes('bilibili.com') || text.includes('b23.tv')
  }

  const isBilibiliRiskControlError = (message: string): boolean => {
    const text = (message || '').toLowerCase()
    return text.includes('412') || text.includes('precondition failed') || text.includes('风控')
  }

  const buildLocalResolverGuidance = () =>
    [
      '当前链接触发 B 站风控，已尝试切换本地解析模式但本地助手不可用。',
      '请在你的电脑启动本地助手后重试：',
      '1) 进入项目目录 `local-resolver`',
      '2) 执行 `pip install -r requirements.txt`',
      '3) 执行 `python server.py`',
      `4) 保持本地服务运行（默认 ${LOCAL_RESOLVER_BASE}）`,
    ].join('\n')

  const tryLocalResolverInfo = async (videoUrl: string): Promise<VideoInfo> => {
    const response = await localResolverClient.post<VideoInfo>('/info', { url: videoUrl })
    resolverMode.value = 'local'
    const encodedThumbnail = response.data.thumbnail ? encodeURIComponent(response.data.thumbnail) : null
    const thumbnailProxyUrl = encodedThumbnail
      ? `${LOCAL_RESOLVER_BASE}/proxy/image?url=${encodedThumbnail}&platform=${encodeURIComponent(response.data.platform || '')}`
      : undefined
    return {
      ...response.data,
      thumbnail_proxy_url: thumbnailProxyUrl,
      note: [response.data.note, '当前使用本地解析模式（你的电脑网络环境）'].filter(Boolean).join(' | '),
    }
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
      scheduleExtractedUrlAutoHide()
    } else {
      extractedUrl.value = null
      clearExtractedUrlTimer()
    }

    loading.value = true
    status.value = 'fetching'
    error.value = null
    resolverMode.value = 'server'

    try {
      const response = await apiClient.post<VideoInfo>('/info', { url: url.value })
      videoInfo.value = response.data
      status.value = 'ready'
    } catch (err: any) {
      const detail = err.response?.data?.detail || '获取视频信息失败'
      const statusCode = err.response?.status as number | undefined
      const shouldTryLocalFallback =
        isBilibiliUrl(url.value) &&
        (isBilibiliRiskControlError(detail) || !statusCode || statusCode >= 500)

      if (shouldTryLocalFallback) {
        try {
          videoInfo.value = await tryLocalResolverInfo(url.value)
          status.value = 'ready'
        } catch {
          error.value = buildLocalResolverGuidance()
          status.value = 'error'
        }
      } else {
        error.value = detail
        status.value = 'error'
      }
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
      const client = resolverMode.value === 'local' ? localResolverClient : apiClient
      const response = await client.post<any>('/download', {
        url: url.value,
        ...options
      })
      taskId.value = response.data.task_id

      // 轮询获取状态
      if (taskId.value) {
        pollStatus(taskId.value, resolverMode.value)
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
  const pollStatus = async (id: string, mode: 'server' | 'local') => {
    const client = mode === 'local' ? localResolverClient : apiClient
    const interval = setInterval(async () => {
      try {
        const response = await client.get<TaskStatus>(`/download/status/${id}`)
        const taskStatus = response.data

        if (taskStatus.status === 'completed') {
          status.value = 'completed'
          progress.value = getDisplayProgress('completed', taskStatus.progress)
          speed.value = taskStatus.speed
          loading.value = false
          clearInterval(interval)
        } else if (taskStatus.status === 'failed') {
          progress.value = taskStatus.progress
          speed.value = taskStatus.speed
          error.value = taskStatus.error || '下载失败'
          status.value = 'error'
          loading.value = false
          clearInterval(interval)
        } else {
          progress.value = getDisplayProgress('downloading', taskStatus.progress)
          speed.value = taskStatus.speed
        }
      } catch (err: any) {
        // 如果是 404 错误（任务不存在），可能是下载已完成但任务被清理
        // 不应该认为是错误
        if (err.response?.status === 404) {
          // 检查是否已经有进度
          if (progress.value > 0) {
            status.value = 'completed'
            progress.value = getDisplayProgress('completed', progress.value)
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
    if (resolverMode.value === 'local') {
      window.open(`${LOCAL_RESOLVER_BASE}/download/file/${taskId.value}`, '_blank')
      return
    }
    window.open(`/api/download/file/${taskId.value}`, '_blank')
  }

  // 重置状态
  const reset = () => {
    clearExtractedUrlTimer()
    url.value = ''
    videoInfo.value = null
    taskId.value = null
    status.value = 'idle'
    progress.value = 0
    speed.value = '0KB/s'
    error.value = null
    loading.value = false
    resolverMode.value = 'server'
  }

  onUnmounted(() => {
    clearExtractedUrlTimer()
  })

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
