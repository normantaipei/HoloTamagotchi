// composables/useI18n.ts — 介面文字的中英切換。
//
// 設計：locale 是「模組層級」的單一 reactive ref，所有元件共用同一份；切換語言時
// 全站一起重繪。t(key, params) 從 messages 取字串，找不到時退回 en、再退回 key 本身。
//
// 注意：模擬器「螢幕內」（320×240 canvas）畫出來的字（Nom nom… / Pet the head! /
// ENDING: GOOD END …）刻意維持英文 —— 那是真機 device 顯示的字串，翻譯會失真，故不納入。

import { ref } from 'vue'

export type Locale = 'zh' | 'en'

const STORAGE_KEY = 'holo-art-sim/locale'

// 模組層級單例：整個 app 共用，確保切換語言時所有元件同步更新。
const locale = ref<Locale>('zh')
let initialized = false

type Dict = Record<string, string>

const messages: Record<Locale, Dict> = {
  zh: {
    // 語言切換
    'lang.label': '語言',
    'lang.zh': '中文',
    'lang.en': 'English',

    // index.vue — 頂部 / 底部工具列
    'app.title': '美術動畫模擬器',
    'parts.label': '部件',
    'sim.onDevice': '模擬（裝置實機）',
    'bar.save': '儲存',
    'bar.load': '載入',
    'bar.simulate': '模擬',
    'bar.assetCount': '共 {n} 張素材',
    'bar.clearAll': '清空全部',
    'toast.exported': '已匯出工作檔（也已自動存在瀏覽器）',
    'toast.loaded': '已載入工作檔',
    'toast.loadFailed': '載入失敗：檔案格式不正確',

    // FrameEditor.vue
    'ed.suggested': '建議 {w}×{h} · {path} · {n} 幀 · 單檔 ≤ {size}',
    'ed.dismiss': '關閉',
    'ed.skippedHead': '以下檔案未上傳（總量上限 {total}）',
    'ed.clickReplace': '點擊換圖：{name}',
    'ed.loading': '載入中…',
    'ed.replace': '換圖',
    'ed.moveLeft': '往前移',
    'ed.deleteFrame': '刪除這幀',
    'ed.moveRight': '往後移',
    'ed.uploadFirst': '上傳第一幀',
    'ed.addFrame': '新增幀',
    'ed.multiSelect': '可多選',
    'ed.tipEmpty': '此格使用佔位顯示（{label}）。上傳一張＝靜圖；上傳多張＝多幀動畫，下方 Anime 會輪播。',
    'ed.tipSingle': '單張＝裝置現行行為（靜圖 + 程序動畫）。想做逐幀動畫就按「＋」繼續加。',
    'ed.tipMulti': '{n} 幀逐幀動畫。Anime 預覽輪播，「模擬」可看裝置上的實際播放。',

    // 上傳被擋原因（useAssetStore）
    'reject.notImage': '{name}：不是圖片檔，已略過',
    'reject.overFile': '{name}（{size}）超過單檔上限 {max}，已略過',
    'reject.overTotal': '{name}：再加會超過素材總量上限 {max}，已略過',

    // AnimePreview.vue
    'anime.loop': '動畫輪播',
    'anime.pause': '暫停',
    'anime.play': '播放',
    'anime.loopBtn': '循環',
    'anime.loopTitle': '循環播放',
    'anime.speed': '速度 {n}fps',
    'anime.speedTitle': '輪播速度',
    'anime.count': '{cur} / {total} 幀',
    'anime.noFrames': '尚無素材',

    // SimulatorModal.vue
    'sim.title': '模擬器 · 裝置實機播放',
    'sim.sub': 'M5Stack Fire 320×240 · 素材規格：PNG 去背、不縮放（上傳尺寸＝上機尺寸）、半透明無效（alpha ≥ 50% 視為不透明，其餘全透明）',
    'sim.close': '關閉',
    'sim.prevFrame': '上一幀',
    'sim.nextFrame': '下一幀',
    'sim.replay': '重播',
    'sim.frameRO': '幀 {cur} / {total} · {dur}s',
    'sim.speed': '速度 {v}×',
    'sim.frameHold': '多幀速度 每 {n} 幀',
    'sim.zoom': '放大 {n}×',

    // 動作分頁（EDIT_GROUPS）
    'group.idle': '待機',
    'group.eat': '餵食',
    'group.sleep': '睡覺',
    'group.yawn': '哈欠',
    'group.cheer': '加油',
    'group.pet': '摸頭',
    'group.egg': '破殼',
    'group.ending': '結局',
    'group.result': '結算',
    'group.bg': '背景',

    // 部件標籤（SPRITES label）
    'sprite.bg_room': '房間背景',
    'sprite.egg': '蛋',
    'sprite.idle': '待機',
    'sprite.yawn': '哈欠',
    'sprite.cheer': '加油',
    'sprite.pet': '摸頭',
    'sprite.eat': '咀嚼',
    'sprite.sleep': '睡覺',
    'sprite.end_good': '好結局',
    'sprite.end_normal': '普通結局',
    'sprite.end_bad': '壞結局',
    'sprite.end_runaway': '離家出走',
    'sprite.emo_success': '成功',
    'sprite.emo_fail': '失敗',
    'sprite.food_0': '蛋糕',
    'sprite.food_1': '布丁',
    'sprite.food_2': '塔',
    'sprite.food_3': '蘇打',
    'sprite.food_4': '百匯',

    // 部件說明（SPRITES desc）
    'desc.bg_room': '普通房間背景（待機 / 餵食 / 摸頭都在這）',
    'desc.egg': '蛋（破殼初始化動畫，會隨進度放大）',
    'desc.idle': '待機（最常出現，是門面）',
    'desc.yawn': '打哈欠（疲勞高時隨機觸發）',
    'desc.cheer': '加油（隨機觸發 + 對話泡泡）',
    'desc.pet': '摸頭時的開心表情',
    'desc.eat': '嚼食（餵食時一口一口咬）',
    'desc.sleep': '蓋被子睡覺（2 幀呼吸輪播）',
    'desc.end_good': '好結局（互動率 > 90%）',
    'desc.end_normal': '普通結局（互動率 30~90%）',
    'desc.end_bad': '壞結局（互動率 < 30%）',
    'desc.end_runaway': '離家出走（飽食度歸零）',
    'desc.emo_success': '成功（時間內摸滿親密度條）',
    'desc.emo_fail': '失敗（時間到沒摸滿）',
    'desc.food_0': '蛋糕',
    'desc.food_1': '布丁',
    'desc.food_2': '塔',
    'desc.food_3': '蘇打',
    'desc.food_4': '百匯',

    // 食物 picker（FOODS）
    'food.food_0': '蛋糕',
    'food.food_1': '布丁',
    'food.food_2': '塔',
    'food.food_3': '蘇打',
    'food.food_4': '百匯',

    // 結局 picker（ENDINGS）
    'ending.good': '好結局',
    'ending.normal': '普通結局',
    'ending.bad': '壞結局',
    'ending.runaway': '離家出走',

    // 結算 picker（GRADES）
    'grade.success': '成功',
    'grade.fail': '失敗',

    // 模擬器動作切換（ACTIONS label）
    'action.egg': '破殼',
    'action.idle': '待機',
    'action.yawn': '打哈欠',
    'action.cheer': '加油',
    'action.eat': '餵食',
    'action.sleep': '睡覺',
    'action.pet': '摸頭',
    'action.ending': '結局',
    'action.result': '摸頭結算',

    // 動作說明（ACTIONS note）
    'actionNote.egg': '素材 egg 150×150 · 黑底全屏，不用背景圖。放大是程式做的（90→150px，24 幀 ≈ 1.2s），圖請直接畫滿 150×150 的最終大小',
    'actionNote.idle': '素材 idle 150×150 + 背景 bg_room 320×240 · 最常出現的門面，建議 2~3 幀輪播（idle_0、idle_1…），切換速度＝下方「多幀速度」',
    'actionNote.yawn': '素材 yawn 150×150（＋背景 bg_room）· 疲勞高時隨機播 24 幀（真機 ~14fps ≈ 1.7s）後接回 idle，起訖姿勢請對得上待機',
    'actionNote.cheer': '素材 cheer 150×150（＋背景 bg_room）· 隨機播 60 幀後回待機。對話泡泡是程式畫在角色上方的，別畫進圖裡',
    'actionNote.eat': '素材 eat 150×150 + 甜點 food_0~4 各 95×95（＋背景 bg_room）· 甜點的縮小與移動都是程式做的（4 口 × 9 幀 + 6 收尾，真機 ≈ 3s），請畫完整一份、不用畫缺角；角色嘴巴請落在畫布高度約 60% 處',
    'actionNote.sleep': '素材 sleep 150×150 · 深藍底 #06141E 全屏，不用背景圖。2 幀輪播呼吸（每 10 幀換 + 上下 2px），請交 sleep_0 / sleep_1 兩張',
    'actionNote.pet': '素材 pet 150×150 + idle（＋背景 bg_room）· pet 是被摸到時的開心表情，沒摸時顯示 idle。手、愛心、親密度條、上方時間條都是程式畫的，別畫進圖裡',
    'actionNote.ending': '素材 end_good / end_normal / end_bad / end_runaway 各 150×150 · 黑底全屏、置中偏上（y 36~186），標題與結算文字由程式疊在上下方',
    'actionNote.result': '素材 emo_success / emo_fail 各 150×150 · 摸頭結算畫面，黑底全屏、置中偏上（y 36~186），標題與次數文字由程式疊上',
  },

  en: {
    // language switch
    'lang.label': 'Language',
    'lang.zh': '中文',
    'lang.en': 'English',

    // index.vue — top / bottom toolbars
    'app.title': 'Art Animation Simulator',
    'parts.label': 'Parts',
    'sim.onDevice': 'Simulate (on-device)',
    'bar.save': 'Save',
    'bar.load': 'Load',
    'bar.simulate': 'Simulate',
    'bar.assetCount': '{n} assets',
    'bar.clearAll': 'Clear all',
    'toast.exported': 'Exported (also auto-saved in your browser)',
    'toast.loaded': 'Loaded',
    'toast.loadFailed': 'Load failed: invalid file format',

    // FrameEditor.vue
    'ed.suggested': 'Suggested {w}×{h} · {path} · {n} frames · ≤ {size}/file',
    'ed.dismiss': 'Dismiss',
    'ed.skippedHead': 'Skipped files (total limit {total})',
    'ed.clickReplace': 'Click to replace: {name}',
    'ed.loading': 'Loading…',
    'ed.replace': 'Replace',
    'ed.moveLeft': 'Move left',
    'ed.deleteFrame': 'Delete frame',
    'ed.moveRight': 'Move right',
    'ed.uploadFirst': 'Upload first frame',
    'ed.addFrame': 'Add frame',
    'ed.multiSelect': 'Multi-select',
    'ed.tipEmpty': 'This slot shows a placeholder ({label}). Upload one = static image; upload several = multi-frame animation, looping in Anime below.',
    'ed.tipSingle': 'One frame = current device behavior (static image + procedural animation). Press “＋” to build a frame-by-frame animation.',
    'ed.tipMulti': '{n}-frame animation. Anime previews the loop; “Simulate” shows the real on-device playback.',

    // upload rejection reasons (useAssetStore)
    'reject.notImage': '{name}: not an image, skipped',
    'reject.overFile': '{name} ({size}) over per-file limit {max}, skipped',
    'reject.overTotal': '{name}: would exceed total asset limit {max}, skipped',

    // AnimePreview.vue
    'anime.loop': 'Anime Loop',
    'anime.pause': 'Pause',
    'anime.play': 'Play',
    'anime.loopBtn': 'Loop',
    'anime.loopTitle': 'Loop playback',
    'anime.speed': 'Speed {n}fps',
    'anime.speedTitle': 'Playback speed',
    'anime.count': '{cur} / {total} frames',
    'anime.noFrames': 'No frames',

    // SimulatorModal.vue
    'sim.title': 'Simulator · On-device playback',
    'sim.sub': 'M5Stack Fire 320×240 · Asset spec: transparent PNG, no scaling (upload size = on-device size), no partial alpha (alpha ≥ 50% is opaque, the rest fully transparent)',
    'sim.close': 'Close',
    'sim.prevFrame': 'Prev frame',
    'sim.nextFrame': 'Next frame',
    'sim.replay': 'Replay',
    'sim.frameRO': 'Frame {cur} / {total} · {dur}s',
    'sim.speed': 'Speed {v}×',
    'sim.frameHold': 'Frame hold every {n}',
    'sim.zoom': 'Zoom {n}×',

    // action tabs (EDIT_GROUPS)
    'group.idle': 'Idle',
    'group.eat': 'Feed',
    'group.sleep': 'Sleep',
    'group.yawn': 'Yawn',
    'group.cheer': 'Cheer',
    'group.pet': 'Pet',
    'group.egg': 'Egg',
    'group.ending': 'Ending',
    'group.result': 'Result',
    'group.bg': 'BG',

    // part labels (SPRITES label)
    'sprite.bg_room': 'Normal Room',
    'sprite.egg': 'Egg',
    'sprite.idle': 'Idle',
    'sprite.yawn': 'Yawn',
    'sprite.cheer': 'Cheer',
    'sprite.pet': 'Pet',
    'sprite.eat': 'Eat',
    'sprite.sleep': 'Sleep',
    'sprite.end_good': 'Good end',
    'sprite.end_normal': 'Normal end',
    'sprite.end_bad': 'Bad end',
    'sprite.end_runaway': 'Run away',
    'sprite.emo_success': 'Success',
    'sprite.emo_fail': 'Fail',
    'sprite.food_0': 'Cake',
    'sprite.food_1': 'Pudding',
    'sprite.food_2': 'Tart',
    'sprite.food_3': 'Soda',
    'sprite.food_4': 'Parfait',

    // part descriptions (SPRITES desc)
    'desc.bg_room': 'Normal room background (idle / feeding / petting)',
    'desc.egg': 'Egg (hatching intro, scales up with progress)',
    'desc.idle': 'Idle (most frequent — the face of the app)',
    'desc.yawn': 'Yawn (random when tired)',
    'desc.cheer': 'Cheer (random + speech bubble)',
    'desc.pet': 'Happy face while being petted',
    'desc.eat': 'Chewing (bite by bite while feeding)',
    'desc.sleep': 'Sleeping under covers (2-frame breathing loop)',
    'desc.end_good': 'Good ending (interaction rate > 90%)',
    'desc.end_normal': 'Normal ending (interaction rate 30–90%)',
    'desc.end_bad': 'Bad ending (interaction rate < 30%)',
    'desc.end_runaway': 'Run away (hunger hits zero)',
    'desc.emo_success': 'Success (filled the affection bar in time)',
    'desc.emo_fail': 'Fail (ran out of time)',
    'desc.food_0': 'Cake',
    'desc.food_1': 'Pudding',
    'desc.food_2': 'Tart',
    'desc.food_3': 'Soda',
    'desc.food_4': 'Parfait',

    // food picker (FOODS)
    'food.food_0': 'Cake',
    'food.food_1': 'Pudding',
    'food.food_2': 'Tart',
    'food.food_3': 'Soda',
    'food.food_4': 'Parfait',

    // ending picker (ENDINGS)
    'ending.good': 'Good End',
    'ending.normal': 'Normal End',
    'ending.bad': 'Bad End',
    'ending.runaway': 'Run Away',

    // grade picker (GRADES)
    'grade.success': 'Success',
    'grade.fail': 'Fail',

    // simulator action tabs (ACTIONS label)
    'action.egg': 'Egg',
    'action.idle': 'Idle',
    'action.yawn': 'Yawn',
    'action.cheer': 'Cheer',
    'action.eat': 'Eat',
    'action.sleep': 'Sleep',
    'action.pet': 'Pet',
    'action.ending': 'Ending',
    'action.result': 'Result',

    // action notes (ACTIONS note)
    'actionNote.egg': 'Asset: egg 150×150 · Full black screen, no background art. The scale-up is code (90→150px, 24 frames ≈ 1.2s) — draw the egg at its final 150×150 size',
    'actionNote.idle': 'Assets: idle 150×150 + background bg_room 320×240 · The most-seen shot; 2–3 looping frames recommended (idle_0, idle_1…), cycling at the “frame hold” rate below',
    'actionNote.yawn': 'Asset: yawn 150×150 (+ bg_room) · Random when tired, 24 frames (~14fps on device ≈ 1.7s), then cuts back to idle — match the idle pose at both ends',
    'actionNote.cheer': 'Asset: cheer 150×150 (+ bg_room) · Random, 60 frames, then back to idle. The speech bubble is drawn by code above the character — keep it out of the art',
    'actionNote.eat': 'Assets: eat 150×150 + desserts food_0–4 at 95×95 each (+ bg_room) · Shrinking and moving the dessert is code (4 bites × 9 frames + 6 tail, ≈ 3s on device) — draw one whole dessert, no bite marks; put the mouth at ~60% of the canvas height',
    'actionNote.sleep': 'Asset: sleep 150×150 · Full navy #06141E screen, no background art. 2-frame breathing loop (swap every 10 frames, ±2px) — deliver sleep_0 / sleep_1',
    'actionNote.pet': 'Assets: pet 150×150 + idle (+ bg_room) · pet is the happy reaction while being petted, idle shows in between. Hand, hearts, affection bar and timer bar are all drawn by code — keep them out of the art',
    'actionNote.ending': 'Assets: end_good / end_normal / end_bad / end_runaway, 150×150 each · Full black screen, placed high-center (y 36–186); title and stats text are overlaid by code above and below',
    'actionNote.result': 'Assets: emo_success / emo_fail, 150×150 each · Petting result screen, full black, placed high-center (y 36–186); title and counts are overlaid by code',
  },
}

export function useI18n() {
  // 首次使用時，從 localStorage 還原上次選的語言。
  if (!initialized && import.meta.client) {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === 'zh' || saved === 'en') locale.value = saved
    initialized = true
  }

  function setLocale(l: Locale) {
    locale.value = l
    if (import.meta.client) localStorage.setItem(STORAGE_KEY, l)
  }

  // t(key, params)：取字串並把 {name} 佔位換成 params.name。
  function t(key: string, params?: Record<string, string | number>): string {
    let str = messages[locale.value][key] ?? messages.en[key] ?? key
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v))
      }
    }
    return str
  }

  return { locale, setLocale, t }
}
