"""
直链 API
"""
from fastapi import APIRouter, HTTPException
from app.models import InfoRequest
from app.services.ytdlp_service import ytdlp_service

router = APIRouter(prefix="/api", tags=["direct"])


@router.post("/direct-url")
async def get_direct_url(request: InfoRequest):
    """
    获取视频直链

    Args:
        request: 包含视频 URL 的请求

    Returns:
        dict: 包含直链的响应
    """
    try:
        direct_url = ytdlp_service.get_direct_url(request.url)
        return {"url": direct_url, "success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
