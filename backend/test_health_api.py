import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

import test_env  # noqa: F401
from app.main import app


class TestHealthAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_liveness_health_stays_lightweight(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_readiness_health_returns_database_ok(self):
        response = self.client.get("/api/health/ready")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "healthy",
                "checks": {
                    "database": "ok",
                },
            },
        )

    def test_readiness_health_returns_503_when_database_unavailable(self):
        with patch("app.main.check_database_ready", side_effect=OperationalError("select 1", {}, None)):
            response = self.client.get("/api/health/ready")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "detail": {
                    "status": "unhealthy",
                    "checks": {
                        "database": "unavailable",
                    },
                }
            },
        )


if __name__ == "__main__":
    unittest.main()
