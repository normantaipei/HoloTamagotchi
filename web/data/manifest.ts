// data/manifest.ts — 角色資源清單，逐一對應裝置端定義，不要憑空增減 key。
//
// 來源（保持同步）：
//   device/assets/characters/marine/character.py  → SPRITES / THEME
//   device/config.py                              → 通用色票
//
// 每個 key 的「佔位色塊規格 (color,label,w,h)」與裝置端一模一樣，
// 這樣沒上傳圖片時，模擬器顯示的佔位畫面會跟真機完全相同。

// --- 通用色票（device/config.py，0xRRGGBB → #RRGGBB）— Cover Corp 風格 ---
export const C = {
  white: '#FFFFFF',
  black: '#000000',
  dark: '#12303D',   // 冷調深板岩
  green: '#78E682',
  yellow: '#FFDC50',
  red: '#F05A5A',
  pink: '#48C5F4',   // 主互動 accent → Cover 亮天藍（沿用 pink 名）
  cyan: '#51CCE8',   // Cover 淺青
}

// --- 角色色彩主題（character.py THEME）---
export const THEME = {
  bg: '#2A1020', // 深紅房間底（assets.color("bg") 用這個清背景）
  primary: '#F0405A',
  accent: '#FFC857',
}

// 裝置螢幕尺寸（config.SCREEN_W/H）與幀率（FRAME_MS）。
export const SCREEN_W = 320
export const SCREEN_H = 240
export const FRAME_MS = 50 // 主迴圈每幀 50ms ≈ 20fps
export const FPS = 1000 / FRAME_MS

export interface SpriteSpec {
  key: string
  color: string // 佔位色塊顏色
  label: string // 佔位標籤（同時是「這格要放什麼圖」的說明）
  w: number
  h: number
  folder: string // 裝置端建議放置的子資料夾
  suggested: string // 建議檔名（device/assets/README.md）
  category: 'background' | 'anim' | 'ending' | 'emotion' | 'food'
  desc: string // 給美術看的中文說明
}

