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

export interface RegisterRequest {
  email: string
  password: string
}

export interface RegisterResponse {
  message: string
  requires_email_verification: boolean
  debug_verify_url?: string | null
}

export interface LoginRequest {
  email: string
  password: string
}

export interface UserProfile {
  id: string
  email: string
  email_verified: boolean
}

export interface LoginResponse {
  user: UserProfile
}

export interface CurrentUserResponse {
  authenticated: boolean
  user?: UserProfile | null
}

export interface MembershipStatusResponse {
  is_member: boolean
  plan_code?: string | null
  status: string
  expires_at?: string | null
  remaining_days: number
}

export interface CheckoutSessionResponse {
  order_id: string
  checkout_url: string
  provider: 'mock' | 'stripe'
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
