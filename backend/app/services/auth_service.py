"""
认证服务
"""
from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import EmailVerificationToken, User
from app.models import UserProfile
from app.security import (
    generate_raw_token,
    hash_password,
    hash_token,
    utcnow,
    verify_password,
)
from app.services.email_service import email_service
from app.config import settings


class AuthService:
    """用户注册、验证和登录核心逻辑。"""

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    def register_user(self, db: Session, email: str, password: str) -> dict:
        normalized_email = self.normalize_email(email)
        existing_user = db.scalar(select(User).where(User.email == normalized_email))

        if existing_user and existing_user.email_verified_at:
            raise ValueError("该邮箱已注册，请直接登录")

        if existing_user:
            user = existing_user
            user.password_hash = hash_password(password)
            user.status = "pending_verification"
            db.query(EmailVerificationToken).filter(
                EmailVerificationToken.user_id == user.id
            ).delete()
        else:
            user = User(
                email=normalized_email,
                password_hash=hash_password(password),
                status="pending_verification",
            )
            db.add(user)
            db.flush()

        raw_token = generate_raw_token()
        verification_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=utcnow() + timedelta(hours=24),
        )
        db.add(verification_token)
        db.commit()

        verify_url = f"{settings.APP_BASE_URL}/api/auth/verify-email?token={raw_token}"
        email_result = email_service.send_verification_email(user.email, verify_url)
        return {
            "message": "注册成功，请查收验证邮件",
            "requires_email_verification": True,
            "debug_verify_url": email_result.get("debug_verify_url"),
        }

    def verify_email(self, db: Session, raw_token: str) -> None:
        token_hash = hash_token(raw_token)
        token = db.scalar(
            select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)
        )
        if not token:
            raise ValueError("验证链接无效或已过期")

        now = utcnow()
        if token.used_at is not None or token.expires_at < now:
            raise ValueError("验证链接无效或已过期")

        user = db.get(User, token.user_id)
        if not user:
            raise ValueError("关联用户不存在")

        token.used_at = now
        user.email_verified_at = now
        user.status = "active"
        db.commit()

    def authenticate_user(self, db: Session, email: str, password: str) -> User:
        normalized_email = self.normalize_email(email)
        user = db.scalar(select(User).where(User.email == normalized_email))

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("邮箱或密码错误")

        if not user.email_verified_at:
            raise PermissionError("邮箱尚未验证，请先查收验证邮件")

        user.last_login_at = utcnow()
        db.commit()
        return user

    def get_user_by_id(self, db: Session, user_id: str) -> User | None:
        return db.get(User, user_id)

    def serialize_user(self, user: User) -> UserProfile:
        return UserProfile(
            id=user.id,
            email=user.email,
            email_verified=bool(user.email_verified_at),
        )


auth_service = AuthService()
