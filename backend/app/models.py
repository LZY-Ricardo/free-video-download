"""
数据模型
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any


class VideoInfo(BaseModel):
    """视频信息"""

    title: str
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    platform: str
    uploader: Optional[str] = None
    view_count: Optional[int] = None
    formats: List[dict] = []

    @field_validator('duration', mode='before')
    @classmethod
    def round_duration(cls, v: Any) -> Optional[int]:
        if v is None:
            return None
        return int(round(float(v)))


class InfoRequest(BaseModel):
    """信息获取请求"""

    url: str = Field(..., description="视频 URL")


class DownloadRequest(BaseModel):
    """下载请求"""

    url: str = Field(..., description="视频 URL")
    format: str = Field(default="best", description="视频格式")
    quality: Optional[str] = Field(default=None, description="视频质量（如 1080p）")


class DownloadResponse(BaseModel):
    """下载响应"""

    task_id: str
    status: str


class TaskStatus(BaseModel):
    """任务状态"""

    task_id: str
    status: str  # pending, downloading, completed, failed
    progress: float = 0.0
    speed: str = "0KB/s"
    eta: int = 0
    file_path: Optional[str] = None
    error: Optional[str] = None


class AnalyzeRequest(BaseModel):
    """AI 分析请求"""

    url: str = Field(..., description="视频 URL")


class AnalyzeStartResponse(BaseModel):
    """AI 分析任务创建响应"""

    task_id: str
    status: str


class TranscriptSegment(BaseModel):
    """带时间戳的转录片段"""

    start: float
    end: float
    timestamp: str
    text: str


class SummarySection(BaseModel):
    """摘要章节"""

    title: str
    start: str
    summary: str


class VideoSummary(BaseModel):
    """视频摘要"""

    overview: str
    key_points: List[str] = []
    sections: List[SummarySection] = []


class MindMapNode(BaseModel):
    """思维导图节点"""

    id: str
    label: str
    children: List["MindMapNode"] = []


class VideoAnalysisResponse(BaseModel):
    """视频 AI 分析结果"""

    analysis_id: str
    video_title: str
    summary: VideoSummary
    transcript: List[TranscriptSegment]
    mind_map: MindMapNode
    transcript_language: Optional[str] = None


class AnalyzeTaskStatusResponse(BaseModel):
    """AI 分析任务状态"""

    task_id: str
    status: str  # pending, processing, completed, failed
    stage: str = "pending"
    progress: float = 0.0
    error: Optional[str] = None
    result: Optional[VideoAnalysisResponse] = None


class ChatRequest(BaseModel):
    """基于视频内容的问答请求"""

    analysis_id: str = Field(..., description="分析任务 ID")
    question: str = Field(..., min_length=1, description="用户问题")


class ChatCitation(BaseModel):
    """问答引用片段"""

    timestamp: str
    text: str


class ChatResponse(BaseModel):
    """视频问答响应"""

    answer: str
    citations: List[ChatCitation] = []


MindMapNode.model_rebuild()
