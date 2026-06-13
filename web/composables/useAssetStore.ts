// composables/useAssetStore.ts — 上傳素材的共享狀態。
//
// 結構：key -> 該動作的素材幀陣列（每幀含檔名 + dataURL + 已載入的 Image）。
// - 單幀：忠實重現「裝置端目前行為」（一張圖 + 程序動畫）。
// - 多幀：依「多幀速度」輪播，預覽未來多幀動畫（device README 標記為 TODO 的方向）。
//
// 以 localStorage 持久化 dataURL，重整網頁不會掉圖。圖片只存在瀏覽器，不會上傳到任何伺服器。

import { reactive } from 'vue'

export interface AssetFrame {
  name: string
  dataUrl: string
  img: HTMLImageElement | null
}

interface StoreState {
  assets: Record<string, AssetFrame[]>
  ready: number // 用來觸發畫面更新的版本號（圖片非同步載入完成時 +1）
}

const STORAGE_KEY = 'holo-art-sim/assets/v1'

// ─── 圖片上傳大小限制 ─────────────────────────────────────────────────────
// 依 M5Stack Fire 記憶體與本專案執行評估：
//  - 裝置走 UIFlow1 lcd.image() 原生尺寸貼圖（不縮放），素材都是小 sprite
//    （角色 150×150、背景 320×240、食物 95×95），正常檔案約 5~40KB。
//  - 圖檔最終要塞進裝置 Flash 可用空間（~3~4MB）；模擬器則以 base64 dataURL
//    存進瀏覽器 localStorage（~5MB 硬上限、base64 再膨脹 ~33% → 原始圖 ~3.7MB）。
//    localStorage 會比 Flash 先爆，故以它為基準。
//  → 單檔 512KB：任何正確尺寸的 sprite 都綽綽有餘，但擋得下手機原圖那種誤上傳。
//  → 總量 3.5MB：壓在 localStorage 預算內，也安全落在裝置 Flash 空間。
export const MAX_FILE_BYTES = 512 * 1024
export const MAX_TOTAL_BYTES = Math.round(3.5 * 1024 * 1024)

export function formatBytes(bytes: number): string {
  if (bytes >= 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + 'MB'
  return Math.round(bytes / 1024) + 'KB'
}

// 從 base64 dataURL 估算原始位元組數（忽略 padding 的微小誤差，估算足夠）。
function dataUrlBytes(dataUrl: string): number {
  const i = dataUrl.indexOf(',')
  const b64 = i >= 0 ? dataUrl.slice(i + 1) : dataUrl
  return Math.floor((b64.length * 3) / 4)
}

// 單例（整個 app 共用一份）。
let store: StoreState | null = null

function loadImage(frame: AssetFrame, bump: () => void) {
  const img = new Image()
  img.onload = () => {
    frame.img = img
    bump()
  }
  img.onerror = () => {
    frame.img = null
  }
  img.src = frame.dataUrl
}

function persist(s: StoreState) {
  try {
    const plain: Record<string, { name: string; dataUrl: string }[]> = {}
    for (const [k, frames] of Object.entries(s.assets)) {
      plain[k] = frames.map((f) => ({ name: f.name, dataUrl: f.dataUrl }))
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(plain))
  } catch (e) {
    // localStorage 滿了（圖太多太大）就略過持久化，不影響當下使用。
    console.warn('[asset-store] 持久化失敗（可能超出 localStorage 容量）', e)
  }
}

function restore(s: StoreState) {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const plain = JSON.parse(raw) as Record<string, { name: string; dataUrl: string }[]>
    for (const [k, frames] of Object.entries(plain)) {
      s.assets[k] = frames.map((f) => {
        const af: AssetFrame = { name: f.name, dataUrl: f.dataUrl, img: null }
        loadImage(af, () => (s.ready += 1))
        return af
      })
    }
  } catch (e) {
    console.warn('[asset-store] 還原失敗', e)
  }
}

