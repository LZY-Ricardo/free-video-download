import assert from 'node:assert/strict'

const {
  resolveInfoPrimaryErrorMessage,
  resolveInfoFallbackErrorMessage,
  shouldPreferLocalResolver,
  shouldTryLocalResolverFallback,
} = await import('../src/utils/downloadFallback.ts')

assert.equal(
  shouldPreferLocalResolver('https://www.bilibili.com/video/BV11zbPzVEUe'),
  true,
)
assert.equal(
  shouldPreferLocalResolver('https://www.youtube.com/watch?v=test'),
  true,
)

assert.equal(
  shouldTryLocalResolverFallback('https://www.bilibili.com/video/BV11zbPzVEUe', 'HTTP 412 风控', 400),
  true,
)
assert.equal(
  shouldTryLocalResolverFallback('https://www.youtube.com/watch?v=test', 'HTTP 412 风控', 400),
  true,
)
assert.equal(
  shouldTryLocalResolverFallback('https://www.youtube.com/watch?v=test', '服务器错误', 500),
  true,
)
assert.equal(
  shouldTryLocalResolverFallback('https://www.instagram.com/reel/test', '获取视频信息失败', undefined),
  true,
)
assert.equal(
  shouldTryLocalResolverFallback('https://www.youtube.com/watch?v=test', '请求参数错误', 400),
  false,
)
assert.equal(
  resolveInfoFallbackErrorMessage(
    { response: { data: { detail: '本地解析失败: 请求超时' } } },
    '获取视频信息失败',
  ),
  '本地解析失败: 请求超时',
)
assert.equal(
  resolveInfoPrimaryErrorMessage(
    { response: { data: { detail: '云端解析失败: 平台响应异常' } } },
    '获取视频信息失败',
  ),
  '云端解析失败: 平台响应异常',
)
assert.equal(
  resolveInfoFallbackErrorMessage({}, '获取视频信息失败'),
  '获取视频信息失败',
)
