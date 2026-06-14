// utils/animations.ts — 每個「動作」的逐幀繪製腳本。
//
// 一個 ACTION = 裝置端某個 state 的動畫。render(r, opts) 會在第 r.frame 幀，
// 把該畫面畫到 320×240。邏輯逐一對照 device/states/*.py，盡量 1:1 重現，
// 讓美術看到的播放（位置 / 縮放 / 點頭 / 呼吸 / 咬食 / 手擺動）跟真機一致。
//
// 對照表：
//   egg     → states/init_state.py
//   idle    → states/normal_room.py（待機）
//   yawn    → states/normal_room.py（哈欠事件 EVENT_FRAMES=24）
//   cheer   → states/normal_room.py（加油事件 CHEER_FRAMES=60 + 對話泡泡）
//   eat     → states/feeding.py（4 口 × 9 幀 + 6 收尾）
//   sleep   → states/sleeping.py（2 幀呼吸輪播 + ±2px）
//   pet     → states/petting.py（摸頭手左右擺 + 開心反應 + 愛心 + 親密度條）
//   ending  → states/ending.py
//   result  → states/petting.py _result_screen（音遊結算）

import type { Renderer } from './renderer'
import { C, THEME, FOODS, ENDINGS, GRADES, PET_SUCCESS_STROKES } from '~/data/manifest'

export interface ActionOpts {
  food?: string // eat：選哪種甜點
  ending?: string // ending：哪個結局 id
  grade?: string // result：哪個評級 id
}

export interface ActionDef {
  id: string
  label: string
  group: string
  frames: number // 一輪幾幀
  loop: boolean
  note?: string // 提示文字
  sprites: string[] // 這個動作會用到的 sprite key（給「相關素材」面板）
  picker?: 'food' | 'ending' | 'grade'
  // 真機實測每幀耗時（ms）。裝置主迴圈固定步調 ~50ms，但「有背景」的畫面每幀要把整張
  // bg_room 寫進 PSRAM canvas + 整張 pushSprite，實測 ~70ms（~14fps）；只清色底的畫面
  // 工作 <50ms、被幀率對齊補到 50ms（20fps）。未填 = 50ms。模擬器照這個播 → 與真機同速。
  deviceFrameMs?: number
  render: (r: Renderer, opts: ActionOpts) => void
}

// === 角色位置常數（與各 state 對齊）。所有角色統一 150×150 畫布，只改擺位不改尺寸 ===
const ROOM = { x: 85, y: 38, w: 150, h: 150 } // normal_room / petting 共用角色框

// --- egg：init_state.py ---
const ANIM_FRAMES = 24
function renderEgg(r: Renderer) {
  const t = Math.min(r.frame, ANIM_FRAMES)
  r.clear(C.black)
  const frac = t / ANIM_FRAMES
  // 蛋維持正方形成長（90→150），最終填滿統一 150×150 畫布
  const w = Math.floor(90 + frac * 60)
  const h = w
  const cx = 160, cy = 120
  r.drawSprite('egg', cx - Math.floor(w / 2), cy - Math.floor(h / 2), w, h)
  if (!r.hasImage('egg')) {
    r.text(`[ANIM: Egg cracking ${Math.floor(frac * 100)}%]`, 70, 222, C.white, 11)
  }
}

// --- 普通房間共用：背景 + 底部 MENU 提示 ---
function room(r: Renderer) {
  r.drawSprite('bg_room', 0, 0, 320, 240)
}

// --- idle：normal_room 待機 ---
function renderIdle(r: Renderer) {
  room(r)
  r.drawSprite('idle', ROOM.x, ROOM.y, ROOM.w, ROOM.h)
  r.hints(null, null, 'MENU')
}

// --- yawn：哈欠事件（24 幀），之後回 idle ---
function renderYawn(r: Renderer) {
  room(r)
  const key = r.frame < ANIM_FRAMES ? 'yawn' : 'idle'
  r.drawSprite(key, ROOM.x, ROOM.y, ROOM.w, ROOM.h)
  r.hints(null, null, 'MENU')
}

// --- cheer：加油事件（60 幀）+ 對話泡泡，之後回 idle ---
const CHEER_FRAMES = 60
function renderCheer(r: Renderer) {
  room(r)
  const cheering = r.frame < CHEER_FRAMES
  r.drawSprite(cheering ? 'cheer' : 'idle', ROOM.x, ROOM.y, ROOM.w, ROOM.h)
  if (cheering) r.dialog('cheer_msg_01')
  r.hints(null, null, 'MENU')
}

