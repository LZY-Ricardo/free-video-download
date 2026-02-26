# 万能视频下载器

基于 Vue 3 + FastAPI + yt-dlp 的万能视频下载工具，支持 YouTube、Bilibili 等多个平台。

## 功能特性

- ✅ 支持多平台视频下载（YouTube、Bilibili、TikTok 等）
- ✅ 实时下载进度显示
- ✅ 多格式选择（MP4、MP3、WebM）
- ✅ 多质量选择（4K、2K、1080p、720p 等）
- ✅ 简洁易用的用户界面
- 🚧 更多功能开发中...

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite
- Tailwind CSS
- Axios

### 后端
- FastAPI
- yt-dlp（视频下载引擎）
- Python 3.11+

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd free-video-download
```

### 2. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m app.main
# 或
uvicorn app.main:app --reload
```

后端将运行在 `http://localhost:8000`

API 文档：`http://localhost:8000/docs`

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 `http://localhost:5173`

### 4. 使用应用

1. 在浏览器中打开 `http://localhost:5173`
2. 粘贴视频链接（支持 YouTube、Bilibili 等）
3. 点击"获取信息"查看视频详情
4. 选择格式和质量
5. 点击"开始下载"

## 项目结构

```
free-video-download/
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── components/   # Vue 组件
│   │   ├── composables/  # 组合式函数
│   │   ├── api/          # API 客户端
│   │   └── types/        # TypeScript 类型定义
│   └── package.json
│
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── routers/      # API 路由
│   │   ├── services/     # 业务逻辑
│   │   ├── models.py     # 数据模型
│   │   └── config.py     # 配置
│   └── requirements.txt
│
└── docs/                 # 项目文档
    ├── 需求分析.md
    └── 方案设计.md
```

## API 接口

### 获取视频信息
```bash
POST /api/info
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=xxx"
}
```

### 开始下载
```bash
POST /api/download
Content-Type: application/json

{
  "url": "https://...",
  "format": "mp4",
  "quality": "1080p"
}
```

### 获取下载状态
```bash
GET /api/download/status/{task_id}
```

### 下载文件
```bash
GET /api/download/file/{task_id}
```

## 开发说明

### 前端开发
```bash
cd frontend
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run preview      # 预览生产构建
```

### 后端开发
```bash
cd backend
python -m app.main   # 启动开发服务器（带热重载）
```

## 环境变量

### 后端 (.env)
```env
DEBUG=true
DOWNLOAD_DIR=downloads
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 许可证

本项目仅供学习使用，请遵守相关法律法规和平台服务条款。

## 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载工具
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Vue 3](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
