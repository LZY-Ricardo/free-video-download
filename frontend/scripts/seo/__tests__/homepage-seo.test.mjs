import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const indexHtmlPath = path.resolve(process.cwd(), 'index.html')

test('index.html contains site-level SEO tags', () => {
  const html = fs.readFileSync(indexHtmlPath, 'utf8')

  assert.match(html, /name="description"/)
  assert.match(html, /property="og:title"/)
  assert.match(html, /application\/ld\+json/)
})
