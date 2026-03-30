"""
会员状态 API
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_current_user
from app.models import MembershipStatusResponse
from app.services.membership_service import membership_service


router = APIRouter(prefix="/api/membership", tags=["membership"])


@router.get("/me", response_model=MembershipStatusResponse)
def membership_me(
    db: Session = Depends(get_db),
    user=Depends(require_current_user),
):
    return membership_service.get_membership_status(db, user.id)
