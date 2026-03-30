# 后端服务

万能视频下载器后端服务

## 安装依赖

```bash
pip install -r requirements.txt
```

## 会员与支付功能环境变量

后端新增了账号、会员和支付能力。最常用的环境变量如下：

```env
DATABASE_URL=sqlite:///./app.db
JWT_SECRET=vidgrab-dev-secret-change-me-to-a-32-byte-key
JWT_EXPIRE_DAYS=7
ACCESS_TOKEN_COOKIE_NAME=vidgrab_access_token

MAIL_MODE=local
APP_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:5173

PAYMENT_PROVIDER_MODE=mock

STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_ID=
```

说明：

- `MAIL_MODE=local` 时，注册接口会在响应中返回 `debug_verify_url`，便于开发环境直接验证邮箱。
- `PAYMENT_PROVIDER_MODE=mock` 时，不会访问外网 Stripe，而是走本地模拟支付。
- `PAYMENT_PROVIDER_MODE=stripe` 时，需要配置 Stripe 测试环境密钥和 `price_id`。

## 运行服务

```bash
# 开发模式
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

首次启动时会自动创建 SQLite 表结构。

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心 API

### 0. 账号与会员

```bash
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
GET  /api/auth/verify-email?token=...
GET  /api/membership/me
```

注意：

- 登录态通过 HttpOnly Cookie 保存。
- `/api/ai/*` 现在要求“已登录 + 会员有效”。

### 1. 获取视频信息
```bash
POST /api/info
{
  "url": "https://www.youtube.com/watch?v=xxx"
}
```

### 2. 开始下载
```bash
POST /api/download
{
  "url": "https://...",
  "format": "best",
  "quality": "1080p"
}
```

### 3. 获取下载状态
```bash
GET /api/download/status/{task_id}
```

### 4. 下载文件
```bash
GET /api/download/file/{task_id}
```

### 5. 获取直链
```bash
POST /api/direct-url
{
  "url": "https://..."
}
```

### 6. AI 分析视频
```bash
POST /api/ai/analyze
{
  "url": "https://..."
}
```

### 6.1 异步启动 AI 分析（推荐）
```bash
POST /api/ai/analyze/start
{
  "url": "https://..."
}
```

### 6.2 查询 AI 分析状态
```bash
GET /api/ai/analyze/status/{task_id}
```

### 7. 基于视频问答
```bash
POST /api/ai/chat
{
  "analysis_id": "uuid",
  "question": "这个视频的核心知识点是什么？"
}
```

### 7.1 基于视频问答（流式，推荐）
```bash
POST /api/ai/chat/stream
{
  "analysis_id": "uuid",
  "question": "这个视频的核心知识点是什么？"
}
```

响应为 `text/event-stream`，事件类型：
- `start`：首包，携带引用片段
- `delta`：增量文本分片
- `done`：结束事件
- `error`：错误事件

## 会员支付开发说明

### 1. 本地 mock 支付模式

适合无外网开发和自动化测试。

配置：

```env
MAIL_MODE=local
PAYMENT_PROVIDER_MODE=mock
```

流程：

1. 调用 `/api/auth/register`
2. 从返回的 `debug_verify_url` 打开邮箱验证链接
3. 调用 `/api/auth/login`
4. 调用 `/api/billing/checkout-session`
5. 使用返回的 `checkout_url` 进入前端 mock 支付页面
6. 前端会调用 `/api/dev/mock-billing/complete-order/{order_id}` 完成模拟支付
7. 之后 `/api/membership/me` 会返回有效会员状态

### 2. Stripe 在线测试模式

配置：

```env
PAYMENT_PROVIDER_MODE=stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PRICE_ID=price_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

启动 webhook 转发：

```bash
stripe login
stripe listen --forward-to localhost:8000/api/billing/webhook --print-secret
```

前端点击“开通 VIP”后会跳转到 Stripe Checkout。测试支付时可使用 Stripe 官方测试卡：

- `4242 4242 4242 4242`

参考：

- https://docs.stripe.com/testing?testing-method=payment-methods
- https://docs.stripe.com/stripe-cli/use-cli

## AI 配置（可选）

未配置 AI Key 时，会使用本地规则回退（仍可返回摘要、思维导图和问答）。

```env
AI_API_KEY=your_key
AI_MODEL=gpt-4o-mini
AI_API_BASE_URL=https://api.openai.com/v1
```

## 无字幕视频的本地转写（ASR）

当平台没有提供 CC 字幕时，系统会尝试从本地已下载视频做离线转写：

1. 使用 `ffmpeg` 的 `whisper` 滤镜  
2. 自动下载 `ggml-base.bin` 到 `backend/models/`（首次）  
3. 生成带时间戳转录并继续摘要/问答流程

注意：
- 该流程依赖本机安装可用的 `ffmpeg`（本项目环境已验证支持 `--enable-whisper`）。
- 首次转写会下载模型，耗时会明显增加。

## 测试命令

```bash
python -m unittest test_auth_api.py test_membership_api.py test_billing_api.py test_billing_service.py test_ai_api.py test_progress_parsing.py test_router.py test_server.py
```
