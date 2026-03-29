# VidGrab SEO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不影响现有下载与 AI 功能的前提下，为 VidGrab 增加首页 SEO 增强、中英双语静态 SEO 页面、`robots.txt` 和 `sitemap.xml`。

**Architecture:** 保留现有 Vue SPA 主页作为工具入口，仅做最小 SEO 增强；新增一套构建期 SEO 数据源与静态页面生成脚本，将 `/zh/...` 与 `/en/...` 输出到 `frontend/public`；通过统一渲染器生成 TDK、`hreflang`、JSON-LD 与站点级资产。

**Tech Stack:** Vue 3、Vite、TypeScript、Node.js 内置 `node:test`、静态 HTML 生成脚本

---

### Task 1: 建立 SEO 数据源与渲染工具

**Files:**
- Create: `frontend/scripts/seo/site-config.mjs`
- Create: `frontend/scripts/seo/content.mjs`
- Create: `frontend/scripts/seo/renderers.mjs`
- Create: `frontend/scripts/seo/__tests__/renderers.test.mjs`

- [ ] **Step 1: Write the failing test**

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { buildMetaTags, buildAlternateLinks } from '../renderers.mjs'

test('buildMetaTags returns canonical and og tags for a zh page', () => {
  const html = buildMetaTags({
    locale: 'zh-CN',
    path: '/zh/platforms/youtube',
    title: 'YouTube 视频下载器 - VidGrab | 在线解析、下载与 AI 总结',
    description: '测试描述',
    keywords: ['YouTube 视频下载器', 'VidGrab'],
    image: '/og/default-share-cover.svg',
  })

  assert.match(html, /rel="canonical"/)
  assert.match(html, /property="og:title"/)
  assert.match(html, /name="keywords"/)
})