// --- eat：feeding.py ---
const EAT = { x: 85, y: 34, w: 150, h: 150 }
const MOUTH = { x: 160, y: 124 } // EAT.x+75, EAT.y+150*3/5
const HOLD = { x: 160, y: 158 } // 嘴下方 34px
const FOOD_SIZE = 95
const BITES = 4
const BITE_FRAMES = 9
const END_PAD = 6
const EAT_FRAMES = BITES * BITE_FRAMES + END_PAD // 42
const CHEW_DIP = 8

// 對應 feeding._frame_state：回傳 [食物中心x, y, 邊長, 角色點頭位移]
function eatFrameState(t: number): [number, number, number, number] {
  const i = Math.floor((t - 1) / BITE_FRAMES)
  const local = (t - 1) % BITE_FRAMES
  const sizeAfter = Math.floor((FOOD_SIZE * (BITES - i - 1)) / BITES)
  const sizeBefore = Math.floor((FOOD_SIZE * (BITES - i)) / BITES)
  if (local === 0) return [HOLD.x, MOUTH.y, sizeBefore, CHEW_DIP]
  if (local === 1) return [HOLD.x, MOUTH.y, sizeAfter, CHEW_DIP]
  return [HOLD.x, HOLD.y, sizeAfter, local % 2 === 0 ? CHEW_DIP : 0]
}

function renderEat(r: Renderer, opts: ActionOpts) {
  const foodKey = opts.food || 'food_0'
  room(r)
  // t 從 1 開始（feeding 進到 eat 後 self.t 從 1 遞增到 EAT_FRAMES）
  const t = Math.min(r.frame + 1, EAT_FRAMES)
  const [cx, cy, size, cdy] = eatFrameState(t)
  // 角色（咀嚼時低頭 cdy）
  r.drawSprite('eat', EAT.x, EAT.y + cdy, EAT.w, EAT.h)
  if (size > 0) {
    r.drawSprite(foodKey, cx - Math.floor(size / 2), cy - Math.floor(size / 2), size, size, false)
  }
  if (!r.hasImage('eat')) r.text('Nom nom...', 130, 216, C.white, 11)
}

// --- sleep：sleeping.py ---
const SLEEP = { x: 85, y: 50, w: 150, h: 150 }
const SLEEP_BG = '#06141E' // Cover 夜間深海軍藍（與 device/states/sleeping.py 對齊）
function renderSleep(r: Renderer) {
  r.clear(SLEEP_BG)
  if (!r.hasImage('sleep')) r.text('Zzz...', 50, 36, C.white, 11)
  const frame = Math.floor(r.frame / 10) % 2 // 2 幀輪播
  r.drawSprite('sleep', SLEEP.x, SLEEP.y + frame * 2, SLEEP.w, SLEEP.h)
  // 假設 IMU 可用
  r.text('Shake or C: wake up', 8, 210, C.dark, 11)
}

// --- pet：petting.py（自動示範一段摸頭）---
const REACT_FRAMES = 6
const HAND = { y: 54, w: 44, h: 24, dx: 97 } // 角色填滿後，手改在頭左右兩側
const HEAD_CX = ROOM.x + Math.floor(ROOM.w / 2) // 160
const HEART = 20
const HEART_Y = 64
const HEART_X = [ROOM.x - 26, ROOM.x + ROOM.w + 6]
const STROKE_PERIOD = 11 // 模擬：每 11 幀來回摸一下
const PET_TARGET = PET_SUCCESS_STROKES // 親密度條滿格 = 成功門檻（與 device 對齊）
function renderPet(r: Renderer) {
  const showDeco = !r.hasImage('pet') // 無圖才畫手 / 愛心（has_image 邏輯）
  room(r)
  r.text('Pet the head!  A <-> C', 20, 14, C.white, 16)

  // 重建到目前幀的互動狀態（strokes / 方向 / 反應剩餘幀）。
  const f = r.frame
  const strokes = Math.floor(f / STROKE_PERIOD)
  const dir = strokes % 2 === 0 ? -1 : 1 // 左右交替
  const sinceStroke = f - strokes * STROKE_PERIOD
  const reacting = sinceStroke < REACT_FRAMES

  // 摸頭手（無圖才畫）：在頭頂左右
  if (showDeco) {
    const hx = HEAD_CX + dir * HAND.dx - Math.floor(HAND.w / 2)
    r.fillRoundRect(hx, HAND.y, HAND.w, HAND.h, 6, C.pink)
  }

  // 角色表情：反應中開心，否則待機
  r.drawSprite(reacting ? 'pet' : 'idle', ROOM.x, ROOM.y, ROOM.w, ROOM.h)

  // 愛心
  if (showDeco && reacting) {
    for (const hx of HEART_X) r.fillRoundRect(hx, HEART_Y, HEART, HEART, 4, C.red)
  }

  // 親密度條 / 時間條 / HUD
  const barW = 320 - 16
  r.fillRect(8, 190, barW, 12, C.dark)
  const fill = Math.floor(barW * Math.min(1, strokes / PET_TARGET))
  if (fill > 0) r.fillRect(8, 190, fill, 12, C.pink)
  const timeW = 320 - 40
  const tf = Math.floor((timeW * (160 - f)) / 160)
  r.fillRect(20, 30, timeW, 6, C.dark)
  if (tf > 0) r.fillRect(20, 30, tf, 6, C.green)
  r.fillRect(0, 212, 320, 24, THEME.bg)
  r.text(`Pets ${strokes}   Combo ${strokes}`, 8, 216, C.white, 16)
}

