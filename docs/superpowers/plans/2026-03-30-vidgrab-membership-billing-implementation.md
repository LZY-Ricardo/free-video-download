# VidGrab Membership Billing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 VidGrab 增加邮箱账号、会员状态、Stripe 一次性购买 30 天会员、AI 会员权限控制，以及可离线开发的 mock 支付模式。

**Architecture:** 后端新增 SQLite + SQLAlchemy 持久化层、认证与会员服务、Stripe 账单服务和 webhook 处理；前端新增登录注册与会员状态展示，并在 AI 学习助手处接入权限引导。真实支付使用 Stripe Checkout Session，开发与测试同时支持 mock provider。

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, Argon2, PyJWT, Stripe Python SDK, Vue 3, Axios, Tailwind CSS

---

## File Structure

### Backend

- Create: `backend/app/database.py`
- Create: `backend/app/db_models.py`
- Create: `backend/app/security.py`
- Create: `backend/app/dependencies.py`
- Create: `backend/app/services/email_service.py`
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/services/membership_service.py`
- Create: `backend/app/services/billing_service.py`
- Create: `backend/app/routers/auth.py`
- Create: `backend/app/routers/membership.py`
- Create: `backend/app/routers/billing.py`
- Create: `backend/app/routers/dev_mock_billing.py`
- Modify: `backend/app/config.py`
- Modify: `backend/app/models.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/routers/ai.py`
- Modify: `backend/app/routers/__init__.py`
- Modify: `backend/requirements.txt`

### Frontend

- Create: `frontend/src/composables/useAuth.ts`
- Create: `frontend/src/composables/useMembership.ts`
- Create: `frontend/src/components/AuthModal.vue`
- Create: `frontend/src/components/MembershipCard.vue`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/components/AIAssistant.vue`

### Tests

- Create: `backend/test_auth_api.py`
- Create: `backend/test_membership_api.py`
- Create: `backend/test_billing_api.py`
- Create: `backend/test_billing_service.py`
- Modify: `backend/test_ai_api.py`

---

### Task 1: Bootstrap Database And Runtime Configuration

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/db_models.py`
- Modify: `backend/app/config.py`
- Modify: `backend/app/main.py`
- Modify: `backend/requirements.txt`
- Test: `backend/test_billing_service.py`

- [ ] **Step 1: Write the failing configuration/database smoke test**

```python
def test_database_bootstrap_creates_sqlite_engine():
    from app.database import engine, SessionLocal

    assert engine is not None
    assert SessionLocal is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "backend"; python -m unittest test_billing_service.py`
Expected: FAIL with `ModuleNotFoundError` for `app.database`

- [ ] **Step 3: Add runtime dependencies and config fields**

```python
DATABASE_URL: str = "sqlite:///./app.db"
JWT_SECRET: str = "change-me"
JWT_EXPIRE_DAYS: int = 7
MAIL_MODE: str = "local"
PAYMENT_PROVIDER_MODE: str = "mock"
STRIPE_SECRET_KEY: str = ""
STRIPE_PUBLISHABLE_KEY: str = ""
STRIPE_WEBHOOK_SECRET: str = ""
STRIPE_PRICE_ID: str = ""
APP_BASE_URL: str = "http://localhost:8000"
FRONTEND_BASE_URL: str = "http://localhost:5173"
```

- [ ] **Step 4: Implement database bootstrap and SQLAlchemy base**

```python
engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
```

- [ ] **Step 5: Add SQLAlchemy models and startup table creation**

```python
@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd "backend"; python -m unittest test_billing_service.py`
Expected: PASS for bootstrap smoke test

---

### Task 2: Build User, Token, Order, Membership, And Webhook Models

**Files:**
- Create: `backend/app/db_models.py`
- Modify: `backend/app/models.py`
- Test: `backend/test_billing_service.py`

- [ ] **Step 1: Write the failing schema behavior tests**

```python
def test_membership_extension_uses_existing_expiry_when_active():
    from datetime import datetime, timedelta
    from app.services.membership_service import MembershipService

    current = datetime.utcnow() + timedelta(days=10)
    starts_at, expires_at = MembershipService.calculate_membership_window(current, 30)
    assert expires_at > current
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "backend"; python -m unittest test_billing_service.py`
Expected: FAIL with `ImportError` for `MembershipService`

- [ ] **Step 3: Add SQLAlchemy entities**

```python
class User(Base):
    __tablename__ = "users"
    id = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    email = mapped_column(String, unique=True, index=True)
    password_hash = mapped_column(String)
    email_verified_at = mapped_column(DateTime, nullable=True)
```

- [ ] **Step 4: Add Pydantic request/response models**

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class CurrentUserResponse(BaseModel):
    authenticated: bool
    user: UserProfile | None = None
```

- [ ] **Step 5: Implement membership window helper**

```python
base_start = active_expires_at if active_expires_at and active_expires_at > now else now
return now, base_start + timedelta(days=duration_days)
```

