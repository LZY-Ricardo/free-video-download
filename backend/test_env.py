"""
测试环境引导。

确保单元测试不受开发机本地 `.env` 配置影响，默认走 sqlite + 本地邮件 + mock 支付。
"""
import os


os.environ["DATABASE_URL"] = "sqlite:///./test_app.db"
os.environ["MAIL_MODE"] = "local"
os.environ["PAYMENT_PROVIDER_MODE"] = "mock"
os.environ.setdefault("APP_BASE_URL", "http://localhost:8000")
os.environ.setdefault("FRONTEND_BASE_URL", "http://localhost:5173")

