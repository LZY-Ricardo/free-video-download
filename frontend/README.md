# VidGrab Frontend

前端基于 Vue 3 + TypeScript + Vite，当前包含：

- 视频解析与下载 UI
- AI 学习助手
- 邮箱注册 / 登录弹窗
- 会员状态展示
- Stripe / mock 支付入口

## 开发命令

```bash
npm install
npm run dev
```

默认通过 Vite 代理把 `/api` 请求转发到 `http://localhost:8000`。

## 生产构建

```bash
npm run build
```

## 会员购买开发说明

### 1. 后端使用 mock 模式时

当前端收到形如：

```text
?mock_checkout_order_id=xxxx
```

的查询参数时，页面顶部会出现本地 mock 支付提示条。点击：

- `模拟支付成功`
- `取消模拟支付`

即可完成无外网联调。

### 2. 后端使用 Stripe 模式时

点击“开通 VIP”会跳转到 Stripe Checkout 页面。支付成功后，前端会根据：

```text
?billing=success&session_id=...
```

自动刷新会员状态。

## 相关页面行为

- 未登录时：顶部显示 `登录 / 注册 / 开通 VIP`
- 已登录未开通会员时：AI 学习助手显示会员引导卡片
- 会员有效时：AI 学习助手恢复正常功能，并在顶部显示会员剩余天数
