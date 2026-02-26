"""
yt-dlp 服务封装
"""
import yt_dlp
import os
import asyncio
from typing import Dict, List, Optional, Callable
from app.config import settings
from app.models import VideoInfo


class YTDLPService:
    """yt-dlp 服务类"""

    def __init__(self):
        self.download_dir = settings.DOWNLOAD_DIR
        self._ensure_download_dir()

    def _ensure_download_dir(self):
        """确保下载目录存在"""
        os.makedirs(self.download_dir, exist_ok=True)

    def get_video_info(self, url: str) -> VideoInfo:
        """
        获取视频信息（不下载）

        Args:
            url: 视频 URL

        Returns:
            VideoInfo: 视频信息
        """
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            # 避免 YouTube 机器人验证 - 使用更激进的配置
            "nocheckcertificate": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"],
                    "player_skip": ["configs", "webpage"],
                }
            },
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # 提取可用格式
                formats = self._extract_formats(info.get("formats", []))

                # 直接返回字典，不使用 Pydantic 模型验证
                return {
                    "title": info.get("title", "Unknown"),
                    "duration": int(round(info.get("duration", 0))) if info.get("duration") else None,
                    "thumbnail": info.get("thumbnail"),
                    "platform": info.get("extractor_key", "").lower(),
                    "uploader": info.get("uploader"),
                    "view_count": info.get("view_count"),
                    "formats": formats,
                }
        except Exception as e:
            import traceback
            error_detail = f"获取视频信息失败: {str(e)}"
            raise ValueError(error_detail)

    def download_video(
        self,
        url: str,
        format: str = "best",
        quality: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        下载视频

        Args:
            url: 视频 URL
            format: 视频格式
            quality: 视频质量
            progress_callback: 进度回调函数

        Returns:
            str: 下载文件路径
        """
        # 构建格式过滤器
        format_selector = self._build_format_selector(format, quality)

        ydl_opts = {
            "format": format_selector,
            "outtmpl": os.path.join(self.download_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [self._build_progress_hook(progress_callback)],
            # 避免 YouTube 机器人验证
            "nocheckcertificate": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"],
                    "player_skip": ["configs", "webpage"],
                }
            },
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                return file_path
        except Exception as e:
            raise ValueError(f"下载视频失败: {str(e)}")

    def get_direct_url(
        self, url: str, format: str = "best", quality: Optional[str] = None
    ) -> str:
        """
        获取视频直链

        Args:
            url: 视频 URL
            format: 视频格式
            quality: 视频质量

        Returns:
            str: 视频直链
        """
        format_selector = self._build_format_selector(format, quality)

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "format": format_selector,
            # 避免 YouTube 机器人验证
            "nocheckcertificate": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"],
                }
            },
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                # 获取最佳格式的 URL
                if "url" in info:
                    return info["url"]
                # 如果没有直接 URL，尝试从 formats 中获取
                formats = info.get("formats", [])
                if formats:
                    return formats[0].get("url", "")
                raise ValueError("无法获取视频直链")
        except Exception as e:
            raise ValueError(f"获取视频直链失败: {str(e)}")

    def _build_format_selector(self, format: str, quality: Optional[str]) -> str:
        """构建格式选择器"""
        if quality:
            # 指定质量
            return f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
        return format

    def _build_progress_hook(self, callback: Optional[Callable]):
        """构建进度钩子"""

        def hook(d: dict):
            if d["status"] == "downloading" and callback:
                progress_data = {
                    "progress": d.get("_percent_str", "0%").replace("%", ""),
                    "speed": d.get("_speed_str", "0KB/s"),
                    "eta": d.get("_eta_str", "00:00"),
                    "downloaded_bytes": d.get("downloaded_bytes", 0),
                    "total_bytes": d.get("total_bytes") or d.get("total_bytes_estimate", 0),
                }
                callback(progress_data)
            elif d["status"] == "finished" and callback:
                callback({"status": "finished"})

        return hook

    def _extract_formats(self, formats: List[dict]) -> List[dict]:
        """提取可用格式"""
        common_formats = []
        seen = set()

        # 定义常用质量
        preferred_heights = [1080, 720, 480, 360, 240]

        for f in formats:
            # 跳过只有音频的格式（用于视频下载）
            if f.get("vcodec") == "none":
                continue

            height = f.get("height")
            ext = f.get("ext")
            file_size = f.get("filesize")

            # 创建唯一标识
            key = (ext, height)

            if key not in seen and height:
                seen.add(key)
                common_formats.append(
                    {
                        "format_id": f.get("format_id"),
                        "ext": ext,
                        "quality": f"{height}p",
                        "filesize": file_size,
                        "fps": f.get("fps"),
                    }
                )

        # 按质量排序（1080p -> 240p）
        def sort_key(f):
            quality_str = f.get("quality", "0p").replace("p", "")
            try:
                return -int(quality_str)
            except:
                return 0

        common_formats.sort(key=sort_key)

        return common_formats[:10]  # 限制返回数量


# 全局实例
ytdlp_service = YTDLPService()
