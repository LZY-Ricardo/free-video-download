import unittest

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


class TestAuthAPI(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_register_returns_success_message_and_debug_verify_url(self):
        response = self.client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["message"], "注册成功，请查收验证邮件")
        self.assertTrue(payload["requires_email_verification"])
        self.assertIn("token=", payload["debug_verify_url"])

    def test_login_requires_verified_email(self):
        self.client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        response = self.client.post(
            "/api/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn("邮箱尚未验证", response.json()["detail"])

    def test_verify_email_then_login_sets_cookie(self):
        register_response = self.client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )
        verify_url = register_response.json()["debug_verify_url"]
        token = verify_url.split("token=")[1]

        verify_response = self.client.get(f"/api/auth/verify-email?token={token}")
        self.assertEqual(verify_response.status_code, 200)
        self.assertEqual(verify_response.json()["message"], "邮箱验证成功")

        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("set-cookie", login_response.headers)

        me_response = self.client.get("/api/auth/me")
        self.assertEqual(me_response.status_code, 200)
        self.assertTrue(me_response.json()["authenticated"])
        self.assertEqual(me_response.json()["user"]["email"], "user@example.com")

    def test_logout_clears_cookie(self):
        register_response = self.client.post(
            "/api/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )
        token = register_response.json()["debug_verify_url"].split("token=")[1]
        self.client.get(f"/api/auth/verify-email?token={token}")
        self.client.post(
            "/api/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        logout_response = self.client.post("/api/auth/logout")
        self.assertEqual(logout_response.status_code, 200)

        me_response = self.client.get("/api/auth/me")
        self.assertEqual(me_response.status_code, 200)
        self.assertFalse(me_response.json()["authenticated"])


if __name__ == "__main__":
    unittest.main()
