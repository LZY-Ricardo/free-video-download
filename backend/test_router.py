"""Test the router logic directly"""
import sys
sys.path.insert(0, '.')

from app.models import InfoRequest
from app.services.douyin_service import douyin_service

test_url = 'https://www.douyin.com/video/7123456789012345678'

print('=' * 60)
print('Testing router logic directly')
print('=' * 60)

# Simulate the router logic
def is_douyin_url(url: str) -> bool:
    douyin_domains = [
        'douyin.com',
        'iesdouyin.com',
        'v.douyin.com',
    ]
    return any(domain in url for domain in douyin_domains)

request = InfoRequest(url=test_url)

if is_douyin_url(request.url):
    print("[Douyin] Detected Douyin URL")
    info = None
    try:
        print("[Douyin] Calling service...")
        info = douyin_service.get_video_info(request.url)
        print(f"[Douyin] Service returned: title={info.get('title', 'N/A')[:40]}")
    except Exception as service_error:
        print(f"[Douyin] Service exception: {service_error}")
        import traceback
        traceback.print_exc()

    if info:
        print("[Douyin] Building success response...")
        formats = [{
            'format_id': 'douyin_default',
            'ext': 'mp4',
            'quality': '720p',
            'filesize': None,
            'filesize_mb': None,
            'filesize_display': 'Unknown',
            'resolution': '1280x720',
            'fps': 30,
            'fps_display': '30 FPS',
        }]

        response = {
            "title": info['title'],
            "duration": info['duration'],
            "thumbnail": info['thumbnail'],
            "platform": "douyin",
            "uploader": info['uploader'],
            "view_count": info.get('view_count', 0),
            "formats": formats,
            "is_douyin": True,
            "direct_url": info.get('direct_url', ''),
        }
        print("[Douyin] SUCCESS!")
        print(f"  Title: {response['title'][:50]}")
        print(f"  Duration: {response['duration']}s")
        print(f"  Has direct_url: {bool(response['direct_url'])}")
    else:
        print("[Douyin] FAIL - info is None")
else:
    print("Not a Douyin URL")
