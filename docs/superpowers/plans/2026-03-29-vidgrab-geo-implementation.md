# VidGrab GEO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不影响现有下载与 AI 功能的前提下，为 VidGrab 增加中英双语的 GEO 答案型页面体系，并让这些页面更容易被 AI 对话引用。

**Architecture:** 复用当前静态 SEO 生成体系，新增 answers 数据源和 GEO 模板渲染器，输出 FAQ、HowTo、Compare 三类页面到 `/zh/answers/...` 与 `/en/answers/...`；首页和现有聚合页只做轻量互链增强。

**Tech Stack:** Vue 3、Vite、Node.js 内置 `node:test`、静态 HTML 生成脚本、JSON-LD

---

### Task 1: 建立 GEO 数据源与答案模板渲染器

**Files:**
- Create: `frontend/scripts/seo/answers-content.mjs`
- Create: `frontend/scripts/seo/answers-renderers.mjs`
- Create: `frontend/scripts/seo/__tests__/answers-renderers.test.mjs`

- [ ] **Step 1: Write the failing test**

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { renderFaqAnswerPage, buildHowToJsonLd } from '../answers-renderers.mjs'

test('renderFaqAnswerPage renders direct-answer intro and FAQ schema', () => {
  const html = renderFaqAnswerPage({
    locale: 'zh-CN',
    page: {
      title: 'VidGrab 支持哪些平台？',
      answer: 'VidGrab 支持 YouTube、Bilibili、TikTok 和 Instagram。',
      faqs: [{ question: '示例问题', answer: '示例答案' }],
    },
  })

  assert.match(html, /VidGrab 支持哪些平台？/)
  assert.match(html, /VidGrab 支持 YouTube/)
  assert.match(html, /FAQPage/)
})

