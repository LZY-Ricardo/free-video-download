# 万能视频下载器 AI 学习助手（P0）实施方案与实现说明

更新时间：2026-03-10  
适用版本：当前 `main` 工作区（下载功能已完成，新增 AI 学习能力）

## 1. 背景与目标

在现有“视频下载”核心能力基础上，新增学习效率场景所需的 4 个 P0 核心功能：

1. 视频总结摘要  
2. 字幕/转录文本展示（带时间戳）  
3. 思维导图可视化  
4. 基于视频内容的 AI 问答

目标是形成“下载 + 学习理解”闭环，并保持对现有下载流程的最小侵入。

## 2. 范围与原则

### 2.1 本次范围（已落地）

1. 后端新增 AI 分析 API 与服务  
2. 前端新增 AI 学习助手区域  
3. 新增基础自动化测试  
4. 保持原有下载链路与接口不变

### 2.2 设计原则

1. 兼容性优先：不破坏现有 `info/download/direct/image` 逻辑  
2. 轻量优先：不引入数据库，分析结果内存缓存  
3. 可运行优先：未提供 API Key 时自动走本地规则回退  
4. 可演进优先：保留 OpenAI-compatible 接口配置，后续可无缝切换供应商

## 3. 总体方案

### 3.1 流程总览

1. 用户输入视频 URL，触发 `/api/ai/analyze`  
2. 后端使用 `yt-dlp` 解析视频信息与字幕轨道  
3. 下载字幕并解析为“带时间戳片段”  
4. 生成结构化摘要（总览、要点、章节）  
5. 基于摘要构建思维导图树  
6. 返回 `analysis_id`、摘要、转录、思维导图  
7. 用户提问时调用 `/api/ai/chat`，根据 `analysis_id` 在缓存中检索上下文并回答

### 3.2 AI 策略（双模式）

1. 有 `AI_API_KEY`：调用 OpenAI-compatible `/chat/completions`  
2. 无 `AI_API_KEY`：使用本地规则摘要 + 关键词检索问答回退

说明：当前默认配置下 `AI_API_KEY=""`，因此运行时使用本地回退逻辑。

## 4. 后端实现设计

### 4.1 新增配置项

文件：`backend/app/config.py`

新增：

1. `AI_PROVIDER`  
2. `AI_MODEL`  
3. `AI_API_BASE_URL`  
4. `AI_API_KEY`  
5. `AI_TIMEOUT_SECONDS`  
6. `AI_MAX_TRANSCRIPT_SEGMENTS`

并增加 `DEBUG` 字段的字符串归一化处理（兼容 `release/prod` 等值）。

### 4.2 新增数据模型

文件：`backend/app/models.py`

新增模型：

1. `AnalyzeRequest`  
2. `TranscriptSegment`  
3. `SummarySection`  
4. `VideoSummary`  
5. `MindMapNode`（递归）  
6. `VideoAnalysisResponse`  
7. `ChatRequest`  
8. `ChatCitation`  
9. `ChatResponse`

### 4.3 新增服务：VideoAIService

文件：`backend/app/services/video_ai_service.py`

核心职责：

1. 视频信息与字幕轨道提取  
2. 字幕下载和 VTT/SRT 类文本解析  
3. 转录清洗、去重和片段数限制  
4. 摘要生成（LLM/回退）  
5. 思维导图树构建  
6. 问答检索与回答（LLM/回退）  
7. 分析结果内存缓存（`analysis_id -> AnalysisRecord`）

关键方法：

1. `analyze_video(url)`：完整分析主流程  
2. `ask_question(analysis_id, question)`：视频问答主流程  
3. `_generate_summary_with_ai(...)`：有 key 时结构化摘要  
4. `_generate_summary_fallback(...)`：回退摘要  
5. `_answer_with_ai_or_fallback(...)`：回退问答  
6. `_retrieve_relevant_segments(...)`：问答证据检索

### 4.4 新增 AI 路由

文件：`backend/app/routers/ai.py`

接口：

1. `POST /api/ai/analyze`：返回摘要、转录、思维导图与 `analysis_id`  
2. `POST /api/ai/chat`：基于 `analysis_id` + 问题返回回答与引用片段

并在 `backend/app/main.py` 注册 `ai.router`。

### 4.5 示例接口

#### 分析视频

```http
POST /api/ai/analyze
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=xxxx"
}
```

返回（示意）：