- [ ] **Step 6: Run tests to verify the helper and models pass**

Run: `cd "backend"; python -m unittest test_billing_service.py`
Expected: PASS for membership window tests

---

### Task 3: Implement Security, Email Verification, And Auth APIs

**Files:**
- Create: `backend/app/security.py`
- Create: `backend/app/services/email_service.py`
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/main.py`
- Test: `backend/test_auth_api.py`

- [ ] **Step 1: Write the failing auth API tests**

```python
def test_register_returns_success_message(self):
    response = self.client.post("/api/auth/register", json={
        "email": "user@example.com",
        "password": "password123"
    })
    self.assertEqual(response.status_code, 200)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "backend"; python -m unittest test_auth_api.py`
Expected: FAIL with `404` for `/api/auth/register`

- [ ] **Step 3: Implement password hashing and JWT helpers**

```python
def hash_password(password: str) -> str:
    return PasswordHasher().hash(password)

def create_access_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.utcnow() + timedelta(days=settings.JWT_EXPIRE_DAYS)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
```

- [ ] **Step 4: Implement local/smtp email sender and verification token generation**

```python
raw_token = secrets.token_urlsafe(32)
token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
verify_url = f"{settings.APP_BASE_URL}/api/auth/verify-email?token={raw_token}"
```

- [ ] **Step 5: Implement register, verify-email, login, logout, and me endpoints**

```python
response.set_cookie(
    key="vidgrab_access_token",
    value=token,
    httponly=True,
    samesite="lax",
    secure=not settings.DEBUG,
)
```

- [ ] **Step 6: Run auth API tests**

Run: `cd "backend"; python -m unittest test_auth_api.py`
Expected: PASS for register/login/verify/logout/me

---

### Task 4: Implement Membership Service And AI Access Guard

**Files:**
- Create: `backend/app/dependencies.py`
- Create: `backend/app/services/membership_service.py`
- Create: `backend/app/routers/membership.py`
- Modify: `backend/app/routers/ai.py`
- Modify: `backend/app/main.py`
- Modify: `backend/test_ai_api.py`
- Create: `backend/test_membership_api.py`

- [ ] **Step 1: Write the failing membership and AI permission tests**

```python
def test_ai_analyze_requires_active_membership(self):
    response = self.client.post("/api/ai/analyze", json={"url": "https://example.com/video"})
    self.assertEqual(response.status_code, 403)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "backend"; python -m unittest test_membership_api.py test_ai_api.py`
Expected: FAIL because AI route currently returns `200`/mock result without membership guard

- [ ] **Step 3: Implement current user and active membership dependencies**

```python
def require_active_member(...):
    if not membership or membership.status != "active" or membership.expires_at <= utcnow():
        raise HTTPException(status_code=403, detail="当前功能仅限会员使用，请先开通会员")
```

- [ ] **Step 4: Add membership status API**

```python
@router.get("/membership/me")
def get_membership_me(...):
    return {"is_member": True, "status": "active", "remaining_days": 29}
