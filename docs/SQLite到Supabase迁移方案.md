# SQLite 到 Supabase(PostgreSQL) 迁移方案（free-video-download）

## 1. 目标与范围

### 1.1 目标
- 将后端持久化层从 `SQLite` 迁移到 `Supabase PostgreSQL`，满足生产环境并发、备份与可维护性要求。
- 保持现有业务行为不变（注册/登录、邮箱验证、会员开通、Webhook 幂等、AI 免费次数限制）。
- 提供可回滚的分阶段迁移流程，降低上线风险。

### 1.2 当前范围（基于代码与实库盘点）
- ORM：`SQLAlchemy 2.x`（同步会话）
- 建表方式：`FastAPI startup -> Base.metadata.create_all(bind=engine)`
- 当前数据库：`backend/app.db`
- 涉及表（6 张）：
1. `users`
2. `email_verification_tokens`
3. `membership_orders`
4. `user_memberships`
5. `daily_ai_usage`
6. `stripe_webhook_events`

### 1.3 非目标
- 本次不改业务流程，不引入 Supabase Auth，不重构为异步 ORM。
- 本次不把视频文件存储迁入数据库（仍应保留文件系统/对象存储方案）。

## 2. 现状数据库设计评估

## 2.1 现有表与关键约束
- `users.email` 唯一索引。
- `email_verification_tokens.token_hash` 唯一索引。
- `membership_orders.idempotency_key` 唯一索引。
- `user_memberships.user_id` 唯一索引（每用户最多一条会员记录）。
- `stripe_webhook_events.stripe_event_id` 唯一索引（Webhook 幂等核心）。

## 2.2 关键查询/写入路径（迁移后必须等价）
- 认证：按 `users.email` 查询、更新 `last_login_at`。
- 邮箱验证：按 `email_verification_tokens.token_hash` 查询并更新 `used_at`。
- 支付：按 `membership_orders.status` + `user_id` 查待支付订单；按 `idempotency_key` 幂等创建。
- Webhook：按 `stripe_event_id` 查重，避免重复处理。
- AI 免费次数：按 `daily_ai_usage(user_id, usage_date)` 查询并自增 `used_count`。

## 2.3 已识别设计改进点（建议在迁移时一起修复）
1. `daily_ai_usage` 缺少 `(user_id, usage_date)` 唯一约束，理论上可能出现并发重复行。
2. 大部分时间字段当前是 `DateTime`（无时区），迁移后建议统一 `timestamptz`。
3. 当前依赖 `create_all`，生产环境建议引入迁移工具（Alembic 或 Supabase SQL migration）。

## 3. 目标架构（Supabase）

## 3.1 连接策略
- 应用继续使用 SQLAlchemy。
- `DATABASE_URL` 指向 Supabase Postgres 连接串。
- 生产建议使用 Supabase 连接池（transaction pooler）URL，降低连接开销。

## 3.2 类型与约束映射原则
- `String(36)` UUID 文本：
  - 方案 A（最小改动，推荐）：继续用 `text/varchar` 存 UUID 字符串。
  - 方案 B（长期优化）：转为原生 `uuid`，需要同步 ORM 类型与数据转换。
- `DateTime` -> `timestamptz`。
- `Integer`、`Text`、`String(N)` 原样映射为 Postgres 等价类型。
- 保留现有唯一索引、外键与查询索引。

## 3.3 建议新增索引/约束（向后兼容）
1. `daily_ai_usage`：`unique (user_id, usage_date)`。
2. `membership_orders`：可补 `index (user_id, status, created_at desc)`（优化 open order 查询）。

## 4. 迁移策略（推荐：停写窗口 + 一次性切换）

当前数据量较小（实库行数较少），推荐采用低复杂度方案：
1. 在 Supabase 先建完整 schema。
2. 对 SQLite 执行一次性导出与导入。
3. 切换应用 `DATABASE_URL` 到 Supabase。
4. 运行冒烟测试。
5. 保留 SQLite 备份以便快速回滚。

该方案符合 KISS/YAGNI，避免过早引入双写或 CDC。

## 5. 执行步骤（Runbook）

## 5.1 上线前准备
1. 冻结后端写流量（发布窗口内短暂停写）。
2. 备份 SQLite：
```bash
cp backend/app.db backend/app.db.bak.$(date +%Y%m%d%H%M%S)
```
3. 创建 Supabase 项目并拿到连接信息（host、port、db、user、password、pooler）。

## 5.2 在 Supabase 建表（首版 DDL）
以下 DDL 可作为基线（按当前模型等价设计，含推荐增强）：

