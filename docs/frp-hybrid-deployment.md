# VidGrab FRP 混合部署方案

本文档用于把本地 `local-resolver` 解析节点通过现有 VPS 暴露给公网，同时保持：

- 前端：Vercel
- 业务后端：VPS Docker
- 数据库：Supabase
- 解析节点：本地电脑 Docker

## 一、目标拓扑

- `vidgrab.sunandyu.top` -> Vercel 前端
- `api.vidgrab.sunandyu.top` -> VPS 后端
- `api.vidgrab.sunandyu.top/local-resolver/*` -> VPS 反代到 `frps` 提供的 HTTP 入口，再转发到本地 `local-resolver`

前端解析策略已实现为：

- 所有平台优先走本地解析节点
- 本地失败时静默回退云端
- 两边都失败时再显示错误

## 二、VPS 侧

### 1. 部署 FRP 服务端

项目目录：

```bash
cd /root/free-video-download
```

使用新增的 FRP compose 文件：

```bash
docker compose -f docker-compose.yml -f ops/frp/docker-compose.frps.yml up -d frps
```

### 2. 修改 `frps` 配置

编辑：

```bash
ops/frp/frps.toml
```

至少替换：

- `auth.token`
- `webServer.user`
- `webServer.password`

推荐：

- `bindPort = 7000`
- `vhostHTTPPort = 18080`

### 3. 开放安全组/防火墙

放行：

- `7000/tcp`：本地 `frpc` 连 VPS `frps`

不要对公网直接开放：

- `18080`
- `17500`

这两个端口只应留在 VPS 本机回环或内网使用。

## 三、VPS 公网反代层

你当前线上公网由 `/opt/openclaw-proxy/Caddyfile` 接管。

需要新增一段：

```caddy
resolver.sunandyu.top {
    encode zstd gzip
    reverse_proxy 127.0.0.1:18080
}
```

保存后重载 Caddy：

```bash
docker restart openclaw-caddy
```

## 四、本地电脑

### 1. 保持本地解析节点运行

```bash
cd local-resolver
docker compose up -d --build
```

### 2. 准备 FRP 客户端配置

复制模板：

```bash
cp frpc.toml.example frpc.toml
```

修改：

- `serverAddr = "120.55.48.68"`
- `auth.token` 与 VPS `frps.toml` 保持一致
- `customDomains = ["resolver.sunandyu.top"]`

### 3. 启动 FRP 客户端容器

```bash
docker compose up -d
```

## 五、验证

### 1. VPS 本机验证

在 VPS 上执行：

```bash
curl http://127.0.0.1:18080/api/health
```

返回：

```json
{"status":"ok"}
```

说明 FRP 链路已打通。

### 2. 公网验证

```bash
curl https://api.vidgrab.sunandyu.top/local-resolver/api/health
```

若启用了 `RESOLVER_API_TOKEN`，请携带请求头：

```bash
curl https://api.vidgrab.sunandyu.top/local-resolver/api/health -H "X-Resolver-Token: your-token"
```

## 六、前端接入

在 Vercel 配置：

```env
VITE_LOCAL_RESOLVER_BASE_URL=https://api.vidgrab.sunandyu.top/local-resolver/api
VITE_LOCAL_RESOLVER_TOKEN=replace-with-resolver-token
```

修改后重新部署前端。

## 七、运行约束

你的本地电脑每天晚上关机，因此：

- 白天开机时，本地解析可用
- 夜间关机后，本地解析不可用
- 前端会静默回退云端
- 高风控平台夜间仍可能失败，这是预期行为
