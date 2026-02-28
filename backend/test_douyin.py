"""Direct test of Douyin integration"""
import sys
sys.path.insert(0, '.')

from app.services.douyin_service import douyin_service

test_url = 'https://www.douyin.com/video/7123456789012345678'

print('=' * 60)
print(f'Testing Douyin service with: {test_url}')
print('=' * 60)

try:
    info = douyin_service.get_video_info(test_url)
    print('\nSUCCESS!')
    print(f'Title: {info.get("title")}')
    print(f'Duration: {info.get("duration")}s')
    print(f'Uploader: {info.get("uploader")}')
    print(f'Has thumbnail: {bool(info.get("thumbnail"))}')
    print(f'Has direct_url: {bool(info.get("direct_url"))}')
except Exception as e:
    print(f'\nFAILED: {e}')
    import traceback
    traceback.print_exc()
