import assert from 'node:assert/strict'

const { getDisplayProgress } = await import('../src/utils/downloadProgress.ts')

assert.equal(getDisplayProgress('completed', 0.4), 100)
assert.equal(getDisplayProgress('completed', 87.5), 100)
assert.equal(getDisplayProgress('downloading', 27.5), 27.5)
assert.equal(getDisplayProgress('ready', 0), 0)
