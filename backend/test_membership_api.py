import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.db_models import User
from app.main import app
from app.security import hash_password, utcnow


class TestMembershipAPI(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def _create_verified_user(self, email: str = "member@example.com", password: str = "password123"):
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
            return {"id": user.id, "email": email, "password": password}

    def _login(self, email: str, password: str):
        response = self.client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(response.status_code, 200)
        return response

    def test_membership_me_requires_login(self):
        response = self.client.get("/api/membership/me")
        self.assertEqual(response.status_code, 401)

    def test_membership_me_returns_inactive_for_logged_in_user_without_membership(self):
        user = self._create_verified_user()
        self._login(user["email"], user["password"])

        response = self.client.get("/api/membership/me")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["is_member"])
        self.assertEqual(payload["status"], "inactive")

    @patch("app.routers.ai.video_ai_service.analyze_video")
    def test_ai_analyze_requires_login(self, mock_analyze_video):
        mock_analyze_video.return_value = {"analysis_id": "x"}

        response = self.client.post(
            "/api/ai/analyze",
            json={"url": "https://example.com/video"},
        )

        self.assertEqual(response.status_code, 401)

    @patch("app.routers.ai.video_ai_service.analyze_video")
    def test_ai_analyze_requires_active_membership(self, mock_analyze_video):
        mock_analyze_video.return_value = {"analysis_id": "x"}
        user = self._create_verified_user()
        self._login(user["email"], user["password"])

        response = self.client.post(
            "/api/ai/analyze",
            json={"url": "https://example.com/video"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn("仅限会员使用", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