```json
{
  "analysis_id": "uuid",
  "video_title": "标题",
  "transcript_language": "zh",
  "summary": {
    "overview": "......",
    "key_points": ["......"],
    "sections": [
      { "title": "章节A", "start": "00:01:20", "summary": "......" }
    ]
  },
  "transcript": [
    { "start": 80.0, "end": 86.2, "timestamp": "00:01:20", "text": "......" }
  ],
  "mind_map": {
    "id": "root",
    "label": "标题",
    "children": []
  }
}
```

#### 视频问答

```http
POST /api/ai/chat
Content-Type: application/json

{
  "analysis_id": "uuid",
  "question": "这个视频最重要的三个观点是什么？"
}
```

返回（示意）：

```json
{
  "answer": "......",
  "citations": [
    { "timestamp": "00:03:10", "text": "......" }
  ]
}
```

## 5. 前端实现设计

### 5.1 新增类型

文件：`frontend/src/types/index.ts`

新增：

1. `TranscriptSegment`  
2. `SummarySection`  
3. `VideoSummary`  
4. `MindMapNode`  
5. `VideoAnalysisResponse`  
6. `VideoChatRequest`  
7. `VideoChatResponse`

并扩展已有 `VideoInfo/Format` 字段以兼容当前后端返回结构。

### 5.2 新增状态管理

文件：`frontend/src/composables/useVideoAI.ts`

能力：

1. `analyzeVideo(url)` 调用 `/ai/analyze`  
2. `askQuestion()` 调用 `/ai/chat`  
3. 管理分析状态、错误状态、问答历史  
4. 支持重置 AI 状态

### 5.3 新增组件

1. `frontend/src/components/AIAssistant.vue`  
   - AI 分析按钮  
   - 摘要展示（总览、要点、章节）  
   - 转录滚动区（带时间戳）  
   - 思维导图区  
   - 视频问答输入与历史

2. `frontend/src/components/MindMapTree.vue`  
   - 递归树形渲染思维导图节点

### 5.4 页面集成

文件：`frontend/src/components/DownloadForm.vue`

在下载流程区域后新增：

1. `<AIAssistant :url="url" />`

说明：AI 功能与下载功能解耦；用户可独立使用 AI 分析，不影响已有下载逻辑。

## 6. 测试与验证

### 6.1 后端测试（新增）

1. `backend/test_ai_api.py`  
   - 覆盖 `/api/ai/analyze` 成功/失败  
   - 覆盖 `/api/ai/chat` 成功/任务不存在

2. `backend/test_video_ai_service.py`  
   - 覆盖字幕解析  
   - 覆盖回退摘要  
   - 覆盖思维导图构建

执行命令：

```bash
cd backend
python -m unittest test_ai_api.py test_video_ai_service.py
```

结果：`Ran 7 tests ... OK`

### 6.2 前端验证

执行命令：

```bash
cd frontend
npm run build
```

结果：`vue-tsc` + `vite build` 通过。

## 7. 已知限制

1. 视频必须存在可访问字幕（人工字幕或自动字幕）  
2. 无 API Key 时摘要与问答为规则回退，质量低于大模型  
3. `analysis_id` 缓存在内存，服务重启后失效  
4. 未实现“点击时间戳联动播放器跳转”  
5. 未实现“分析结果导出（Markdown/PDF）”

## 8. 后续建议（P1）

1. 接入可配置模型供应商（OpenAI/DeepSeek/通义）与切换策略  
2. 问答改造成 RAG（向量检索）提升命中准确率  
3. 增加时间戳点击跳转与播放器联动  
4. 增加摘要/脑图导出与知识库同步  
5. 增加分析任务持久化与过期清理策略

## 9. 本次改动文件清单

### 后端

1. `backend/app/config.py`
2. `backend/app/models.py`
3. `backend/app/main.py`
4. `backend/app/routers/ai.py`（新增）
5. `backend/app/routers/__init__.py`
6. `backend/app/services/video_ai_service.py`（新增）
7. `backend/app/services/__init__.py`
8. `backend/test_ai_api.py`（新增）
9. `backend/test_video_ai_service.py`（新增）
10. `backend/README.md`

### 前端

1. `frontend/src/types/index.ts`
2. `frontend/src/composables/useVideoAI.ts`（新增）
3. `frontend/src/components/AIAssistant.vue`（新增）
4. `frontend/src/components/MindMapTree.vue`（新增）
5. `frontend/src/components/DownloadForm.vue`
6. `frontend/src/components/FormatSelector.vue`
7. `frontend/src/components/VideoInfo.vue`
8. `frontend/src/composables/useDownload.ts`
