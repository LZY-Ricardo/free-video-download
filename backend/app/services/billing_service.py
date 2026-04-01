"""
账单与支付服务
"""
from __future__ import annotations

import httpx
from uuid import uuid4

import stripe
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db_models import MembershipOrder, StripeWebhookEvent, User
from app.security import utcnow
from app.services.membership_service import membership_service


class BillingService:
    LEMONSQUEEZY_CHECKOUT_ENDPOINT = "https://api.lemonsqueezy.com/v1/checkouts"
    PLAN_CODE = "vip_30d"
    AMOUNT_FEN = 1990
    CURRENCY = "cny"
    DURATION_DAYS = 30

    @staticmethod
    def _get_checkout_sessions_api(client):
        """
        兼容不同版本 stripe-python 的 StripeClient 结构。

        - 新版：client.v1.checkout.sessions
        - 旧版：client.checkout.sessions
        """
        if hasattr(client, "v1") and getattr(client.v1, "checkout", None):
            return client.v1.checkout.sessions
        return client.checkout.sessions

    def create_checkout_session(self, db: Session, user: User) -> dict:
        existing_order = self._find_open_order(db, user.id)
        if existing_order:
            if settings.PAYMENT_PROVIDER_MODE == "lemonsqueezy":
                return self._create_lemonsqueezy_checkout(db, user, existing_order)
            return self._build_existing_checkout_response(existing_order)

        order = MembershipOrder(
            user_id=user.id,
            order_type="checkout_session",
            plan_code=self.PLAN_CODE,
            amount_fen=self.AMOUNT_FEN,
            currency=self.CURRENCY,
            duration_days=self.DURATION_DAYS,
            status="pending",
            idempotency_key=str(uuid4()),
        )
        db.add(order)
        db.flush()

        if settings.PAYMENT_PROVIDER_MODE == "mock":
            order.status = "checkout_created"
            db.commit()
            return {
                "order_id": order.id,
                "checkout_url": f"{settings.FRONTEND_BASE_URL}/?mock_checkout_order_id={order.id}",
                "provider": "mock",
            }

        if settings.PAYMENT_PROVIDER_MODE == "lemonsqueezy":
            return self._create_lemonsqueezy_checkout(db, user, order)

        return self._create_stripe_checkout_session(db, user, order)

    def _find_open_order(self, db: Session, user_id: str) -> MembershipOrder | None:
        return db.scalar(
            select(MembershipOrder)
            .where(
                MembershipOrder.user_id == user_id,
                MembershipOrder.plan_code == self.PLAN_CODE,
                MembershipOrder.status.in_(("pending", "checkout_created")),
            )
            .order_by(desc(MembershipOrder.created_at))
            .limit(1)
        )

    def _build_existing_checkout_response(self, order: MembershipOrder) -> dict:
        if settings.PAYMENT_PROVIDER_MODE == "mock":
            return {
                "order_id": order.id,
                "checkout_url": f"{settings.FRONTEND_BASE_URL}/?mock_checkout_order_id={order.id}",
                "provider": "mock",
            }

        if settings.PAYMENT_PROVIDER_MODE == "stripe" and order.stripe_checkout_session_id:
            client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)
            sessions_api = self._get_checkout_sessions_api(client)
            session = sessions_api.retrieve(order.stripe_checkout_session_id)
            return {
                "order_id": order.id,
                "checkout_url": session["url"],
                "provider": "stripe",
            }

        return {
            "order_id": order.id,
            "checkout_url": f"{settings.FRONTEND_BASE_URL}/?mock_checkout_order_id={order.id}",
            "provider": settings.PAYMENT_PROVIDER_MODE,
        }

    def _create_stripe_checkout_session(self, db: Session, user: User, order: MembershipOrder) -> dict:
        client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)
        sessions_api = self._get_checkout_sessions_api(client)
        params = {
            "mode": "payment",
            "line_items": [{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
            "success_url": f"{settings.FRONTEND_BASE_URL}/?billing=success&session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{settings.FRONTEND_BASE_URL}/?billing=cancel",
            "metadata": {
                "order_id": order.id,
                "user_id": user.id,
                "plan_code": self.PLAN_CODE,
            },
        }
        if user.stripe_customer_id:
            params["customer"] = user.stripe_customer_id
        else:
            params["customer_email"] = user.email

        session = sessions_api.create(
            params=params,
            options={"idempotency_key": order.idempotency_key},
        )
        order.status = "checkout_created"
        order.stripe_checkout_session_id = session["id"]
        db.commit()
        return {
            "order_id": order.id,
            "checkout_url": session["url"],
            "provider": "stripe",
        }

    def _create_lemonsqueezy_checkout(self, db: Session, user: User, order: MembershipOrder) -> dict:
        if not settings.LEMONSQUEEZY_API_KEY:
            raise ValueError("未配置 LEMONSQUEEZY_API_KEY")
        if not settings.LEMONSQUEEZY_STORE_ID:
            raise ValueError("未配置 LEMONSQUEEZY_STORE_ID")
        if not settings.LEMONSQUEEZY_VARIANT_ID:
            raise ValueError("未配置 LEMONSQUEEZY_VARIANT_ID")

        payload = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_options": {
                        "embed": False,
                    },
                    "checkout_data": {
                        "custom": {
                            "order_id": order.id,
                            "user_id": user.id,
                            "plan_code": self.PLAN_CODE,
                        }
                    },
                },
                "relationships": {
                    "store": {
                        "data": {
                            "type": "stores",
                            "id": str(settings.LEMONSQUEEZY_STORE_ID),
                        }
                    },
                    "variant": {
                        "data": {
                            "type": "variants",
                            "id": str(settings.LEMONSQUEEZY_VARIANT_ID),
                        }
                    },
                },
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.LEMONSQUEEZY_API_KEY}",
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
        }

        with httpx.Client(timeout=15) as client:
            response = client.post(self.LEMONSQUEEZY_CHECKOUT_ENDPOINT, json=payload, headers=headers)

        if response.status_code >= 400:
            raise ValueError(f"Lemon Squeezy 创建结账失败: {response.text}")

        body = response.json()
        checkout_url = body.get("data", {}).get("attributes", {}).get("url")
        checkout_id = body.get("data", {}).get("id")
        if not checkout_url:
            raise ValueError("Lemon Squeezy 返回缺少 checkout URL")

        order.status = "checkout_created"
        # 复用现有字段保存第三方 checkout id，避免引入新迁移。
        order.stripe_checkout_session_id = checkout_id
        db.commit()
        return {
            "order_id": order.id,
            "checkout_url": checkout_url,
            "provider": "lemonsqueezy",
        }

    def complete_mock_order(self, db: Session, order_id: str, user_id: str) -> MembershipOrder:
        order = db.get(MembershipOrder, order_id)
        if not order:
            raise ValueError("订单不存在")

        if order.user_id != user_id:
            raise PermissionError("无权操作该订单")

        if order.status == "paid":
            return order

        if order.status not in {"pending", "checkout_created"}:
            raise ValueError("订单当前状态不允许完成支付")

        order.status = "paid"
        order.paid_at = utcnow()
        membership_service.activate_membership_from_order(db, order)
        db.commit()
        db.refresh(order)
        return order

    def mark_webhook_received(
        self,
        db: Session,
        stripe_event_id: str,
        event_type: str,
        livemode: bool,
        payload_json: str,
    ) -> tuple[StripeWebhookEvent, bool]:
        existing = db.query(StripeWebhookEvent).filter(
            StripeWebhookEvent.stripe_event_id == stripe_event_id
        ).one_or_none()
        if existing:
            return existing, False

        event = StripeWebhookEvent(
            stripe_event_id=stripe_event_id,
            event_type=event_type,
            livemode=1 if livemode else 0,
            payload_json=payload_json,
            processing_status="received",
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event, True


billing_service = BillingService()
