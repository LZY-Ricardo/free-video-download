"""
支付 API
"""
from __future__ import annotations

import json

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.db_models import MembershipOrder, User
from app.dependencies import require_current_user
from app.security import utcnow
from app.services.billing_service import billing_service
from app.services.membership_service import membership_service


router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.post("/checkout-session")
def create_checkout_session(
    db: Session = Depends(get_db),
    user=Depends(require_current_user),
):
    try:
        return billing_service.create_checkout_session(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Stripe 创建结账会话失败: {exc.user_message or str(exc)}") from exc


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=400, detail="未配置 Stripe webhook secret")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="无效的 webhook payload") from exc
    except stripe.error.SignatureVerificationError as exc:
        raise HTTPException(status_code=400, detail="无效的 webhook 签名") from exc

    webhook_event, is_new = billing_service.mark_webhook_received(
        db=db,
        stripe_event_id=event["id"],
        event_type=event["type"],
        livemode=event.get("livemode", False),
        payload_json=json.dumps(event, ensure_ascii=False),
    )

    if not is_new:
        return {"received": True, "duplicate": True}

    if event["type"] == "checkout.session.completed":
        session_object = event["data"]["object"]
        order_id = (session_object.get("metadata") or {}).get("order_id")
        if not order_id:
            raise HTTPException(status_code=400, detail="缺少订单元数据")
        order = db.get(MembershipOrder, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        if order.status != "paid":
            order.status = "paid"
            order.paid_at = utcnow()
            order.stripe_checkout_session_id = session_object.get("id")
            order.stripe_payment_intent_id = session_object.get("payment_intent")
            order.stripe_customer_id = session_object.get("customer")
            user = db.get(User, order.user_id)
            if user and order.stripe_customer_id and not user.stripe_customer_id:
                user.stripe_customer_id = order.stripe_customer_id
            membership_service.activate_membership_from_order(db, order)
            webhook_event.processing_status = "processed"
            webhook_event.processed_at = utcnow()
            db.commit()

    return {"received": True}
