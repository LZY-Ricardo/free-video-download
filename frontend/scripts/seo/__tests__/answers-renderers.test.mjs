import test from 'node:test'
import assert from 'node:assert/strict'

import { buildHowToJsonLd, renderFaqAnswerPage } from '../answers-renderers.mjs'

test('renderFaqAnswerPage renders direct-answer intro and FAQ schema', () => {
  const html = renderFaqAnswerPage({
    locale: 'zh-CN',
    page: {
      path: '/zh/answers/faq/vidgrab-supported-platforms',
      title: 'VidGrab 支持哪些平台？ - VidGrab | AI 引用答案',
      description: 'VidGrab 支持哪些平台的答案页。',
      keywords: ['VidGrab 支持平台'],
      h1: 'VidGrab 支持哪些平台？',
      answer: 'VidGrab 支持 YouTube、Bilibili、TikTok 和 Instagram。',
      sections: [
        {
          title: '为什么这很重要',
          paragraphs: ['这是示例段落。'],
        },
      ],
      faqs: [{ question: '示例问题', answer: '示例答案' }],
      relatedLinks: [],
    },
    alternates: [],
    breadcrumbs: [],
  })

  assert.match(html, /VidGrab 支持哪些平台？/)
  assert.match(html, /VidGrab 支持 YouTube、Bilibili、TikTok 和 Instagram。/)
  assert.match(html, /FAQPage/)
})

test('buildHowToJsonLd returns HowTo schema', () => {
  const schema = buildHowToJsonLd({
    title: '如何用 VidGrab 导出字幕',
    steps: [
      { name: '粘贴链接', text: '粘贴一个公开视频链接。' },
      { name: '解析视频', text: '等待视频信息加载。' },
      { name: '下载字幕', text: '选择字幕格式并下载。' },
    ],
  })

  assert.equal(schema['@type'], 'HowTo')
  assert.equal(schema.step.length, 3)
})
