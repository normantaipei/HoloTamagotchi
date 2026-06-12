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

  // 加入一批檔案到某個 key（多選 = 多幀，依檔名排序）。
  async function addFiles(key: string, files: File[]) {
    const sorted = [...files].sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }))
    const frames = s.assets[key] || (s.assets[key] = [])
    for (const file of sorted) {
      if (!file.type.startsWith('image/')) continue
      const dataUrl = await fileToDataUrl(file)
      const af: AssetFrame = { name: file.name, dataUrl, img: null }
      loadImage(af, bump)
      frames.push(af)
    }
    persist(s)
    bump()
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
  async function replaceFrame(key: string, idx: number, file: File) {
    const frames = s.assets[key]
    if (!frames || !frames[idx] || !file.type.startsWith('image/')) return
    const dataUrl = await fileToDataUrl(file)
    const af: AssetFrame = { name: file.name, dataUrl, img: null }
    loadImage(af, bump)
    frames[idx] = af
    persist(s)
    bump()
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

  return { state: s, addFiles, getImages, getFrames, removeFrame, replaceFrame, moveFrame, clearKey, clearAll, count, totalCount, exportJSON, importJSON }
}
