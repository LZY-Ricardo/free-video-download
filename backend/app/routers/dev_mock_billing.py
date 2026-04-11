"""
开发环境 mock 支付接口
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import require_current_user
from app.services.billing_service import billing_service
from app.services.membership_service import membership_service


router = APIRouter(prefix="/api/dev/mock-billing", tags=["mock-billing"])


@router.post("/complete-order/{order_id}")
def complete_mock_order(
    order_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_current_user),
):
    if settings.PAYMENT_PROVIDER_MODE != "mock":
        raise HTTPException(status_code=404, detail="mock 支付模式未启用")

    try:
        order = billing_service.complete_mock_order(db, order_id, user.id)
        return {"message": "模拟支付成功", "order_id": order.id, "status": order.status}
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/grant-lifetime")
def grant_lifetime_membership(
    db: Session = Depends(get_db),
    user=Depends(require_current_user),
):
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="开发接口未启用")

    membership = membership_service.activate_lifetime_membership(db, user.id)
    db.commit()
    status = membership_service.get_membership_status(db, user.id)
    return {
        "message": "永久会员已开通",
        "user_id": user.id,
        "plan_code": membership.plan_code,
        "is_member": status.is_member,
    }
