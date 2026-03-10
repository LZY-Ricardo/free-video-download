"""
AI 视频分析 API
"""
from fastapi import APIRouter, HTTPException

from app.models import (
    AnalyzeRequest,
    AnalyzeStartResponse,
    AnalyzeTaskStatusResponse,
    ChatRequest,
    ChatResponse,
    VideoAnalysisResponse,
)
from app.services.video_ai_service import video_ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/analyze/start", response_model=AnalyzeStartResponse)
async def start_analyze_video(request: AnalyzeRequest):
    """
    启动异步视频分析任务
    """
    try:
        task_id = video_ai_service.start_analysis(request.url)
        return AnalyzeStartResponse(task_id=task_id, status="processing")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"启动 AI 分析失败: {exc}")


@router.get("/analyze/status/{task_id}", response_model=AnalyzeTaskStatusResponse)
async def get_analyze_status(task_id: str):
    """
    查询 AI 分析任务状态
    """
    task = video_ai_service.get_analysis_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="分析任务不存在")
    return task


@router.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_video(request: AnalyzeRequest):
    """
    对视频执行 AI 分析：摘要、转录、思维导图
    """
    try:
        return video_ai_service.analyze_video(request.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI 分析失败: {exc}")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_video(request: ChatRequest):
    """
    针对已分析的视频内容进行问答
    """
    try:
        return video_ai_service.ask_question(request.analysis_id, request.question)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI 问答失败: {exc}")