```sql
create table if not exists users (
  id varchar(36) primary key,
  email varchar(320) not null unique,
  password_hash text not null,
  email_verified_at timestamptz null,
  status varchar(32) not null default 'pending_verification',
  stripe_customer_id varchar(128) null,
  created_at timestamptz not null,
  updated_at timestamptz not null,
  last_login_at timestamptz null
);
create index if not exists ix_users_stripe_customer_id on users (stripe_customer_id);

create table if not exists email_verification_tokens (
  id varchar(36) primary key,
  user_id varchar(36) not null references users(id),
  token_hash varchar(128) not null unique,
  expires_at timestamptz not null,
  used_at timestamptz null,
  created_at timestamptz not null
);
create index if not exists ix_email_verification_tokens_user_id on email_verification_tokens (user_id);

create table if not exists membership_orders (
  id varchar(36) primary key,
  user_id varchar(36) not null references users(id),
  order_type varchar(32) not null default 'checkout_session',
  plan_code varchar(64) not null default 'vip_30d',
  amount_fen integer not null default 1990,
  currency varchar(8) not null default 'cny',
  duration_days integer not null default 30,
  status varchar(32) not null default 'pending',
  stripe_checkout_session_id varchar(128) null,
  stripe_payment_intent_id varchar(128) null,
  stripe_customer_id varchar(128) null,
  idempotency_key varchar(128) not null unique,
  paid_at timestamptz null,
  created_at timestamptz not null,
  updated_at timestamptz not null
);
create index if not exists ix_membership_orders_user_id on membership_orders (user_id);
create index if not exists ix_membership_orders_status on membership_orders (status);
create index if not exists ix_membership_orders_stripe_checkout_session_id on membership_orders (stripe_checkout_session_id);
create index if not exists ix_membership_orders_stripe_payment_intent_id on membership_orders (stripe_payment_intent_id);
create index if not exists ix_membership_orders_stripe_customer_id on membership_orders (stripe_customer_id);
create index if not exists ix_membership_orders_user_status_created_at on membership_orders (user_id, status, created_at desc);

create table if not exists user_memberships (
  id varchar(36) primary key,
  user_id varchar(36) not null unique references users(id),
  plan_code varchar(64) not null default 'vip_30d',
  started_at timestamptz not null,
  expires_at timestamptz not null,
  status varchar(32) not null default 'active',
  source_order_id varchar(36) null references membership_orders(id),
  created_at timestamptz not null,
  updated_at timestamptz not null
);
create index if not exists ix_user_memberships_expires_at on user_memberships (expires_at);
create index if not exists ix_user_memberships_source_order_id on user_memberships (source_order_id);

create table if not exists daily_ai_usage (
  id varchar(36) primary key,
  user_id varchar(36) not null references users(id),
  usage_date varchar(10) not null,
  used_count integer not null default 0,
  created_at timestamptz not null,
  updated_at timestamptz not null,
  unique (user_id, usage_date)
);
create index if not exists ix_daily_ai_usage_usage_date on daily_ai_usage (usage_date);

create table if not exists stripe_webhook_events (
  id varchar(36) primary key,
  stripe_event_id varchar(128) not null unique,
  event_type varchar(128) not null,
  livemode integer not null default 0,
  payload_json text not null,
  processing_status varchar(32) not null default 'received',
  processed_at timestamptz null,
  error_message text null,
  created_at timestamptz not null
);
create index if not exists ix_stripe_webhook_events_event_type on stripe_webhook_events (event_type);
```

## 5.3 数据迁移（建议脚本化）
建议实现 `backend/scripts/migrate_sqlite_to_postgres.py`：
1. 从 SQLite 分批读取。
2. 按依赖顺序写入 Postgres：
   - `users`
   - `email_verification_tokens`
   - `membership_orders`
   - `user_memberships`
   - `daily_ai_usage`
   - `stripe_webhook_events`
3. 每张表导入后校验 `count(*)` 一致。
4. 记录失败行到日志，保证可重试。

注意：如果 `daily_ai_usage` 存在重复 `(user_id, usage_date)`，导入前先聚合修复。

## 5.4 应用配置切换
1. 安装 Postgres 驱动（推荐 `psycopg[binary]`）。
2. 更新 `DATABASE_URL`：
```env
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<db>
```
3. 在 `database.py` 保持 SQLite 分支仅用于本地；Postgres 分支不需要 `check_same_thread`。
4. 发布后端并执行 API 冒烟：
   - `/api/auth/register`
   - `/api/auth/login`
   - `/api/membership/me`
   - `/api/billing/checkout-session`
   - `/api/billing/webhook`（测试事件）

## 5.5 上线后验证清单
1. 行数校验：SQLite 与 Postgres 各表 `count(*)` 一致。
2. 唯一性校验：
   - `users.email`
   - `membership_orders.idempotency_key`
   - `stripe_webhook_events.stripe_event_id`
3. 业务校验：
   - 已有用户可登录。
   - 已有会员状态正确。
   - Webhook 重放不重复入账。
   - 免费 AI 次数限制仍正确。

## 6. 回滚方案

若切换后出现阻断问题：
1. 立即将 `DATABASE_URL` 回切到 SQLite。
2. 回滚后端版本到切流前构建。
3. 通过 `app.db.bak.<timestamp>` 恢复数据（如需）。
4. 故障复盘后再执行二次迁移。

回滚前提：切流窗口内禁止对旧库进行破坏性操作，且完整备份已落地。

## 7. 代码层后续治理建议（迁移后）

1. 引入 Alembic，替换 `startup create_all` 机制（生产可追溯）。
2. 为 `daily_ai_usage` 的更新增加并发安全写法（`INSERT ... ON CONFLICT ... DO UPDATE`）。
3. 补充一组“数据库兼容性集成测试”（SQLite + Postgres 两套 CI）。

## 8. 里程碑拆分建议

1. M1（0.5 天）：完成 Supabase schema 落地与迁移脚本。
2. M2（0.5 天）：预发布演练（全量迁移 + 冒烟 + 性能观察）。
3. M3（0.5 天）：生产切换与回归。
4. M4（0.5 天）：引入 Alembic 与并发写优化。

---

## 附录 A：本次盘点结果（2026-03-31）

- SQLite 实库文件：`backend/app.db`
- 当前数据规模（行数）：
  - `users`: 6
  - `email_verification_tokens`: 5
  - `membership_orders`: 3
  - `user_memberships`: 2
  - `daily_ai_usage`: 1
  - `stripe_webhook_events`: 5
- 已检查：`users.email`、`membership_orders.idempotency_key`、`daily_ai_usage(user_id, usage_date)` 暂无重复数据。
