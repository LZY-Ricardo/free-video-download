from __future__ import annotations

import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from threading import Lock
from typing import Any, Annotated

import shutil
import subprocess
import yt_dlp
from faster_whisper import WhisperModel
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from urllib.request import Request, urlopen
from urllib.parse import urlencode


TIMECODE_PATTERN = __import__("re").compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2}[.,]\d{3})"
)
HTML_TAG_PATTERN = __import__("re").compile(r"<[^>]+>")
WHITESPACE_PATTERN = __import__("re").compile(r"\s+")


DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
BASE_DIR = Path(os.path.dirname(__file__))
MODELS_DIR = BASE_DIR / "models"
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "small")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

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


class LocalAnalyzePrepareResponse(BaseModel):
    video_title: str
    transcript: list[dict[str, Any]]
    transcript_language: str | None = None
    source_url: str | None = None


@dataclass
class TaskRecord:
    task_id: str
    status: str = "processing"
    progress: float = 0.0
    speed: str = "0KB/s"
    eta: int = 0
    file_path: str | None = None
    error: str | None = None


@dataclass
class PrepareTaskRecord:
    task_id: str
    status: str = "processing"
    result: dict[str, Any] | None = None
    error: str | None = None


TASKS: dict[str, TaskRecord] = {}
TASK_LOCK = Lock()
PREPARE_TASKS: dict[str, PrepareTaskRecord] = {}
PREPARE_TASK_LOCK = Lock()
WHISPER_MODEL: WhisperModel | None = None
WHISPER_MODEL_LOCK = Lock()

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


PREFERRED_LANGUAGES = ["zh-Hans", "zh-CN", "zh", "en", "en-US"]


def _pick_subtitle_track(info: dict[str, Any]) -> tuple[str | None, str | None]:
    subtitles = info.get("subtitles") or {}
    auto_captions = info.get("automatic_captions") or {}

    url, language = _pick_from_tracks(subtitles)
    if url:
        return url, language

    url, language = _pick_from_tracks(auto_captions)
    if url:
        return url, language

    bilibili_url, bilibili_lang = _try_bilibili_subtitle(info)
    if bilibili_url:
        return bilibili_url, bilibili_lang

    return None, None


def _pick_from_tracks(tracks: dict[str, Any]) -> tuple[str | None, str | None]:
    if not tracks:
        return None, None

    for lang in PREFERRED_LANGUAGES:
        selected = _pick_subtitle_entry(tracks.get(lang))
        if selected:
            return selected, lang

    for lang, entries in tracks.items():
        selected = _pick_subtitle_entry(entries)
        if selected:
            return selected, str(lang)
    return None, None


def _pick_subtitle_entry(entries: Any) -> str | None:
    if not isinstance(entries, list):
        return None

    preferred_ext_order = ["vtt", "srt", "ttml", "srv3", "srv2", "srv1"]
    sorted_entries = sorted(
        entries,
        key=lambda item: preferred_ext_order.index(item.get("ext"))
        if item.get("ext") in preferred_ext_order
        else len(preferred_ext_order),
    )
    for entry in sorted_entries:
        subtitle_url = entry.get("url")
        ext = (entry.get("ext") or "").lower()
        if ext == "xml":
            continue
        if subtitle_url and "comment.bilibili.com" not in subtitle_url:
            return str(subtitle_url)
    return None


def _extract_bvid(info: dict[str, Any]) -> str | None:
    import re

    bvid_pattern = re.compile(r"(BV[0-9A-Za-z]{10})", re.IGNORECASE)
    for field in ("id", "webpage_url", "original_url"):
        value = info.get(field)
        if not value:
            continue
        match = bvid_pattern.search(str(value))
        if match:
            return match.group(1)
    return None


def _pick_bilibili_subtitle(subtitle_list: list[dict[str, Any]]) -> dict[str, Any] | None:
    for preferred in PREFERRED_LANGUAGES:
        for item in subtitle_list:
            if (item.get("lan") or "").lower() == preferred.lower():
                return item
    return subtitle_list[0] if subtitle_list else None


def _try_bilibili_subtitle(info: dict[str, Any]) -> tuple[str | None, str | None]:
    extractor_key = (info.get("extractor_key") or "").lower()
    if "bili" not in extractor_key:
        return None, None

    bvid = _extract_bvid(info)
    if not bvid:
        return None, None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": f"https://www.bilibili.com/video/{bvid}",
        }
        view_url = f"https://api.bilibili.com/x/web-interface/view?{urlencode({'bvid': bvid})}"
        with urlopen(Request(view_url, headers=headers), timeout=15) as response:
            view_data = __import__("json").loads(response.read().decode("utf-8"))
        cid = ((view_data.get("data") or {}).get("cid"))
        if not cid:
            return None, None

        player_url = (
            "https://api.bilibili.com/x/player/v2?"
            + urlencode({"cid": cid, "bvid": bvid})
        )
        with urlopen(Request(player_url, headers=headers), timeout=15) as response:
            player_data = __import__("json").loads(response.read().decode("utf-8"))
        subtitle_list = (((player_data.get("data") or {}).get("subtitle") or {}).get("subtitles") or [])
        selected = _pick_bilibili_subtitle(subtitle_list)
        if not selected:
            return None, None

        subtitle_url = selected.get("subtitle_url")
        if not subtitle_url:
            return None, None
        if str(subtitle_url).startswith("//"):
            subtitle_url = f"https:{subtitle_url}"
        return str(subtitle_url), str(selected.get("lan") or selected.get("lan_doc") or "")
    except Exception:
        return None, None


