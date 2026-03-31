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