// 把 0xRRGGBB 數字轉成 css；這裡直接寫好十六進位，與 character.py 對齊。
// 【統一畫布】所有「角色」一律 150×150 正方形（與 device character.py 對齊）；
// 食物 95×95、背景 320×240 各自一套。裝置端貼圖不縮放，畫布大小＝上機顯示大小。
const CHAR_W = 150
const CHAR_H = 150
export const SPRITES: Record<string, SpriteSpec> = {
  // --- 背景 ---
  bg_room: { key: 'bg_room', color: '#2A1020', label: 'BG: Normal Room', w: 320, h: 240, folder: 'backgrounds', suggested: 'room.jpg', category: 'background', desc: '普通房間背景（待機 / 餵食 / 摸頭都在這）' },
  bg_game: { key: 'bg_game', color: '#0C1828', label: 'BG: Game Room', w: 320, h: 240, folder: 'backgrounds', suggested: 'game_room.jpg', category: 'background', desc: '遊戲房間背景（唱跳用）' },
  // --- 動作 / 待機（皆 150×150 統一畫布）---
  egg: { key: 'egg', color: '#F0E6C8', label: 'Egg', w: CHAR_W, h: CHAR_H, folder: 'anim', suggested: 'egg.jpg', category: 'anim', desc: '蛋（破殼初始化動畫，會隨進度放大）' },
  idle: { key: 'idle', color: '#F0405A', label: 'Marine idle', w: CHAR_W, h: CHAR_H, folder: 'anim', suggested: 'idle_00.jpg', category: 'anim', desc: '待機（最常出現，是門面）' },
  yawn: { key: 'yawn', color: '#C0506A', label: 'ANIM: Yawn', w: CHAR_W, h: CHAR_H, folder: 'anim', suggested: 'yawn.jpg', category: 'anim', desc: '打哈欠（疲勞高時隨機觸發）' },
  cheer: { key: 'cheer', color: '#FF6080', label: 'ANIM: Cheer', w: CHAR_W, h: CHAR_H, folder: 'anim', suggested: 'cheer.jpg', category: 'anim', desc: '加油（隨機觸發 + 對話泡泡）' },
  pet: { key: 'pet', color: '#FF7090', label: 'ANIM: Pet', w: CHAR_W, h: CHAR_H, folder: 'anim', suggested: 'pet.jpg', category: 'anim', desc: '摸頭時的開心表情' },
  eat: { key: 'eat', color: '#F07090', label: 'ANIM: Eat', w: CHAR_W, h: CHAR_H, folder: 'anim', suggested: 'eat.jpg', category: 'anim', desc: '嚼食（餵食時一口一口咬）' },
  sleep: { key: 'sleep', color: '#405080', label: 'ANIM: Sleep', w: CHAR_W, h: CHAR_H, folder: 'anim', suggested: 'sleep.jpg', category: 'anim', desc: '蓋被子睡覺（2 幀呼吸輪播）' },
  // --- 結局圖（皆 150×150 統一畫布）---
  end_good: { key: 'end_good', color: '#FFD24A', label: 'END: Good', w: CHAR_W, h: CHAR_H, folder: 'portraits', suggested: 'idol.jpg', category: 'ending', desc: '好結局（互動率 > 90%）' },
  end_normal: { key: 'end_normal', color: '#6A86C0', label: 'END: Normal', w: CHAR_W, h: CHAR_H, folder: 'portraits', suggested: 'office.jpg', category: 'ending', desc: '普通結局（互動率 30~90%）' },
  end_bad: { key: 'end_bad', color: '#9A3A3A', label: 'END: Bad', w: CHAR_W, h: CHAR_H, folder: 'portraits', suggested: 'pirate.jpg', category: 'ending', desc: '壞結局（互動率 < 30%）' },
  end_runaway: { key: 'end_runaway', color: '#404048', label: 'END: Run away', w: CHAR_W, h: CHAR_H, folder: 'portraits', suggested: 'runaway.jpg', category: 'ending', desc: '離家出走（飽食度歸零）' },
  // --- 摸頭結算情緒圖（成功 / 失敗，皆 150×150 統一畫布）---
  emo_success: { key: 'emo_success', color: '#FFD24A', label: 'EMO: Success', w: CHAR_W, h: CHAR_H, folder: 'portraits', suggested: 'emo_success.jpg', category: 'emotion', desc: '成功（時間內摸滿親密度條）' },
  emo_fail: { key: 'emo_fail', color: '#9A6A6A', label: 'EMO: Fail', w: CHAR_W, h: CHAR_H, folder: 'portraits', suggested: 'emo_fail.jpg', category: 'emotion', desc: '失敗（時間到沒摸滿）' },
  // --- 食物 / 甜點 ---
  food_0: { key: 'food_0', color: '#F0A0B0', label: 'Cake', w: 95, h: 95, folder: 'food', suggested: 'cake.jpg', category: 'food', desc: '蛋糕' },
  food_1: { key: 'food_1', color: '#C08050', label: 'Pudding', w: 95, h: 95, folder: 'food', suggested: 'pudding.jpg', category: 'food', desc: '布丁' },
  food_2: { key: 'food_2', color: '#F0D060', label: 'Tart', w: 95, h: 95, folder: 'food', suggested: 'tart.jpg', category: 'food', desc: '塔' },
  food_3: { key: 'food_3', color: '#B0E0F0', label: 'Soda', w: 95, h: 95, folder: 'food', suggested: 'soda.jpg', category: 'food', desc: '蘇打' },
  food_4: { key: 'food_4', color: '#E07070', label: 'Parfait', w: 95, h: 95, folder: 'food', suggested: 'parfait.jpg', category: 'food', desc: '百匯' },
}

// 給上傳面板分組用。
export const CATEGORIES: { id: SpriteSpec['category']; label: string; keys: string[] }[] = [
  { id: 'background', label: '背景 Backgrounds', keys: ['bg_room', 'bg_game'] },
  { id: 'anim', label: '動作 Animations', keys: ['egg', 'idle', 'yawn', 'cheer', 'pet', 'eat', 'sleep'] },
  { id: 'ending', label: '結局 Endings', keys: ['end_good', 'end_normal', 'end_bad', 'end_runaway'] },
  { id: 'emotion', label: '摸頭結算 Emotions', keys: ['emo_success', 'emo_fail'] },
  { id: 'food', label: '食物 Food', keys: ['food_0', 'food_1', 'food_2', 'food_3', 'food_4'] },
]

