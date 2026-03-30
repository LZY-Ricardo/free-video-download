# VidGrab 会员购买功能设计方案

## 1. 背景

当前项目已经完成：

- 免费视频解析与下载
- AI 视频分析、字幕下载、思维导图、流式问答

本次新增的能力是：

- 邮箱注册账号
- 邮箱验证
- JWT 登录态
- 用户购买会员
- 会员到期与手动续费
- 仅对 AI 学习助手做会员权限控制

本次设计必须遵守以下已确认决策：

- 账号体系：邮箱注册，简单 Token/JWT 认证
- 邮件策略：开发环境本地模式，生产环境真实发信
- 支付方式：Stripe Checkout Session
- 支付模型：一次性购买 30 天会员，不自动续费，到期手动续费
- 商品价格：19.9 CNY / 30 天
- 权益模型：下载继续免费，AI 学习助手收费

## 2. 目标与非目标

### 2.1 目标

1. 在现有 Vue + FastAPI 项目中补齐最小账号体系。
2. 使用 Stripe Checkout 实现一次性会员购买。
3. 使用 webhook 作为唯一的支付到账依据。
4. 通过持久化存储实现订单幂等、事件去重和会员状态恢复。
5. 在没有外网时仍可通过 mock 模式完成开发和验证。

### 2.2 非目标

1. 本次不实现自动续费订阅。
2. 本次不实现忘记密码、修改邮箱、后台管理页面。
3. 本次不实现下载次数限制或下载质量限制。
4. 本次不引入第三方 Auth 平台。

## 3. 当前系统现状

### 3.1 前端

- 技术栈：Vue 3 + Vite + Tailwind CSS
- 主页面入口：`frontend/src/App.vue`
- 下载主流程：`frontend/src/components/DownloadForm.vue`
- AI 学习助手：`frontend/src/components/AIAssistant.vue`
- API 客户端：`frontend/src/api/client.ts`

### 3.2 后端

- 技术栈：FastAPI
- 已有接口分组：`info`、`download`、`direct`、`image`、`ai`
- 当前状态存储：下载任务与 AI 分析结果主要依赖内存
- 当前无用户、无数据库、无鉴权、无支付

### 3.3 关键约束

1. 支付与会员状态不能继续依赖内存，否则会导致服务重启丢单。
2. AI 功能已经有完整业务闭环，新增会员功能应尽量只在路由层补权限网关。
3. 下载功能继续免费，不应被认证和支付逻辑阻塞。

## 4. 总体架构

### 4.1 模块拆分

新增以下模块：

1. `Auth` 模块：注册、邮箱验证、登录、登出、当前用户。
2. `Mail` 模块：开发环境本地发信、生产环境 SMTP 发信。
3. `Membership` 模块：会员状态查询、到期判断、续费顺延。
4. `Billing` 模块：本地订单创建、Stripe Checkout Session 创建。
5. `Webhook` 模块：Stripe 事件验签、事件去重、订单入账、会员到账。
6. `AI 权限网关`：统一拦截 `/api/ai/*`。

### 4.2 技术选型

- 持久化：SQLite
- ORM：SQLAlchemy
- 密码哈希：Argon2id
- JWT：服务端签发，保存在 HttpOnly Cookie
- 支付：Stripe Checkout Session
- 支付测试：
  - 在线：Stripe test mode + Stripe CLI
  - 离线：mock provider

### 4.3 总体数据流

#### 注册登录链路

1. 用户注册邮箱和密码。
2. 后端创建未验证用户，并生成一次性验证 token。
3. 邮件模块发送验证链接。
4. 用户点击链接完成邮箱验证。
5. 用户登录，后端签发 JWT Cookie。
6. 前端通过 `/api/auth/me` 恢复登录态。

#### 购买会员链路

1. 用户登录并验证邮箱。
2. 前端请求创建结账会话。
3. 后端先创建本地订单，再调用 Stripe 创建 Checkout Session。
4. Stripe 托管支付页完成支付。
5. Stripe 向 webhook 发送 `checkout.session.completed`。
6. 后端验签、去重、更新本地订单并开通会员。
7. 用户回站后查询会员状态，AI 功能解锁。

#### 会员续费链路

1. 用户再次购买 30 天会员。
2. 如果当前会员仍有效，则从现有 `expires_at` 顺延 30 天。
3. 如果当前会员已过期，则从当前时间起新增 30 天。

## 5. 数据模型

### 5.1 `users`

字段建议：

- `id`
- `email`，唯一，统一转小写
- `password_hash`
- `email_verified_at`
- `status`
- `stripe_customer_id`
- `created_at`
- `updated_at`
- `last_login_at`

### 5.2 `email_verification_tokens`

字段建议：

- `id`
- `user_id`
- `token_hash`
- `expires_at`
- `used_at`
- `created_at`

规则：

- 只保存 token 哈希，不保存原始 token。
- token 仅允许使用一次。
- 建议 24 小时过期。

### 5.3 `membership_orders`

字段建议：

- `id`
- `user_id`
- `order_type`
- `plan_code`
- `amount_fen`
- `currency`
- `duration_days`
- `status`
- `stripe_checkout_session_id`
- `stripe_payment_intent_id`
- `stripe_customer_id`
- `idempotency_key`
- `paid_at`
- `created_at`
- `updated_at`

规则：

- `plan_code` 固定为 `vip_30d`
- `amount_fen` 固定为 `1990`
- `currency` 固定为 `cny`
- 每次购买都创建新订单
- `idempotency_key` 唯一

### 5.4 `user_memberships`

字段建议：

- `id`
- `user_id`
- `plan_code`
- `started_at`
- `expires_at`
- `status`
- `source_order_id`
- `created_at`
- `updated_at`

