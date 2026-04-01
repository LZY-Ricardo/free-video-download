import unittest
import json
import hmac
import hashlib
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

from fastapi.testclient import TestClient

import test_env  # noqa: F401
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.db_models import MembershipOrder, User
from app.main import app
from app.security import hash_password, utcnow


class TestBillingAPI(unittest.TestCase):
    def setUp(self):
        self.original_mode = settings.PAYMENT_PROVIDER_MODE
        self.original_secret = settings.STRIPE_SECRET_KEY
        self.original_price_id = settings.STRIPE_PRICE_ID
        self.original_webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self.original_ls_api_key = settings.LEMONSQUEEZY_API_KEY
        self.original_ls_store_id = settings.LEMONSQUEEZY_STORE_ID
        self.original_ls_variant_id = settings.LEMONSQUEEZY_VARIANT_ID
        self.original_ls_webhook_secret = settings.LEMONSQUEEZY_WEBHOOK_SECRET
        settings.PAYMENT_PROVIDER_MODE = "mock"
        settings.STRIPE_SECRET_KEY = ""
        settings.STRIPE_PRICE_ID = ""
        settings.STRIPE_WEBHOOK_SECRET = ""
        settings.LEMONSQUEEZY_API_KEY = ""
        settings.LEMONSQUEEZY_STORE_ID = ""
        settings.LEMONSQUEEZY_VARIANT_ID = ""
        settings.LEMONSQUEEZY_WEBHOOK_SECRET = ""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.user = self._create_verified_user()
        self.client.post(
            "/api/auth/login",
            json={"email": self.user["email"], "password": self.user["password"]},
        )

    def tearDown(self):
        self.client.close()
        settings.PAYMENT_PROVIDER_MODE = self.original_mode
        settings.STRIPE_SECRET_KEY = self.original_secret
        settings.STRIPE_PRICE_ID = self.original_price_id
        settings.STRIPE_WEBHOOK_SECRET = self.original_webhook_secret
        settings.LEMONSQUEEZY_API_KEY = self.original_ls_api_key
        settings.LEMONSQUEEZY_STORE_ID = self.original_ls_store_id
        settings.LEMONSQUEEZY_VARIANT_ID = self.original_ls_variant_id
        settings.LEMONSQUEEZY_WEBHOOK_SECRET = self.original_ls_webhook_secret

    def _create_verified_user(self):
        with SessionLocal() as db:
            user = User(
                email="payer@example.com",
                password_hash=hash_password("password123"),
                email_verified_at=utcnow(),
                status="active",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return {"id": user.id, "email": user.email, "password": "password123"}

    def _create_verified_user_with_email(self, email: str, password: str = "password123"):
        with SessionLocal() as db:
            user = User(
                email=email,
                password_hash=hash_password(password),
                email_verified_at=utcnow(),
                status="active",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return {"id": user.id, "email": user.email, "password": password}

    def test_create_checkout_session_in_mock_mode(self):
        response = self.client.post("/api/billing/checkout-session")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("order_id", payload)
        self.assertIn("checkout_url", payload)
        self.assertIn("mock_checkout_order_id", payload["checkout_url"])

    def test_complete_mock_order_activates_membership(self):
        checkout_response = self.client.post("/api/billing/checkout-session")
        order_id = checkout_response.json()["order_id"]

        complete_response = self.client.post(f"/api/dev/mock-billing/complete-order/{order_id}")
        self.assertEqual(complete_response.status_code, 200)

        membership_response = self.client.get("/api/membership/me")
        self.assertEqual(membership_response.status_code, 200)
        self.assertTrue(membership_response.json()["is_member"])
        self.assertEqual(membership_response.json()["status"], "active")

    def test_complete_mock_order_is_idempotent_for_paid_orders(self):
        checkout_response = self.client.post("/api/billing/checkout-session")
        order_id = checkout_response.json()["order_id"]

        self.client.post(f"/api/dev/mock-billing/complete-order/{order_id}")
        first_membership = self.client.get("/api/membership/me").json()

        second_complete = self.client.post(f"/api/dev/mock-billing/complete-order/{order_id}")
        second_membership = self.client.get("/api/membership/me").json()

        self.assertEqual(second_complete.status_code, 200)
        self.assertEqual(first_membership["expires_at"], second_membership["expires_at"])

    def test_reuses_existing_open_mock_order_for_same_user(self):
        first_response = self.client.post("/api/billing/checkout-session")
        second_response = self.client.post("/api/billing/checkout-session")

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(first_response.json()["order_id"], second_response.json()["order_id"])

    def test_user_cannot_complete_another_users_mock_order(self):
        checkout_response = self.client.post("/api/billing/checkout-session")
        order_id = checkout_response.json()["order_id"]

        second_client = TestClient(app)
        other_user = self._create_verified_user_with_email("other@example.com")
        second_client.post(
            "/api/auth/login",
            json={"email": other_user["email"], "password": other_user["password"]},
        )
        try:
            response = second_client.post(f"/api/dev/mock-billing/complete-order/{order_id}")
        finally:
            second_client.close()

        self.assertEqual(response.status_code, 403)

    @patch("app.services.billing_service.stripe.StripeClient")
    def test_create_checkout_session_in_stripe_mode_includes_metadata_and_idempotency_key(self, mock_stripe_client):
        mock_session = {"id": "cs_test_123", "url": "https://checkout.stripe.com/test"}
        mock_instance = MagicMock()
        mock_instance.v1.checkout.sessions.create.return_value = mock_session
        mock_stripe_client.return_value = mock_instance

        original_mode = settings.PAYMENT_PROVIDER_MODE
        original_secret = settings.STRIPE_SECRET_KEY
        original_price_id = settings.STRIPE_PRICE_ID
        try:
            settings.PAYMENT_PROVIDER_MODE = "stripe"
            settings.STRIPE_SECRET_KEY = "sk_test_123"
            settings.STRIPE_PRICE_ID = "price_123"

            response = self.client.post("/api/billing/checkout-session")
            self.assertEqual(response.status_code, 200)

            _, kwargs = mock_instance.v1.checkout.sessions.create.call_args
            self.assertEqual(kwargs["params"]["mode"], "payment")
            self.assertEqual(kwargs["params"]["line_items"][0]["price"], "price_123")
            self.assertEqual(kwargs["params"]["metadata"]["plan_code"], "vip_30d")
            self.assertEqual(kwargs["params"]["metadata"]["user_id"], self.user["id"])
            self.assertIn("idempotency_key", kwargs["options"])
        finally:
            settings.PAYMENT_PROVIDER_MODE = original_mode
            settings.STRIPE_SECRET_KEY = original_secret
            settings.STRIPE_PRICE_ID = original_price_id

    @patch("app.services.billing_service.stripe.StripeClient")
    def test_create_checkout_session_supports_legacy_stripe_client_without_v1(self, mock_stripe_client):
        legacy_create = MagicMock(return_value={"id": "cs_legacy_123", "url": "https://checkout.stripe.com/legacy"})
        legacy_checkout = SimpleNamespace(
            sessions=SimpleNamespace(create=legacy_create),
        )
        mock_stripe_client.return_value = SimpleNamespace(checkout=legacy_checkout)

        original_mode = settings.PAYMENT_PROVIDER_MODE
        original_secret = settings.STRIPE_SECRET_KEY
        original_price_id = settings.STRIPE_PRICE_ID
        try:
            settings.PAYMENT_PROVIDER_MODE = "stripe"
            settings.STRIPE_SECRET_KEY = "sk_test_123"
            settings.STRIPE_PRICE_ID = "price_123"

            response = self.client.post("/api/billing/checkout-session")
        finally:
            settings.PAYMENT_PROVIDER_MODE = original_mode
            settings.STRIPE_SECRET_KEY = original_secret
            settings.STRIPE_PRICE_ID = original_price_id

        self.assertEqual(response.status_code, 200)
        _, kwargs = legacy_create.call_args
        self.assertEqual(kwargs["params"]["metadata"]["plan_code"], "vip_30d")

    @patch("app.routers.billing.stripe.Webhook.construct_event")
    def test_webhook_duplicate_event_is_idempotent(self, mock_construct_event):
        with SessionLocal() as db:
            order = MembershipOrder(
                user_id=self.user["id"],
                plan_code="vip_30d",
                amount_fen=1990,
                currency="cny",
                duration_days=30,
                status="checkout_created",
                idempotency_key="order-idempotency-1",
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            order_id = order.id

        mock_construct_event.return_value = {
            "id": "evt_test_duplicate_1",
            "type": "checkout.session.completed",
            "livemode": False,
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "payment_intent": "pi_test_123",
                    "customer": "cus_test_123",
                    "metadata": {"order_id": order_id},
                }
            },
        }

        original_secret = settings.STRIPE_WEBHOOK_SECRET
        settings.STRIPE_WEBHOOK_SECRET = "whsec_test"
        try:
            first_response = self.client.post(
                "/api/billing/webhook",
                content=b"{}",
                headers={"Stripe-Signature": "sig_test"},
            )
            second_response = self.client.post(
                "/api/billing/webhook",
                content=b"{}",
                headers={"Stripe-Signature": "sig_test"},
            )
        finally:
            settings.STRIPE_WEBHOOK_SECRET = original_secret

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertTrue(second_response.json()["duplicate"])

        membership_response = self.client.get("/api/membership/me")
        self.assertTrue(membership_response.json()["is_member"])

    @patch("app.services.billing_service.httpx.Client")
    def test_create_checkout_session_in_lemonsqueezy_mode(self, mock_httpx_client):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "data": {
                "id": "lsc_123",
                "attributes": {
                    "url": "https://vidgrab.lemonsqueezy.com/buy/abc123",
                },
            }
        }
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_httpx_client.return_value = mock_client

        original_mode = settings.PAYMENT_PROVIDER_MODE
        try:
            settings.PAYMENT_PROVIDER_MODE = "lemonsqueezy"
            settings.LEMONSQUEEZY_API_KEY = "ls_api_xxx"
            settings.LEMONSQUEEZY_STORE_ID = "1111"
            settings.LEMONSQUEEZY_VARIANT_ID = "2222"

            response = self.client.post("/api/billing/checkout-session")
        finally:
            settings.PAYMENT_PROVIDER_MODE = original_mode

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["provider"], "lemonsqueezy")
        self.assertIn("lemonsqueezy.com", payload["checkout_url"])

        _, kwargs = mock_client.post.call_args
        custom = kwargs["json"]["data"]["attributes"]["checkout_data"]["custom"]
        self.assertEqual(custom["plan_code"], "vip_30d")
        self.assertEqual(custom["user_id"], self.user["id"])

    def test_lemonsqueezy_order_created_webhook_activates_membership(self):
        original_mode = settings.PAYMENT_PROVIDER_MODE
        original_secret = settings.LEMONSQUEEZY_WEBHOOK_SECRET
        try:
            settings.PAYMENT_PROVIDER_MODE = "mock"
            checkout_response = self.client.post("/api/billing/checkout-session")
            order_id = checkout_response.json()["order_id"]

            settings.PAYMENT_PROVIDER_MODE = "lemonsqueezy"
            settings.LEMONSQUEEZY_WEBHOOK_SECRET = "ls_whsec_123"

            event = {
                "meta": {
                    "event_name": "order_created",
                    "test_mode": True,
                    "custom_data": {
                        "order_id": order_id,
                    },
                },
                "data": {"id": "123456"},
            }
            payload = json.dumps(event).encode("utf-8")
            signature = hmac.new(
                settings.LEMONSQUEEZY_WEBHOOK_SECRET.encode("utf-8"),
                payload,
                hashlib.sha256,
            ).hexdigest()

            response = self.client.post(
                "/api/billing/webhook",
                content=payload,
                headers={"X-Signature": signature},
            )
            duplicate_response = self.client.post(
                "/api/billing/webhook",
                content=payload,
                headers={"X-Signature": signature},
            )
        finally:
            settings.PAYMENT_PROVIDER_MODE = original_mode
            settings.LEMONSQUEEZY_WEBHOOK_SECRET = original_secret

        self.assertEqual(response.status_code, 200)
        self.assertEqual(duplicate_response.status_code, 200)
        self.assertTrue(duplicate_response.json()["duplicate"])

        membership_response = self.client.get("/api/membership/me")
        self.assertTrue(membership_response.json()["is_member"])


if __name__ == "__main__":
    unittest.main()
