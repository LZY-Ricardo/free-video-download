from __future__ import annotations

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock
from typing import Any, Annotated

import yt_dlp
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from urllib.request import Request, urlopen


DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = FastAPI(title="VidGrab Local Resolver", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=2)


def get_resolver_token() -> str:
    return (os.getenv("RESOLVER_API_TOKEN") or "").strip()


def require_resolver_token(
    token: Annotated[str | None, Header(alias="X-Resolver-Token")] = None,
) -> None:
    expected_token = get_resolver_token()
    if not expected_token:
        return
    if token != expected_token:
        raise HTTPException(status_code=401, detail="本地解析节点未授权")


class InfoRequest(BaseModel):
    url: str


class DownloadRequest(BaseModel):
    url: str
    format: str = "best"
    quality: str | None = None


@dataclass
class TaskRecord:
    task_id: str
    status: str = "processing"
    progress: float = 0.0
    speed: str = "0KB/s"
    eta: int = 0
    file_path: str | None = None
    error: str | None = None


TASKS: dict[str, TaskRecord] = {}
TASK_LOCK = Lock()

PLATFORM_REFERERS = {
    "bilibili": "https://www.bilibili.com/",
    "youtube": "https://www.youtube.com/",
    "tiktok": "https://www.tiktok.com/",
    "instagram": "https://www.instagram.com/",
}


def _base_opts() -> dict[str, Any]:
    # 通用选项：浏览器 cookies 在具体策略中按优先级注入
    return {
        "quiet": True,
        "no_warnings": True,
        "no_color": True,
        "nocheckcertificate": True,
    }


def _iter_cookie_strategies() -> list[dict[str, Any]]:
    return [
        {"cookiesfrombrowser": ("chrome",)},
        {"cookiesfrombrowser": ("edge",)},
        {},
    ]


def _extract_with_fallback(url: str, download: bool, extra_opts: dict[str, Any]) -> tuple[dict[str, Any], str]:
    errors: list[str] = []
    for strategy in _iter_cookie_strategies():
        opts = _base_opts()
        opts.update(extra_opts)
        opts.update(strategy)
        strategy_name = strategy.get("cookiesfrombrowser", ("none",))[0]
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info_obj = ydl.extract_info(url, download=download)
            return info_obj, str(strategy_name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{strategy_name}: {exc}")
            continue
    raise ValueError(" | ".join(errors))


def _extract_formats(formats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[tuple[str | None, int | None]] = set()
    for item in formats:
        if item.get("vcodec") == "none":
            continue
        height = item.get("height")
        width = item.get("width")
        ext = item.get("ext")
        if not height or not width:
            continue
        key = (ext, height)
        if key in seen:
            continue
        seen.add(key)
        size = item.get("filesize")
        size_mb = round(size / (1024 * 1024), 2) if size else None
        result.append(
            {
                "format_id": item.get("format_id"),
                "ext": ext,
                "quality": f"{height}p",
                "filesize": size,
                "filesize_mb": size_mb,
                "filesize_display": f"{size_mb} MB" if size_mb else "未知大小",
                "resolution": f"{width}x{height}",
                "fps": item.get("fps"),
                "fps_display": f"{item.get('fps')} FPS" if item.get("fps") else "未知",
            }
        )
    result.sort(key=lambda x: int(str(x.get("quality", "0p")).replace("p", "") or "0"), reverse=True)
    return result[:10]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/info")
def info(req: InfoRequest, _: None = Depends(require_resolver_token)) -> dict[str, Any]:
    try:
        info_obj, strategy = _extract_with_fallback(
            req.url,
            download=False,
            extra_opts={"skip_download": True},
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"本地解析失败: {exc}") from exc

    return {
        "title": info_obj.get("title", "Unknown"),
        "duration": int(round(info_obj.get("duration", 0))) if info_obj.get("duration") else None,
        "thumbnail": info_obj.get("thumbnail"),
        "platform": (info_obj.get("extractor_key") or "").lower(),
        "uploader": info_obj.get("uploader"),
        "view_count": info_obj.get("view_count"),
        "formats": _extract_formats(info_obj.get("formats", [])),
        "note": f"由本地解析助手提供（策略: {strategy}）",
    }


def _update_task(task_id: str, **fields: Any) -> None:
    with TASK_LOCK:
        task = TASKS.get(task_id)
        if not task:
            return
        for key, value in fields.items():
            setattr(task, key, value)


def _build_format_selector(fmt: str, quality: str | None) -> str:
    if quality:
        return f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
    return fmt or "best"


def _run_download(task_id: str, req: DownloadRequest) -> None:
    def hook(payload: dict[str, Any]) -> None:
        if payload.get("status") == "downloading":
            _update_task(
                task_id,
                progress=float(str(payload.get("_percent_str", "0")).replace("%", "").strip() or 0),
                speed=str(payload.get("_speed_str", "0KB/s")),
            )
        elif payload.get("status") == "finished":
            _update_task(task_id, progress=100.0)

    try:
        info_obj, _ = _extract_with_fallback(
            req.url,
            download=True,
            extra_opts={
                "format": _build_format_selector(req.format, req.quality),
                "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
                "progress_hooks": [hook],
                "overwrite": True,
            },
        )
        with yt_dlp.YoutubeDL(_base_opts()) as ydl:
            file_path = ydl.prepare_filename(info_obj)
        _update_task(task_id, status="completed", progress=100.0, file_path=file_path)
    except Exception as exc:  # noqa: BLE001
        _update_task(task_id, status="failed", error=f"本地下载失败: {exc}")


@app.post("/api/download")
def download(req: DownloadRequest, _: None = Depends(require_resolver_token)) -> dict[str, str]:
    task_id = str(uuid.uuid4())
    with TASK_LOCK:
        TASKS[task_id] = TaskRecord(task_id=task_id)
    executor.submit(_run_download, task_id, req)
    return {"task_id": task_id, "status": "processing"}


@app.get("/api/proxy/image")
def proxy_image(
    url: str = Query(..., description="图片 URL"),
    platform: str | None = Query(None, description="平台名"),
    _: None = Depends(require_resolver_token),
) -> Response:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    if platform and platform in PLATFORM_REFERERS:
        headers["Referer"] = PLATFORM_REFERERS[platform]
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            data = resp.read()
            content_type = resp.headers.get("Content-Type", "image/jpeg")
        return Response(content=data, media_type=content_type)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"本地图片代理失败: {exc}") from exc


@app.get("/api/download/status/{task_id}")
def download_status(task_id: str, _: None = Depends(require_resolver_token)) -> dict[str, Any]:
    with TASK_LOCK:
        task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "speed": task.speed,
        "eta": task.eta,
        "file_path": task.file_path,
        "error": task.error,
    }


@app.get("/api/download/file/{task_id}")
def download_file(task_id: str, _: None = Depends(require_resolver_token)) -> FileResponse:
    with TASK_LOCK:
        task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.status != "completed" or not task.file_path:
        raise HTTPException(status_code=400, detail="任务尚未完成")
    if not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    filename = os.path.basename(task.file_path)
    return FileResponse(path=task.file_path, filename=filename, media_type="application/octet-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=61337, reload=False)
