"""
应用配置
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator


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

    # AI 配置（可选，未配置时使用本地规则回退）
    AI_PROVIDER: str = "openai_compatible"
    AI_MODEL: str = "gpt-4o-mini"
    AI_API_BASE_URL: str = "https://api.openai.com/v1"
    AI_API_KEY: str = ""
    AI_TIMEOUT_SECONDS: int = 60
    AI_MAX_TRANSCRIPT_SEGMENTS: int = 400
    AI_NORMALIZE_ZH_TO_SIMPLIFIED: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def normalize_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "off", "no"}:
                return False
            if normalized in {"debug", "true", "1", "on", "yes"}:
                return True
        return value

    class Config:
        env_file = ".env"


settings = Settings()
