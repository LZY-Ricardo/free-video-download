"""Standalone test server for Douyin functionality"""
import sys
sys.path.insert(0, '.')

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.douyin_service import douyin_service

app = FastAPI(title="Douyin Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InfoRequest(BaseModel):
    url: str

def is_douyin_url(url: str) -> bool:
    douyin_domains = ['douyin.com', 'iesdouyin.com', 'v.douyin.com']
    return any(domain in url for domain in douyin_domains)

@app.post("/api/info")
async def get_video_info(request: InfoRequest):
    """Get video info"""
    if is_douyin_url(request.url):
        info = douyin_service.get_video_info(request.url)
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
        return {
            "title": info['title'],
            "duration": info['duration'],
            "thumbnail": info['thumbnail'],
            "platform": "douyin",
            "uploader": info['uploader'],
            "view_count": info.get('view_count', 0),
            "formats": formats,
            "is_douyin": True,
            "direct_url": info.get('direct_url', ''),
            "note": "Douyin video with parser"
        }
    else:
        return {"error": "Not a Douyin URL"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
