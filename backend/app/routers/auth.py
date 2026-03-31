"""
认证 API
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user_optional
from app.models import (
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import auth_service
from app.security import create_access_token


router = APIRouter(prefix="/api/auth", tags=["auth"])


def _should_use_secure_cookie() -> bool:
    return (not settings.DEBUG) and settings.FRONTEND_BASE_URL.startswith("https://")


@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        result = auth_service.register_user(db, request.email, request.password)
        return RegisterResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    try:
        auth_service.verify_email(db, token)
        return RedirectResponse(f"{settings.FRONTEND_BASE_URL}/?verify=success")
    except ValueError:
        return RedirectResponse(f"{settings.FRONTEND_BASE_URL}/?verify=failed")


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        user = auth_service.authenticate_user(db, request.email, request.password)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    token = create_access_token(user.id)
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        max_age=settings.JWT_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
        secure=_should_use_secure_cookie(),
    )
    return LoginResponse(user=auth_service.serialize_user(user))


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=_should_use_secure_cookie(),
    )
    return {"message": "已退出登录"}


@router.get("/me", response_model=CurrentUserResponse)
def current_user(user=Depends(get_current_user_optional)):
    if not user:
        return CurrentUserResponse(authenticated=False, user=None)
    return CurrentUserResponse(authenticated=True, user=auth_service.serialize_user(user))