def _download_subtitle(subtitle_url: str) -> str:
    try:
        with urlopen(Request(subtitle_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15) as response:
            return response.read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"字幕下载失败: {exc}") from exc


def _timecode_to_seconds(value: str) -> float:
    value = value.replace(",", ".")
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _format_timestamp(seconds: float) -> str:
    total_seconds = int(max(0, seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _parse_json_subtitle(raw: str) -> list[dict[str, Any]]:
    content = raw.strip()
    if not content or not content.startswith("{"):
        return []
    try:
        payload = __import__("json").loads(content)
    except Exception:
        return []

    body = payload.get("body")
    if not isinstance(body, list):
        return []

    segments: list[dict[str, Any]] = []
    for item in body:
        if not isinstance(item, dict):
            continue
        start = float(item.get("from", 0))
        end = float(item.get("to", start))
        text = WHITESPACE_PATTERN.sub(" ", unescape(str(item.get("content") or ""))).strip()
        if not text:
            continue
        segments.append(
            {
                "start": round(start, 3),
                "end": round(end, 3),
                "timestamp": _format_timestamp(start),
                "text": text,
            }
        )
    return segments


def _build_segment(start: float, end: float, lines: list[str]) -> dict[str, Any] | None:
    text = " ".join(lines)
    text = HTML_TAG_PATTERN.sub("", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    if not text:
        return None
    return {
        "start": round(start, 3),
        "end": round(end, 3),
        "timestamp": _format_timestamp(start),
        "text": text,
    }


def _parse_subtitle(raw: str) -> list[dict[str, Any]]:
    json_segments = _parse_json_subtitle(raw)
    if json_segments:
        return json_segments

    segments: list[dict[str, Any]] = []
    current_start: float | None = None
    current_end: float | None = None
    buffer: list[str] = []

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            if current_start is not None and buffer:
                segment = _build_segment(current_start, current_end or current_start, buffer)
                if segment:
                    segments.append(segment)
            current_start = None
            current_end = None
            buffer = []
            continue

        match = TIMECODE_PATTERN.search(stripped)
        if match:
            if current_start is not None and buffer:
                segment = _build_segment(current_start, current_end or current_start, buffer)
                if segment:
                    segments.append(segment)
            current_start = _timecode_to_seconds(match.group("start"))
            current_end = _timecode_to_seconds(match.group("end"))
            buffer = []
            continue

        if (
            stripped.startswith("WEBVTT")
            or stripped.startswith("NOTE")
            or stripped.startswith("Kind:")
            or stripped.startswith("Language:")
            or stripped.isdigit()
        ):
            continue

        buffer.append(stripped)

    if current_start is not None and buffer:
        segment = _build_segment(current_start, current_end or current_start, buffer)
        if segment:
            segments.append(segment)

    return segments


def _download_media_for_asr(url: str, info: dict[str, Any]) -> Path | None:
    media_id = str(info.get("id") or "video").strip() or "video"
    safe_media_id = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in media_id)
    outtmpl = str(BASE_DIR / "downloads" / f"asr_src_{safe_media_id}_%(autonumber)s.%(ext)s")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "no_color": True,
        "nocheckcertificate": True,
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "overwrites": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_obj = ydl.extract_info(url, download=True)
            downloaded = Path(ydl.prepare_filename(info_obj))
            if downloaded.exists():
                return downloaded
    except Exception:
        return None
    return None


def _cleanup_temp_media(media_path: Path | None) -> None:
    if not media_path:
        return
    try:
        media_path.unlink(missing_ok=True)
    except Exception:
        pass


def _ensure_whisper_model() -> WhisperModel:
    global WHISPER_MODEL

    if WHISPER_MODEL is not None:
        return WHISPER_MODEL

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with WHISPER_MODEL_LOCK:
        if WHISPER_MODEL is None:
            WHISPER_MODEL = WhisperModel(
                WHISPER_MODEL_SIZE,
                device="cpu",
                compute_type=WHISPER_COMPUTE_TYPE,
                download_root=str(MODELS_DIR),
            )
    return WHISPER_MODEL


def _transcribe_local_video_with_whisper(video_path: Path) -> list[dict[str, Any]]:
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise ValueError("未检测到 ffmpeg，无法进行本地语音转写。")

    model = _ensure_whisper_model()

    try:
        segments, _info = model.transcribe(
            str(video_path),
            language="zh",
            vad_filter=True,
            beam_size=1,
        )
        transcript = [
            {
                "start": round(float(segment.start), 3),
                "end": round(float(segment.end), 3),
                "timestamp": _format_timestamp(float(segment.start)),
                "text": WHITESPACE_PATTERN.sub(" ", str(segment.text or "")).strip(),
            }
            for segment in segments
            if str(segment.text or "").strip()
        ]
        if not transcript:
            raise ValueError("本地转写结果为空。")
        return transcript
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"本地语音转写失败: {exc}") from exc


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


@app.post("/api/ai/prepare", response_model=LocalAnalyzePrepareResponse)
def prepare_ai_analysis(req: InfoRequest, _: None = Depends(require_resolver_token)) -> dict[str, Any]:
    temp_media_path: Path | None = None
    try:
        info_obj, _ = _extract_with_fallback(
            req.url,
            download=False,
            extra_opts={"skip_download": True, "writesubtitles": True, "writeautomaticsub": True, "subtitleslangs": ["all"]},
        )
        subtitle_url, language = _pick_subtitle_track(info_obj)
        transcript: list[dict[str, Any]] = []
        if subtitle_url:
            subtitle_content = _download_subtitle(subtitle_url)
            transcript = _parse_subtitle(subtitle_content)
        else:
            temp_media_path = _download_media_for_asr(req.url, info_obj)
            if not temp_media_path:
                raise ValueError("本地解析未找到可用字幕，且无法准备音频转写。")
            transcript = _transcribe_local_video_with_whisper(temp_media_path)
            language = language or "zh-ASR"

        if not transcript:
            raise ValueError("本地字幕解析/转写为空，无法继续 AI 分析。")

        return {
            "video_title": info_obj.get("title", "Unknown"),
            "transcript": transcript,
            "transcript_language": language,
            "source_url": req.url,
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"本地 AI 预处理失败: {exc}") from exc
    finally:
        _cleanup_temp_media(temp_media_path)


def _run_prepare_ai_analysis(task_id: str, url: str) -> None:
    temp_media_path: Path | None = None
    try:
        info_obj, _ = _extract_with_fallback(
            url,
            download=False,
            extra_opts={"skip_download": True, "writesubtitles": True, "writeautomaticsub": True, "subtitleslangs": ["all"]},
        )
        subtitle_url, language = _pick_subtitle_track(info_obj)
        transcript: list[dict[str, Any]] = []
        if subtitle_url:
            subtitle_content = _download_subtitle(subtitle_url)
            transcript = _parse_subtitle(subtitle_content)
        else:
            temp_media_path = _download_media_for_asr(url, info_obj)
            if not temp_media_path:
                raise ValueError("本地解析未找到可用字幕，且无法准备音频转写。")
            transcript = _transcribe_local_video_with_whisper(temp_media_path)
            language = language or "zh-ASR"

        if not transcript:
            raise ValueError("本地字幕解析/转写为空，无法继续 AI 分析。")

        result = {
            "video_title": info_obj.get("title", "Unknown"),
            "transcript": transcript,
            "transcript_language": language,
            "source_url": url,
        }
        with PREPARE_TASK_LOCK:
            task = PREPARE_TASKS.get(task_id)
            if task:
                task.status = "completed"
                task.result = result
                task.error = None
    except Exception as exc:  # noqa: BLE001
        with PREPARE_TASK_LOCK:
            task = PREPARE_TASKS.get(task_id)
            if task:
                task.status = "failed"
                task.error = f"本地 AI 预处理失败: {exc}"
    finally:
        _cleanup_temp_media(temp_media_path)


@app.post("/api/ai/prepare/start")
def prepare_ai_analysis_start(req: InfoRequest, _: None = Depends(require_resolver_token)) -> dict[str, str]:
    task_id = str(uuid.uuid4())
    with PREPARE_TASK_LOCK:
        PREPARE_TASKS[task_id] = PrepareTaskRecord(task_id=task_id)
    executor.submit(_run_prepare_ai_analysis, task_id, req.url)
    return {"task_id": task_id, "status": "processing"}


@app.get("/api/ai/prepare/status/{task_id}")
def prepare_ai_analysis_status(task_id: str, _: None = Depends(require_resolver_token)) -> dict[str, Any]:
    with PREPARE_TASK_LOCK:
        task = PREPARE_TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="AI 预处理任务不存在")

    payload: dict[str, Any] = {
        "task_id": task.task_id,
        "status": task.status,
    }
    if task.error:
        payload["error"] = task.error
    if task.result:
        payload["result"] = task.result
    return payload


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
