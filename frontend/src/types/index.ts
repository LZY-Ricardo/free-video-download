export interface VideoInfo {
  title: string
  duration?: number
  thumbnail?: string
  platform: string
  uploader?: string
  view_count?: number
  formats: Format[]
  is_douyin?: boolean
  note?: string
  direct_url?: string
  error?: string
}

export interface Format {
  format_id: string
  ext: string
  quality: string
  filesize?: number
  filesize_display?: string
  resolution?: string
  fps_display?: string
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

export interface AnalyzeRequest {
  url: string
}

export interface TranscriptSegment {
  start: number
  end: number
  timestamp: string
  text: string
}

export interface SummarySection {
  title: string
  start: string
  summary: string
}

export interface VideoSummary {
  overview: string
  key_points: string[]
  sections: SummarySection[]
}

export interface MindMapNode {
  id: string
  label: string
  children: MindMapNode[]
}

export interface VideoAnalysisResponse {
  analysis_id: string
  video_title: string
  summary: VideoSummary
  transcript: TranscriptSegment[]
  mind_map: MindMapNode
  transcript_language?: string
}

export interface AnalyzeStartResponse {
  task_id: string
  status: string
}

export interface AnalyzeTaskStatusResponse {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  stage: string
  progress: number
  error?: string
  result?: VideoAnalysisResponse
}

export interface VideoChatRequest {
  analysis_id: string
  question: string
}

export interface ChatCitation {
  timestamp: string
  text: string
}

export interface VideoChatResponse {
  answer: string
  citations: ChatCitation[]
}
