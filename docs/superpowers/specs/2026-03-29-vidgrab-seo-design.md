# VidGrab SEO 扩展设计

**日期：** 2026-03-29

## 背景

当前项目的前端是基于 Vite 的单页应用，现有首页承担视频解析、下载与 AI 学习助手能力，但 SEO 基础设施基本缺失：只有静态 `title`，没有 `description`、`keywords`、`canonical`、`robots.txt`、`sitemap.xml`、Open Graph、结构化数据，也没有中英双语的内容承接页。

本次目标是在**不影响现有下载与 AI 功能流程**的前提下，为站点增加可被中文搜索引擎与 Google 抓取的 SEO 能力，并统一站点品牌口径为 `VidGrab`，主域名为 `https://vidgrab.sunandyu.top`。

## 目标

1. 保留现有首页与功能交互逻辑不变。
2. 为首页补齐站点级 SEO 元信息与结构化数据。
3. 新增中英双语 SEO 内容页，覆盖平台词、功能词、FAQ 与场景词。
4. 自动生成 `robots.txt` 与 `sitemap.xml`，便于搜索引擎抓取。
5. 保证所有新增能力与现有前端构建链路兼容。

## 非目标

1. 不将当前前端整体改造为 SSR / SSG 框架。
2. 不修改现有后端 API、下载逻辑或 AI 分析流程。
3. 不引入登录、CMS、数据库或运营后台。
4. 不在本次实现中扩展新的下载功能。

## 约束

1. 现有功能优先，SEO 改动只能做“旁路扩展”和“安全增强”。
2. 需要同时兼顾中文搜索与 Google，因此采用中英双语页面体系。
3. 页面内容必须是搜索引擎可直接读取的静态 HTML，不能仅依赖客户端渲染。
4. 首页、中文页、英文页必须有清晰的 canonical 与 `hreflang` 关系，避免重复内容风险。

## 总体方案

采用“**保留现有工具首页 + 新增静态 SEO 内容层**”的方案：

1. 保留 `/` 作为现有工具主页，仅补齐首页的基础 SEO 元信息、结构化数据与少量语义化内容。
2. 新增一套构建期生成的静态页面，输出到 `/zh/...` 与 `/en/...` 路径。
3. 通过统一的 SEO 数据源维护页面内容、TDK、FAQ、面包屑与内部链接。
4. 在构建前自动生成静态 HTML、`robots.txt`、`sitemap.xml` 与默认分享图。

这样可以避免重构现有 SPA，同时让搜索引擎获得真正的可抓取页面。

## 信息架构

### 功能入口

- `/`：工具首页，承担品牌词与工具转化。

### 语言入口

- `/zh/`：中文 SEO 聚合页。
- `/en/`：英文 SEO 聚合页。

### 平台页

- `/zh/platforms/youtube`
- `/zh/platforms/bilibili`
- `/zh/platforms/tiktok`
- `/zh/platforms/instagram`
- `/en/platforms/youtube`
- `/en/platforms/bilibili`
- `/en/platforms/tiktok`
- `/en/platforms/instagram`

### 功能页

- `/zh/features/video-downloader`
- `/zh/features/audio-extractor`
- `/zh/features/subtitle-downloader`
- `/zh/features/ai-video-summarizer`
- `/en/features/video-downloader`
- `/en/features/audio-extractor`
- `/en/features/subtitle-downloader`
- `/en/features/ai-video-summarizer`

### 问答页

- `/zh/faq`
- `/en/faq`

## TDK 规范

### 品牌口径

- 品牌名：`VidGrab`
- 域名：`https://vidgrab.sunandyu.top`
- 品牌定位：`AI Video Downloader & Summarizer`

### Title 规则

统一采用三段式结构：

- 中文：`页面主题 - VidGrab | 核心价值`
- 英文：`Page Topic - VidGrab | Core Value`

### Description 规则

1. 中文页将关键信息压缩在前 150-180 个字符内。
2. 英文页尽量控制在 140-160 characters。
3. 每页必须独立，不可只替换一个词后重复使用。
4. 必须覆盖页面的主关键词、使用场景与价值点。

### Keywords 规则

1. 保留 `keywords` 以兼容百度等国内搜索引擎。
2. 每页控制在 5-8 个关键词。
3. 中文与英文页面分别维护关键词集，避免混用。

