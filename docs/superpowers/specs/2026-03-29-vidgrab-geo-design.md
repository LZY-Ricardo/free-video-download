# VidGrab GEO 扩展设计

**日期：** 2026-03-29

## 背景

VidGrab 当前已经具备基础 SEO 能力，包括首页站点级元信息、双语静态 SEO 页面、站点地图与结构化数据，但这些内容仍偏向搜索引擎抓取与传统点击流量。针对 ChatGPT、Gemini、Perplexity 以及中文大模型等生成式回答场景，站点还缺少专门面向 AI 引用的“答案型内容层”。

本次 GEO 的目标是在**不影响现有视频下载、字幕导出和 AI 学习助手功能**的前提下，为 VidGrab 增加可被 AI 对话优先抽取、引用和推荐的内容资产。

## 目标

1. 新增中英双语的 GEO 答案型内容页。
2. 首批覆盖 FAQ、HowTo、Compare 三类页面，并以 FAQ 为主。
3. 所有页面都满足“结论先行、结构清晰、便于引用”的 GEO 写法。
4. 继续复用当前静态生成链路，避免改动现有业务功能。
5. 为首页和现有聚合页增加轻量互链，把用户与 AI 引用流量导回产品入口。

## 非目标

1. 不调整现有下载、解析、AI 总结、字幕导出与问答主流程。
2. 不重构前端为 SSR 框架。
3. 不在本次实现中引入数据库、CMS 或内容后台。
4. 不尝试在本次内直接影响第三方 AI 爬虫策略，只专注于站内可引用内容资产建设。

## 约束

1. 必须保持现有前端交互和 API 行为不变。
2. GEO 内容必须是静态 HTML，可直接被抓取和引用。
3. 首批内容需要同时兼顾中文模型与国际模型，因此保持中英双语对等结构。
4. 内容组织应偏“问答和参考资料”，而不是营销长文。

## 总体方案

采用“**复用现有静态 SEO 生成体系，新增 answers 内容层**”的方案：

1. 在现有 `frontend/scripts/seo` 生成体系上扩展 `answers` 内容数据源和页面模板。
2. 新增路径：
   - `/zh/answers/`
   - `/en/answers/`
   - `/zh/answers/faq/...`
   - `/en/answers/faq/...`
   - `/zh/answers/how-to/...`
   - `/en/answers/how-to/...`
   - `/zh/answers/compare/...`
   - `/en/answers/compare/...`
3. 首页与现有双语聚合页仅做轻量互链增强，不改动业务组件逻辑。
4. GEO 页面在结构上优先服务 AI 引用，再承接用户点击和转化。

## GEO 内容原则

### 1. 结论先行

每个页面的第一段必须在前 100 字内直接回答问题，不写空洞铺垫。

### 2. 结构化表达

页面采用明确层级：

1. H1：完整问题或结论型标题
2. 第一段：直接答案
3. H2：原因、步骤、限制、适用场景、补充建议

### 3. 短段落

一段只讲一个观点，段落短小，利于 AI 抽取。

### 4. 明确边界

每个页面应说明：

1. 适用条件
2. 局限性
3. 注意事项

### 5. 明确动作建议

每个页面底部提供 CTA，引导回首页工具页。

## 信息架构

### answers 聚合页

- `/zh/answers/`
- `/en/answers/`

角色：

1. 作为 GEO 内容入口
2. 汇总 FAQ、HowTo、Compare 三类页面
3. 提供中英互链与同类推荐

### FAQ 页面

角色：承接“是什么 / 支持吗 / 能不能 / 有什么区别”类问题。

首批建议主题：

1. VidGrab 支持哪些平台？
2. VidGrab 可以下载字幕吗？
3. VidGrab 能总结视频内容吗？
4. VidGrab 适合哪些人使用？
5. VidGrab 和普通视频下载器有什么区别？
6. 使用 VidGrab 处理公开视频时需要注意什么？

### HowTo 页面

角色：承接“怎么做 / 如何操作”类问题。

首批建议主题：

