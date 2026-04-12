# VidGrab 本地解析助手

用于解决 B 站对云服务器 IP 风控（HTTP 412）场景。  
思路是把解析/下载请求切到你本机执行，复用你本地网络与浏览器 cookies。

## 启动方式

```bash
cd local-resolver
pip install -r requirements.txt
python server.py
```

默认监听：`http://127.0.0.1:61337`

## Docker 部署

```bash
cd local-resolver
docker compose up -d --build
```

该命令会同时启动：

- `vidgrab-local-resolver`
- `vidgrab-frpc`

默认映射端口：`61337:61337`

如需对公网暴露，建议配置 token：

```bash
RESOLVER_API_TOKEN=replace-with-a-long-random-string
```

然后通过环境变量注入到容器。

## 对接前端

前端默认读取：

- `VITE_LOCAL_RESOLVER_BASE_URL`（默认 `http://127.0.0.1:61337/api`）
- `VITE_LOCAL_RESOLVER_TOKEN`（可选，对应请求头 `X-Resolver-Token`）

当前推荐的生产入口：

```bash
VITE_LOCAL_RESOLVER_BASE_URL=https://api.vidgrab.sunandyu.top/local-resolver/api
```

不配置也能用默认值。

## 已提供接口

- `GET /api/health`
- `POST /api/info`
- `POST /api/download`
- `GET /api/download/status/{task_id}`
- `GET /api/download/file/{task_id}`

接口响应结构与线上后端保持兼容，前端可无缝复用原有下载 UI。

