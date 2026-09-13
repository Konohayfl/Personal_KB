import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createdLabel, dateValue, libraryTone, selectLibraries } from '../src/libs/library-view.js'

const rows = Object.freeze([
  Object.freeze({ id: 'a', reposNm: 'Vue 实践', crtTm: '2026-09-10 08:30:00' }),
  Object.freeze({ id: 'b', reposNm: '阅读笔记', crtTm: '2026-09-12 10:30:00' }),
  Object.freeze({ id: 'c', reposNm: 'Vue 文档', crtTm: '2026-09-11 09:30:00' }),
  Object.freeze({ id: 'd', reposNm: null, crtTm: null })
])

test('搜索忽略首尾空白与大小写，排序不改变接口原数组', () => {
  assert.deepEqual(selectLibraries(rows, '  vUE ', 'newest', 'reposNm').map(x => x.id), ['c', 'a'])
  assert.deepEqual(rows.map(x => x.id), ['a', 'b', 'c', 'd'])
})
test('中文搜索、空结果和清除搜索', () => {
  assert.deepEqual(selectLibraries(rows, '阅读', 'newest', 'reposNm').map(x => x.id), ['b'])
  assert.equal(selectLibraries(rows, '不存在', 'newest', 'reposNm').length, 0)
  assert.equal(selectLibraries(rows, '  ', 'newest', 'reposNm').length, 4)
})
test('创建时间支持 SQLite 时间格式并能正反排序', () => {
  assert.ok(dateValue('2026-09-12 10:30:00') > dateValue('2026-09-10 08:30:00'))
  assert.deepEqual(selectLibraries(rows, '', 'newest', 'reposNm').map(x => x.id), ['b', 'c', 'a', 'd'])
  assert.deepEqual(selectLibraries(rows, '', 'oldest', 'reposNm').map(x => x.id), ['d', 'a', 'c', 'b'])
})
test('文档集名称排序使用文档集字段并支持自然数字顺序', () => {
  const docs = [{ setNm: '笔记10' }, { setNm: '笔记2' }, { setNm: '笔记1' }]
  assert.deepEqual(selectLibraries(docs, '', 'name', 'setNm').map(x => x.setNm), ['笔记1', '笔记2', '笔记10'])
})
test('缺失或无效日期不伪造时间，空列表可正常展示', () => {
  for (const value of [null, undefined, '', 'not-a-date']) {
    assert.equal(dateValue(value), 0)
    assert.equal(createdLabel(value), '创建时间未记录')
  }
  assert.match(createdLabel('2026-09-12 10:30:00'), /2026\/09\/12 创建/)
  assert.deepEqual(selectLibraries([], '', 'name'), [])
})
test('卡片颜色由稳定 ID 决定，搜索和重新排序不会改变颜色', () => {
  const before = rows.map(x => [x.id, libraryTone(x.id)])
  for (const row of selectLibraries(rows, '', 'newest', 'reposNm')) {
    assert.equal(libraryTone(row.id), before.find(([id]) => id === row.id)[1])
  }
  assert.ok(libraryTone('中文-知识库') >= 0 && libraryTone('中文-知识库') < 6)
})
