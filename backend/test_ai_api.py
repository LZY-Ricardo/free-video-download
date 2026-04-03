"""
AI API 测试
"""
from datetime import timedelta
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import test_env  # noqa: F401
from app.database import Base, SessionLocal, engine
from app.db_models import User, UserMembership
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
from app.security import hash_password, utcnow


class TestAIAPI(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.user = self._create_member_user()
        self.client.post(
            "/api/auth/login",
            json={"email": self.user["email"], "password": self.user["password"]},
        )

    def tearDown(self):
        self.client.close()

    def _create_member_user(self):
        with SessionLocal() as db:
            user = User(
                email="member@example.com",
                password_hash=hash_password("password123"),
                email_verified_at=utcnow(),
                status="active",
            )
            db.add(user)
            db.flush()
            membership = UserMembership(
                user_id=user.id,
                plan_code="vip_30d",
                started_at=utcnow(),
                expires_at=utcnow() + timedelta(days=30),
                status="active",
            )
            db.add(membership)
            db.commit()
            db.refresh(user)
            return {"email": user.email, "password": "password123"}

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

    def test_analyze_video_accepts_bearer_token(self):
        fresh_client = TestClient(app)
        try:
            login_response = fresh_client.post(
                "/api/auth/login",
                json={"email": self.user["email"], "password": self.user["password"]},
            )
            access_token = login_response.json()["access_token"]

            mock_result = VideoAnalysisResponse(
                analysis_id="analysis-bearer",
                video_title="Bearer 测试视频",
                transcript_language="zh",
                summary=VideoSummary(
                    overview="这是摘要",
                    key_points=["要点1"],
                    sections=[SummarySection(title="章节1", start="00:00:10", summary="章节摘要")],
                ),
                transcript=[TranscriptSegment(start=10, end=15, timestamp="00:00:10", text="第一段内容")],
                mind_map=MindMapNode(id="root", label="测试视频", children=[]),
            )

            with patch("app.routers.ai.video_ai_service.analyze_video", return_value=mock_result):
                response = fresh_client.post(
                    "/api/ai/analyze",
                    json={"url": "https://example.com/video"},
                    headers={"Authorization": f"Bearer {access_token}"},
                )
        finally:
            fresh_client.close()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["analysis_id"], "analysis-bearer")

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

    def test_analyze_local_video_success(self):
        mock_result = VideoAnalysisResponse(
            analysis_id="local-analysis-id",
            video_title="本地测试视频",
            transcript_language="zh",
            summary=VideoSummary(
                overview="这是本地摘要",
                key_points=["本地要点1", "本地要点2"],
                sections=[
                    SummarySection(title="章节1", start="00:00:05", summary="章节摘要"),
                ],
            ),
            transcript=[
                TranscriptSegment(
                    start=5,
                    end=10,
                    timestamp="00:00:05",
                    text="本地转录内容",
                )
            ],
            mind_map=MindMapNode(
                id="root",
                label="本地测试视频",
                children=[],
            ),
        )

        with patch("app.routers.ai.video_ai_service.analyze_transcript", return_value=mock_result) as mock_analyze:
            response = self.client.post(
                "/api/ai/analyze/local",
                json={
                    "source_url": "https://www.bilibili.com/video/BV1test",
                    "video_title": "本地测试视频",
                    "transcript_language": "zh",
                    "transcript": [
                        {
                            "start": 5,
                            "end": 10,
                            "timestamp": "00:00:05",
                            "text": "本地转录内容",
                        }
                    ],
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["analysis_id"], "local-analysis-id")
        self.assertEqual(payload["video_title"], "本地测试视频")
        mock_analyze.assert_called_once()

    def test_analyze_local_video_bad_request(self):
        with patch("app.routers.ai.video_ai_service.analyze_transcript", side_effect=ValueError("本地转录为空")):
            response = self.client.post(
                "/api/ai/analyze/local",
                json={
                    "video_title": "空转录视频",
                    "transcript_language": "zh",
                    "transcript": [
                        {
                            "start": 0,
                            "end": 1,
                            "timestamp": "00:00:00",
                            "text": "占位文本",
                        }
                    ],
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("本地转录为空", response.json()["detail"])

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

    def test_download_transcript_success(self):
        with patch(
            "app.routers.ai.video_ai_service.build_transcript_download",
            return_value=("1\n00:00:00,000 --> 00:00:01,000\n测试内容\n", "测试视频.srt", "application/x-subrip"),
        ):
            response = self.client.get("/api/ai/transcript/download/analysis-1?format=srt")

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment;", response.headers.get("content-disposition", ""))
        self.assertIn("测试内容", response.text)

    def test_download_transcript_not_found(self):
        with patch(
            "app.routers.ai.video_ai_service.build_transcript_download",
            side_effect=ValueError("分析任务不存在或已过期，请先重新执行视频分析。"),
        ):
            response = self.client.get("/api/ai/transcript/download/missing?format=srt")

        self.assertEqual(response.status_code, 404)
        self.assertIn("分析任务不存在", response.json()["detail"])

    def test_download_transcript_bad_format(self):
        with patch(
            "app.routers.ai.video_ai_service.build_transcript_download",
            side_effect=ValueError("不支持的字幕格式，仅支持 srt/vtt/txt。"),
        ):
            response = self.client.get("/api/ai/transcript/download/analysis-1?format=docx")

        self.assertEqual(response.status_code, 400)
        self.assertIn("不支持的字幕格式", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
