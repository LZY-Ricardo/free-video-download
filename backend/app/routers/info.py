"""
信息获取 API
"""
import re
from fastapi import APIRouter, HTTPException
from app.models import InfoRequest
from app.services.ytdlp_service import ytdlp_service
from app.services.douyin_service import douyin_service

router = APIRouter(prefix="/api", tags=["info"])


def is_douyin_url(url: str) -> bool:
    """检测是否为抖音链接"""
    douyin_domains = [
        'douyin.com',
        'iesdouyin.com',
        'v.douyin.com',
    ]
    return any(domain in url for domain in douyin_domains)


@router.post("/info")
async def get_video_info(request: InfoRequest) -> dict:
    """
    获取视频信息（不下载）

    Args:
        request: 包含视频 URL 的请求

    Returns:
        dict: 视频信息
    """
    try:
        # 检测是否为抖音链接
        if is_douyin_url(request.url):
            # 使用抖音专用服务
            info = douyin_service.get_video_info(request.url)

            # 使用从API获取的格式列表，如果没有则提供默认格式
            formats = info.get('formats', [{
                'format_id': 'douyin_default',
                'ext': 'mp4',
                'quality': '720p',
                'quality_label': '高清',
                'filesize': None,
                'filesize_mb': None,
                'filesize_display': '未知大小（推荐）',
                'resolution': '1280x720',
                'fps': 30,
                'fps_display': '30 FPS',
                'is_default': True
            }])

            return {
                "title": info['title'],
                "duration": info['duration'],
                "thumbnail": info['thumbnail'],
                "platform": "douyin",
                "uploader": info['uploader'],
                "view_count": info.get('view_count', 0),
                "formats": formats,
                "is_douyin": True,
                "direct_url": info.get('direct_url', ''),
                "note": "抖音视频使用专用解析器，支持无水印下载"
            }
        else:
            # 使用 yt-dlp 处理其他平台
            video_info = ytdlp_service.get_video_info(request.url)
            return {
                **video_info,
                "is_douyin": False,
            }

    except ValueError as e:
        error_msg = str(e)
        # 检查是否是抖音相关的错误
        if 'cookie' in error_msg.lower() or 'douyin' in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="抖音视频需要浏览器 cookies 才能下载。建议使用其他平台的视频，或使用命令行工具：yt-dlp --cookies-from-browser chrome \"视频链接\""
            )
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
