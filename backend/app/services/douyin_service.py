"""
抖音专用解析服务
使用多种方法解析抖音视频信息
"""
import httpx
import re
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs


class DouyinService:
    """抖音视频解析服务"""

    def __init__(self):
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        # 移动端客户端（用于移动 API）
        self.mobile_client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "com.ss.android.ugc.aweme/280102 (Linux; U; Android 12; zh_CN; Pixel 6; Build/SQ3A.220605.009; Cronet/TTNetVersion:6c7b701a 2021-08-10 QuicVersion:0144d358 2021-07-28)"
            }
        )

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        从抖音链接中提取 video_id

        支持的链接格式：
        - https://www.douyin.com/video/7123456789012345678
        - https://v.douyin.com/ABC123
        - https://www.iesdouyin.com/share/video/7123456789012345678
        """
        # 尝试从 URL 中直接提取
        patterns = [
            r'/video/(\d+)',
            r'/note/(\d+)',           # 抖音笔记/图文
            r'/share/video/(\d+)',
            r'item_ids=(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # 如果直接提取失败，尝试通过短链接重定向获取
        if 'v.douyin.com' in url or 'douyin.com' in url:
            try:
                response = self.client.get(url, follow_redirects=True, timeout=10.0)
                final_url = str(response.url)

                # 从重定向后的 URL 提取
                for pattern in patterns:
                    match = re.search(pattern, final_url)
                    if match:
                        return match.group(1)

                # 尝试从 URL 参数中提取
                if 'item_ids' in final_url:
                    parsed = urlparse(final_url)
                    params = parse_qs(parsed.query)
                    if 'item_ids' in params:
                        return params['item_ids'][0]
            except:
                pass

        return None

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        获取抖音视频信息（尝试多种方法）

        Args:
            url: 抖音视频链接

        Returns:
            Dict: 视频信息
        """
        # 提取 video_id
        video_id = self.extract_video_id(url)

        if not video_id:
            raise ValueError("无法从链接中提取视频 ID，请检查链接格式是否正确")

        # 尝试多种方法，从最可靠到最宽松
        methods = [
            self._try_v1_web_api,
            self._try_v2_web_api,
            self._try_mobile_api,
            self._try_html_parsing,
        ]

        last_error = None
        for method in methods:
            try:
                result = method(video_id, url)
                if result:
                    return result
            except Exception as e:
                last_error = e
                continue

        # 所有方法都失败
        raise ValueError(f"无法解析抖音视频。API 接口可能已变更。建议使用：\n"
                        f"1. 命令行工具：yt-dlp --cookies-from-browser chrome \"{url}\"\n"
                        f"2. 在线抖音下载工具\n"
                        f"3. 或下载其他平台的视频")

    def _try_v2_web_api(self, video_id: str, original_url: str) -> Optional[Dict[str, Any]]:
        """尝试使用 V2 Web API"""
        api_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={video_id}"

        response = self.client.get(api_url)
        if response.status_code != 200 or len(response.content) == 0:
            return None

        data = response.json()

        if data.get('status_code') != 0 or not data.get('item_list'):
            return None

        return self._parse_api_response(data, video_id)

    def _try_v1_web_api(self, video_id: str, original_url: str) -> Optional[Dict[str, Any]]:
        """尝试使用 V1 Web API（更新版本）"""
        api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}"

        response = self.client.get(
            api_url,
            headers={
                "Referer": "https://www.douyin.com/",
                "Accept": "application/json",
            }
        )

        if response.status_code != 200 or len(response.content) == 0:
            return None

        data = response.json()

        if not data.get('aweme_detail'):
            return None

        # 转换为统一格式
        return self._parse_aweme_detail(data.get('aweme_detail'), video_id)

    def _try_mobile_api(self, video_id: str, original_url: str) -> Optional[Dict[str, Any]]:
        """尝试使用移动端 API"""
        api_url = f"https://aweme.snssdk.com/aweme/v1/feed/?aweme_id={video_id}"

        response = self.mobile_client.get(api_url)

        if response.status_code != 200 or len(response.content) == 0:
            return None

        data = response.json()

        if not data.get('aweme_list') or len(data['aweme_list']) == 0:
            return None

        aweme = data['aweme_list'][0]
        return self._parse_aweme_detail(aweme, video_id)

    def _try_html_parsing(self, video_id: str, original_url: str) -> Optional[Dict[str, Any]]:
        """尝试从 HTML 页面解析数据"""
        # 先访问页面获取真实 URL
        response = self.client.get(original_url)
        html = response.text

        # 尝试多种数据模式
        patterns = [
            r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            r'<script[^>]*id="RENDER_DATA"[^>]*>(.*?)</script>',
            r'window\._SSR_HYDRATED_DATA\s*=\s*({.*?});',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    data = json.loads(json_str)

                    # 从 NEXT_DATA 解析
                    if 'props' in data and 'pageProps' in data['props']:
                        page_props = data['props']['pageProps']
                        if 'aweme' in page_props or 'detail' in page_props:
                            aweme = page_props.get('aweme') or page_props.get('detail')
                            return self._parse_aweme_detail(aweme, video_id)

                    # 从 RENDER_DATA 解析
                    if 'app' in data and 'videoDetail' in data['app']:
                        video_detail = data['app']['videoDetail']
                        return self._parse_video_detail(video_detail, video_id)

                except (json.JSONDecodeError, KeyError):
                    continue

        return None

    def _parse_api_response(self, data: Dict, video_id: str) -> Dict[str, Any]:
        """解析 API 响应"""
        item = data['item_list'][0]
        video_info = item.get('video', {})
        author = item.get('author', {})
        statistics = item.get('statistics', {})

        # 提取播放地址
        play_addr = video_info.get('play_addr', {})
        play_url = play_addr.get('url_list', [''])[0] if play_addr.get('url_list') else ''

        # 构造无水印地址
        clean_url = self._get_clean_url(play_url, video_id) if play_url else ''

        title = item.get('desc') or video_info.get('desc', '未知标题')
        # 如果标题为空或太短，使用默认标题
        if not title or len(title) < 2:
            title = f"抖音视频_{video_id[-6:]}"

        return {
            "title": title,
            "duration": video_info.get('duration', 0) // 1000,
            "thumbnail": self._get_best_thumbnail(video_info),
            "platform": "douyin",
            "uploader": author.get('nickname', '抖音用户'),
            "view_count": statistics.get('play_count', 0),
            "video_id": video_id,
            "direct_url": clean_url,
        }

    def _parse_aweme_detail(self, aweme: Dict, video_id: str) -> Dict[str, Any]:
        """解析 aweme_detail 数据"""
        video_info = aweme.get('video', {})
        author = aweme.get('author', {})
        statistics = aweme.get('statistics', {})

        title = aweme.get('desc', '未知标题')
        if not title or len(title) < 2:
            title = f"抖音视频_{video_id[-6:]}"

        # 提取所有可用的格式
        formats = self._extract_formats(video_info, video_id)

        return {
            "title": title,
            "duration": video_info.get('duration', 0) // 1000,
            "thumbnail": self._get_best_thumbnail(video_info),
            "platform": "douyin",
            "uploader": author.get('nickname', '抖音用户'),
            "view_count": statistics.get('play_count', 0),
            "video_id": video_id,
            "direct_url": formats[0]['url'] if formats else '',  # 默认使用最高质量
            "formats": formats,  # 返回所有格式
        }

    def _extract_formats(self, video_info: Dict, video_id: str) -> list:
        """从视频信息中提取所有可用格式"""
        formats = []

        # 尝试从 bit_rate 中提取多个质量选项
        bit_rates = video_info.get('bit_rate', [])
        if bit_rates:
            # 按比特率排序（从高到低）
            sorted_rates = sorted(bit_rates, key=lambda x: x.get('bit_rate', 0), reverse=True)

            for i, br in enumerate(sorted_rates):
                play_addr = br.get('play_addr', {})
                url_list = play_addr.get('url_list', [])
                if url_list:
                    # url_list 是字符串列表，直接取第一个
                    original_url = url_list[0] if isinstance(url_list[0], str) else url_list[0].get('url', '')
                    clean_url = self._get_clean_url(original_url, video_id)

                    # 计算质量等级
                    bit_rate = br.get('bit_rate', 0)
                    if bit_rate >= 1000000:
                        quality = '1080p'
                        quality_label = '超清'
                    elif bit_rate >= 600000:
                        quality = '720p'
                        quality_label = '高清'
                    elif bit_rate >= 400000:
                        quality = '480p'
                        quality_label = '标清'
                    else:
                        quality = '360p'
                        quality_label = '流畅'

                    # 计算文件大小（估算）
                    width = br.get('width', 0)
                    height = br.get('height', 0)
                    resolution = f'{width}x{height}' if width and height else '1280x720'

                    # 估算文件大小 (比特率 * 时长 / 8)
                    duration = video_info.get('duration', 0) / 1000  # 毫秒转秒
                    estimated_size = int(bit_rate * duration / 8) if duration > 0 else None

                    formats.append({
                        'format_id': f'douyin_{i}',
                        'ext': 'mp4',
                        'quality': quality,
                        'quality_label': quality_label,
                        'filesize': estimated_size,
                        'filesize_mb': round(estimated_size / 1024 / 1024, 2) if estimated_size else None,
                        'filesize_display': f'{round(estimated_size / 1024 / 1024, 1)}MB' if estimated_size else '未知大小',
                        'resolution': resolution,
                        'fps': 30,
                        'fps_display': '30 FPS',
                        'bitrate': bit_rate,
                        'url': clean_url,
                        'is_default': (i == 0)  # 第一个是默认（最高质量）
                    })

        # 如果没有bit_rate，使用原始的play_addr
        if not formats:
            play_addr = video_info.get('play_addr', {})
            url_list = play_addr.get('url_list', [])
            if url_list:
                original_url = url_list[0] if isinstance(url_list[0], str) else url_list[0].get('url', '')
                clean_url = self._get_clean_url(original_url, video_id)

                width = video_info.get('width', 0)
                height = video_info.get('height', 0)
                resolution = f'{width}x{height}' if width and height else '1280x720'

                formats.append({
                    'format_id': 'douyin_default',
                    'ext': 'mp4',
                    'quality': '720p',
                    'quality_label': '高清',
                    'filesize': None,
                    'filesize_mb': None,
                    'filesize_display': '未知大小',
                    'resolution': resolution,
                    'fps': 30,
                    'fps_display': '30 FPS',
                    'url': clean_url,
                    'is_default': True
                })

        return formats

    def _parse_video_detail(self, video_detail: Dict, video_id: str) -> Dict[str, Any]:
        """解析 video_detail 数据"""
        # 类似的解析逻辑
        return self._parse_aweme_detail(video_detail, video_id)

    def _get_best_thumbnail(self, video_info: Dict) -> str:
        """获取最佳缩略图"""
        # 优先使用 cover，其次 origin_cover，最后 dynamic_cover
        for key in ['cover', 'origin_cover', 'dynamic_cover']:
            cover_data = video_info.get(key, {})
            if cover_data and 'url_list' in cover_data and cover_data['url_list']:
                return cover_data['url_list'][0]
        return ''

    def _get_clean_url(self, original_url: str, video_id: str) -> Optional[str]:
        """
        获取无水印播放地址

        方法：将 URL 中的 playwm 替换为 play
        """
        if not original_url:
            return None

        try:
            # 方法1: 替换 playwm 为 play
            clean_url = original_url.replace('playwm', 'play')

            # 验证 URL 是否有效
            try:
                head_response = self.client.head(clean_url, timeout=5.0)
                if head_response.status_code == 200:
                    return clean_url
            except:
                pass

            # 方法2: 构造无水印下载地址
            # 从原始 URL 中提取关键参数
            if '?' in original_url:
                base_url = original_url.split('?')[0]
                query_params = original_url.split('?')[1]

                # 替换 playwm 参数
                query_params = query_params.replace('playwm', 'play')
                clean_url = f"{base_url}?{query_params}"

                try:
                    head_response = self.client.head(clean_url, timeout=5.0)
                    if head_response.status_code == 200:
                        return clean_url
                except:
                    pass

            return None

        except Exception:
            return original_url

    def download_video(self, url: str, output_path: str) -> str:
        """
        下载抖音视频

        Args:
            url: 抖音视频链接
            output_path: 输出文件路径

        Returns:
            str: 下载的文件路径
        """
        video_info = self.get_video_info(url)
        download_url = video_info.get('direct_url')

        if not download_url:
            raise ValueError("无法获取下载地址")

        try:
            # 下载视频
            response = self.client.get(download_url)
            response.raise_for_status()

            # 保存文件
            with open(output_path, 'wb') as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return output_path

        except httpx.HTTPStatusError as e:
            raise ValueError(f"下载视频失败: HTTP {e.response.status_code}")
        except Exception as e:
            raise ValueError(f"下载视频失败: {str(e)}")


# 全局实例
douyin_service = DouyinService()