// asset_manager.py PET_EXPR：哪些 key 在「沒有圖」時會畫成有表情的小寵物佔位。
// 沒列到的（背景、食物）維持「色塊 + 標籤」。
export const PET_EXPR: Record<string, string> = {
  egg: 'neutral',
  idle: 'happy',
  yawn: 'sleepy',
  cheer: 'excited',
  pet: 'happy',
  eat: 'eating',
  sleep: 'sleepy',
  end_good: 'excited',
  end_normal: 'neutral',
  end_bad: 'happy',
  end_runaway: 'sad',
  emo_success: 'excited',
  emo_fail: 'sad',
}

// 餵食可選的 5 種甜點。
export const FOODS = [
  { key: 'food_0', label: 'Cake 蛋糕' },
  { key: 'food_1', label: 'Pudding 布丁' },
  { key: 'food_2', label: 'Tart 塔' },
  { key: 'food_3', label: 'Soda 蘇打' },
  { key: 'food_4', label: 'Parfait 百匯' },
]

// 結局分支（ending.py）。
export const ENDINGS = [
  { id: 'good', key: 'end_good', title: 'GOOD END', rate: 95 },
  { id: 'normal', key: 'end_normal', title: 'NORMAL END', rate: 60 },
  { id: 'bad', key: 'end_bad', title: 'BAD END', rate: 15 },
  { id: 'runaway', key: 'end_runaway', title: 'RUN AWAY', rate: 0 },
]

// 摸頭遊戲結算（petting.py _result_screen）：只有成功 / 失敗兩種。
export const PET_SUCCESS_STROKES = 28 // 與 device/config.PET_SUCCESS_STROKES 對齊
export const GRADES = [
  { id: 'success', title: 'SUCCESS!', emo: 'emo_success', pets: 28 },
  { id: 'fail', title: 'FAILED...', emo: 'emo_fail', pets: 11 },
]

// 編輯群組 = 上方「動作 List」每個分頁。
//   parts   : 這個動作可編輯的 sprite key（多數只有一個；eat/結局/結算有多個「部件」）。
//   actionId: 對應 utils/animations.ts 的動作（「模擬」時用哪支腳本在裝置螢幕上重播）；
//             null 表示只是素材分組（背景），沒有對應動畫。
//   partType: 多部件動作切換時，要連動模擬器的哪個 picker（food/ending/grade）。
export interface EditGroup {
  id: string
  label: string
  parts: string[]
  actionId: string | null
  partType?: 'food' | 'ending' | 'grade'
}

export const EDIT_GROUPS: EditGroup[] = [
  { id: 'idle', label: 'Idle 待機', parts: ['idle'], actionId: 'idle' },
  { id: 'eat', label: 'Eat 餵食', parts: ['eat', 'food_0', 'food_1', 'food_2', 'food_3', 'food_4'], actionId: 'eat', partType: 'food' },
  { id: 'sleep', label: 'Sleep 睡覺', parts: ['sleep'], actionId: 'sleep' },
  { id: 'yawn', label: 'Yawn 哈欠', parts: ['yawn'], actionId: 'yawn' },
  { id: 'cheer', label: 'Cheer 加油', parts: ['cheer'], actionId: 'cheer' },
  { id: 'pet', label: 'Pet 摸頭', parts: ['pet'], actionId: 'pet' },
  { id: 'egg', label: 'Egg 破殼', parts: ['egg'], actionId: 'egg' },
  { id: 'ending', label: 'Ending 結局', parts: ['end_good', 'end_normal', 'end_bad', 'end_runaway'], actionId: 'ending', partType: 'ending' },
  { id: 'result', label: 'Result 結算', parts: ['emo_success', 'emo_fail'], actionId: 'result', partType: 'grade' },
  { id: 'bg', label: 'BG 背景', parts: ['bg_room', 'bg_game'], actionId: null },
]

// 對話字串（assets/strings/en.py），對話泡泡用。
export const STRINGS: Record<string, string> = {
  cheer_msg_01: "Let's do our best today!",
  cheer_msg_02: 'Thanks for staying with me!',
  yawn_msg_01: "Mmm... I'm getting sleepy...",
}
