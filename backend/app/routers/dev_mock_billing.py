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
