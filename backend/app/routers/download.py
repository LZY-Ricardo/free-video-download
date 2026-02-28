"""
下载 API
"""
import asyncio
import os
import re
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models import DownloadRequest, DownloadResponse, TaskStatus
from app.services.ytdlp_service import ytdlp_service
from app.services.douyin_service import douyin_service
from app.services.task_manager import task_manager
from app.config import settings

router = APIRouter(prefix="/api", tags=["download"])

# 创建线程池用于真正的后台下载
executor = ThreadPoolExecutor(max_workers=3)


def is_douyin_url(url: str) -> bool:
    """检测是否为抖音链接"""
    douyin_domains = [
        'douyin.com',
        'iesdouyin.com',
        'v.douyin.com',
    ]
    return any(domain in url for domain in douyin_domains)


@router.post("/download", response_model=DownloadResponse)
async def start_download(request: DownloadRequest):
    """
    开始下载视频

    Args:
        request: 下载请求

    Returns:
        DownloadResponse: 包含任务 ID 的响应
    """
    # 创建任务
    task_id = task_manager.create_task(request.url)

    # 在线程池中运行下载（不等待，fire-and-forget）
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        executor,
        _run_download,
        task_id,
        request.url,
        request.format,
        request.quality
    )

    return DownloadResponse(task_id=task_id, status="processing")


def _run_download(task_id: str, url: str, format: str, quality: str):
    """运行下载任务（在线程中运行）"""
    try:
        # 更新状态为下载中
        task_manager.update_task(task_id, status="downloading")

        # 检测是否为抖音链接
        if is_douyin_url(url):
            # 使用抖音专用下载
            file_name = f"douyin_{task_id}.mp4"
            file_path = os.path.join(settings.DOWNLOAD_DIR, file_name)

            douyin_service.download_video(url, file_path)

            task_manager.update_task(
                task_id, status="completed", file_path=file_path, progress=100.0
            )
        else:
            # 使用 yt-dlp 下载
            def progress_callback(data):
                if data.get("status") == "finished":
                    task_manager.update_task(task_id, progress=100, status="completed")
                else:
                    progress = float(data.get("progress", 0))
                    speed = data.get("speed", "0KB/s")
                    task_manager.update_task(
                        task_id,
                        progress=progress,
                        speed=speed,
                    )

            # 开始下载
            file_path = ytdlp_service.download_video(
                url=url, format=format, quality=quality, progress_callback=progress_callback
            )

            # 下载完成
            task_manager.update_task(
                task_id, status="completed", file_path=file_path, progress=100.0
            )

    except Exception as e:
        # 下载失败
        import traceback
        error_msg = str(e)
        print(f"Download error: {error_msg}")
        traceback.print_exc()
        task_manager.update_task(task_id, status="failed", error=error_msg)


@router.get("/download/status/{task_id}", response_model=TaskStatus)
async def get_download_status(task_id: str):
    """
    获取下载状态

    Args:
        task_id: 任务 ID

    Returns:
        TaskStatus: 任务状态
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return TaskStatus(
        task_id=task.task_id,
        status=task.status,
        progress=task.progress,
        speed=task.speed,
        eta=task.eta,
        file_path=task.file_path,
        error=task.error,
    )


@router.get("/download/file/{task_id}")
async def download_file(task_id: str):
    """
    下载已完成的文件

    Args:
        task_id: 任务 ID

    Returns:
        FileResponse: 文件响应
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    if not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 返回文件
    filename = os.path.basename(task.file_path)
    # 处理中文文件名编码
    try:
        from urllib.parse import quote
        filename_encoded = quote(filename)
    except:
        filename_encoded = filename

    return FileResponse(
        path=task.file_path,
        filename=filename,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"
        }
    )


@router.delete("/download/{task_id}")
async def cancel_download(task_id: str):
    """
    取消下载

    Args:
        task_id: 任务 ID

    Returns:
        dict: 操作结果
    """
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status == "completed":
        raise HTTPException(status_code=400, detail="任务已完成，无法取消")

    task_manager.update_task(task_id, status="cancelled")
    task_manager.delete_task(task_id)

    return {"message": "任务已取消"}
