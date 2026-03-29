import test from 'node:test'
import assert from 'node:assert/strict'

import { geoAnswerContent } from '../answers-content.mjs'

test('first FAQ pages provide direct answers and limits', () => {
  const firstFaq = geoAnswerContent.zh.faq[0]

  assert.ok(firstFaq.answer.length > 0)
  assert.ok(
    firstFaq.sections.some((section) => section.title.includes('注意') || section.title.includes('限制')),
  )
})
