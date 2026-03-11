"""
视频 AI 分析服务
"""
from __future__ import annotations

import json
import re
import uuid
from html import unescape
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse
from pathlib import Path
import shutil
import subprocess

import httpx
import yt_dlp

from app.config import settings
from app.models import (
    ChatCitation,
    ChatResponse,
    MindMapNode,
    AnalyzeTaskStatusResponse,
    SummarySection,
    TranscriptSegment,
    VideoAnalysisResponse,
    VideoSummary,
)


TIMECODE_PATTERN = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2}[.,]\d{3})"
)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


@dataclass
class AnalysisRecord:
    """缓存的分析记录"""

    analysis_id: str
    video_title: str
    transcript_language: Optional[str]
    transcript: List[TranscriptSegment]
    summary: VideoSummary
    mind_map: MindMapNode


@dataclass
class AnalysisTask:
    """异步分析任务"""

    task_id: str
    url: str
    status: str = "pending"
    stage: str = "pending"
    progress: float = 0.0
    error: Optional[str] = None
    result: Optional[VideoAnalysisResponse] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class VideoAIService:
    """视频 AI 功能：摘要、转录、思维导图、问答"""

    def __init__(self):
        self.analysis_cache: Dict[str, AnalysisRecord] = {}
        self.analysis_tasks: Dict[str, AnalysisTask] = {}
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.asr_cache: Dict[str, List[TranscriptSegment]] = {}
        self.preferred_languages = ["zh-Hans", "zh-CN", "zh", "en", "en-US"]
        self.backend_root = Path(__file__).resolve().parents[2]
        self.project_root = self.backend_root.parent
        self.download_dirs = [
            self.project_root,
            self.backend_root / "downloads",
        ]
        self.models_dir = self.backend_root / "models"
        self.whisper_model_path = self.models_dir / "ggml-base.bin"
        self.whisper_model_url = (
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin?download=true"
        )
        self.zh_converter = self._init_zh_converter()

    def _init_zh_converter(self):
        if not settings.AI_NORMALIZE_ZH_TO_SIMPLIFIED:
            return None
        try:
            from opencc import OpenCC

            return OpenCC("t2s")
        except Exception:
            return None

    def analyze_video(self, url: str) -> VideoAnalysisResponse:
        """
        同步分析视频并生成摘要、转录文本和思维导图
        """
        return self._analyze_video_sync(url)

    def start_analysis(self, url: str) -> str:
        """
        创建异步分析任务并立即返回任务 ID
        """
        task_id = str(uuid.uuid4())
        self.analysis_tasks[task_id] = AnalysisTask(task_id=task_id, url=url)
        self.executor.submit(self._run_analysis_task, task_id, url)
        return task_id

    def get_analysis_task(self, task_id: str) -> Optional[AnalyzeTaskStatusResponse]:
        task = self.analysis_tasks.get(task_id)
        if not task:
            return None
        return AnalyzeTaskStatusResponse(
            task_id=task.task_id,
            status=task.status,
            stage=task.stage,
            progress=task.progress,
            error=task.error,
            result=task.result,
        )

    def _run_analysis_task(self, task_id: str, url: str):
        def update(progress: float, stage: str):
            self._update_task(task_id, progress=progress, stage=stage, status="processing")

        self._update_task(task_id, status="processing", stage="解析视频信息", progress=3)
        try:
            result = self._analyze_video_sync(url, progress_callback=update)
            self._update_task(
                task_id,
                status="completed",
                stage="分析完成",
                progress=100.0,
                result=result,
                error=None,
            )
        except Exception as exc:
            self._update_task(
                task_id,
                status="failed",
                stage="分析失败",
                error=str(exc),
            )

    def _update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        stage: Optional[str] = None,
        progress: Optional[float] = None,
        error: Optional[str] = None,
        result: Optional[VideoAnalysisResponse] = None,
    ):
        task = self.analysis_tasks.get(task_id)
        if not task:
            return
        if status is not None:
            task.status = status
        if stage is not None:
            task.stage = stage
        if progress is not None:
            task.progress = max(0.0, min(100.0, float(progress)))
        if error is not None:
            task.error = error
        if result is not None:
            task.result = result
        task.updated_at = datetime.now()

    def _analyze_video_sync(
        self, url: str, progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> VideoAnalysisResponse:
        if progress_callback:
            progress_callback(8, "提取视频信息")
        info = self._extract_video_info(url)
        if progress_callback:
            progress_callback(16, "检测字幕轨道")
        subtitle_url, language = self._pick_subtitle_track(info)

        transcript: List[TranscriptSegment] = []

        if subtitle_url:
            if progress_callback:
                progress_callback(28, "下载字幕文本")
            subtitle_content = self._download_subtitle(subtitle_url)
            transcript = self._parse_subtitle(subtitle_content)
            if progress_callback:
                progress_callback(60, "字幕解析完成")
        else:
            local_video_path = self._find_local_video_file(info, url)
            if local_video_path:
                if progress_callback:
                    progress_callback(25, "开始本地语音转写")
                duration_sec = float(info.get("duration") or 0)
                transcript = self._transcribe_local_video_with_whisper(
                    local_video_path,
                    duration_sec=duration_sec,
                    progress_callback=progress_callback,
                )
                language = "zh-ASR"
                if progress_callback:
                    progress_callback(78, "转写完成")

        if not transcript:
            if self._has_only_danmaku(info):
                raise ValueError(
                    "该视频仅检测到弹幕（danmaku），且未找到可转写的本地视频文件。请先下载到本地后再试 AI 分析。"
                )
            raise ValueError(
                "未找到可用字幕，且无法从本地视频生成转写。请先完成下载后再试。"
            )

        transcript = self._normalize_transcript_script(transcript, language)
        transcript = self._compact_transcript(transcript)

        title = info.get("title") or "未命名视频"
        if progress_callback:
            progress_callback(86, "生成摘要")
        summary = self._generate_summary(title, transcript)
        if progress_callback:
            progress_callback(94, "生成思维导图")
        mind_map = self._build_mind_map(title, summary)

        analysis_id = str(uuid.uuid4())
        record = AnalysisRecord(
            analysis_id=analysis_id,
            video_title=title,
            transcript_language=language,
            transcript=transcript,
            summary=summary,
            mind_map=mind_map,
        )
        self.analysis_cache[analysis_id] = record

        response = VideoAnalysisResponse(
            analysis_id=analysis_id,
            video_title=title,
            transcript_language=language,
            summary=summary,
            transcript=transcript,
            mind_map=mind_map,
        )
        if progress_callback:
            progress_callback(100, "分析完成")
        return response

    def ask_question(self, analysis_id: str, question: str) -> ChatResponse:
        """
        针对指定视频分析结果进行问答
        """
        record, candidates, citation_segments = self._prepare_chat_context(analysis_id, question)
        answer, citations = self._answer_with_ai_or_fallback(
            question=question,
            title=record.video_title,
            candidates=candidates,
            summary=record.summary,
        )
        if not citations:
            citations = citation_segments

        return ChatResponse(
            answer=answer,
            citations=[
                ChatCitation(timestamp=seg.timestamp, text=self._truncate(seg.text, 120))
                for seg in citations
            ],
        )

    def stream_answer(self, analysis_id: str, question: str) -> Iterator[Dict[str, Any]]:
        """
        流式输出问答结果，优先走大模型 token stream，失败时回退本地答案分片输出。
        """
        record, candidates, citation_segments = self._prepare_chat_context(analysis_id, question)
        citations_payload = [
            {
                "timestamp": segment.timestamp,
                "text": self._truncate(segment.text, 120),
            }
            for segment in citation_segments
        ]
        yield {"event": "start", "data": {"citations": citations_payload}}

        streamed = False
        if settings.AI_API_KEY:
            for delta in self._answer_with_ai_stream(
                question=question,
                title=record.video_title,
                candidates=candidates,
                summary=record.summary,
            ):
                if not delta:
                    continue
                streamed = True
                yield {"event": "delta", "data": {"delta": delta}}

        if not streamed:
            fallback_answer = self._build_fallback_answer(candidates)
            for chunk in self._chunk_text_for_stream(fallback_answer):
                yield {"event": "delta", "data": {"delta": chunk}}

        yield {"event": "done", "data": {"citations": citations_payload}}

    def _prepare_chat_context(
        self, analysis_id: str, question: str
    ) -> Tuple[AnalysisRecord, List[TranscriptSegment], List[TranscriptSegment]]:
        record = self.analysis_cache.get(analysis_id)
        if not record:
            raise ValueError("分析任务不存在或已过期，请先重新执行视频分析。")

        candidates = self._retrieve_relevant_segments(question, record.transcript, top_k=6)
        citation_segments = candidates[:4]
        return record, candidates, citation_segments

    def _build_fallback_answer(self, candidates: List[TranscriptSegment]) -> str:
        snippets = [f"[{seg.timestamp}] {seg.text}" for seg in candidates[:4]]
        if not snippets:
            return "暂无足够内容回答该问题，请先执行视频分析。"
        return "根据视频转录内容，与你问题最相关的信息如下：\n" + "\n".join(snippets)

    def _chunk_text_for_stream(self, text: str, chunk_size: int = 24) -> Iterator[str]:
        if not text:
            return
        for index in range(0, len(text), chunk_size):
            yield text[index : index + chunk_size]

    def _extract_video_info(self, url: str) -> dict:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "nocheckcertificate": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["all"],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as exc:
            raise ValueError(f"视频解析失败: {exc}") from exc

    def _pick_subtitle_track(self, info: dict) -> Tuple[Optional[str], Optional[str]]:
        subtitles = info.get("subtitles") or {}
        auto_captions = info.get("automatic_captions") or {}

        # 优先人工字幕
        url, language = self._pick_from_tracks(subtitles)
        if url:
            return url, language

        # 回退自动字幕
        url, language = self._pick_from_tracks(auto_captions)
        if url:
            return url, language

        # B 站兜底：直接请求官方 player/v2 接口获取字幕列表
        bilibili_url, bilibili_lang = self._try_bilibili_subtitle(info)
        if bilibili_url:
            return bilibili_url, bilibili_lang

        return None, None

    def _pick_from_tracks(self, tracks: dict) -> Tuple[Optional[str], Optional[str]]:
        if not tracks:
            return None, None

        # 语言优先级
        for lang in self.preferred_languages:
            entries = tracks.get(lang)
            selected = self._pick_subtitle_entry(entries)
            if selected:
                return selected, lang

        # 兜底：任意第一条
        for lang, entries in tracks.items():
            selected = self._pick_subtitle_entry(entries)
            if selected:
                return selected, lang
        return None, None

    def _pick_subtitle_entry(self, entries: Any) -> Optional[str]:
        if not entries:
            return None
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
            # bilibili danmaku 不是语音字幕，不作为转录来源
            if ext == "xml":
                continue
            if subtitle_url and "comment.bilibili.com" not in subtitle_url:
                return subtitle_url
        return None

    def _try_bilibili_subtitle(self, info: dict) -> Tuple[Optional[str], Optional[str]]:
        extractor_key = (info.get("extractor_key") or "").lower()
        if "bili" not in extractor_key:
            return None, None

        bvid = self._extract_bvid(info)
        if not bvid:
            return None, None

        try:
            with httpx.Client(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                view_resp = client.get(
                    f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                view_resp.raise_for_status()
                view_data = view_resp.json()
                view_payload = view_data.get("data") or {}
                cid = view_payload.get("cid")
                if not cid:
                    return None, None

                player_resp = client.get(
                    f"https://api.bilibili.com/x/player/v2?cid={cid}&bvid={bvid}",
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Referer": f"https://www.bilibili.com/video/{bvid}",
                    },
                )
                player_resp.raise_for_status()
                player_data = player_resp.json()
                subtitle_payload = ((player_data.get("data") or {}).get("subtitle") or {})
                subtitle_list = subtitle_payload.get("subtitles") or []

                if not subtitle_list:
                    return None, None

                selected = self._pick_bilibili_subtitle(subtitle_list)
                if not selected:
                    return None, None

                subtitle_url = selected.get("subtitle_url")
                if not subtitle_url:
                    return None, None
                if subtitle_url.startswith("//"):
                    subtitle_url = f"https:{subtitle_url}"

                lang = selected.get("lan") or selected.get("lan_doc")
                return subtitle_url, lang
        except Exception:
            return None, None

    def _pick_bilibili_subtitle(self, subtitle_list: List[dict]) -> Optional[dict]:
        if not subtitle_list:
            return None

        for preferred in self.preferred_languages:
            for sub in subtitle_list:
                if (sub.get("lan") or "").lower() == preferred.lower():
                    return sub

        return subtitle_list[0]

    def _extract_bvid(self, info: dict) -> Optional[str]:
        bvid_pattern = re.compile(r"(BV[0-9A-Za-z]{10})", re.IGNORECASE)

        for field in ("id", "webpage_url", "original_url"):
            value = info.get(field)
            if not isinstance(value, str):
                continue
            match = bvid_pattern.search(value)
            if match:
                return match.group(1)

        webpage_url = info.get("webpage_url")
        if isinstance(webpage_url, str):
            parsed = urlparse(webpage_url)
            query = parse_qs(parsed.query)
            bvid_values = query.get("bvid")
            if bvid_values:
                return bvid_values[0]
        return None

    def _find_local_video_file(self, info: dict, url: str) -> Optional[Path]:
        """
        在常见目录中查找已下载本地视频，供 ASR 转写使用。
        """
        title = (info.get("title") or "").strip()
        bvid = self._extract_bvid(info) or self._extract_bvid({"webpage_url": url})

        candidates: List[Path] = []
        for base_dir in self.download_dirs:
            if not base_dir.exists():
                continue
            for ext in ("*.mp4", "*.mkv", "*.webm", "*.mov"):
                candidates.extend(base_dir.glob(ext))

        if not candidates:
            return None

        # 1) 标题精确匹配
        if title:
            safe_title = self._safe_filename(title)
            for path in candidates:
                stem = path.stem
                if stem == title or stem == safe_title:
                    return path

        # 2) 标题包含匹配
        if title:
            key = title[:12]
            for path in candidates:
                if key and key in path.stem:
                    return path

        # 3) BVID 匹配
        if bvid:
            for path in candidates:
                if bvid.lower() in path.stem.lower():
                    return path

        # 4) 兜底：取 backend/downloads 中最新文件
        backend_download_dir = self.backend_root / "downloads"
        backend_candidates = [p for p in candidates if p.parent == backend_download_dir]
        if backend_candidates:
            backend_candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return backend_candidates[0]

        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0]

    def _safe_filename(self, value: str) -> str:
        return re.sub(r"[<>:\"/\\\\|?*]+", "_", value).strip()

    def _ensure_whisper_model(self):
        self.models_dir.mkdir(parents=True, exist_ok=True)
        if self.whisper_model_path.exists():
            return

        with httpx.Client(timeout=120) as client:
            response = client.get(self.whisper_model_url)
            response.raise_for_status()
            self.whisper_model_path.write_bytes(response.content)

    def _transcribe_local_video_with_whisper(
        self,
        video_path: Path,
        duration_sec: float = 0,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> List[TranscriptSegment]:
        """
        使用 ffmpeg whisper 滤镜对本地视频做离线转写。
        """
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            raise ValueError("本机未检测到 ffmpeg，无法进行 ASR 转写。")

        cache_key = self._build_asr_cache_key(video_path)
        if cache_key in self.asr_cache:
            if progress_callback:
                progress_callback(74, "命中本地转写缓存")
            return self.asr_cache[cache_key]

        if progress_callback:
            progress_callback(30, "准备转写模型")
        self._ensure_whisper_model()

        output_dir = self.backend_root / "downloads"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_srt = output_dir / f"asr_{uuid.uuid4().hex}.srt"

        model_rel = self.whisper_model_path.relative_to(self.backend_root).as_posix()
        out_rel = output_srt.relative_to(self.backend_root).as_posix()
        if progress_callback:
            progress_callback(34, "正在语音转写")

        run_error: Optional[Exception] = None
        for use_gpu in (True, False):
            filter_expr = (
                f"whisper=model={model_rel}:language=zh:destination={out_rel}:format=srt"
                f":use_gpu={'true' if use_gpu else 'false'}"
            )
            cmd = [
                ffmpeg_bin,
                "-y",
                "-i",
                str(video_path),
                "-vn",
                "-af",
                filter_expr,
                "-progress",
                "pipe:1",
                "-nostats",
                "-f",
                "null",
                "-",
            ]
            try:
                self._run_ffmpeg_with_progress(
                    cmd=cmd,
                    duration_sec=duration_sec,
                    progress_callback=progress_callback,
                    stage="正在语音转写",
                )
                run_error = None
                break
            except Exception as exc:
                run_error = exc
                if output_srt.exists():
                    output_srt.unlink(missing_ok=True)
                continue

        if run_error is not None:
            raise ValueError(f"ASR 转写失败: {run_error}") from run_error

        if not output_srt.exists():
            raise ValueError("ASR 转写失败：未生成字幕文件。")

        try:
            content = output_srt.read_text(encoding="utf-8", errors="ignore")
            segments = self._parse_subtitle(content)
            if cache_key and segments:
                self.asr_cache[cache_key] = segments
            return segments
        finally:
            try:
                output_srt.unlink(missing_ok=True)
            except Exception:
                pass

    def _run_ffmpeg_with_progress(
        self,
        cmd: List[str],
        duration_sec: float,
        progress_callback: Optional[Callable[[float, str], None]],
        stage: str,
    ):
        process = subprocess.Popen(
            cmd,
            cwd=str(self.backend_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1,
        )
        assert process.stdout is not None

        for line in process.stdout:
            if "=" not in line:
                continue
            key, value = line.strip().split("=", 1)
            if key == "out_time_ms" and duration_sec > 0 and progress_callback:
                try:
                    out_ms = int(value)
                    ratio = max(0.0, min(1.0, (out_ms / 1_000_000.0) / duration_sec))
                    progress_callback(34 + ratio * 38, stage)
                except Exception:
                    pass

        code = process.wait()
        if code != 0:
            raise RuntimeError(f"ffmpeg exited with code {code}")

    def _build_asr_cache_key(self, video_path: Path) -> str:
        try:
            stat = video_path.stat()
            return f"{video_path.resolve()}:{int(stat.st_mtime)}:{stat.st_size}"
        except Exception:
            return str(video_path.resolve())

    def _has_only_danmaku(self, info: dict) -> bool:
        subtitles = info.get("subtitles") or {}
        if not isinstance(subtitles, dict):
            return False

        if not subtitles:
            return False

        # 只存在 danmaku 语言或 xml/comment.bilibili.com 轨道，视为无可用字幕
        keys = {str(k).lower() for k in subtitles.keys()}
        if keys != {"danmaku"}:
            return False

        entries = subtitles.get("danmaku") or []
        if not isinstance(entries, list) or not entries:
            return True

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            ext = (entry.get("ext") or "").lower()
            url = str(entry.get("url") or "")
            if ext != "xml" and "comment.bilibili.com" not in url:
                return False
        return True

    def _download_subtitle(self, subtitle_url: str) -> str:
        try:
            with httpx.Client(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                response = client.get(subtitle_url)
                response.raise_for_status()
                return response.text
        except Exception as exc:
            raise ValueError(f"字幕下载失败: {exc}") from exc

    def _parse_subtitle(self, raw: str) -> List[TranscriptSegment]:
        json_segments = self._parse_json_subtitle(raw)
        if json_segments:
            return json_segments

        segments: List[TranscriptSegment] = []
        current_start: Optional[float] = None
        current_end: Optional[float] = None
        buffer: List[str] = []

        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped:
                if current_start is not None and buffer:
                    segment = self._build_segment(current_start, current_end or current_start, buffer)
                    if segment:
                        segments.append(segment)
                current_start = None
                current_end = None
                buffer = []
                continue

            match = TIMECODE_PATTERN.search(stripped)
            if match:
                if current_start is not None and buffer:
                    segment = self._build_segment(current_start, current_end or current_start, buffer)
                    if segment:
                        segments.append(segment)
                current_start = self._timecode_to_seconds(match.group("start"))
                current_end = self._timecode_to_seconds(match.group("end"))
                buffer = []
                continue

            # 跳过 WEBVTT 元数据行
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
            segment = self._build_segment(current_start, current_end or current_start, buffer)
            if segment:
                segments.append(segment)

        return segments

    def _parse_json_subtitle(self, raw: str) -> List[TranscriptSegment]:
        content = raw.strip()
        if not content or not content.startswith("{"):
            return []

        try:
            payload = json.loads(content)
        except Exception:
            return []

        body = payload.get("body")
        if not isinstance(body, list):
            return []

        segments: List[TranscriptSegment] = []
        for item in body:
            if not isinstance(item, dict):
                continue
            start = float(item.get("from", 0))
            end = float(item.get("to", start))
            text = item.get("content") or ""
            text = WHITESPACE_PATTERN.sub(" ", unescape(str(text))).strip()
            if not text:
                continue
            segments.append(
                TranscriptSegment(
                    start=round(start, 3),
                    end=round(end, 3),
                    timestamp=self._format_timestamp(start),
                    text=text,
                )
            )
        return segments

    def _build_segment(self, start: float, end: float, lines: List[str]) -> Optional[TranscriptSegment]:
        text = " ".join(lines)
        text = HTML_TAG_PATTERN.sub("", text)
        text = text.replace("&nbsp;", " ").replace("&amp;", "&")
        text = WHITESPACE_PATTERN.sub(" ", text).strip()
        if not text:
            return None
        return TranscriptSegment(
            start=round(start, 3),
            end=round(end, 3),
            timestamp=self._format_timestamp(start),
            text=text,
        )

    def _compact_transcript(self, segments: List[TranscriptSegment]) -> List[TranscriptSegment]:
        """
        清洗重复片段并限制数量，避免请求过大
        """
        deduped: List[TranscriptSegment] = []
        last_text = ""

        for segment in segments:
            if segment.text == last_text:
                continue
            deduped.append(segment)
            last_text = segment.text
            if len(deduped) >= settings.AI_MAX_TRANSCRIPT_SEGMENTS:
                break

        return deduped

    def _normalize_transcript_script(
        self, segments: List[TranscriptSegment], language: Optional[str]
    ) -> List[TranscriptSegment]:
        """
        将简繁混合文本统一成简体中文，改善转写阅读体验。
        """
        if not segments:
            return segments
        if not self._should_normalize_zh(language, segments):
            return segments

        normalized: List[TranscriptSegment] = []
        for segment in segments:
            normalized_text = self._to_simplified(segment.text)
            normalized.append(
                TranscriptSegment(
                    start=segment.start,
                    end=segment.end,
                    timestamp=segment.timestamp,
                    text=normalized_text,
                )
            )
        return normalized

    def _should_normalize_zh(
        self, language: Optional[str], segments: List[TranscriptSegment]
    ) -> bool:
        if not settings.AI_NORMALIZE_ZH_TO_SIMPLIFIED:
            return False

        lang = (language or "").lower()
        if any(tag in lang for tag in ("zh", "cmn", "chi")):
            return True

        sample = "".join(segment.text for segment in segments[:30])
        chinese_chars = re.findall(r"[\u4e00-\u9fff]", sample)
        return len(chinese_chars) >= 20

    def _to_simplified(self, text: str) -> str:
        if not text:
            return text
        if self.zh_converter is None:
            return text
        try:
            return self.zh_converter.convert(text)
        except Exception:
            return text

    def _generate_summary(self, title: str, transcript: List[TranscriptSegment]) -> VideoSummary:
        ai_summary = self._generate_summary_with_ai(title, transcript)
        if ai_summary:
            return ai_summary
        return self._generate_summary_fallback(transcript)

    def _generate_summary_with_ai(
        self, title: str, transcript: List[TranscriptSegment]
    ) -> Optional[VideoSummary]:
        if not settings.AI_API_KEY:
            return None

        transcript_text = "\n".join(
            f"[{segment.timestamp}] {segment.text}" for segment in transcript[:220]
        )

        system_prompt = (
            "你是一名学习效率助手。请基于视频转录生成结构化 JSON，"
            "必须包含 overview(字符串)、key_points(字符串数组)、sections(数组)。"
            "sections 每一项必须包含 title/start/summary。"
            "确保输出是合法 JSON，不能包含 markdown。"
        )
        user_prompt = (
            f"视频标题：{title}\n"
            "请输出可快速学习的视频摘要。\n"
            f"转录内容：\n{transcript_text}"
        )

        response_json = self._call_ai_model(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )
        if not response_json:
            return None

        try:
            payload = json.loads(response_json)
            sections = [
                SummarySection(
                    title=item.get("title", "章节"),
                    start=item.get("start", "00:00:00"),
                    summary=item.get("summary", ""),
                )
                for item in payload.get("sections", [])[:8]
            ]
            key_points = [str(point) for point in payload.get("key_points", [])[:8]]
            overview = str(payload.get("overview", "")).strip()
            if not overview:
                return None
            return VideoSummary(overview=overview, key_points=key_points, sections=sections)
        except Exception:
            return None

    def _generate_summary_fallback(self, transcript: List[TranscriptSegment]) -> VideoSummary:
        sections: List[SummarySection] = []
        key_points: List[str] = []

        total_duration = transcript[-1].end if transcript else 0
        if total_duration <= 0:
            total_duration = max(300, len(transcript) * 8)

        target_section_count = 4
        window_size = max(120.0, total_duration / target_section_count)

        grouped: Dict[int, List[TranscriptSegment]] = {}
        for segment in transcript:
            bucket = int(segment.start // window_size)
            grouped.setdefault(bucket, []).append(segment)

        for _, group in sorted(grouped.items()):
            if not group:
                continue
            title = self._build_section_title(group)
            summary = self._summarize_group_text(group)
            sections.append(
                SummarySection(
                    title=title,
                    start=group[0].timestamp,
                    summary=summary,
                )
            )

        for segment in transcript:
            text = segment.text.strip()
            if len(text) < 15:
                continue
            if text in key_points:
                continue
            key_points.append(self._truncate(text, 80))
            if len(key_points) >= 6:
                break

        overview_parts = [section.summary for section in sections[:3] if section.summary]
        overview = "；".join(overview_parts) if overview_parts else "该视频主要围绕核心主题进行讲解。"

        return VideoSummary(
            overview=self._truncate(overview, 220),
            key_points=key_points,
            sections=sections[:6],
        )

    def _build_section_title(self, group: List[TranscriptSegment]) -> str:
        first = group[0].text
        # 通过句子前半段作为章节名，避免空泛
        title = re.split(r"[。！？.!?]", first)[0]
        title = self._truncate(title.strip(), 20)
        return title or "章节要点"

    def _summarize_group_text(self, group: List[TranscriptSegment]) -> str:
        merged = " ".join(segment.text for segment in group[:6])
        sentences = re.split(r"[。！？.!?]", merged)
        useful = [sentence.strip() for sentence in sentences if len(sentence.strip()) >= 10]
        if not useful:
            return self._truncate(merged, 100)
        return self._truncate("；".join(useful[:2]), 120)

    def _build_mind_map(self, title: str, summary: VideoSummary) -> MindMapNode:
        root = MindMapNode(id="root", label=title, children=[])

        summary_node = MindMapNode(
            id="summary",
            label="视频总览",
            children=[
                MindMapNode(id="summary-overview", label=self._truncate(summary.overview, 60), children=[])
            ],
        )
        root.children.append(summary_node)

        key_points_node = MindMapNode(id="key-points", label="核心要点", children=[])
        for idx, point in enumerate(summary.key_points[:8]):
            key_points_node.children.append(
                MindMapNode(id=f"kp-{idx}", label=self._truncate(point, 50), children=[])
            )
        root.children.append(key_points_node)

        sections_node = MindMapNode(id="sections", label="章节结构", children=[])
        for idx, section in enumerate(summary.sections[:8]):
            section_node = MindMapNode(
                id=f"section-{idx}",
                label=f"{section.start} {self._truncate(section.title, 30)}",
                children=[
                    MindMapNode(
                        id=f"section-{idx}-detail",
                        label=self._truncate(section.summary, 60),
                        children=[],
                    )
                ],
            )
            sections_node.children.append(section_node)
        root.children.append(sections_node)
        return root

    def _retrieve_relevant_segments(
        self, question: str, transcript: List[TranscriptSegment], top_k: int
    ) -> List[TranscriptSegment]:
        tokens = self._tokenize(question)
        if not tokens:
            return transcript[:top_k]

        scored: List[Tuple[int, TranscriptSegment]] = []
        for segment in transcript:
            score = 0
            text = segment.text.lower()
            for token in tokens:
                if token in text:
                    score += 2
            if score == 0:
                # 轻量语义兜底：较短问题时按前缀词匹配
                for token in tokens:
                    if any(word.startswith(token[:2]) for word in text.split()):
                        score += 1
            if score > 0:
                scored.append((score, segment))

        if not scored:
            return transcript[:top_k]

        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def _answer_with_ai_or_fallback(
        self,
        question: str,
        title: str,
        candidates: List[TranscriptSegment],
        summary: VideoSummary,
    ) -> Tuple[str, List[TranscriptSegment]]:
        if settings.AI_API_KEY:
            ai_answer = self._answer_with_ai(question, title, candidates, summary)
            if ai_answer:
                return ai_answer, candidates[:4]

        return self._build_fallback_answer(candidates), candidates[:4]

    def _answer_with_ai(
        self,
        question: str,
        title: str,
        candidates: List[TranscriptSegment],
        summary: VideoSummary,
    ) -> Optional[str]:
        context = "\n".join(f"[{s.timestamp}] {s.text}" for s in candidates)
        system_prompt = (
            "你是视频学习助手。请基于给定转录片段回答问题，"
            "答案要简洁、结构化，若证据不足要明确说明。"
        )
        user_prompt = (
            f"视频标题：{title}\n"
            f"视频总览：{summary.overview}\n"
            f"用户问题：{question}\n"
            f"可用证据：\n{context}"
        )
        response = self._call_ai_model(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
            response_as_json=False,
        )
        if not response:
            return None
        return response.strip()

    def _answer_with_ai_stream(
        self,
        question: str,
        title: str,
        candidates: List[TranscriptSegment],
        summary: VideoSummary,
    ) -> Iterator[str]:
        context = "\n".join(f"[{s.timestamp}] {s.text}" for s in candidates)
        system_prompt = (
            "你是视频学习助手。请基于给定转录片段回答问题，"
            "答案要简洁、结构化，若证据不足要明确说明。"
        )
        user_prompt = (
            f"视频标题：{title}\n"
            f"视频总览：{summary.overview}\n"
            f"用户问题：{question}\n"
            f"可用证据：\n{context}"
        )
        for delta in self._call_ai_model_stream(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        ):
            yield delta

    def _call_ai_model(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        response_as_json: bool = True,
    ) -> Optional[str]:
        if not settings.AI_API_KEY:
            return None

        payload: Dict[str, Any] = {
            "model": settings.AI_MODEL,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if response_as_json:
            payload["response_format"] = {"type": "json_object"}

        api_base = settings.AI_API_BASE_URL.rstrip("/")
        url = f"{api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None

    def _call_ai_model_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> Iterator[str]:
        if not settings.AI_API_KEY:
            return

        payload: Dict[str, Any] = {
            "model": settings.AI_MODEL,
            "temperature": temperature,
            "stream": True,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        api_base = settings.AI_API_BASE_URL.rstrip("/")
        url = f"{api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                with client.stream("POST", url, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line:
                            continue
                        if isinstance(line, bytes):
                            line = line.decode("utf-8", errors="ignore")
                        raw = line.strip()
                        if not raw.startswith("data:"):
                            continue
                        data_text = raw[5:].strip()
                        if data_text == "[DONE]":
                            break
                        try:
                            payload_item = json.loads(data_text)
                        except json.JSONDecodeError:
                            continue

                        choice = ((payload_item.get("choices") or [{}])[0] or {})
                        delta = choice.get("delta") or {}
                        content = delta.get("content")
                        text_delta = self._extract_stream_delta_text(content)
                        if text_delta:
                            yield text_delta
        except Exception:
            return

    def _extract_stream_delta_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content

        if isinstance(content, dict):
            text = content.get("text")
            if isinstance(text, str):
                return text
            return ""

        if isinstance(content, list):
            text_parts: List[str] = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                    continue
                if not isinstance(item, dict):
                    continue
                if isinstance(item.get("text"), str):
                    text_parts.append(item["text"])
                    continue
                text_payload = item.get("text")
                if isinstance(text_payload, dict) and isinstance(text_payload.get("value"), str):
                    text_parts.append(text_payload["value"])
            return "".join(text_parts)

        return ""

    def _tokenize(self, text: str) -> List[str]:
        normalized = re.sub(r"[^\w\u4e00-\u9fa5]+", " ", text.lower()).strip()
        if not normalized:
            return []
        return [token for token in normalized.split() if len(token) > 1][:10]

    def _timecode_to_seconds(self, value: str) -> float:
        value = value.replace(",", ".")
        hours, minutes, seconds = value.split(":")
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    def _format_timestamp(self, seconds: float) -> str:
        total_seconds = int(max(0, seconds))
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _truncate(self, text: str, max_len: int) -> str:
        if len(text) <= max_len:
            return text
        return f"{text[:max_len].rstrip()}..."


video_ai_service = VideoAIService()
