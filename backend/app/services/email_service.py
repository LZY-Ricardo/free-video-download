"""
邮件发送服务
"""
from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.config import settings


def _build_html_email(verify_url: str) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>VidGrab 邮箱验证</title>
</head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.06);">
          <!-- Header -->
          <tr>
            <td style="background:#1D4ED8;padding:28px 36px;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:36px;height:36px;background:#2563EB;border-radius:50%;text-align:center;vertical-align:middle;">
                    <span style="color:#fff;font-size:18px;line-height:36px;">&#9654;</span>
                  </td>
                  <td style="padding-left:10px;color:#ffffff;font-size:20px;font-weight:700;">VidGrab</td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:36px 36px 12px;">
              <h1 style="margin:0 0 12px;font-size:22px;font-weight:700;color:#111827;">验证你的邮箱</h1>
              <p style="margin:0 0 24px;font-size:15px;line-height:1.6;color:#6B7280;">
                感谢注册 VidGrab！点击下方按钮完成邮箱验证，即可登录并使用 AI 学习助手。
              </p>
              <a href="{verify_url}"
                 style="display:inline-block;padding:13px 28px;background:#1D4ED8;color:#ffffff;font-size:15px;font-weight:600;border-radius:8px;text-decoration:none;">
                验证邮箱
              </a>
              <p style="margin:24px 0 0;font-size:13px;color:#9CA3AF;">
                按钮无法点击？复制以下链接到浏览器：<br />
                <a href="{verify_url}" style="color:#1D4ED8;word-break:break-all;">{verify_url}</a>
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:24px 36px 32px;border-top:1px solid #F3F4F6;margin-top:24px;">
              <p style="margin:0;font-size:12px;color:#D1D5DB;">
                此链接 24 小时内有效。如果这不是你的操作，请忽略此邮件。
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


class EmailService:
    """开发环境和生产环境共用的邮件发送抽象。"""

    def send_verification_email(self, email: str, verify_url: str) -> dict:
        if settings.MAIL_MODE == "local":
            print(f"[local-mail] verification email -> {email}: {verify_url}")
            return {
                "mode": "local",
                "debug_verify_url": verify_url,
            }

        if settings.MAIL_MODE == "resend":
            self._send_resend_email(email, verify_url)
            return {"mode": "resend", "debug_verify_url": None}

        if settings.MAIL_MODE == "smtp":
            self._send_smtp_email(email, verify_url)
            return {"mode": "smtp", "debug_verify_url": None}

        raise ValueError("不支持的邮件模式，请检查 MAIL_MODE 配置")

    def _send_resend_email(self, email: str, verify_url: str) -> None:
        import resend

        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            "from": f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM_ADDRESS}>",
            "to": [email],
            "subject": "VidGrab 邮箱验证",
            "html": _build_html_email(verify_url),
        })

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
