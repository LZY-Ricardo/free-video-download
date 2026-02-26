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
