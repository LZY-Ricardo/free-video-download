# 使用指南

## 当前状态

✅ **阶段 1**: FastAPI 后端 + yt-dlp 封装 - 已完成
✅ **阶段 2**: Vue3 + Vite + TailwindCSS 前端框架 - 已完成
✅ **阶段 3**: 前后端联调 - 准备就绪

## 快速开始

### 方法 1: 使用启动脚本（Windows）

双击运行 `start.bat` 文件，会自动启动前后端服务。

### 方法 2: 手动启动

#### 1. 启动后端

```bash
cd backend

# 验证依赖（可选）
python verify.py

# 启动服务
python -m app.main
```

后端将运行在 `http://localhost:8000`

#### 2. 启动前端

打开新的终端窗口：

```bash
cd frontend
npm run dev
```

前端将运行在 `http://localhost:5173`

#### 3. 访问应用

在浏览器中打开 `http://localhost:5173`

## API 文档

后端启动后，可以访问以下地址查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 使用流程

1. **粘贴视频链接**
   - 支持 YouTube、Bilibili、TikTok 等平台
   - 示例: `https://www.youtube.com/watch?v=xxxxx`

2. **获取视频信息**
   - 点击"获取信息"按钮
   - 查看视频标题、时长、缩略图等

3. **选择格式和质量**
   - 格式: MP4 (视频+音频)、MP3 (仅音频)、WebM
   - 质量: 4K、2K、1080p、720p、480p、360p

4. **开始下载**
   - 点击"开始下载"按钮
   - 实时查看下载进度

5. **下载文件**
   - 下载完成后，点击"下载文件到本地"

## 项目结构说明

```
free-video-download/
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── components/      # 组件
│   │   │   ├── DownloadForm.vue    # 下载表单
│   │   │   ├── VideoInfo.vue       # 视频信息
│   │   │   ├── FormatSelector.vue  # 格式选择器
│   │   │   └── ProgressBar.vue     # 进度条
│   │   ├── composables/     # 组合式函数
│   │   │   └── useDownload.ts      # 下载逻辑
│   │   ├── api/             # API 客户端
│   │   └── types/           # TypeScript 类型
│   └── package.json
│
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── routers/         # API 路由
│   │   │   ├── info.py            # 获取视频信息
│   │   │   ├── download.py        # 下载视频
│   │   │   └── direct.py          # 获取直链
│   │   ├── services/        # 业务逻辑
│   │   │   ├── ytdlp_service.py   # yt-dlp 封装
│   │   │   └── task_manager.py    # 任务管理
│   │   ├── models.py        # 数据模型
│   │   └── config.py        # 配置
│   ├── downloads/           # 临时下载目录
│   └── verify.py            # 依赖验证脚本
│
└── docs/                    # 项目文档
    ├── 需求分析.md
    └── 方案设计.md
```

## 技术栈说明

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Vite**: 下一代前端构建工具
- **Tailwind CSS**: 实用优先的 CSS 框架
- **Axios**: HTTP 客户端

### 后端
- **FastAPI**: 现代化的 Python Web 框架
- **yt-dlp**: 强大的视频下载工具（支持 1800+ 网站）
- **Uvicorn**: ASGI 服务器

## 常见问题

### Q: 下载失败怎么办？

A: 请检查：
1. 视频链接是否正确
2. 网络连接是否正常
3. 后端服务是否正在运行
4. 查看浏览器控制台是否有错误信息

### Q: 支持哪些平台？

A: yt-dlp 支持 1800+ 网站，包括：
- YouTube
- Bilibili
- TikTok
- Instagram
- Twitter
- Vimeo
- 等等...

完整列表请查看: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

### Q: 下载的视频保存在哪里？

A: 后端会将下载的视频临时保存在 `backend/downloads/` 目录中，您点击"下载文件到本地"后，浏览器会将文件下载到您指定的位置。

### Q: 如何修改端口？

A:
- 前端端口: 编辑 `frontend/vite.config.ts` 中的 `server.port`
- 后端端口: 编辑 `backend/app/main.py` 中的 uvicorn 端口配置

## 开发说明

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 后端开发

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器（带热重载）
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload
```

## 注意事项

1. **仅供学习使用**: 本项目仅供学习使用，请遵守相关法律法规和平台服务条款
2. **版权问题**: 请尊重原作者版权，不要用于商业用途
3. **网络要求**: 需要能够访问目标视频平台的网络环境
4. **存储空间**: 下载的视频会临时占用服务器存储空间

## 后续开发计划

- [ ] 批量下载功能
- [ ] 字幕下载和翻译
- [ ] 用户系统
- [ ] 付费功能
- [ ] AI 视频总结

## 技术支持

如有问题，请查看：
- 项目文档: `docs/` 目录
- API 文档: `http://localhost:8000/docs`
- yt-dlp 文档: https://github.com/yt-dlp/yt-dlp
