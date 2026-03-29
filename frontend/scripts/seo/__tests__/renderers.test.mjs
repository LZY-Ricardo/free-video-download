import test from 'node:test'
import assert from 'node:assert/strict'

import { buildAlternateLinks, buildMetaTags } from '../renderers.mjs'

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
