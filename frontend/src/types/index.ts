export interface VideoInfo {
  title: string
  duration?: number
  thumbnail?: string
  platform: string
  uploader?: string
  view_count?: number
  formats: Format[]
}

export interface Format {
  format_id: string
  ext: string
  quality: string
  filesize?: number
  fps?: number
}

export interface DownloadRequest {
  url: string
  format?: string
  quality?: string
}

export interface DownloadResponse {
  task_id: string
  status: string
}

export interface TaskStatus {
  task_id: string
  status: string
  progress: number
  speed: string
  eta: number
  file_path?: string
  error?: string
}
