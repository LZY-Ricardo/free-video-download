"""
应用配置
"""
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用设置"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./app.db"

    # 限流配置
    RATE_LIMIT_REQUESTS: int = 5
    RATE_LIMIT_PERIOD: int = 60  # 秒

    # 认证配置
    JWT_SECRET: str = "vidgrab-dev-secret-change-me-to-a-32-byte-key"
    JWT_EXPIRE_DAYS: int = 7
    ACCESS_TOKEN_COOKIE_NAME: str = "vidgrab_access_token"

    # 邮件配置
    MAIL_MODE: str = "local"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    # Resend 配置
    RESEND_API_KEY: str = ""
    MAIL_FROM_NAME: str = "VidGrab"
    MAIL_FROM_ADDRESS: str = "noreply@mail.sunandyu.top"
    APP_BASE_URL: str = "http://localhost:8000"
    FRONTEND_BASE_URL: str = "http://localhost:5173"

    # 支付配置
    PAYMENT_PROVIDER_MODE: str = "mock"
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID: str = ""

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


settings = Settings()
