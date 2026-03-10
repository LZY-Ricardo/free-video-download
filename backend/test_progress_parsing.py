"""
下载进度解析测试
"""
import unittest

from app.routers.download import _safe_float
from app.services.ytdlp_service import YTDLPService


class TestProgressParsing(unittest.TestCase):
    def setUp(self):
        self.service = YTDLPService()

    def test_parse_percent_with_ansi(self):
        raw = "\x1b[0;94m 0.0%\x1b[0m"
        result = self.service._parse_percent(raw)
        self.assertEqual(result, 0.0)

    def test_parse_percent_normal(self):
        self.assertEqual(self.service._parse_percent("62.2%"), 62.2)
        self.assertEqual(self.service._parse_percent(" 100.0 "), 100.0)

    def test_safe_float(self):
        self.assertEqual(_safe_float("12.5"), 12.5)
        self.assertEqual(_safe_float("\x1b[0;94m 0.0\x1b[0m"), 0.0)
        self.assertEqual(_safe_float("xx"), 0.0)


if __name__ == "__main__":
    unittest.main()
