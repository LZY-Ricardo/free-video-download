"""
应用配置
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""

    # 应用配置
    APP_NAME: str = "万能视频下载器"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS 配置
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # 下载配置
    DOWNLOAD_DIR: str = "downloads"
    MAX_CONCURRENT_DOWNLOADS: int = 3

    # 限流配置
    RATE_LIMIT_REQUESTS: int = 5
    RATE_LIMIT_PERIOD: int = 60  # 秒

    class Config:
        env_file = ".env"


settings = Settings()