export function useAssetStore() {
  if (!store) {
    store = reactive<StoreState>({ assets: {}, ready: 0 })
    if (import.meta.client) restore(store)
  }
  const s = store
  const bump = () => (s.ready += 1)

  function fileToDataUrl(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  // 目前所有素材的總位元組數（給總量上限判斷）。
  function totalBytes(): number {
    let n = 0
    for (const frames of Object.values(s.assets)) for (const f of frames) n += dataUrlBytes(f.dataUrl)
    return n
  }

  // 檢查單一檔案是否可上傳；可上傳回 null，否則回傳被擋原因（給 UI 顯示）。
  // remainingBudget：本批此前已預扣後，總量上限還剩多少。
  function rejectReason(file: File, remainingBudget: number): string | null {
    if (!file.type.startsWith('image/'))
      return `${file.name}：不是圖片檔，已略過 / not an image, skipped`
    if (file.size > MAX_FILE_BYTES)
      return `${file.name}（${formatBytes(file.size)}）超過單檔上限 ${formatBytes(MAX_FILE_BYTES)}，已略過 / over per-file limit, skipped`
    if (file.size > remainingBudget)
      return `${file.name}：再加會超過素材總量上限 ${formatBytes(MAX_TOTAL_BYTES)}，已略過 / would exceed total limit, skipped`
    return null
  }

  // 加入一批檔案到某個 key（多選 = 多幀，依檔名排序）。
  // 回傳被擋下的檔案原因清單（空陣列＝全部成功）。
  async function addFiles(key: string, files: File[]): Promise<string[]> {
    const sorted = [...files].sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }))
    const frames = s.assets[key] || (s.assets[key] = [])
    const rejected: string[] = []
    let budget = MAX_TOTAL_BYTES - totalBytes()
    for (const file of sorted) {
      const reason = rejectReason(file, budget)
      if (reason) {
        rejected.push(reason)
        continue
      }
      const dataUrl = await fileToDataUrl(file)
      const af: AssetFrame = { name: file.name, dataUrl, img: null }
      loadImage(af, bump)
      frames.push(af)
      budget -= file.size
    }
    if (!frames.length) delete s.assets[key]
    persist(s)
    bump()
    return rejected
  }

  // 取得某 key 已載入的 Image 陣列（給 Renderer 用）。
  function getImages(key: string): HTMLImageElement[] | undefined {
    const frames = s.assets[key]
    if (!frames) return undefined
    const imgs = frames.map((f) => f.img).filter((x): x is HTMLImageElement => !!x)
    return imgs.length ? imgs : undefined
  }

  function getFrames(key: string): AssetFrame[] {
    return s.assets[key] || []
  }

  function removeFrame(key: string, idx: number) {
    const frames = s.assets[key]
    if (!frames) return
    frames.splice(idx, 1)
    if (!frames.length) delete s.assets[key]
    persist(s)
    bump()
  }

  // 替換某一幀的圖（per-frame「上傳」）。
  // 回傳被擋原因（null＝成功）。
  async function replaceFrame(key: string, idx: number, file: File): Promise<string | null> {
    const frames = s.assets[key]
    if (!frames || !frames[idx]) return null
    // 替換：先扣掉被換掉那幀的位元組，再判斷總量。
    const budget = MAX_TOTAL_BYTES - totalBytes() + dataUrlBytes(frames[idx].dataUrl)
    const reason = rejectReason(file, budget)
    if (reason) return reason
    const dataUrl = await fileToDataUrl(file)
    const af: AssetFrame = { name: file.name, dataUrl, img: null }
    loadImage(af, bump)
    frames[idx] = af
    persist(s)
    bump()
    return null
  }

  // 調整幀順序（往左 / 往右）。
  function moveFrame(key: string, from: number, to: number) {
    const frames = s.assets[key]
    if (!frames || to < 0 || to >= frames.length || from === to) return
    const [x] = frames.splice(from, 1)
    frames.splice(to, 0, x)
    persist(s)
    bump()
  }

  // 匯出 / 匯入整份工作（給「Save / 載入」用）。
  function exportJSON(): Record<string, { name: string; dataUrl: string }[]> {
    const out: Record<string, { name: string; dataUrl: string }[]> = {}
    for (const [k, frames] of Object.entries(s.assets)) {
      out[k] = frames.map((f) => ({ name: f.name, dataUrl: f.dataUrl }))
    }
    return out
  }

  function importJSON(obj: Record<string, { name: string; dataUrl: string }[]>, merge = false) {
    if (!merge) for (const k of Object.keys(s.assets)) delete s.assets[k]
    for (const [k, frames] of Object.entries(obj)) {
      s.assets[k] = frames.map((f) => {
        const af: AssetFrame = { name: f.name, dataUrl: f.dataUrl, img: null }
        loadImage(af, () => (s.ready += 1))
        return af
      })
    }
    persist(s)
    bump()
  }

  // 總共上傳了幾張圖（給狀態列顯示）。
  function totalCount(): number {
    return Object.values(s.assets).reduce((n, f) => n + f.length, 0)
  }

  function clearKey(key: string) {
    delete s.assets[key]
    persist(s)
    bump()
  }

  function clearAll() {
    for (const k of Object.keys(s.assets)) delete s.assets[k]
    persist(s)
    bump()
  }

  function count(key: string): number {
    return s.assets[key]?.length || 0
  }

  return { state: s, addFiles, getImages, getFrames, removeFrame, replaceFrame, moveFrame, clearKey, clearAll, count, totalCount, totalBytes, exportJSON, importJSON }
}
