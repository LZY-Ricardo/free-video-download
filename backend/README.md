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