```

- [ ] **Step 5: Attach membership dependency to all `/api/ai/*` routes**

```python
@router.post("/analyze", dependencies=[Depends(require_active_member)])
```

- [ ] **Step 6: Run membership and AI guard tests**

Run: `cd "backend"; python -m unittest test_membership_api.py test_ai_api.py`
Expected: PASS for membership API and `403` guard behavior

---

### Task 5: Implement Mock Billing Provider And Membership Activation

**Files:**
- Create: `backend/app/services/billing_service.py`
- Create: `backend/app/routers/dev_mock_billing.py`
- Create: `backend/app/routers/billing.py`
- Create: `backend/test_billing_api.py`
- Create: `backend/test_billing_service.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write the failing mock billing tests**

```python
def test_create_checkout_session_in_mock_mode(self):
    response = self.client.post("/api/billing/checkout-session")
    self.assertEqual(response.status_code, 200)
    self.assertIn("checkout_url", response.json())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "backend"; python -m unittest test_billing_api.py test_billing_service.py`
Expected: FAIL with `404` for `/api/billing/checkout-session`

- [ ] **Step 3: Implement local order creation and idempotency handling**

```python
order = MembershipOrder(
    user_id=user.id,
    plan_code="vip_30d",
    amount_fen=1990,
    currency="cny",
    duration_days=30,
    status="pending",
    idempotency_key=str(uuid4()),
)
```

- [ ] **Step 4: Implement mock checkout response**

```python
checkout_url = f"{settings.FRONTEND_BASE_URL}/?mock_checkout_order_id={order.id}"
return {"order_id": order.id, "checkout_url": checkout_url}
```

- [ ] **Step 5: Implement mock success/failure endpoints for debug mode**

```python
@router.post("/dev/mock-billing/complete-order/{order_id}")
def complete_mock_order(order_id: str): ...
```

- [ ] **Step 6: Run billing tests**

Run: `cd "backend"; python -m unittest test_billing_api.py test_billing_service.py`
Expected: PASS for mock order creation and membership activation

---

### Task 6: Integrate Real Stripe Checkout And Verified Webhooks

**Files:**
- Modify: `backend/app/services/billing_service.py`
- Modify: `backend/app/routers/billing.py`
- Modify: `backend/app/config.py`
- Modify: `backend/requirements.txt`
- Modify: `backend/test_billing_api.py`

- [ ] **Step 1: Write the failing Stripe integration tests with mocks**

```python
@patch("app.services.billing_service.stripe.checkout.Session.create")
def test_stripe_checkout_session_includes_metadata(self, mock_create):
    ...
    self.assertEqual(kwargs["metadata"]["order_id"], expected_order_id)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "backend"; python -m unittest test_billing_api.py`
Expected: FAIL because Stripe call is not implemented

- [ ] **Step 3: Add Stripe SDK dependency and client wrapper**

```python
checkout_session = stripe.checkout.Session.create(
    mode="payment",
    line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
    success_url=f"{settings.FRONTEND_BASE_URL}/?billing=success&session_id={{CHECKOUT_SESSION_ID}}",
    cancel_url=f"{settings.FRONTEND_BASE_URL}/?billing=cancel",
    customer=customer_id,
    metadata={"order_id": order.id, "user_id": user.id, "plan_code": "vip_30d"},
    idempotency_key=order.idempotency_key,
)
```

- [ ] **Step 4: Implement webhook signature verification and event de-duplication**

```python
event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
```

- [ ] **Step 5: Handle `checkout.session.completed` and session expiry states**

```python
if event["type"] == "checkout.session.completed":
    billing_service.handle_checkout_completed(session)
```

- [ ] **Step 6: Run Stripe billing tests**

Run: `cd "backend"; python -m unittest test_billing_api.py test_billing_service.py`
Expected: PASS for Stripe request metadata, webhook verification, and duplicate event skipping

---

### Task 7: Build Frontend Auth, Membership State, And Billing UI

**Files:**
- Create: `frontend/src/composables/useAuth.ts`
- Create: `frontend/src/composables/useMembership.ts`
- Create: `frontend/src/components/AuthModal.vue`
- Create: `frontend/src/components/MembershipCard.vue`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/components/AIAssistant.vue`

- [ ] **Step 1: Write the failing TypeScript shape and build assumptions**

```ts
export interface CurrentUserResponse {
  authenticated: boolean
  user?: { id: string; email: string; email_verified: boolean }
}
```

- [ ] **Step 2: Run frontend build to verify it currently fails after type references are added**

Run: `cd "frontend"; npm run build`
Expected: FAIL until new composables/components are implemented

- [ ] **Step 3: Implement auth and membership composables**

```ts
const me = await apiClient.get<CurrentUserResponse>('/auth/me')
const membership = await apiClient.get<MembershipStatusResponse>('/membership/me')
```

- [ ] **Step 4: Add auth modal and membership card components**

```vue
<AuthModal :open="authModalOpen" @login-success="refreshAuth" />
<MembershipCard :membership="membership" @buy="startCheckout" />
```

- [ ] **Step 5: Update App and AI assistant to render auth/member states**

```vue
<template v-if="membership?.is_member">
  <!-- existing AI UI -->
</template>
<template v-else>
  <MembershipCard ... />
</template>
```

- [ ] **Step 6: Enable credentialed API calls and rebuild frontend**

Run: `cd "frontend"; npm run build`
Expected: PASS with new auth/member UI integrated

---

### Task 8: End-To-End Verification And Developer Documentation

**Files:**
- Modify: `backend/README.md`
- Modify: `frontend/README.md`
- Modify: `docs/superpowers/specs/2026-03-30-vidgrab-membership-billing-design.md`
- Test: `backend/test_auth_api.py`
- Test: `backend/test_membership_api.py`
- Test: `backend/test_billing_api.py`
- Test: `backend/test_billing_service.py`

- [ ] **Step 1: Document environment variables and local test flows**

```md
PAYMENT_PROVIDER_MODE=mock
MAIL_MODE=local
```

- [ ] **Step 2: Run backend verification suite**

Run: `cd "backend"; python -m unittest test_auth_api.py test_membership_api.py test_billing_api.py test_billing_service.py test_ai_api.py`
Expected: PASS

- [ ] **Step 3: Run frontend production build**

Run: `cd "frontend"; npm run build`
Expected: PASS

- [ ] **Step 4: Run manual mock payment checklist**

Run:
```text
1. 注册账号
2. 查看本地验证链接
3. 验证邮箱
4. 登录
5. 开通会员
6. 模拟支付成功
7. 验证 AI 解锁
```
Expected: 所有步骤成功

- [ ] **Step 5: Run optional Stripe live-like test checklist**

Run:
```bash
stripe listen --forward-to localhost:8000/api/billing/webhook --print-secret
```
Expected: webhook 成功转发，测试卡支付后会员到账

