import unittest
from datetime import timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.db_models import User
from app.main import app
from app.models import MindMapNode, SummarySection, TranscriptSegment, VideoAnalysisResponse, VideoSummary
from app.security import hash_password, utcnow
from app.services.video_ai_service import AnalysisRecord, video_ai_service


def build_analysis_response(analysis_id: str = "analysis-free-1") -> VideoAnalysisResponse:
    return VideoAnalysisResponse(
        analysis_id=analysis_id,
        video_title="测试视频",
        transcript_language="zh",
        summary=VideoSummary(
            overview="这是摘要",
            key_points=["要点1", "要点2"],
            sections=[SummarySection(title="章节1", start="00:00:10", summary="章节摘要")],
        ),
        transcript=[TranscriptSegment(start=10, end=15, timestamp="00:00:10", text="第一段内容")],
        mind_map=MindMapNode(id="root", label="测试视频", children=[]),
    )


class TestAIQuotaAPI(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        video_ai_service.analysis_cache.clear()
        video_ai_service.analysis_tasks.clear()
        self.client = TestClient(app)
        self.user = self._create_verified_user()
        login_response = self.client.post(
            "/api/auth/login",
            json={"email": self.user["email"], "password": self.user["password"]},
        )
        self.assertEqual(login_response.status_code, 200)

    def tearDown(self):
        self.client.close()
        video_ai_service.analysis_cache.clear()
        video_ai_service.analysis_tasks.clear()

    def _create_verified_user(self, email: str = "free@example.com", password: str = "password123"):
        with SessionLocal() as db:
            user = User(
                email=email,
                password_hash=hash_password(password),
                email_verified_at=utcnow(),
                status="active",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return {"id": user.id, "email": user.email, "password": password}

    @patch("app.routers.ai.video_ai_service.analyze_video")
    def test_free_user_can_analyze_twice_then_third_request_is_blocked(self, mock_analyze_video):
        mock_analyze_video.side_effect = [
            build_analysis_response("analysis-1"),
            build_analysis_response("analysis-2"),
        ]

        first_response = self.client.post("/api/ai/analyze", json={"url": "https://example.com/video-1"})
        second_response = self.client.post("/api/ai/analyze", json={"url": "https://example.com/video-2"})
        third_response = self.client.post("/api/ai/analyze", json={"url": "https://example.com/video-3"})

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(third_response.status_code, 403)
        self.assertIn("今日免费 AI 次数已用完", third_response.json()["detail"])

    @patch("app.services.video_ai_service.VideoAIService._answer_with_ai_or_fallback")
    def test_free_user_can_chat_with_owned_analysis_record(self, mock_answer):
        mock_answer.return_value = ("这是回答", [])
        response = build_analysis_response("analysis-owned")
        video_ai_service.analysis_cache[response.analysis_id] = AnalysisRecord(
            analysis_id=response.analysis_id,
            user_id=self.user["id"],
            access_mode="free_quota",
            video_title=response.video_title,
            transcript_language=response.transcript_language,
            transcript=response.transcript,
            summary=response.summary,
            mind_map=response.mind_map,
        )

        chat_response = self.client.post(
            "/api/ai/chat",
            json={"analysis_id": response.analysis_id, "question": "核心观点是什么？"},
        )

        self.assertEqual(chat_response.status_code, 200)
        self.assertEqual(chat_response.json()["answer"], "这是回答")


if __name__ == "__main__":
    unittest.main()
