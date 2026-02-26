"""
后端 API 测试脚本
"""
import asyncio
from app.services.ytdlp_service import ytdlp_service


def test_get_video_info():
    """测试获取视频信息"""
    print("测试 1: 获取视频信息")
    print("-" * 50)

    # 使用一个简单的测试视频
    test_urls = [
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # "Me at the zoo" - YouTube 第一个视频
        # 添加其他测试 URL
    ]

    for url in test_urls:
        try:
            print(f"\nURL: {url}")
            info = ytdlp_service.get_video_info(url)
            print(f"✅ 标题: {info.title}")
            print(f"   时长: {info.duration}秒")
            print(f"   平台: {info.platform}")
            print(f"   可用格式: {len(info.formats)} 种")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


def test_format_selector():
    """测试格式选择器构建"""
    print("\n\n测试 2: 格式选择器")
    print("-" * 50)

    test_cases = [
        ("best", None, "best"),
        ("best", "1080p", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"),
        ("mp3", None, "bestaudio"),
    ]

    for format_val, quality, expected in test_cases:
        result = ytdlp_service._build_format_selector(format_val, quality)
        status = "✅" if result == expected else "❌"
        print(f"{status} format={format_val}, quality={quality}")
        print(f"   结果: {result}")


if __name__ == "__main__":
    print("=" * 50)
    print("后端 API 测试")
    print("=" * 50)

    test_get_video_info()
    test_format_selector()

    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)
