# VPS Docker 部署说明

## 1. 首次准备

```bash
cp .env.production.example .env.production
mkdir -p backend/downloads backend/models
chmod +x ops/deploy.sh ops/cleanup-temp-files.sh
```

按实际域名与密钥编辑 `.env.production`。

## 2. 启动/更新

```bash
./ops/deploy.sh
```

## 3. 查看状态

```bash
docker compose ps
docker compose logs -f api
docker compose logs -f caddy
```

## 4. 定时清理临时文件

建议每天清理一次 24 小时前的下载与转写中间文件：

```bash
0 3 * * * cd /path/to/free-video-download && EXPIRE_HOURS=24 ./ops/cleanup-temp-files.sh >> /var/log/vidgrab-cleanup.log 2>&1
```

## 5. 反向代理与 HTTPS

当前 `docker-compose.yml` 内置 Caddy（自动申请与续期 HTTPS 证书）。
确保 `.env.production` 中配置：

```env
API_DOMAIN=api.your-domain.com
LETSENCRYPT_EMAIL=admin@your-domain.com
APP_BASE_URL=https://api.your-domain.com
FRONTEND_BASE_URL=https://www.your-domain.com
ALLOWED_ORIGINS=["https://www.your-domain.com"]
```

## 6. DNS 与 Vercel 绑定（推荐拓扑）

推荐域名拆分：
- `www.your-domain.com` -> Vercel 前端
- `api.your-domain.com` -> VPS 后端

DNS 记录建议：
- `A` 记录：`api` 指向 VPS 公网 IP
- `CNAME` 记录：`www` 指向 Vercel 提供的别名（例如 `cname.vercel-dns.com`）

根域名 `your-domain.com`：
- 可在 DNS 中做 `@ -> www` 跳转，或在 Vercel 内设置根域到 `www` 的重定向。

## 7. 当前线上环境维护清单

当前实际部署目录：

```bash
/root/free-video-download
```

当前推荐的标准更新流程：

```bash
cd /root/free-video-download
git fetch origin
git reset --hard origin/main
docker compose up -d --build api
docker compose ps
```

如需查看 API 日志：

```bash
cd /root/free-video-download
docker compose logs --tail=100 api
```

当前线上关键配置检查：

```bash
cd /root/free-video-download
grep -n 'MAIL_MODE\|APP_BASE_URL\|FRONTEND_BASE_URL' .env.production
```

当前线上已验证通过的关键链路：
- 注册接口 `/api/auth/register`
- 邮箱验证 `/api/auth/verify-email`
- 登录态接口 `/api/auth/me`
- 会员状态接口 `/api/membership/me`

注意事项：
- 生产环境配置以 `.env.production` 为准，不要把临时文件当成正式配置。
- 不要再直接手改服务器 Python 文件；先改 Git 仓库，再通过 `git fetch` + `git reset --hard origin/main` 收口部署。
- 如果线上再次出现“本地正常、服务器异常”，先执行 `git status --short` 检查服务器部署目录是否漂移。