// --- ending：ending.py ---
function renderEnding(r: Renderer, opts: ActionOpts) {
  const e = ENDINGS.find((x) => x.id === (opts.ending || 'good')) || ENDINGS[0]
  r.clear(C.black)
  r.drawSprite(e.key, 85, 36) // 統一 150×150
  r.text('ENDING: ' + e.title, 30, 14, C.yellow, 22)
  r.text(`Rhythm rate: ${e.rate}%`, 100, 196, C.white, 11)
  r.text('Press any button to restart', 50, 210, C.white, 11)
}

// --- result：petting _result_screen（摸頭結算：成功 / 失敗）---
function renderResult(r: Renderer, opts: ActionOpts) {
  const g = GRADES.find((x) => x.id === (opts.grade || 'success')) || GRADES[0]
  const win = g.id === 'success'
  r.clear(C.black)
  r.drawSprite(g.emo, 85, 36) // 統一 150×150
  r.text(g.title, 95, 18, win ? C.yellow : C.red, 22)
  r.text(`Pets ${g.pets} / ${PET_SUCCESS_STROKES}`, 80, 190, C.white, 16)
  r.text(`Max combo ${g.pets}   B: back`, 70, 210, C.dark, 11)
}

// deviceFrameMs：有背景的畫面（idle/yawn/cheer/eat/pet）真機 ~70ms（~14fps）；
// 只清色底的（egg/sleep/ending/result）~50ms（20fps，未填即 50）。
export const ACTIONS: ActionDef[] = [
  { id: 'egg', label: '破殼 Egg', group: '生命週期', frames: ANIM_FRAMES + 1, loop: false, note: '開機 / 重置：蛋隨進度放大（24 幀 ≈ 1.2s）', sprites: ['egg'], render: renderEgg },
  { id: 'idle', label: '待機 Idle', group: '日常', frames: 40, loop: true, deviceFrameMs: 70, note: '主畫面待機。多幀素材會依「多幀速度」輪播', sprites: ['idle', 'bg_room'], render: renderIdle },
  { id: 'yawn', label: '打哈欠 Yawn', group: '日常', frames: 48, loop: true, deviceFrameMs: 70, note: '疲勞高時隨機觸發（24 幀）後回待機', sprites: ['yawn', 'idle', 'bg_room'], render: renderYawn },
  { id: 'cheer', label: '加油 Cheer', group: '日常', frames: 90, loop: true, deviceFrameMs: 70, note: '隨機觸發（60 幀）+ 對話泡泡，後回待機', sprites: ['cheer', 'idle', 'bg_room'], render: renderCheer },
  { id: 'eat', label: '餵食 Eat', group: '互動', frames: EAT_FRAMES, loop: false, deviceFrameMs: 70, note: '一口一口咬（4 口 × 9 幀 + 6 收尾）。真機 ~14fps 故實際 ~3s。可換甜點', sprites: ['eat', 'bg_room', 'food_0'], picker: 'food', render: renderEat },
  { id: 'sleep', label: '睡覺 Sleep', group: '日常', frames: 40, loop: true, note: '2 幀呼吸輪播（每 10 幀換 + 上下 2px）', sprites: ['sleep'], render: renderSleep },
  { id: 'pet', label: '摸頭 Pet', group: '互動', frames: 160, loop: true, deviceFrameMs: 70, note: '時間內摸滿親密度條＝成功，沒滿＝失敗。自動示範：手左右擺、開心 + 愛心', sprites: ['pet', 'idle', 'bg_room'], render: renderPet },
  { id: 'ending', label: '結局 Ending', group: '結局', frames: 40, loop: true, note: '4 種結局圖。可切換分支', sprites: ['end_good', 'end_normal', 'end_bad', 'end_runaway'], picker: 'ending', render: renderEnding },
  { id: 'result', label: '摸頭結算 Result', group: '結局', frames: 40, loop: true, note: '摸頭結算情緒圖（成功 / 失敗）。可切換', sprites: ['emo_success', 'emo_fail'], picker: 'grade', render: renderResult },
]