test('buildHowToJsonLd returns HowTo schema', () => {
  const schema = buildHowToJsonLd({
    title: '如何用 VidGrab 导出字幕',
    steps: ['粘贴链接', '解析视频', '下载字幕'],
  })

  assert.equal(schema['@type'], 'HowTo')
  assert.equal(schema.step.length, 3)
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test "frontend/scripts/seo/__tests__/answers-renderers.test.mjs"`
Expected: FAIL，因为 `answers-renderers.mjs` 尚不存在。

- [ ] **Step 3: Write minimal implementation**

1. 在 `answers-content.mjs` 中定义首批中英 FAQ / HowTo / Compare 数据。
2. 在 `answers-renderers.mjs` 中实现：
   - FAQ 渲染
   - HowTo 渲染
   - Compare 渲染
   - FAQ / HowTo 的 JSON-LD 生成

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test "frontend/scripts/seo/__tests__/answers-renderers.test.mjs"`
Expected: PASS

- [ ] **Step 5: Refactor**

确保：

1. 中英内容结构一致。
2. FAQ / HowTo / Compare 模板职责清晰。
3. 可复用现有 meta 与 `hreflang` 渲染逻辑。

### Task 2: 接入 answers 页面生成链路

**Files:**
- Modify: `frontend/scripts/generate-seo-pages.mjs`
- Modify: `frontend/scripts/seo/content.mjs`
- Create: `frontend/scripts/seo/__tests__/answers-generation.test.mjs`

- [ ] **Step 1: Write the failing test**

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { generateSiteFiles } from '../../generate-seo-pages.mjs'

test('generateSiteFiles includes zh and en answer pages', () => {
  const result = generateSiteFiles()

  assert.ok(result.pages['zh/answers/index.html'])
  assert.ok(result.pages['en/answers/index.html'])
  assert.ok(result.pages['zh/answers/faq/vidgrab-supported-platforms/index.html'])
  assert.ok(result.pages['en/answers/how-to/how-to-export-subtitles-with-vidgrab/index.html'])
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test "frontend/scripts/seo/__tests__/answers-generation.test.mjs"`
Expected: FAIL，因为 answers 页面尚未纳入生成结果。

- [ ] **Step 3: Write minimal implementation**

1. 在 `generate-seo-pages.mjs` 中把 answers 页面纳入 `collectPages()`。
2. 生成：
   - `/zh/answers/`
   - `/en/answers/`
   - FAQ 页面
   - HowTo 页面
   - Compare 页面
3. 保持 sitemap 自动带出这些新路径。

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm run test:seo`
Expected: PASS

- [ ] **Step 5: Verify generated files**

Run:

```bash
Get-ChildItem -Recurse "frontend/public/zh/answers"
Get-ChildItem -Recurse "frontend/public/en/answers"
```

Expected:

1. 首批 answers 页面文件存在。
2. FAQ / HowTo / Compare 路径结构正确。

### Task 3: 首页与双语聚合页增加 GEO 入口

**Files:**
- Modify: `frontend/src/App.vue`
- Modify: `frontend/scripts/seo/content.mjs`
- Create: `frontend/scripts/seo/__tests__/geo-links.test.mjs`

- [ ] **Step 1: Write the failing test**

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'

test('App.vue links to GEO answer hubs', () => {
  const source = fs.readFileSync('frontend/src/App.vue', 'utf8')

  assert.match(source, /\\/zh\\/answers\\//)
  assert.match(source, /\\/en\\/answers\\//)
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test "frontend/scripts/seo/__tests__/geo-links.test.mjs"`
Expected: FAIL，因为当前首页还没有 answers 入口。

- [ ] **Step 3: Write minimal implementation**

1. 在首页底部增加一个 GEO 入口区块或链接。
2. 在 `/zh/` 与 `/en/` 聚合页的相关链接中加入 answers 入口。
3. 保持现有下载功能区域完全不变。

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm run test:seo`
Expected: PASS

- [ ] **Step 5: Manual sanity check**

确认：

1. 首页工具入口、下载表单和 AI 助手未被修改行为。
2. 只新增了轻量内容入口和链接。

### Task 4: 补充首批 GEO 页面内容质量与结构化数据

**Files:**
- Modify: `frontend/scripts/seo/answers-content.mjs`
- Modify: `frontend/scripts/seo/answers-renderers.mjs`
- Create: `frontend/scripts/seo/__tests__/geo-content-quality.test.mjs`

- [ ] **Step 1: Write the failing test**

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { geoAnswerContent } from '../answers-content.mjs'

test('first FAQ pages provide direct answers and limits', () => {
  const firstFaq = geoAnswerContent.zh.faq[0]

  assert.ok(firstFaq.answer.length > 0)
  assert.ok(firstFaq.sections.some((section) => section.title.includes('注意') || section.title.includes('限制')))
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test "frontend/scripts/seo/__tests__/geo-content-quality.test.mjs"`
Expected: FAIL，直到内容模型包含直接答案和边界说明。

- [ ] **Step 3: Write minimal implementation**

为首批页面补齐：

1. 6 个 FAQ（中英对等）
2. 3 个 HowTo（中英对等）
3. 2 个 Compare（中英对等）

每页必须有：

1. 第一段直接答案
2. 至少 3 个结构化章节
3. 边界或注意事项
4. CTA

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm run test:seo`
Expected: PASS

- [ ] **Step 5: Spot-check generated HTML**

Run:

```bash
Get-Content -Raw "frontend/public/zh/answers/faq/vidgrab-supported-platforms/index.html"
Get-Content -Raw "frontend/public/en/answers/compare/vidgrab-vs-regular-video-downloaders/index.html"
```

Expected:

1. 页面开头直接给答案。
2. FAQ / HowTo / Compare 对应结构化数据存在。
3. 页面底部有回首页 CTA。

### Task 5: 全量验证

**Files:**
- Verify only

- [ ] **Step 1: Run SEO/GEO tests**

Run: `npm run test:seo`
Expected: PASS

- [ ] **Step 2: Regenerate static files**

Run: `npm run seo:generate`
Expected: PASS

- [ ] **Step 3: Run production build**

Run: `npm run build`
Expected: PASS

- [ ] **Step 4: Inspect dist output**

Run:

```bash
Get-ChildItem -Recurse "frontend/dist/zh/answers"
Get-ChildItem -Recurse "frontend/dist/en/answers"
```

Expected:

1. 构建产物包含 answers 页面。
2. 现有 `/zh`、`/en`、首页仍正常输出。

- [ ] **Step 5: Prepare handoff summary**

总结：

1. 新增了哪些 GEO 页面
2. 这些页面如何帮助 AI 引用
3. 后续可继续扩展的话题池

## Notes

1. 当前仓库规则要求 `git commit` 前需用户确认，因此本计划不包含自动提交动作。
2. 当前会话未得到用户对代理委托的明确授权，因此计划审查采用本地自检，不调用子代理。
