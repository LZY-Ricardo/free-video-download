import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import server


class LocalResolverAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(server.app)

    def tearDown(self):
        self.client.close()

    def test_health_endpoint_does_not_require_token(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    @patch.dict(os.environ, {"RESOLVER_API_TOKEN": "secret-token"}, clear=False)
    def test_info_requires_token_when_configured(self):
        response = self.client.post("/api/info", json={"url": "https://example.com/video"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "本地解析节点未授权")


if __name__ == "__main__":
    unittest.main()
