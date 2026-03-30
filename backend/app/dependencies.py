"""
FastAPI 依赖
"""
from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.db_models import User
from app.security import decode_access_token
from app.services.auth_service import auth_service
from app.services.membership_service import membership_service


def get_current_user_optional(
    token: str | None = Cookie(default=None, alias=settings.ACCESS_TOKEN_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> User | None:
    if not token:
        return None

    try:
        payload = decode_access_token(token)
    except ValueError:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None
    return auth_service.get_user_by_id(db, user_id)


def require_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    return user


def require_active_member(
    db: Session = Depends(get_db),
    user: User = Depends(require_current_user),
) -> User:
    if not membership_service.has_active_membership(db, user.id):
        raise HTTPException(status_code=403, detail="当前功能仅限会员使用，请先开通会员")
    return user