test('buildAlternateLinks returns zh/en hreflang links', () => {
  const html = buildAlternateLinks({
    currentPath: '/zh/platforms/youtube',
    alternatePath: '/en/platforms/youtube',
  })

  assert.match(html, /hreflang="zh-CN"/)
  assert.match(html, /hreflang="en"/)
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test "frontend/scripts/seo/__tests__/renderers.test.mjs"`
Expected: FAIL，因为 `renderers.mjs` 尚不存在。

- [ ] **Step 3: Write minimal implementation**

实现 `site-config.mjs`、`content.mjs`、`renderers.mjs`，至少包含：

```js
export const SITE = {
  brandName: 'VidGrab',
  baseUrl: 'https://vidgrab.sunandyu.top',
}

export function buildMetaTags(page) {
  return `<link rel="canonical" href="${SITE.baseUrl}${page.path}">`
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test "frontend/scripts/seo/__tests__/renderers.test.mjs"`
Expected: PASS

- [ ] **Step 5: Refactor**

整理数据结构，确保：

1. 品牌与域名常量只定义一次。
2. 页面内容数据与 HTML 渲染逻辑分离。
3. 中英页面使用统一字段结构。

- [ ] **Step 6: Re-run tests**

Run: `node --test "frontend/scripts/seo/__tests__/renderers.test.mjs"`
Expected: PASS

### Task 2: 实现静态页面与站点资产生成脚本

**Files:**
- Create: `frontend/scripts/generate-seo-pages.mjs`
- Create: `frontend/scripts/seo/__tests__/generate-seo-pages.test.mjs`
- Modify: `frontend/package.json`

- [ ] **Step 1: Write the failing test**

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import { generateSiteFiles } from '../generate-seo-pages.mjs'

test('generateSiteFiles returns sitemap, robots and html pages', () => {
  const result = generateSiteFiles()

  assert.ok(result.pages['zh/index.html'])
  assert.ok(result.pages['en/index.html'])
  assert.match(result.sitemap, /https:\/\/vidgrab\.sunandyu\.top\/zh\//)
  assert.match(result.robots, /Sitemap:/)
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test "frontend/scripts/seo/__tests__/generate-seo-pages.test.mjs"`
Expected: FAIL，因为导出函数尚不存在。

- [ ] **Step 3: Write minimal implementation**

实现 `generateSiteFiles()`，返回：

```js
{
  pages: {
    'zh/index.html': '<!doctype html>...</html>',
    'en/index.html': '<!doctype html>...</html>',
  },
  sitemap: '<?xml version="1.0" ...',
  robots: 'User-agent: *\\nAllow: /\\nSitemap: ...',
}
```

并在 `frontend/package.json` 中新增脚本：

```json
{
  "scripts": {
    "seo:generate": "node ./scripts/generate-seo-pages.mjs",
    "build": "npm run seo:generate && vue-tsc -b && vite build",
    "test:seo": "node --test \"scripts/seo/__tests__/*.test.mjs\""
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm run test:seo`
Expected: PASS

- [ ] **Step 5: Verify generation side effects**

Run: `npm run seo:generate`
Expected:

1. `frontend/public/robots.txt` 已生成。
2. `frontend/public/sitemap.xml` 已生成。
3. `frontend/public/zh/...` 与 `frontend/public/en/...` 页面已生成。

### Task 3: 为首页补齐基础 SEO 元信息与语义内容

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/src/App.vue`
- Create: `frontend/public/og/default-share-cover.svg`

- [ ] **Step 1: Write the failing test**

新增对首页输出的静态检查用例，确认默认 head 里包含关键 meta：

```js
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'

test('index.html contains site-level SEO tags', () => {
  const html = fs.readFileSync('frontend/index.html', 'utf8')
  assert.match(html, /name="description"/)
  assert.match(html, /property="og:title"/)
  assert.match(html, /application\/ld\+json/)
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test "frontend/scripts/seo/__tests__/homepage-seo.test.mjs"`
Expected: FAIL，因为首页当前未补全这些标签。

- [ ] **Step 3: Write minimal implementation**

1. 在 `frontend/index.html` 中补：
   - `description`
   - `keywords`
   - `robots`
   - `canonical`
   - `og:*`
   - `twitter:*`
   - 首页 JSON-LD
2. 在 `frontend/src/App.vue` 中新增可抓取的说明区块与内链入口，保持现有下载功能区不变。
3. 新增默认分享图资源。

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm run test:seo`
Expected: PASS

- [ ] **Step 5: Manual sanity check**

确认：

1. `frontend/src/App.vue` 仍保留现有下载入口与 AI 组件。
2. 新增文案不改变现有按钮、输入框和功能事件绑定。

### Task 4: 生成中英 SEO 页面正文与内部链接

**Files:**
- Modify: `frontend/scripts/seo/content.mjs`
- Modify: `frontend/scripts/seo/renderers.mjs`
- Modify: `frontend/scripts/generate-seo-pages.mjs`

- [ ] **Step 1: Write the failing test**

补充测试，验证至少包含以下页面：

```js
test('generated pages include platform, feature and faq routes', () => {
  const result = generateSiteFiles()

  assert.ok(result.pages['zh/platforms/youtube/index.html'])
  assert.ok(result.pages['en/platforms/youtube/index.html'])
  assert.ok(result.pages['zh/features/ai-video-summarizer/index.html'])
  assert.ok(result.pages['en/faq/index.html'])
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test:seo`
Expected: FAIL，因为首批页面尚未全部生成。

- [ ] **Step 3: Write minimal implementation**

补齐首批页面数据：

1. 中文/英文聚合页各 1 个。
2. 平台页 4 组。
3. 功能页 4 组。
4. FAQ 页中英文各 1 个。

正文必须包含：

1. 单一 H1
2. 至少 3 个 H2
3. CTA 链接回 `/`
4. 同语言内部链接

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm run test:seo`
Expected: PASS

- [ ] **Step 5: Review generated output**

Run:

```bash
Get-Content -Raw "frontend/public/zh/platforms/youtube/index.html"
Get-Content -Raw "frontend/public/en/faq/index.html"
```

Expected:

1. HTML 中存在 title、description、canonical、`hreflang`。
2. 正文结构包含 H1/H2。
3. FAQ 页包含 `FAQPage` JSON-LD。

### Task 5: 全量构建与结果验证

**Files:**
- Verify only

- [ ] **Step 1: Run SEO tests**

Run: `npm run test:seo`
Expected: PASS

- [ ] **Step 2: Run production build**

Run: `npm run build`
Expected: PASS，无 TypeScript 或 Vite 构建错误。

- [ ] **Step 3: Inspect generated assets**

Run:

```bash
Get-Content -Raw "frontend/public/robots.txt"
Get-Content -Raw "frontend/public/sitemap.xml"
```

Expected:

1. `robots.txt` 允许抓取并引用站点地图。
2. `sitemap.xml` 包含首页、中文页、英文页与首批平台/功能/FAQ 页面。

- [ ] **Step 4: Spot-check homepage safety**

Run:

```bash
Get-Content -Raw "frontend/src/App.vue"
```

Expected:

1. 下载输入区、视频信息区、AI 助手区仍在。
2. 未修改现有 API 调用逻辑。

- [ ] **Step 5: Prepare handoff summary**

总结：

1. 已新增的 SEO 页面与站点资产。
2. 已验证的命令与结果。
3. 尚未覆盖的后续扩展项，例如更多平台页与指南页。

## Notes

1. 当前仓库规则要求 `git commit` 之前必须征得用户明确确认，因此本计划不包含自动提交动作。
2. 当前会话未获得用户显式授权，不能调用子代理进行计划审查，因此计划审查采用本地自检替代。
