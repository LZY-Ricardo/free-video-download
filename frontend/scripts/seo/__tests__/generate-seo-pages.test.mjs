import test from 'node:test'
import assert from 'node:assert/strict'

import { generateSiteFiles } from '../../generate-seo-pages.mjs'

test('generateSiteFiles returns sitemap, robots and html pages', () => {
  const result = generateSiteFiles({ lastmodDate: '2026-03-31' })

  assert.ok(result.pages['zh/index.html'])
  assert.ok(result.pages['en/index.html'])
  assert.match(result.sitemap, /https:\/\/vidgrab\.sunandyu\.top\/zh\//)
  assert.match(result.sitemap, /<lastmod>2026-03-31<\/lastmod>/)
  assert.match(result.sitemap, /xmlns:xhtml="http:\/\/www\.w3\.org\/1999\/xhtml"/)
  assert.match(result.sitemap, /<xhtml:link rel="alternate" hreflang="en" href="https:\/\/vidgrab\.sunandyu\.top\/en\/" \/>/)
  assert.match(result.robots, /Sitemap:/)
})

test('generated pages include platform, feature and faq routes', () => {
  const result = generateSiteFiles()

  assert.ok(result.pages['zh/platforms/youtube/index.html'])
  assert.ok(result.pages['en/platforms/youtube/index.html'])
  assert.ok(result.pages['zh/features/ai-video-summarizer/index.html'])
  assert.ok(result.pages['en/faq/index.html'])
})
