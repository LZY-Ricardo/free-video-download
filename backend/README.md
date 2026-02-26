# 后端服务

万能视频下载器后端服务

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
# 开发模式
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心 API

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
