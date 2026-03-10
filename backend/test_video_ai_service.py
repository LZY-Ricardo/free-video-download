"""
VideoAIService 测试
"""
import unittest

from app.services.video_ai_service import VideoAIService


class TestVideoAIService(unittest.TestCase):
    def setUp(self):
        self.service = VideoAIService()

    def test_parse_subtitle_vtt(self):
        raw_vtt = """WEBVTT

00:00:01.000 --> 00:00:03.500
第一段测试文本

00:00:04.000 --> 00:00:07.000
第二段测试文本
"""
        segments = self.service._parse_subtitle(raw_vtt)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].timestamp, "00:00:01")
        self.assertIn("第一段测试文本", segments[0].text)

    def test_generate_summary_fallback(self):
        segments = self.service._parse_subtitle(
            """WEBVTT

00:00:00.000 --> 00:00:05.000
今天我们介绍机器学习的基本概念和整体框架

00:01:00.000 --> 00:01:05.000
接下来讲解监督学习和非监督学习的区别

00:02:00.000 --> 00:02:05.000
最后我们总结常见算法及其适用场景
"""
        )
        summary = self.service._generate_summary_fallback(segments)
        self.assertTrue(summary.overview)
        self.assertGreaterEqual(len(summary.key_points), 1)
        self.assertGreaterEqual(len(summary.sections), 1)

    def test_build_mind_map(self):
        segments = self.service._parse_subtitle(
            """WEBVTT

00:00:00.000 --> 00:00:05.000
这里是第一部分内容
"""
        )
        summary = self.service._generate_summary_fallback(segments)
        mind_map = self.service._build_mind_map("测试标题", summary)
        self.assertEqual(mind_map.label, "测试标题")
        self.assertGreaterEqual(len(mind_map.children), 1)

    def test_parse_bilibili_json_subtitle(self):
        raw_json = """{
  "body": [
    {"from": 1.2, "to": 3.6, "content": "第一句字幕"},
    {"from": 4.0, "to": 6.0, "content": "第二句字幕"}
  ]
}"""
        segments = self.service._parse_subtitle(raw_json)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].timestamp, "00:00:01")
        self.assertEqual(segments[1].text, "第二句字幕")

    def test_has_only_danmaku(self):
        info = {
            "subtitles": {
                "danmaku": [
                    {"ext": "xml", "url": "https://comment.bilibili.com/123.xml"}
                ]
            }
        }
        self.assertTrue(self.service._has_only_danmaku(info))

    def test_normalize_transcript_script_to_simplified(self):
        class FakeConverter:
            def convert(self, text: str) -> str:
                return text.replace("開", "开").replace("發", "发").replace("碼", "码")

        self.service.zh_converter = FakeConverter()
        segments = self.service._parse_subtitle(
            """WEBVTT

00:00:01.000 --> 00:00:03.000
代碼全部開源，專注開發體驗
"""
        )
        normalized = self.service._normalize_transcript_script(segments, "zh-ASR")
        self.assertIn("代码全部开源", normalized[0].text)
        self.assertIn("开发", normalized[0].text)


if __name__ == "__main__":
    unittest.main()
