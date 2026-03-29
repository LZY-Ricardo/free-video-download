import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const appVuePath = path.resolve(process.cwd(), 'src/App.vue')

test('App.vue uses VidGrab consistently in visible branding', () => {
  const source = fs.readFileSync(appVuePath, 'utf8')

  assert.match(source, /VidGrab/)
  assert.doesNotMatch(source, /SaveAny/)
})
