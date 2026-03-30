"""
FastAPI 主应用
"""
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
