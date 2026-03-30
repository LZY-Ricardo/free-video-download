"""
邮件发送服务
"""
from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.config import settings


class EmailService:
    """开发环境和生产环境共用的邮件发送抽象。"""

    def send_verification_email(self, email: str, verify_url: str) -> dict:
        if settings.MAIL_MODE == "local":
            print(f"[local-mail] verification email -> {email}: {verify_url}")
            return {
                "mode": "local",
                "debug_verify_url": verify_url,
            }

        if settings.MAIL_MODE == "smtp":
            self._send_smtp_email(email, verify_url)
            return {"mode": "smtp", "debug_verify_url": None}

        raise ValueError("不支持的邮件模式，请检查 MAIL_MODE 配置")

    def _send_smtp_email(self, email: str, verify_url: str) -> None:
        message = EmailMessage()
        message["Subject"] = "VidGrab 邮箱验证"
        message["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
        message["To"] = email
        message.set_content(
            "欢迎注册 VidGrab。\n\n"
            f"请点击以下链接完成邮箱验证：\n{verify_url}\n\n"
            "如果这不是你的操作，请忽略此邮件。"
        )

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)


email_service = EmailService()
