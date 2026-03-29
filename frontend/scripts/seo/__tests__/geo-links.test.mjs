import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const appVuePath = path.resolve(process.cwd(), 'src/App.vue')

test('App.vue links to GEO answer hubs', () => {
  const source = fs.readFileSync(appVuePath, 'utf8')

  assert.match(source, /\/zh\/answers\//)
  assert.match(source, /\/en\/answers\//)
})