规则：

- 一个用户只保留一条当前快照记录
- 权限判断使用 `status == active` 且 `expires_at > now`

### 5.5 `stripe_webhook_events`

字段建议：

- `id`
- `stripe_event_id`，唯一
- `event_type`
- `livemode`
- `payload_json`
- `processing_status`
- `processed_at`
- `error_message`
- `created_at`

规则：

- 先记事件，再处理业务
- 同一事件只允许成功处理一次

## 6. 认证与安全设计

### 6.1 密码安全

- 使用 Argon2id 存储密码哈希
- 统一错误提示为“邮箱或密码错误”
- 不在数据库中保存明文密码

### 6.2 JWT 设计

- 使用 JWT 作为服务端认证令牌
- 令牌通过 HttpOnly Cookie 下发
- Cookie 设置：
  - `HttpOnly=true`
  - `SameSite=Lax`
  - 生产环境 `Secure=true`
- JWT 有效期建议为 7 天

### 6.3 邮箱验证规则

- 未验证邮箱不能登录
- 未验证邮箱不能发起支付
- 验证链接使用一次性 token

### 6.4 支付安全

- 前端不能传价格、币种、会员天数
- 所有商品参数由后端固定配置
- 创建 Checkout Session 必须带本地订单 ID
- 会员到账只认 webhook，不认 success 页面

### 6.5 幂等与去重

#### 创建支付单

- 每个本地订单生成唯一 `idempotency_key`
- Stripe 请求复用该 key，避免重复创建 Session

#### 处理 webhook

- 使用 `stripe_event_id` 去重
- 同一个事件重复推送时直接跳过

## 7. 接口设计

### 7.1 认证接口

- `POST /api/auth/register`
- `GET /api/auth/verify-email`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### 7.2 支付接口

- `POST /api/billing/checkout-session`
- `POST /api/billing/webhook`

### 7.3 会员接口

- `GET /api/membership/me`

### 7.4 AI 接口改造

统一在 `/api/ai/*` 增加：

- 登录校验
- 会员状态校验

不改造：

- `/api/info`
- `/api/download*`
- `/api/direct-url`

## 8. 前端改造设计

### 8.1 新增能力

新增前端状态模块：

- `useAuth.ts`
- `useMembership.ts`

新增组件：

- `AuthModal.vue`
- `MembershipCard.vue`

### 8.2 页面改造点

#### `App.vue`

- 顶部导航增加登录、注册、会员状态入口
- “开通 VIP”按钮改为状态化展示

#### `AIAssistant.vue`

- 会员用户：正常显示 AI 功能
- 非会员用户：显示功能介绍和购买引导

#### `api/client.ts`

- 增加 `withCredentials`

### 8.3 前端状态流

1. 页面加载调用 `/api/auth/me`
2. 已登录后调用 `/api/membership/me`
3. 根据会员状态决定 AI 区域是功能态还是引导态

## 9. Stripe 与离线开发设计

### 9.1 在线模式

环境变量：

- `PAYMENT_PROVIDER_MODE=stripe`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID`

本地测试使用：

```bash
stripe login
stripe listen --forward-to localhost:8000/api/billing/webhook --print-secret
```

参考文档：

- https://docs.stripe.com/api/checkout/sessions
- https://docs.stripe.com/stripe-cli/use-cli
- https://docs.stripe.com/testing?testing-method=payment-methods

### 9.2 离线 mock 模式

环境变量：

- `PAYMENT_PROVIDER_MODE=mock`

规则：

- 不调用 Stripe API
- 仍创建本地订单
- 返回本地模拟结账地址
- 通过本地模拟成功/失败流程驱动会员开通

### 9.3 邮件模式

- `MAIL_MODE=local`
  - 通过日志或开发接口返回验证链接
- `MAIL_MODE=smtp`
  - 通过真实邮件服务发送验证邮件

## 10. 验证与测试策略

### 10.1 后端测试

至少覆盖：

1. 注册、重复注册、未验证用户登录失败
2. 邮箱验证成功、过期、重复使用
3. JWT 登录与当前用户接口
4. 会员状态查询
5. 非会员访问 AI 接口返回 403
6. mock 支付成功后会员到账
7. Stripe webhook 成功到账
8. 同一 webhook 重放不会重复开会员
9. 已有会员续费会顺延 30 天

### 10.2 前端验证

至少覆盖：

1. 登录/注册弹窗交互
2. 顶部登录态展示
3. 非会员看到 AI 购买引导
4. 会员状态展示与续费入口
5. 支付成功回站后会员状态刷新

### 10.3 构建验证

- 后端：新增测试文件执行通过
- 前端：`npm run build` 通过

## 11. 风险与约束

1. 当前项目原本无数据库，本次会新增持久化基础设施。
2. 如果未来切换到生产数据库，需要补迁移机制；本次先使用 `create_all` 控制复杂度。
3. 离线 mock 模式只能验证本地业务逻辑，不能替代 Stripe 真实链路测试。
4. 本次暂不实现退款后台和客服手工补单页面。

## 12. 上线前检查清单

1. Stripe test mode 全链路支付成功
2. Stripe webhook 验签通过
3. 同一 webhook 重试不重复开会员
4. 会员到期后 AI 权限正确回收
5. 本地 mock 模式可稳定运行
6. 用户协议与隐私政策页补齐

## 13. 实施结论

本方案通过“最小账号体系 + SQLite 持久化 + Stripe Checkout + webhook 最终一致性 + mock 离线支付”的组合，在不破坏现有下载链路的前提下，为项目补齐了稳定、可测试、可上线的会员付费能力。
