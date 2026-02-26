"""
下载 API
"""
import asyncio
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.models import DownloadRequest, DownloadResponse, TaskStatus
from app.services.ytdlp_service import ytdlp_service
from app.services.task_manager import task_manager
from app.config import settings

router = APIRouter(prefix="/api", tags=["download"])


@router.post("/download", response_model=DownloadResponse)
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """
    开始下载视频

    Args:
        request: 下载请求
        background_tasks: 后台任务

    Returns:
        DownloadResponse: 包含任务 ID 的响应
    """
    # 创建任务
    task_id = task_manager.create_task(request.url)

    # 在后台启动下载
    background_tasks.add_task(
        _run_download, task_id, request.url, request.format, request.quality
    )

    return DownloadResponse(task_id=task_id, status="processing")


async def _run_download(task_id: str, url: str, format: str, quality: str):
    """运行下载任务"""
    try:
        # 更新状态为下载中
        task_manager.update_task(task_id, status="downloading")

        # 定义进度回调
        def progress_callback(data):
            if data.get("status") == "finished":
                task_manager.update_task(task_id, progress=100, status="completed")
            else:
                task_manager.update_task(
                    task_id,
                    progress=float(data.get("progress", 0)),
                    speed=data.get("speed", "0KB/s"),
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
        task_manager.update_task(task_id, status="failed", error=str(e))


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
    return FileResponse(
        path=task.file_path, filename=filename, media_type="application/octet-stream"
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
