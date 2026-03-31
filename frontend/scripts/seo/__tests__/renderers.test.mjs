import test from 'node:test'
import assert from 'node:assert/strict'

import { buildAlternateLinks, buildJsonLdScripts, buildMetaTags } from '../renderers.mjs'

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

test('buildAlternateLinks returns zh and en hreflang links', () => {
  const html = buildAlternateLinks([
    {
      hrefLang: 'zh-CN',
      path: '/zh/platforms/youtube',
    },
    {
      hrefLang: 'en',
      path: '/en/platforms/youtube',
    },
  ])

  assert.match(html, /hreflang="zh-CN"/)
  assert.match(html, /hreflang="en"/)
})

test('buildMetaTags accepts custom og:type and json-ld scripts are not stringified twice', () => {
  const meta = buildMetaTags({
    locale: 'en',
    path: '/en/answers/how-to/how-to-generate-ai-video-summary',
    title: 'How to generate AI video summaries',
    description: 'Test description',
    keywords: ['VidGrab'],
    ogType: 'article',
  })
  const scripts = buildJsonLdScripts([
    '{"@context":"https://schema.org","@type":"WebPage","name":"Demo"}',
  ])

  assert.match(meta, /property="og:type" content="article"/)
  assert.match(scripts, /<script type="application\/ld\+json">\{"@context":"https:\/\/schema.org","@type":"WebPage","name":"Demo"\}<\/script>/)
})
