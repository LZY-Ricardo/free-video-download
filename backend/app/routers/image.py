"""
图片代理 API
用于绕过防盗链限制，代理获取外部图片
"""
import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Optional
import hashlib
import time
from pathlib import Path

router = APIRouter(prefix="/api", tags=["image"])

# 缓存目录
CACHE_DIR = Path(__file__).parent.parent.parent / "image_cache"
CACHE_DIR.mkdir(exist_ok=True)

# 客户端（带超时设置）
client = httpx.AsyncClient(
    timeout=10.0,
    follow_redirects=True,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)

# 不同平台的 Referer 设置
PLATFORM_REFERERS = {
    "bilibili": "https://www.bilibili.com/",
    "youtube": "https://www.youtube.com/",
    "tiktok": "https://www.tiktok.com/",
    "instagram": "https://www.instagram.com/",
    "twitter": "https://twitter.com/",
    "facebook": "https://www.facebook.com/",
}


def get_cache_filename(url: str) -> Path:
    """生成缓存文件名"""
    # 使用 URL 的 MD5 作为文件名
    url_hash = hashlib.md5(url.encode()).hexdigest()
    # 根据扩展名确定文件类型
    ext = ".jpg"  # 默认扩展名
    if ".png" in url.lower():
        ext = ".png"
    elif ".webp" in url.lower():
        ext = ".webp"
    elif ".gif" in url.lower():
        ext = ".gif"

    return CACHE_DIR / f"{url_hash}{ext}"


def is_cache_valid(cache_path: Path, max_age_hours: int = 24) -> bool:
    """检查缓存是否有效"""
    if not cache_path.exists():
        return False

    # 检查文件年龄
    file_age = time.time() - cache_path.stat().st_mtime
    max_age_seconds = max_age_hours * 3600

    return file_age < max_age_seconds


@router.get("/proxy/image")
async def proxy_image(
    url: str = Query(..., description="图片 URL"),
    platform: Optional[str] = Query(None, description="平台名称（用于设置 Referer）")
):
    """
    代理获取外部图片

    Args:
        url: 图片 URL
        platform: 平台名称（可选，用于设置正确的 Referer）

    Returns:
        Response: 图片数据
    """
    try:
        # 尝试从缓存读取
        cache_path = get_cache_filename(url)

        if is_cache_valid(cache_path):
            # 从缓存返回
            with open(cache_path, "rb") as f:
                image_data = f.read()

            # 确定媒体类型
            media_type = "image/jpeg"
            if cache_path.suffix == ".png":
                media_type = "image/png"
            elif cache_path.suffix == ".webp":
                media_type = "image/webp"
            elif cache_path.suffix == ".gif":
                media_type = "image/gif"

            return Response(content=image_data, media_type=media_type)

        # 从网络获取
        headers = {}

        # 根据平台设置 Referer
        if platform and platform in PLATFORM_REFERERS:
            headers["Referer"] = PLATFORM_REFERERS[platform]

        # 下载图片
        response = await client.get(url, headers=headers)
        response.raise_for_status()

        image_data = response.content

        # 保存到缓存
        with open(cache_path, "wb") as f:
            f.write(image_data)

        # 确定媒体类型
        media_type = response.headers.get("content-type", "image/jpeg")

        return Response(content=image_data, media_type=media_type)

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"获取图片失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"代理图片时发生错误: {str(e)}"
        )


@router.get("/proxy/image/clear")
async def clear_image_cache():
    """
    清理图片缓存

    Returns:
        dict: 操作结果
    """
    try:
        # 删除所有缓存文件
        cache_files = list(CACHE_DIR.glob("*"))
        deleted_count = 0

        for cache_file in cache_files:
            if cache_file.is_file():
                cache_file.unlink()
                deleted_count += 1

        return {
            "message": f"已清理 {deleted_count} 个缓存文件",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"清理缓存失败: {str(e)}"
        )
