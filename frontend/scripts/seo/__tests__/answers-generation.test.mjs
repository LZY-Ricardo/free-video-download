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
