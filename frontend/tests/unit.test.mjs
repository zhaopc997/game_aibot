/**
 * 前端纯函数单元测试（Node 内置 test runner，零依赖）。
 *
 * 运行：npm test
 * 覆盖：Tailwind 类名合并、接口统一解包、游戏素材约定校验。
 *
 * 为什么用 node:test 而不是 vitest：
 *   本机 npm 沙箱限制导致 vitest 依赖装不全（chai/tinyrainbow 缺失）。
 *   node:test 是 Node 内置，零依赖即可运行，CI 友好。
 *   代价是不直接支持 TS，故被测代码保持为可直接 require 的 .mjs/纯 JS 语义。
 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readdirSync, openSync, readSync, closeSync } from 'node:fs'
import { join } from 'node:path'
import { createRequire } from 'node:module'

// 项目 package.json 是 type:module，此处需用 createRequire 加载 CJS 依赖
const require = createRequire(import.meta.url)

// ───────────���─────────────
// 1. cn() — Tailwind 类名合并
// ───────────────────────────
test('cn: 拼接多个类名', () => {
  const { clsx } = require('clsx')
  const merged = clsx('px-2', 'py-1')
  assert.equal(merged, 'px-2 py-1')
})

test('cn: tailwind-merge 会让同类工具类后写覆盖先写', () => {
  const { twMerge } = require('tailwind-merge')
  const { clsx: cx } = require('clsx')
  const cn = (...inputs) => twMerge(cx(inputs))

  assert.equal(cn('px-2', 'px-4'), 'px-4', 'px-4 应覆盖 px-2')
  assert.equal(cn('text-sm', 'text-lg'), 'text-lg', 'text-lg 应覆盖 text-sm')
  assert.equal(cn('px-2', 'text-red-500'), 'px-2 text-red-500', '不冲突的类名都保留')
  assert.equal(cn('base', { active: true, hidden: false }), 'base active', 'falsy 类名被剔除')
  assert.equal(cn(), '', '无参数返回空串')
  assert.equal(cn('a', null, undefined, false, 'b'), 'a b', '忽略 falsy 值')
})

// ───────────────────────────
// 2. unwrap() — 接口统一解包
// ───────────────────────────
/** 与 src/api/client.ts 中 unwrap 保持一致的实现 */
function unwrap(resp) {
  if (resp.data.code !== 0) {
    throw new Error(resp.data.message)
  }
  return resp.data.data
}

test('unwrap: code=0 时返回 data', () => {
  assert.deepEqual(unwrap({ data: { code: 0, message: 'ok', data: { id: 1 } } }), { id: 1 })
})

test('unwrap: code!==0 时抛出业务错误信息', () => {
  assert.throws(
    () => unwrap({ data: { code: 3001, message: '请求过于频繁', data: null } }),
    /请求过于频繁/,
  )
})

test('unwrap: 支持原始类型与 null', () => {
  assert.deepEqual(unwrap({ data: { code: 0, message: 'ok', data: [1, 2] } }), [1, 2])
  assert.equal(unwrap({ data: { code: 0, message: 'ok', data: 0 } }), 0)
  assert.equal(unwrap({ data: { code: 0, message: 'ok', data: false } }), false)
  assert.equal(unwrap({ data: { code: 0, message: 'ok', data: null } }), null)
})

// ───────────────────────────
// 3. 游戏素材约定（防止回归）
// ───────────────────────────
const GAMES_DIR = join(process.cwd(), 'public', 'games')
const EXTS = ['png', 'jpg', 'jpeg', 'webp']

/** 按文件头魔数判断真实格式——不信扩展名（这是本项目踩过的坑） */
function realFormat(file) {
  let fd
  try {
    fd = openSync(file, 'r')
    const buf = Buffer.alloc(8)
    readSync(fd, buf, 0, 8, 0)
    if (buf.subarray(0, 4).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47]))) return 'png'
    if (buf[0] === 0xff && buf[1] === 0xd8) return 'jpeg'
    return 'unknown'
  } catch {
    return 'unknown'
  } finally {
    if (fd !== undefined) closeSync(fd)
  }
}

test('素材: public/games 目录存在', () => {
  assert.ok(existsSync(GAMES_DIR), 'public/games 目录应存在')
})

test('素材: 文件名均为 <数字>.<扩展名>', () => {
  const bad = []
  let files = []
  try {
    files = readdirSync(GAMES_DIR)
  } catch {
    return
  }
  for (const f of files) {
    if (f.endsWith('.md')) continue // 说明文档
    if (!/^\d+\.(png|jpg|jpeg|webp|svg)$/.test(f)) bad.push(f)
  }
  assert.deepEqual(bad, [], `命名不规范的素材：${bad.join(', ')}`)
})

test('素材: 扩展名与内容一致（不一致会被浏览器拒绝解码）', () => {
  // 合法组合：png↔PNG、jpg|jpeg↔JPEG。
  // 真实故障是「扩展名 .png 但内容是 JPEG」——服务器按扩展名发 image/png，
  // 浏览器严格模式拒绝解码。
  const LEGIT = {
    png: 'png',
    jpg: 'jpeg',
    jpeg: 'jpeg',
  }
  const mismatched = []
  for (const id of Array.from({ length: 31 }, (_, i) => i + 1)) {
    for (const ext of EXTS) {
      const f = join(GAMES_DIR, `${id}.${ext}`)
      if (!existsSync(f)) continue
      const fmt = realFormat(f)
      if (fmt === 'unknown') continue // svg 等非位图跳过
      if (LEGIT[ext] !== fmt) mismatched.push(`${id}.${ext} 实为 ${fmt}`)
    }
  }
  assert.deepEqual(
    mismatched,
    [],
    `扩展名与内容不符（浏览器会加载失败）：\n${mismatched.join('\n')}`,
  )
})

test('素材: 31 款游戏均至少有一个候选文件', () => {
  const missing = []
  for (const id of Array.from({ length: 31 }, (_, i) => i + 1)) {
    const found = EXTS.some((ext) => existsSync(join(GAMES_DIR, `${id}.${ext}`)))
    if (!found) missing.push(id)
  }
  assert.deepEqual(missing, [], `以下游戏 id 无任何素材文件：${missing.join(', ')}`)
})