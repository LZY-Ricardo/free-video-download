"""
信息获取 API
"""
from fastapi import APIRouter, HTTPException
from app.models import InfoRequest
from app.services.ytdlp_service import ytdlp_service

router = APIRouter(prefix="/api", tags=["info"])


@router.post("/info")
async def get_video_info(request: InfoRequest):
    """
    获取视频信息（不下载）

    Args:
        request: 包含视频 URL 的请求

    Returns:
        dict: 视频信息
    """
    try:
        video_info = ytdlp_service.get_video_info(request.url)
        return video_info  # 直接返回字典
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
