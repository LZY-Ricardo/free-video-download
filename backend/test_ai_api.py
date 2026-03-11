"""
AI API 测试
"""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models import (
    AnalyzeTaskStatusResponse,
    ChatResponse,
    MindMapNode,
    SummarySection,
    TranscriptSegment,
    VideoAnalysisResponse,
    VideoSummary,
)


class TestAIAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_analyze_video_success(self):
        mock_result = VideoAnalysisResponse(
            analysis_id="test-analysis-id",
            video_title="测试视频",
            transcript_language="zh",
            summary=VideoSummary(
                overview="这是摘要",
                key_points=["要点1", "要点2"],
                sections=[
                    SummarySection(title="章节1", start="00:00:10", summary="章节1摘要"),
                ],
            ),
            transcript=[
                TranscriptSegment(
                    start=10,
                    end=15,
                    timestamp="00:00:10",
                    text="第一段内容",
                )
            ],
            mind_map=MindMapNode(
                id="root",
                label="测试视频",
                children=[],
            ),
        )

        with patch("app.routers.ai.video_ai_service.analyze_video", return_value=mock_result):
            response = self.client.post("/api/ai/analyze", json={"url": "https://example.com/video"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["analysis_id"], "test-analysis-id")
        self.assertEqual(payload["video_title"], "测试视频")
        self.assertEqual(len(payload["transcript"]), 1)

    def test_start_analyze_video(self):
        with patch("app.routers.ai.video_ai_service.start_analysis", return_value="task-123"):
            response = self.client.post("/api/ai/analyze/start", json={"url": "https://example.com/video"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["task_id"], "task-123")
        self.assertEqual(payload["status"], "processing")

    def test_get_analyze_status(self):
        mock_status = AnalyzeTaskStatusResponse(
            task_id="task-123",
            status="processing",
            stage="转写中",
            progress=45.0,
        )
        with patch("app.routers.ai.video_ai_service.get_analysis_task", return_value=mock_status):
            response = self.client.get("/api/ai/analyze/status/task-123")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["stage"], "转写中")

    def test_analyze_video_bad_request(self):
        with patch("app.routers.ai.video_ai_service.analyze_video", side_effect=ValueError("字幕缺失")):
            response = self.client.post("/api/ai/analyze", json={"url": "https://example.com/video"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("字幕缺失", response.json()["detail"])

    def test_chat_success(self):
        mock_result = ChatResponse(
            answer="这是回答",
            citations=[],
        )

        with patch("app.routers.ai.video_ai_service.ask_question", return_value=mock_result):
            response = self.client.post(
                "/api/ai/chat",
                json={"analysis_id": "analysis-1", "question": "核心观点是什么？"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "这是回答")

    def test_chat_not_found(self):
        with patch(
            "app.routers.ai.video_ai_service.ask_question",
            side_effect=ValueError("分析任务不存在"),
        ):
            response = self.client.post(
                "/api/ai/chat",
                json={"analysis_id": "missing", "question": "问题"},
            )

        self.assertEqual(response.status_code, 404)
        self.assertIn("分析任务不存在", response.json()["detail"])

    def test_chat_stream_success(self):
        mock_stream = iter(
            [
                {"event": "start", "data": {"citations": []}},
                {"event": "delta", "data": {"delta": "这是"}},
                {"event": "delta", "data": {"delta": "流式回答"}},
                {"event": "done", "data": {"citations": []}},
            ]
        )

        with patch("app.routers.ai.video_ai_service.stream_answer", return_value=mock_stream):
            response = self.client.post(
                "/api/ai/chat/stream",
                json={"analysis_id": "analysis-1", "question": "核心观点是什么？"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers["content-type"])
        self.assertIn("event: delta", response.text)
        self.assertIn("流式回答", response.text)

    def test_chat_stream_error_event(self):
        with patch(
            "app.routers.ai.video_ai_service.stream_answer",
            side_effect=ValueError("分析任务不存在"),
        ):
            response = self.client.post(
                "/api/ai/chat/stream",
                json={"analysis_id": "missing", "question": "问题"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("event: error", response.text)
        self.assertIn("分析任务不存在", response.text)


if __name__ == "__main__":
    unittest.main()