1. 如何用 VidGrab 下载公开视频
2. 如何用 VidGrab 导出字幕
3. 如何用 VidGrab 生成 AI 视频总结

### Compare 页面

角色：承接“怎么选 / 对比 / 替代方案”类问题。

首批建议主题：

1. VidGrab vs 普通视频下载工具
2. 在线视频下载与 AI 总结工具怎么选

## 页面模板

### FAQ 模板

结构：

1. H1：完整问题
2. 直接答案
3. 为什么会这样
4. 适用场景
5. 限制与注意事项
6. 下一步建议

结构化数据：

1. `FAQPage`
2. `BreadcrumbList`
3. `WebPage`

### HowTo 模板

结构：

1. H1：目标动作
2. 先给结果与适用条件
3. 准备条件
4. 步骤列表
5. 常见错误
6. 补充建议

结构化数据：

1. `HowTo`
2. `BreadcrumbList`
3. `WebPage`

### Compare 模板

结构：

1. H1：对比主题
2. 第一段给推荐结论
3. 核心差异表
4. 适合谁
5. 优缺点
6. 推荐选择

结构化数据：

1. `WebPage`
2. `BreadcrumbList`

## 技术实现

### 复用现有生成器

继续使用现有静态页面生成入口：

- `frontend/scripts/generate-seo-pages.mjs`
- `frontend/scripts/seo/content.mjs`
- `frontend/scripts/seo/renderers.mjs`

但为 GEO 内容单独增加 answers 数据与模板函数，避免 SEO 与 GEO 内容耦合混乱。

### 建议新增模块

1. `frontend/scripts/seo/answers-content.mjs`
   - 维护中英 FAQ / HowTo / Compare 数据
2. `frontend/scripts/seo/answers-renderers.mjs`
   - 负责按模板渲染 GEO 页面正文与结构化数据

### 生成结果

构建期自动输出：

1. `frontend/public/zh/answers/...`
2. `frontend/public/en/answers/...`

并继续由 Vite 在构建时带入 `dist`。

## 结构化数据策略

### FAQ 页面

使用：

1. `WebPage`
2. `FAQPage`
3. `BreadcrumbList`

### HowTo 页面

使用：

1. `WebPage`
2. `HowTo`
3. `BreadcrumbList`

### Compare 页面

使用：

1. `WebPage`
2. `BreadcrumbList`

## 互链策略

1. 在首页底部新增 GEO 入口卡片链接。
2. 在 `/zh/` 和 `/en/` 聚合页新增 answers 入口。
3. 在 GEO 页面内部提供：
   - 同类问题推荐
   - 回首页 CTA
   - 中英互链

## 验证要求

1. `npm run test:seo` 继续通过。
2. `npm run seo:generate` 后新增 answers 页面文件生成成功。
3. `npm run build` 成功。
4. 抽样检查 FAQ、HowTo、Compare 页面：
   - H1 是否明确
   - 第一段是否直接回答问题
   - JSON-LD 是否正确
   - canonical / hreflang 是否正确
5. 首页原有下载、AI 区域仍可正常渲染。

## 风险与控制

### 风险 1：GEO 内容与现有 SEO 内容重复

控制方式：

1. GEO 页面聚焦“直接回答问题”
2. SEO 页面聚焦“平台与功能介绍”
3. 两者在信息架构上区分用途

### 风险 2：首页改动影响现有功能

控制方式：

1. 首页只增加轻量互链区块
2. 不修改 `DownloadForm`、`useDownload`、`useVideoAI` 行为

### 风险 3：模板扩展导致生成脚本复杂化

控制方式：

1. GEO 模板单独拆分模块
2. 用测试覆盖 FAQ / HowTo / Compare 输出

## 实施优先级

1. 先扩展 GEO 数据源与渲染器
2. 再接入生成脚本并输出首批页面
3. 最后在首页与聚合页加入轻量入口

## 说明

当前仓库规则要求在执行 `git commit` 前必须获得用户确认，因此本设计文档只负责固化方案，不自动提交。
