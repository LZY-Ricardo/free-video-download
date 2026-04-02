"""
支付 API
"""
from __future__ import annotations

import hmac
import hashlib
import json

import httpx
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
    if settings.PAYMENT_PROVIDER_MODE == "disabled":
        raise HTTPException(status_code=503, detail="支付服务暂未开放，敬请期待")
    try:
        return billing_service.create_checkout_session(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"支付服务请求失败: {exc}") from exc
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Stripe 创建结账会话失败: {exc.user_message or str(exc)}") from exc


def _activate_order_and_membership(db: Session, order_id: str, checkout_id: str | None = None, customer_id: str | None = None):
    order = db.get(MembershipOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status == "paid":
        return

    order.status = "paid"
    order.paid_at = utcnow()
    if checkout_id:
        order.stripe_checkout_session_id = checkout_id
    if customer_id:
        order.stripe_customer_id = customer_id
    user = db.get(User, order.user_id)
    if user and customer_id and not user.stripe_customer_id:
        user.stripe_customer_id = customer_id
    membership_service.activate_membership_from_order(db, order)


def _verify_lemonsqueezy_signature(payload: bytes, signature: str):
    if not settings.LEMONSQUEEZY_WEBHOOK_SECRET:
        raise HTTPException(status_code=400, detail="未配置 Lemon Squeezy webhook secret")
    expected = hmac.new(
        settings.LEMONSQUEEZY_WEBHOOK_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    if not signature or not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=400, detail="无效的 Lemon Squeezy webhook 签名")


@router.post("/webhook")
async def provider_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    provider = settings.PAYMENT_PROVIDER_MODE

    if provider == "stripe":
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
            stripe_event_id=f"stripe:{event['id']}",
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
            _activate_order_and_membership(
                db=db,
                order_id=order_id,
                checkout_id=session_object.get("id"),
                customer_id=session_object.get("customer"),
            )
            order = db.get(MembershipOrder, order_id)
            if order:
                order.stripe_payment_intent_id = session_object.get("payment_intent")
            webhook_event.processing_status = "processed"
            webhook_event.processed_at = utcnow()
            db.commit()
        return {"received": True}

    if provider == "lemonsqueezy":
        signature = request.headers.get("X-Signature", "")
        _verify_lemonsqueezy_signature(payload, signature)
        try:
            event = json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="无效的 webhook payload") from exc

        event_name = event.get("meta", {}).get("event_name", "")
        data_id = event.get("data", {}).get("id", "unknown")
        livemode = not event.get("meta", {}).get("test_mode", False)
        webhook_event, is_new = billing_service.mark_webhook_received(
            db=db,
            stripe_event_id=f"lemonsqueezy:{event_name}:{data_id}",
            event_type=event_name,
            livemode=livemode,
            payload_json=json.dumps(event, ensure_ascii=False),
        )

        if not is_new:
            return {"received": True, "duplicate": True}

        if event_name == "order_created":
            custom_data = event.get("meta", {}).get("custom_data", {}) or {}
            order_id = custom_data.get("order_id")
            if not order_id:
                raise HTTPException(status_code=400, detail="缺少订单元数据")
            _activate_order_and_membership(
                db=db,
                order_id=order_id,
                checkout_id=data_id,
            )
            webhook_event.processing_status = "processed"
            webhook_event.processed_at = utcnow()
            db.commit()
        return {"received": True}

    raise HTTPException(status_code=400, detail=f"当前支付模式不支持 webhook: {provider}")