## 页面模板

### 首页 `/`

角色：品牌词与主转化页。

要求：

1. 保持现有下载和 AI 工作流不变。
2. 补齐完整的 title、description、keywords、canonical、robots、OG、Twitter Card。
3. 增加 `WebSite`、`Organization`、`WebApplication` 的 JSON-LD。
4. 优化语义结构，确保保留单一 H1，并增加可抓取的说明性区块。

### 聚合页 `/zh/`、`/en/`

角色：语言级导航页。

要求：

1. 汇总平台页、功能页和 FAQ 页入口。
2. 输出自引用 canonical。
3. 建立同语言内部链接和中英互链。

### 平台页

角色：承接“平台 + 下载器 / summarizer”类关键词。

正文结构：

1. H1：平台主关键词。
2. H2：支持的能力。
3. H2：使用步骤。
4. H2：适用场景。
5. H2：常见问题与 CTA。

结构化数据：

1. `WebPage`
2. `BreadcrumbList`

### 功能页

角色：承接“功能词 + 工具词”。

正文结构：

1. H1：功能主关键词。
2. H2：功能价值。
3. H2：使用步骤。
4. H2：支持平台。
5. H2：常见问题与 CTA。

结构化数据：

1. `WebPage`
2. `BreadcrumbList`

### FAQ 页

角色：覆盖问题型长尾词。

结构化数据：

1. `FAQPage`
2. `BreadcrumbList`

## canonical 与 hreflang 规则

1. 首页 `/` 使用自引用 canonical，不和 `/zh/`、`/en/` 互指。
2. 中英文对应页面使用自引用 canonical。
3. 中英文对应页面互设 `hreflang="zh-CN"` 与 `hreflang="en"`。
4. 每组页面增加 `x-default` 指向首页或对应语言入口页。

## 结构化数据策略

### 首页

- `WebSite`
- `Organization`
- `WebApplication`

### 聚合页 / 平台页 / 功能页

- `WebPage`
- `BreadcrumbList`

### FAQ 页

- `FAQPage`
- `BreadcrumbList`

## 技术落地

### 数据源

新增统一的 SEO 内容配置，集中维护：

1. 品牌与域名
2. 默认 TDK
3. 页面正文内容
4. FAQ 问答
5. 内链关系
6. 结构化数据所需字段

### 生成方式

新增构建期脚本，负责：

1. 将中英双语数据渲染为静态 HTML 页面。
2. 生成 `robots.txt`。
3. 生成 `sitemap.xml`。
4. 输出到 `frontend/public`，由 Vite 构建时原样带入。

### 首页增强

首页仅做最小改动：

1. 更新 `frontend/index.html` 的默认站点级 meta。
2. 在 `App.vue` 或新增 SEO 组件中补充首页可抓取说明块。
3. 补默认 OG 图与 favicon 资源。

## 验证要求

1. `npm run build` 必须成功。
2. 生成的 `robots.txt`、`sitemap.xml` 存在且内容正确。
3. 抽样检查首页、中文页、英文页的：
   - title
   - description
   - keywords
   - canonical
   - H1
   - `hreflang`
   - JSON-LD
4. 现有首页工具区仍能正常渲染，不影响现有下载与 AI 组件挂载。

## 风险与控制

### 风险 1：重复内容与 canonical 错误

控制方式：

1. 首页与 SEO 内容页职责分离。
2. 每页使用自引用 canonical。
3. 中英页面只做互链，不交叉 canonical。

### 风险 2：静态页面与 SPA 路径冲突

控制方式：

1. SEO 页面仅使用 `/zh/...`、`/en/...`。
2. 现有首页保留在 `/`，避免混淆。

### 风险 3：构建链路被新增脚本破坏

控制方式：

1. 采用独立脚本与纯静态输出。
2. 为渲染函数与 sitemap 生成逻辑补自动化测试。
3. 保持现有前端入口代码改动最小。

## 实施优先级

1. 先完成 SEO 数据源、渲染器与构建期生成脚本。
2. 再补首页基础元信息和站点级结构化数据。
3. 最后完成 robots、sitemap、分享图与验证。

## 说明

由于当前仓库规则要求执行 `git commit` 前必须获得用户明确确认，本设计文档会先写入仓库，但不在本阶段自动提交。
