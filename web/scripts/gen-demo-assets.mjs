// scripts/gen-demo-assets.mjs — 產生「明天 demo 用」的角色素材包。
//
// 為什麼：模擬器沒上傳圖時畫的是預設紅色方塊小寵物（renderer.pet，主色 #F0405A）。
// demo 時要讓觀眾一眼看出「換了素材」，所以這裡生成一隻**完全不同**的吉祥物——
// 薄荷綠「圓形」身體 + 頭頂金色星星 + 大眼睛腮紅（色系/形狀都與預設區隔）。
//
// 輸出：holo-art-demo.json（格式＝ store.importJSON 吃的 { key: [{name,dataUrl}] }）。
// 圖用 SVG dataURL（瀏覽器原生支援、檔案極小、透明背景能漂亮疊在房間背景上）。
// 用法：在模擬器底部按「載入 / Load」選這個 json 檔即可。
//
//   node scripts/gen-demo-assets.mjs
//
import { writeFileSync, mkdirSync, rmSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import sharp from 'sharp'

const __dirname = dirname(fileURLToPath(import.meta.url))

// 各 sprite 的原生輸出尺寸（與 data/manifest.ts 對齊）：
//   背景 320×240、食物 95×95、其餘（角色/蛋/結局/情緒）150×150。
function sizeOf(key) {
  if (key.startsWith('bg_')) return [320, 240]
  if (key.startsWith('food_')) return [95, 95]
  return [150, 150]
}

// ── 吉祥物色票（刻意避開預設紅 #F0405A）──────────────────────────────
const P = {
  body: '#3FD8C9', bodyDark: '#22B6A8', belly: '#E4FCF7',
  outline: '#0F3D43', star: '#FFD24A', starDark: '#F0A93A',
  cheek: '#FF8FB6', pupil: '#143438', white: '#FFFFFF',
}

const round = (n) => Math.round(n * 100) / 100

// 五角星 path
function starPath(cx, cy, outer, inner, rotDeg = 0) {
  const pts = []
  for (let i = 0; i < 10; i++) {
    const r = i % 2 === 0 ? outer : inner
    const a = ((-90 + rotDeg + i * 36) * Math.PI) / 180
    pts.push(`${round(cx + r * Math.cos(a))},${round(cy + r * Math.sin(a))}`)
  }
  return `M${pts.join('L')}Z`
}

// 心形 path（給摸頭/開心用）
function heartPath(cx, cy, s) {
  return `M${cx},${round(cy + s * 0.3)} C${round(cx - s)},${round(cy - s * 0.5)} ${round(cx - s * 0.5)},${round(cy - s)} ${cx},${round(cy - s * 0.35)} C${round(cx + s * 0.5)},${round(cy - s)} ${round(cx + s)},${round(cy - s * 0.5)} ${cx},${round(cy + s * 0.3)}Z`
}

// ── 臉部零件 ─────────────────────────────────────────────────────────
function eyesOpen(lx, rx, y, look = 0) {
  const eye = (x) => `
    <circle cx="${x}" cy="${y}" r="12.5" fill="${P.white}" stroke="${P.outline}" stroke-width="2"/>
    <circle cx="${round(x + look)}" cy="${round(y + 1)}" r="7" fill="${P.pupil}"/>
    <circle cx="${round(x + look - 2)}" cy="${y - 2}" r="2.6" fill="${P.white}"/>`
  return eye(lx) + eye(rx)
}
function eyesHappy(lx, rx, y) {
  const arc = (x) => `<path d="M${x - 9},${y + 3} Q${x},${y - 8} ${x + 9},${y + 3}" fill="none" stroke="${P.pupil}" stroke-width="3.5" stroke-linecap="round"/>`
  return arc(lx) + arc(rx)
}
function eyesSleep(lx, rx, y) {
  const arc = (x) => `<path d="M${x - 9},${y - 1} Q${x},${y + 6} ${x + 9},${y - 1}" fill="none" stroke="${P.pupil}" stroke-width="3.5" stroke-linecap="round"/>`
  return arc(lx) + arc(rx)
}
function eyesStar(lx, rx, y) {
  const s = (x) => `<path d="${starPath(x, y, 11, 4.6)}" fill="${P.star}" stroke="${P.starDark}" stroke-width="1.5"/>`
  return s(lx) + s(rx)
}
function eyesSad(lx, rx, y) {
  return eyesOpen(lx, rx, y, 0) +
    `<path d="M${lx + 11},${y + 9} q3,7 -1,12 q-4,-5 1,-12Z" fill="#7FD4FF"/>`
}

function mouth(type, cx, y) {
  switch (type) {
    case 'smile': return `<path d="M${cx - 11},${y} Q${cx},${y + 11} ${cx + 11},${y}" fill="none" stroke="${P.pupil}" stroke-width="3" stroke-linecap="round"/>`
    case 'grin': return `<path d="M${cx - 13},${y - 1} Q${cx},${y + 15} ${cx + 13},${y - 1} Q${cx},${y + 5} ${cx - 13},${y - 1}Z" fill="${P.pupil}"/><path d="M${cx - 7},${y + 5} Q${cx},${y + 11} ${cx + 7},${y + 5} Q${cx},${y + 3} ${cx - 7},${y + 5}Z" fill="${P.cheek}"/>`
    case 'open': return `<ellipse cx="${cx}" cy="${y + 4}" rx="9" ry="12" fill="${P.pupil}"/><ellipse cx="${cx}" cy="${y + 9}" rx="5" ry="5" fill="${P.cheek}"/>`
    case 'o': return `<circle cx="${cx}" cy="${y + 2}" r="6" fill="${P.pupil}"/>`
    case 'frown': return `<path d="M${cx - 10},${y + 7} Q${cx},${y - 4} ${cx + 10},${y + 7}" fill="none" stroke="${P.pupil}" stroke-width="3" stroke-linecap="round"/>`
    case 'wavy': return `<path d="M${cx - 11},${y + 2} q5,-6 5.5,0 q0.5,6 5.5,0 q5,-6 5.5,0" fill="none" stroke="${P.pupil}" stroke-width="2.6" stroke-linecap="round"/>`
    default: return `<path d="M${cx - 8},${y} L${cx + 8},${y}" stroke="${P.pupil}" stroke-width="3" stroke-linecap="round"/>`
  }
}

// ── 身體（150×150 統一畫布；透明背景）────────────────────────────────
// opts: eyes, mouth, arms('side'|'up'|'wave'|'tuck'), dy, tone(亮度), extra(前景), behind(背景)
function mascot(opts = {}) {
  const { eyes = 'open', mouthType = 'smile', arms = 'side', dy = 0, blush = true, extra = '', behind = '', tone = 1, star = true } = opts
  const cx = 75
  const cy = 86 + dy
  const body = tone < 1 ? '#6FB7B0' : P.body
  const bodyDark = tone < 1 ? '#4E938C' : P.bodyDark
  const lx = cx - 18, rx = cx + 18, ey = cy - 4

  let eyeSvg = ''
  if (eyes === 'happy') eyeSvg = eyesHappy(lx, rx, ey)
  else if (eyes === 'sleep') eyeSvg = eyesSleep(lx, rx, ey)
  else if (eyes === 'star') eyeSvg = eyesStar(lx, rx, ey)
  else if (eyes === 'sad') eyeSvg = eyesSad(lx, rx, ey)
  else eyeSvg = eyesOpen(lx, rx, ey, eyes === 'left' ? -2 : 0)

  // 手臂
  let armSvg = ''
  const armBlob = (x, y, rot) => `<g transform="rotate(${rot} ${x} ${y})"><ellipse cx="${x}" cy="${y}" rx="9" ry="13" fill="${body}" stroke="${P.outline}" stroke-width="2.5"/></g>`
  if (arms === 'up') armSvg = armBlob(cx - 42, cy - 30, -35) + armBlob(cx + 42, cy - 30, 35)
  else if (arms === 'wave') armSvg = armBlob(cx - 42, cy + 6, 20) + armBlob(cx + 44, cy - 28, 40)
  else if (arms === 'tuck') armSvg = armBlob(cx - 40, cy + 10, -10) + armBlob(cx + 40, cy + 10, 10)
  else armSvg = armBlob(cx - 41, cy + 8, -18) + armBlob(cx + 41, cy + 8, 18)

  const starSvg = star ? `<path d="${starPath(cx, cy - 52, 14, 6)}" fill="${P.star}" stroke="${P.starDark}" stroke-width="2"/>` : ''

  return wrap(150, 150, `
    ${behind}
    <!-- 腳 -->
    <ellipse cx="${cx - 18}" cy="${cy + 44}" rx="12" ry="8" fill="${bodyDark}" stroke="${P.outline}" stroke-width="2"/>
    <ellipse cx="${cx + 18}" cy="${cy + 44}" rx="12" ry="8" fill="${bodyDark}" stroke="${P.outline}" stroke-width="2"/>
    ${armSvg}
    <!-- 身體 -->
    <ellipse cx="${cx}" cy="${cy}" rx="45" ry="43" fill="${body}" stroke="${P.outline}" stroke-width="3"/>
    <ellipse cx="${cx}" cy="${cy + 10}" rx="30" ry="26" fill="${P.belly}" opacity="0.85"/>
    <ellipse cx="${cx - 16}" cy="${cy - 16}" rx="14" ry="10" fill="${P.white}" opacity="0.4"/>
    ${starSvg}
    ${eyeSvg}
    ${blush ? `<ellipse cx="${cx - 30}" cy="${cy + 8}" rx="8" ry="5.5" fill="${P.cheek}" opacity="0.8"/><ellipse cx="${cx + 30}" cy="${cy + 8}" rx="8" ry="5.5" fill="${P.cheek}" opacity="0.8"/>` : ''}
    ${mouth(mouthType, cx, cy + 14)}
    ${extra}
  `)
}

function wrap(w, h, inner) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${inner}</svg>`
}

// 小裝飾
const sparkle = (x, y, s) => `<path d="${starPath(x, y, s, s * 0.4)}" fill="${P.star}"/>`
const zzz = (x, y) => `<text x="${x}" y="${y}" font-family="Arial" font-weight="bold" font-size="16" fill="${P.white}">z</text><text x="${x + 12}" y="${y - 12}" font-family="Arial" font-weight="bold" font-size="20" fill="${P.white}">Z</text>`
const note = (x, y) => `<text x="${x}" y="${y}" font-family="Arial" font-size="22" fill="${P.star}">♪</text>`

// ── 每個動作的幀 ────────────────────────────────────────────────────
function frames() {
  const out = {}

  // idle：眨眼 + 上下呼吸（3 幀）
  out.idle = [
    mascot({ eyes: 'open', mouthType: 'smile', dy: 0 }),
    mascot({ eyes: 'open', mouthType: 'smile', dy: -3, extra: note(118, 40) }),
    mascot({ eyes: 'happy', mouthType: 'smile', dy: 0 }),
  ]

  // yawn：張嘴打哈欠 + 舉手 → 想睡（2 幀）
  out.yawn = [
    mascot({ eyes: 'sleep', mouthType: 'open', arms: 'up', blush: false, extra: `<text x="104" y="34" font-family="Arial" font-size="15" fill="${P.outline}">...</text>` }),
    mascot({ eyes: 'sleep', mouthType: 'o', arms: 'tuck', blush: false }),
  ]

  // cheer：舉手 + 火花 + 音符（2 幀）
  out.cheer = [
    mascot({ eyes: 'star', mouthType: 'grin', arms: 'up', extra: sparkle(28, 40, 8) + sparkle(122, 36, 7) + note(110, 70) }),
    mascot({ eyes: 'happy', mouthType: 'grin', arms: 'wave', dy: -3, extra: sparkle(120, 44, 9) + sparkle(30, 60, 6) }),
  ]

  // pet：開心臉紅 + 愛心（2 幀）
  out.pet = [
    mascot({ eyes: 'happy', mouthType: 'smile', extra: `<path d="${heartPath(120, 40, 11)}" fill="${P.cheek}"/><path d="${heartPath(30, 50, 8)}" fill="${P.cheek}"/>` }),
    mascot({ eyes: 'happy', mouthType: 'grin', dy: -2, extra: `<path d="${heartPath(118, 30, 13)}" fill="${P.cheek}"/><path d="${heartPath(32, 42, 9)}" fill="${P.cheek}"/>` }),
  ]

  // eat：鼓腮咀嚼（2 幀；食物由 renderer 另外疊上）。拿叉子。
  const fork = `<g transform="rotate(20 118 96)"><rect x="116" y="78" width="3.5" height="30" rx="1.5" fill="${P.starDark}"/><rect x="112.5" y="74" width="3" height="9" fill="${P.starDark}"/><rect x="116" y="74" width="3" height="9" fill="${P.starDark}"/><rect x="119.5" y="74" width="3" height="9" fill="${P.starDark}"/></g>`
  out.eat = [
    mascot({ eyes: 'happy', mouthType: 'o', extra: fork, blush: true }),
    mascot({ eyes: 'open', mouthType: 'smile', dy: 1, extra: fork }),
  ]

  // sleep：閉眼 + 蓋被子 + Zzz（2 幀呼吸）
  const blanket = (dy) => `<path d="M22,${118 + dy} Q75,${104 + dy} 128,${118 + dy} L128,150 L22,150 Z" fill="#7AA8E0" stroke="${P.outline}" stroke-width="2.5"/><path d="M22,${118 + dy} Q75,${104 + dy} 128,${118 + dy}" fill="none" stroke="#A9C8F0" stroke-width="3"/>`
  out.sleep = [
    mascot({ eyes: 'sleep', mouthType: 'o', blush: true, dy: 0, star: false, extra: blanket(0) + zzz(108, 44) }),
    mascot({ eyes: 'sleep', mouthType: 'o', blush: true, dy: 2, star: false, extra: blanket(2) + zzz(110, 50) }),
  ]

  // egg：破殼放大（renderer 會再縮放）。4 幀：完整 → 裂 → 大裂 → 孵出。
  const eggBase = (cracks, hatch) => wrap(150, 150, `
    ${hatch ? '' : ''}
    <ellipse cx="75" cy="84" rx="40" ry="50" fill="#CFF3EE" stroke="${P.outline}" stroke-width="3"/>
    <ellipse cx="75" cy="84" rx="40" ry="50" fill="url(#eg)"/>
    <defs><radialGradient id="eg" cx="38%" cy="32%"><stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.6"/><stop offset="70%" stop-color="#3FD8C9" stop-opacity="0"/></radialGradient></defs>
    <circle cx="60" cy="62" r="4" fill="${P.star}" opacity="0.8"/>
    <circle cx="92" cy="100" r="5" fill="${P.cheek}" opacity="0.7"/>
    <circle cx="84" cy="56" r="3.5" fill="${P.star}" opacity="0.7"/>
    ${cracks}
    ${hatch ? `<path d="${starPath(75, 50, 12, 5)}" fill="${P.star}" stroke="${P.starDark}" stroke-width="1.5"/>${eyesHappy(64, 86, 78)}${mouth('smile', 75, 92)}${sparkle(36, 60, 7)}${sparkle(116, 70, 7)}` : ''}
  `)
  out.egg = [
    eggBase('', false),
    eggBase(`<path d="M62,50 l8,12 -6,10 9,8" fill="none" stroke="${P.outline}" stroke-width="2.5"/>`, false),
    eggBase(`<path d="M50,60 l10,10 -7,11 11,9 -6,12" fill="none" stroke="${P.outline}" stroke-width="2.5"/><path d="M98,66 l-8,12 7,9" fill="none" stroke="${P.outline}" stroke-width="2.5"/>`, false),
    eggBase(`<path d="M40,96 l12,-9 9,9 12,-9 10,9 12,-8" fill="none" stroke="${P.outline}" stroke-width="2.5"/>`, true),
  ]

  // ── 結局圖（單幀，各有道具）──────────────────────────────────
  // idol：麥克風 + 耳機 + 舞台火花
  out.end_idol = [mascot({
    eyes: 'star', mouthType: 'grin', arms: 'wave', tone: 1,
    behind: sparkle(24, 30, 10) + sparkle(126, 36, 9) + sparkle(20, 90, 7) + sparkle(132, 96, 8),
    extra: `<g transform="rotate(18 118 96)"><circle cx="118" cy="74" r="8" fill="#C0C0C8" stroke="${P.outline}" stroke-width="2"/><rect x="116" y="80" width="4" height="26" rx="2" fill="${P.outline}"/></g>` +
      `<path d="M44,${86 - 4 - 22} a31,31 0 0 1 62,0" fill="none" stroke="${P.cheek}" stroke-width="4"/><circle cx="44" cy="60" r="6" fill="${P.cheek}"/><circle cx="106" cy="60" r="6" fill="${P.cheek}"/>`,
  })]

  // office：眼鏡 + 領帶 + 咖啡（略累）
  out.end_office = [mascot({
    eyes: 'open', mouthType: 'default', tone: 0.8, star: false, blush: false,
    extra: `<g stroke="${P.outline}" stroke-width="2.5" fill="none"><circle cx="57" cy="82" r="13"/><circle cx="93" cy="82" r="13"/><path d="M70,82 h10"/></g>` +
      `<path d="M75,108 l-7,22 7,6 7,-6 Z" fill="#C0443A" stroke="${P.outline}" stroke-width="2"/><path d="M75,100 l-6,8 6,5 6,-5 Z" fill="#C0443A" stroke="${P.outline}" stroke-width="2"/>` +
      `<g transform="translate(112 96)"><rect x="0" y="0" width="16" height="14" rx="2" fill="#F0F0F0" stroke="${P.outline}" stroke-width="2"/><path d="M16,3 q6,4 0,9" fill="none" stroke="${P.outline}" stroke-width="2"/><path d="M3,-3 q2,-5 5,0 M9,-3 q2,-5 5,0" fill="none" stroke="#BBB" stroke-width="2"/></g>`,
  })]

  // pirate：海賊帽 + 眼罩 + 彎刀
  out.end_pirate = [mascot({
    eyes: 'left', mouthType: 'grin', arms: 'wave', star: false,
    extra: `<path d="M40,42 q35,-30 70,0 q-35,12 -70,0Z" fill="#2A2A30" stroke="${P.outline}" stroke-width="2.5"/><path d="${starPath(75, 36, 10, 4.5)}" fill="${P.white}"/>` +
      `<g stroke="${P.outline}" stroke-width="2.5"><rect x="48" y="74" width="20" height="14" rx="3" fill="#1A1A1E"/><path d="M58,74 q26,-6 30,8" fill="none"/></g>` +
      `<g transform="rotate(25 116 92)"><path d="M116,68 q14,18 0,40" fill="none" stroke="#D8D8E0" stroke-width="5" stroke-linecap="round"/><rect x="112" y="104" width="9" height="6" rx="2" fill="${P.starDark}"/></g>`,
  })]

  // runaway：暗色 + 包袱 + 眼淚 + 雨（壞結局）
  out.end_runaway = [mascot({
    eyes: 'sad', mouthType: 'frown', tone: 0.6, star: false, blush: false, arms: 'tuck',
    behind: `<g stroke="#5C7A8C" stroke-width="2" stroke-linecap="round">${[28, 52, 96, 120].map((x, i) => `<path d="M${x},${10 + i * 4} l-5,14"/>`).join('')}</g>`,
    extra: `<g transform="rotate(-30 118 70)"><rect x="116" y="40" width="3" height="46" fill="#6B5234"/><circle cx="118" cy="36" r="13" fill="#C9A45E" stroke="${P.outline}" stroke-width="2"/><path d="M108,30 l20,0 M118,24 l0,22" stroke="#9A7A40" stroke-width="2"/></g>`,
  })]

  // ── 摸頭結算情緒圖 ──────────────────────────────────────────
  out.emo_success = [mascot({
    eyes: 'star', mouthType: 'grin', arms: 'up',
    behind: sparkle(22, 28, 11) + sparkle(128, 34, 10) + sparkle(18, 84, 7) + sparkle(134, 92, 8),
    extra: `<path d="${heartPath(116, 36, 12)}" fill="${P.cheek}"/><path d="${heartPath(34, 44, 10)}" fill="${P.cheek}"/>` + note(100, 30),
  })]
  out.emo_fail = [mascot({
    eyes: 'sad', mouthType: 'wavy', tone: 0.8, star: false, blush: false, arms: 'tuck',
    behind: `<g stroke="#7FB0D0" stroke-width="2" stroke-linecap="round" opacity="0.7">${[40, 75, 110].map((x) => `<path d="M${x},14 l-4,12"/>`).join('')}</g>`,
    extra: `<path d="M90,72 q3,9 -1,15 q-4,-6 1,-15Z" fill="#7FD4FF"/>`,
  })]

  // ── 食物（95×95，跟預設食物色塊不同）──────────────────────────
  out.food_0 = [foodCake()]
  out.food_1 = [foodPudding()]
  out.food_2 = [foodTart()]
  out.food_3 = [foodSoda()]
  out.food_4 = [foodParfait()]

  // ── 背景（320×240）──────────────────────────────────────────
  out.bg_room = [bgRoom()]
  out.bg_game = [bgGame()]

  return out
}

// ── 食物 95×95 ───────────────────────────────────────────────────────
function foodCake() {
  return wrap(95, 95, `
    <ellipse cx="47" cy="86" rx="30" ry="6" fill="#000" opacity="0.12"/>
    <path d="M20,46 L74,46 L66,82 Q47,88 28,82 Z" fill="#FFE6B0" stroke="#7A5A2A" stroke-width="2"/>
    <path d="M20,46 Q47,38 74,46 L74,54 Q47,46 20,54 Z" fill="#FF9CC0" stroke="#7A5A2A" stroke-width="2"/>
    <path d="M20,46 L74,46" stroke="#E07AA0" stroke-width="2"/>
    <rect x="32" y="58" width="30" height="6" rx="3" fill="#C0443A"/>
    <circle cx="47" cy="30" r="8" fill="#F0403A" stroke="#7A2A2A" stroke-width="2"/>
    <path d="M47,22 q4,-8 9,-9" fill="none" stroke="#4A8A30" stroke-width="2.5"/>
  `)
}
function foodPudding() {
  return wrap(95, 95, `
    <ellipse cx="47" cy="86" rx="30" ry="6" fill="#000" opacity="0.12"/>
    <path d="M26,40 L68,40 L62,80 Q47,86 32,80 Z" fill="#FFD98A" stroke="#A06A2A" stroke-width="2.5"/>
    <path d="M26,40 Q47,30 68,40 Q47,50 26,40Z" fill="#B5712E" stroke="#7A4A1A" stroke-width="2"/>
    <path d="M40,33 q7,-6 14,0" fill="none" stroke="#7A4A1A" stroke-width="2" opacity="0.6"/>
    <ellipse cx="47" cy="22" rx="9" ry="7" fill="#FFF6E0" opacity="0.9"/>
    <circle cx="47" cy="20" r="4" fill="#F0403A"/>
  `)
}
function foodTart() {
  return wrap(95, 95, `
    <ellipse cx="47" cy="84" rx="30" ry="6" fill="#000" opacity="0.12"/>
    <path d="M20,52 Q47,44 74,52 L70,68 Q47,78 24,68 Z" fill="#E0A860" stroke="#8A5A2A" stroke-width="2.5"/>
    <path d="M22,56 q25,-8 50,0" fill="none" stroke="#FFE0B0" stroke-width="6"/>
    <circle cx="36" cy="54" r="6" fill="#7A3AB0"/><circle cx="50" cy="51" r="6" fill="#C03A5A"/>
    <circle cx="62" cy="55" r="6" fill="#7A3AB0"/><circle cx="44" cy="58" r="5" fill="#3A6AC0"/>
    <circle cx="58" cy="60" r="5" fill="#C03A5A"/>
    <path d="M34,46 q3,-5 5,0" fill="none" stroke="#FFF" stroke-width="1.5" opacity="0.7"/>
  `)
}
function foodSoda() {
  return wrap(95, 95, `
    <ellipse cx="47" cy="88" rx="22" ry="5" fill="#000" opacity="0.12"/>
    <path d="M30,32 L64,32 L60,84 Q47,90 34,84 Z" fill="#BFEFFF" stroke="#3A8AB0" stroke-width="2.5" opacity="0.9"/>
    <path d="M32,52 L62,52 L59,82 Q47,87 35,82 Z" fill="#48C5F4"/>
    <rect x="52" y="14" width="5" height="40" rx="2.5" fill="#F0506A" transform="rotate(12 54 34)"/>
    <circle cx="42" cy="60" r="3.5" fill="#FFF" opacity="0.8"/>
    <circle cx="52" cy="68" r="2.6" fill="#FFF" opacity="0.8"/>
    <circle cx="46" cy="74" r="2" fill="#FFF" opacity="0.8"/>
    <circle cx="40" cy="40" r="6" fill="#FFF" stroke="#C0443A" stroke-width="0" opacity="0.85"/>
  `)
}
function foodParfait() {
  return wrap(95, 95, `
    <ellipse cx="47" cy="88" rx="20" ry="5" fill="#000" opacity="0.12"/>
    <path d="M32,40 L62,40 L57,80 Q47,86 37,80 Z" fill="#EAF7FF" stroke="#9AB8C8" stroke-width="2" opacity="0.55"/>
    <path d="M33,58 L61,58 L57,78 Q47,84 37,78 Z" fill="#C0443A"/>
    <path d="M33,50 L61,50 L60,60 L34,60 Z" fill="#FFE08A"/>
    <path d="M34,42 L60,42 L61,52 L33,52 Z" fill="#9C5ABF"/>
    <path d="M34,40 Q47,24 60,40 Q47,34 34,40Z" fill="#FFF6FB" stroke="#E0B0C8" stroke-width="1.5"/>
    <path d="M40,30 q7,-7 14,0" fill="none" stroke="#FFF" stroke-width="3"/>
    <circle cx="47" cy="24" r="5" fill="#F0403A"/><path d="M47,19 l2,-6" stroke="#4A8A30" stroke-width="2"/>
    <rect x="58" y="16" width="4" height="30" rx="2" fill="#FFD24A" transform="rotate(18 60 30)"/>
  `)
}

// ── 背景 320×240 ─────────────────────────────────────────────────────
function bgRoom() {
  return wrap(320, 240, `
    <rect width="320" height="240" fill="#FFE3EC"/>
    <rect y="150" width="320" height="90" fill="#F3C9A0"/>
    <path d="M0,150 L320,150" stroke="#D8A878" stroke-width="3"/>
    <g opacity="0.5" stroke="#E0B488" stroke-width="2">
      <path d="M40,150 L0,210"/><path d="M110,150 L70,240"/><path d="M190,150 L180,240"/><path d="M260,150 L300,240"/>
    </g>
    <!-- 窗 -->
    <rect x="30" y="34" width="96" height="78" rx="6" fill="#BFE8FF" stroke="#FFF" stroke-width="6"/>
    <circle cx="62" cy="60" r="12" fill="#FFE9A0"/>
    <path d="M30,90 q24,-16 48,0 q24,16 48,0 L126,112 L30,112Z" fill="#9FD8F5" opacity="0.7"/>
    <path d="M78,34 L78,112 M30,73 L126,73" stroke="#FFF" stroke-width="4"/>
    <!-- 掛畫（星星） -->
    <rect x="210" y="40" width="66" height="56" rx="5" fill="#FFF7DF" stroke="#E0C088" stroke-width="4"/>
    <path d="${starPath(243, 68, 18, 8)}" fill="#FFD24A" stroke="#F0A93A" stroke-width="2"/>
    <!-- 地毯 -->
    <ellipse cx="170" cy="196" rx="92" ry="26" fill="#9FE6DC" opacity="0.8"/>
    <ellipse cx="170" cy="196" rx="70" ry="18" fill="#7FD8CC" opacity="0.7"/>
    <!-- 盆栽 -->
    <rect x="284" y="120" width="26" height="26" rx="4" fill="#C97A4A"/>
    <path d="M297,120 q-14,-22 -6,-34 q10,8 6,34 q14,-20 16,-8 q-2,14 -16,8Z" fill="#5FB87A"/>
  `)
}
function bgGame() {
  return wrap(320, 240, `
    <rect width="320" height="240" fill="#15183A"/>
    <rect y="0" width="320" height="120" fill="url(#sky)"/>
    <defs>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2A1E55"/><stop offset="100%" stop-color="#15183A"/></linearGradient>
      <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#3A2E6A"/><stop offset="100%" stop-color="#1C1838"/></linearGradient>
    </defs>
    <!-- 聚光燈 -->
    <path d="M60,0 L20,150 L150,150 Z" fill="#FFD24A" opacity="0.18"/>
    <path d="M260,0 L300,150 L170,150 Z" fill="#48C5F4" opacity="0.18"/>
    <path d="M160,0 L120,150 L210,150 Z" fill="#FF8FB6" opacity="0.16"/>
    <!-- 舞台地板 -->
    <rect y="150" width="320" height="90" fill="url(#floor)"/>
    <g stroke="#5A4A9A" stroke-width="1.5" opacity="0.6">
      <path d="M0,150 L160,240 M320,150 L160,240 M60,150 L120,240 M260,150 L200,240 M160,150 L160,240"/>
      <path d="M0,180 L320,180 M0,210 L320,210"/>
    </g>
    <!-- 星星燈光 -->
    ${[ [40, 30], [120, 20], [200, 28], [280, 22], [70, 70], [250, 64] ].map(([x, y], i) => `<path d="${starPath(x, y, i % 2 ? 6 : 8, 3)}" fill="${i % 2 ? '#48C5F4' : '#FFD24A'}" opacity="0.9"/>`).join('')}
    <!-- LIVE 燈牌 -->
    <rect x="118" y="44" width="84" height="30" rx="8" fill="#0E1030" stroke="#FF8FB6" stroke-width="3"/>
    <text x="160" y="66" text-anchor="middle" font-family="Arial" font-weight="bold" font-size="20" fill="#FF8FB6">LIVE</text>
  `)
}

// ── 點陣化 + 打包輸出 ───────────────────────────────────────────────
// 每幀：SVG → PNG（依原生尺寸、保留透明背景）。
//   1) 寫成 PNG 檔到 web/demo-assets/<key>_NN.png（可直接看 / 上裝置）。
//   2) 同時收成 dataURL 打包成 holo-art-demo.json（模擬器「載入」一鍵吃）。
async function svgToPng(svg, w, h) {
  return sharp(Buffer.from(svg, 'utf8'), { density: 384 })
    .resize(w, h, { fit: 'fill' })
    .png({ compressionLevel: 9 })
    .toBuffer()
}

const f = frames()
const outDir = join(__dirname, '..', 'demo-assets')
rmSync(outDir, { recursive: true, force: true })
mkdirSync(outDir, { recursive: true })

const json = {}
let nFrames = 0
for (const [key, svgs] of Object.entries(f)) {
  const [w, h] = sizeOf(key)
  json[key] = []
  for (let i = 0; i < svgs.length; i++) {
    const name = `${key}_${String(i).padStart(2, '0')}.png`
    const png = await svgToPng(svgs[i], w, h)
    writeFileSync(join(outDir, name), png)
    json[key].push({ name, dataUrl: 'data:image/png;base64,' + png.toString('base64') })
    nFrames++
  }
}

const jsonPath = join(__dirname, '..', 'holo-art-demo.json')
writeFileSync(jsonPath, JSON.stringify(json))

console.log(`✅ ${Object.keys(json).length} 個 key、${nFrames} 張 PNG → ${outDir}`)
console.log(`   一鍵載入檔 → ${jsonPath}（${(JSON.stringify(json).length / 1024).toFixed(0)}KB）`)
