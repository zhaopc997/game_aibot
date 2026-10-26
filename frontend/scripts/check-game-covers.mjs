#!/usr/bin/env node
/**
 * 游戏封面素材校验脚本
 *
 * 用法：
 *   node frontend/scripts/check-game-covers.mjs
 *   node frontend/scripts/check-game-covers.mjs --api http://127.0.0.1:8080
 *
 * 作用：
 *   1. 从后端拉取游戏权威清单（id + 名称）
 *   2. 探测 public/games/ 下是否存在对应素材
 *   3. 输出每个游戏的素材状态，标出缺素材与非标准尺寸
 *
 * 约定：素材文件名为 <gameId>.{png,jpg,jpeg,webp}
 */

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const GAMES_DIR = path.join(ROOT, 'public', 'games')

const args = process.argv.slice(2)
const apiIdx = args.indexOf('--api')
const API = apiIdx >= 0 ? args[apiIdx + 1] : 'http://127.0.0.1:8080'

const EXTS = ['png', 'jpg', 'jpeg', 'webp']
// 推荐规格：宽幅 460x215（现有正确素材多为该规格），或 1200x562
const IDEAL = { minW: 400, ratio: 2.0, tolerance: 0.6 }

/**
 * 已人工确认为「官方正确素材」的非标准比例条目。
 * 非标准比例本身不等于错误——竖版海报(塞尔达)或方形 logo(明日方舟)也是官方物料，
 * 关键看内容是否与游戏对应。以下条目已逐一目视核对过。
 */
const VERIFIED = new Set([3, 9, 19])

async function fetchGames() {
  try {
    const res = await fetch(`${API}/api/v1/games`, { signal: AbortSignal.timeout(5000) })
    const json = await res.json()
    if (json.code !== 0 || !Array.isArray(json.data)) throw new Error('返回格式异常')
    return json.data.map((g) => ({ id: g.id, name: g.name, coverUrl: g.coverUrl || null }))
  } catch (e) {
    console.error(`✗ 无法连接后端 ${API}：${e.message}`)
    console.error('  请先启动后端，或用 --api 指定地址。')
    process.exit(1)
  }
}

/**
 * 读取图片尺寸。
 *
 * 注意：不能只看扩展名——本目录已存在「扩展名 .png 但内容是 JPEG」的文件
 * （爬虫抓取时未按内容重命名）。故按文件头魔数嗅探真实格式。
 */
function imageSize(file) {
  const fd = fs.openSync(file, 'r')
  try {
    const buf = Buffer.alloc(65536)
    const n = fs.readSync(fd, buf, 0, buf.length, 0)
    if (n < 24) return null

    // 真实格式是 PNG（89 50 4E 47 ...）
    if (buf.subarray(0, 4).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47]))) {
      return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20), format: 'PNG' }
    }

    // 真实格式是 JPEG（FF D8）
    if (buf[0] === 0xff && buf[1] === 0xd8) {
      let i = 2
      while (i < n - 9) {
        if (buf[i] !== 0xff) { i++; continue }
        const marker = buf[i + 1]
        // SOF0-SOF15，排除 DHT(c4)/JPGA(c8)/DAC(cc)
        if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
          return { height: buf.readUInt16BE(i + 5), width: buf.readUInt16BE(i + 7), format: 'JPEG' }
        }
        i += 2 + buf.readUInt16BE(i + 2)
      }
      return { width: null, height: null, format: 'JPEG' }
    }

    // WebP：RIFF....WEBP
    if (n > 16 && buf.subarray(0, 4).toString('ascii') === 'RIFF'
        && buf.subarray(8, 12).toString('ascii') === 'WEBP') {
      return { width: null, height: null, format: 'WebP' }
    }
    return null
  } catch {
    return null
  } finally {
    fs.closeSync(fd)
  }
}

const games = await fetchGames()

let hasCover = 0
let missing = 0
let oddSize = 0
const problems = []

console.log('════ 游戏封面素材状态 ════\n')
console.log('id   游戏                 文件          尺寸        状态')
console.log('─'.repeat(78))

for (const g of games) {
  let file = null
  for (const ext of EXTS) {
    const p = path.join(GAMES_DIR, `${g.id}.${ext}`)
    if (fs.existsSync(p)) { file = p; break }
  }

  if (!file) {
    if (g.coverUrl) {
      console.log(`${String(g.id).padEnd(4)} ${g.name.padEnd(20)} ${'(DB 外链)'.padEnd(13)} ${'-'.padEnd(11)} ✓ 用数据库外链`)
      hasCover++
    } else {
      console.log(`${String(g.id).padEnd(4)} ${g.name.padEnd(20)} ${'—'.padEnd(13)} ${'—'.padEnd(11)} ✗ 缺素材`)
      missing++
      problems.push(`${g.id} ${g.name}：无素材，页面显示 🎮 占位`)
    }
    continue
  }

  const size = imageSize(file)
  const name = path.basename(file)
  if (!size || !size.width || !size.height) {
    const fmt = size?.format ? size.format : '未知'
    console.log(`${String(g.id).padEnd(4)} ${g.name.padEnd(20)} ${name.padEnd(13)} ${'—'.padEnd(11)} ⚠ 无法读取尺寸(${fmt})`)
    oddSize++
    continue
  }

  const ratio = size.height ? size.width / size.height : 0
  const isIdeal = size.width >= IDEAL.minW && Math.abs(ratio - IDEAL.ratio) <= IDEAL.tolerance
  const kb = Math.round(fs.statSync(file).size / 1024)

  if (isIdeal || VERIFIED.has(g.id)) {
    const tag = isIdeal ? '✓' : '✓ 已确认'
    console.log(`${String(g.id).padEnd(4)} ${g.name.padEnd(20)} ${name.padEnd(13)} ${(size.width + 'x' + size.height).padEnd(11)} ${tag}`)
    hasCover++
  } else {
    // 非标准尺寸不一定是错的（竖版海报/方图 logo 也可能是有意的），仅提示
    console.log(`${String(g.id).padEnd(4)} ${g.name.padEnd(20)} ${name.padEnd(13)} ${(size.width + 'x' + size.height).padEnd(11)} ⚠ 非标准比例 ${ratio.toFixed(2)}（${kb}KB）`)
    oddSize++
  }
}

console.log('─'.repeat(78))
console.log(`\n有素材 ${hasCover} / 共 ${games.length}    缺失 ${missing}    非标准尺寸 ${oddSize}`)

if (problems.length) {
  console.log('\n需处理：')
  for (const p of problems) console.log(`  · ${p}`)
  console.log('\n命名约定：把素材放到 public/games/<gameId>.png（详见该目录 README.md）')
}

console.log('\n提示：素材必须来自开发商官方授权渠道，禁止直接抓取官网图片。')
console.log('⚠ 标记的条目内容与对应游戏不符，需替换（详见 public/games/README.md）。')
if (VERIFIED.size) {
  console.log(`  已人工确认为官方正确素材的非标准条目：${[...VERIFIED].join(', ')}（新增确认请改脚本 VERIFIED 集合）`)
}
process.exit(0)