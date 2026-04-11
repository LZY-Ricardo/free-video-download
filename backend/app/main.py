"""
FastAPI 主应用
"""
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app import db_models  # noqa: F401
from app.routers import auth, info, download, direct, image, ai, membership, billing, dev_mock_billing

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(info.router)
app.include_router(download.router)
app.include_router(direct.router)
app.include_router(image.router)
app.include_router(ai.router)
app.include_router(auth.router)
app.include_router(membership.router)
app.include_router(billing.router)
app.include_router(dev_mock_billing.router)


@app.on_event("startup")
def create_tables() -> None:
    """创建持久化表。"""
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/api/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


def should_enable_reload(platform_name: Optional[str] = None, env_value: Optional[str] = None) -> bool:
    """决定是否启用 uvicorn reload。

    Windows 下默认关闭，避免 watch/reload 触发的多进程命名管道权限异常。
    可通过 DEV_RELOAD=true 显式开启。
    """
    normalized_env = (env_value if env_value is not None else os.getenv("DEV_RELOAD", "")).strip().lower()
    if normalized_env in {"1", "true", "yes", "on"}:
        return True
    if normalized_env in {"0", "false", "no", "off"}:
        return False

    current_platform = platform_name or os.name
    return current_platform != "nt"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=should_enable_reload(),
    )
