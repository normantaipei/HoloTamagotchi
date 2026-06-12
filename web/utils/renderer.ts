// utils/renderer.ts — 在 320×240 的離屏 canvas 上「重現裝置端畫面」。
//
// 這支是模擬器的心臟：把裝置端 asset_manager.py 與 ui.py 的繪圖逐一搬到 canvas，
// 讓「有上傳圖片就畫圖片、沒圖就畫佔位（小寵物臉 / 色塊+標籤）」的行為與真機一致。
// 動畫腳本（utils/animations.ts）只透過這裡提供的 helper 作畫，不直接碰 canvas API。
//
// 所有座標都用「裝置像素」（320×240）。放大顯示由外層 SimulatorCanvas 用
// imageSmoothingEnabled=false 做最近鄰放大，忠實呈現小螢幕的顆粒感。

import { SPRITES, PET_EXPR, C, THEME, STRINGS } from '~/data/manifest'

// 上傳的素材：key -> 已載入的 HTMLImageElement 陣列（可多幀）。
export type AssetGetter = (key: string) => HTMLImageElement[] | undefined

export class Renderer {
  ctx: CanvasRenderingContext2D
  getAssets: AssetGetter
  frame = 0 // 目前動作的幀（0-based）；多幀切換與程序動畫都用它，方便拖曳時間軸時可重現
  frameHold = 5 // 多幀素材：每張圖顯示幾個裝置幀（5 → ~4fps 輪播）

  constructor(ctx: CanvasRenderingContext2D, getAssets: AssetGetter) {
    this.ctx = ctx
    this.getAssets = getAssets
  }

  // 這個 key 是否已有可用圖片（對應 asset_manager.has_image）。
  hasImage(key: string): boolean {
    const imgs = this.getAssets(key)
    return !!(imgs && imgs.length)
  }

  // 多幀素材：依目前幀挑出要顯示的那一張。
  private pickImage(key: string): HTMLImageElement | null {
    const imgs = this.getAssets(key)
    if (!imgs || !imgs.length) return null
    if (imgs.length === 1) return imgs[0]
    const idx = Math.floor(this.frame / Math.max(1, this.frameHold)) % imgs.length
    return imgs[idx]
  }

  // === 基本繪圖 ===
  clear(color: string) {
    this.fillRect(0, 0, 320, 240, color)
  }

  fillRect(x: number, y: number, w: number, h: number, color: string) {
    const c = this.ctx
    c.fillStyle = color
    c.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h))
  }

  fillRoundRect(x: number, y: number, w: number, h: number, r: number, color: string) {
    const c = this.ctx
    x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h)
    r = Math.min(r, w / 2, h / 2)
    c.fillStyle = color
    c.beginPath()
    // @ts-ignore roundRect 在現代瀏覽器可用
    if (c.roundRect) { c.roundRect(x, y, w, h, r); c.fill(); return }
    c.moveTo(x + r, y)
    c.arcTo(x + w, y, x + w, y + h, r)
    c.arcTo(x + w, y + h, x, y + h, r)
    c.arcTo(x, y + h, x, y, r)
    c.arcTo(x, y, x + w, y, r)
    c.closePath()
    c.fill()
  }

  // 文字：textBaseline=top，對應裝置 lcd.print(x, y) 以 y 為頂端。
  // size 約略對應裝置字型：FONT_DefaultSmall≈12、FONT_DejaVu18≈16、FONT_DejaVu24≈22。
  text(s: string, x: number, y: number, color: string, size = 12) {
    const c = this.ctx
    c.fillStyle = color
    c.textBaseline = 'top'
    c.textAlign = 'left'
    c.font = `${size}px "DejaVu Sans", "Helvetica Neue", Arial, sans-serif`
    c.fillText(s, Math.round(x), Math.round(y))
  }

  // 粗估字寬（給置中用），對應 lcd.textWidth。
  textWidth(s: string, size = 12): number {
    const c = this.ctx
    c.font = `${size}px "DejaVu Sans", "Helvetica Neue", Arial, sans-serif`
    return c.measureText(s).width
  }

  // === 資源繪製：對應 asset_manager.AssetManager.draw ===
  // 有圖 → 畫圖（多幀依 frame 輪播）；無圖 → 小寵物臉 / 色塊+標籤。
  drawSprite(key: string, x?: number, y?: number, w?: number, h?: number, showLabel = true) {
    const spec = SPRITES[key]
    if (!spec) {
      // 未定義 key：畫洋紅警示（對應裝置端）。
      this.fillRect(x ?? 0, y ?? 0, w ?? 40, h ?? 20, '#FF00FF')
      return
    }
    const dw = w ?? spec.w
    const dh = h ?? spec.h
    const dx = x ?? (320 - dw) / 2
    const dy = y ?? (240 - dh) / 2

    const img = this.pickImage(key)
    if (img) {
      this.ctx.drawImage(img, Math.round(dx), Math.round(dy), Math.round(dw), Math.round(dh))
      return
    }
    if (PET_EXPR[key]) this.pet(dx, dy, dw, dh, spec.color, PET_EXPR[key])
    else this.placeholder(dx, dy, dw, dh, spec.color, showLabel ? spec.label : null)
  }

  // 角色用 theme bg 色清背景（對應 assets.color("bg")）。
  bgColor(): string {
    return THEME.bg
  }

  // === 色塊佔位（asset_manager._placeholder）===
  private placeholder(x: number, y: number, w: number, h: number, color: string, label: string | null) {
    this.fillRect(x, y, w, h, color)
    if (!label) return
    this.text('[' + label + ']', x + 3, y + h / 2 - 6, C.white, 11)
  }

  // === 小寵物臉佔位（asset_manager._pet / _arc / _dot）===
  private dot(x: number, y: number, s: number, col: string) {
    this.fillRect(x, y, s, s, col)
  }

  private arc(cx: number, my: number, halfW: number, sag: number, t: number, col: string) {
    const n = 4
    const step = Math.max(1, Math.floor(halfW / n))
    for (let i = -n; i <= n; i++) {
      const px = cx + i * step
      const f = 1.0 - (i * i) / (n * n)
      const py = my + Math.floor(sag * f)
      this.fillRect(px - Math.floor(t / 2), py - Math.floor(t / 2), t, t, col)
    }
  }

  private pet(x: number, y: number, w: number, h: number, color: string, expr: string) {
    const DARK = C.black
    const WHITE = C.white
    // 身體：圓角色塊
    this.fillRoundRect(x, y, w, h, Math.floor(Math.min(w, h) / 4), color)

    const cx = x + Math.floor(w / 2)
    const eyeY = y + Math.floor((h * 2) / 5)
    const eyeDx = Math.floor(w / 4)
    const es = Math.max(4, Math.floor(w / 8))
    const t = Math.max(2, Math.floor(w / 18))
    const mouthY = y + Math.floor((h * 3) / 5)
    const half = Math.floor(w / 5)
    const lx = cx - eyeDx
    const rx = cx + eyeDx

    // 眼睛：sleepy/eating 閉眼，其餘睜眼
    if (expr === 'sleepy' || expr === 'eating') {
      for (const ex of [lx, rx]) this.fillRect(ex - Math.floor(es / 2), eyeY, es, t, DARK)
    } else {
      for (const ex of [lx, rx]) {
        this.fillRoundRect(ex - Math.floor(es / 2), eyeY - Math.floor(es / 2), es, es, Math.floor(es / 3), WHITE)
        this.fillRect(ex - t, eyeY - t, t * 2, t * 2, DARK)
      }
    }

    // 嘴巴 + 表情點綴
    if (expr === 'happy') {
      this.arc(cx, mouthY, half, Math.floor(es / 2), t, DARK)
    } else if (expr === 'excited') {
      const mw = Math.floor(w / 3)
      const mh = Math.floor(h / 6)
      this.fillRoundRect(cx - Math.floor(mw / 2), mouthY - Math.floor(mh / 2), mw, mh, Math.floor(mh / 2), DARK)
      this.dot(x + w - es, y + es, t * 2, C.yellow)
    } else if (expr === 'eating') {
      const mw = Math.floor(w / 5)
      this.fillRoundRect(cx - Math.floor(mw / 2), mouthY - Math.floor(mw / 2), mw, mw, Math.floor(mw / 2), DARK)
    } else if (expr === 'sad') {
      this.arc(cx, mouthY + Math.floor(es / 2), half, -Math.floor(es / 2), t, DARK)
      this.dot(lx, eyeY + es, t, C.cyan)
    } else if (expr === 'sleepy') {
      const zx = x + w - es * 2
      const zy = y + es
      this.fillRect(zx, zy, es, t, WHITE)
      this.fillRect(zx, zy + es, es, t, WHITE)
      this.arc(cx, mouthY, Math.floor(half / 2), t, t, DARK)
    } else {
      // neutral
      this.fillRect(cx - Math.floor(half / 2), mouthY, half, t, DARK)
    }
  }

  // === 共用 UI（ui.py）===

  // 對話泡泡（DialogBox.show）：天藍框線 + 深藍底 + 朝下尾巴 + 文字（Cover Corp 配色）。
  dialog(key: string) {
    const x = 12, y = 34, w = 296, h = 36, tailX = 160, TAIL = 12
    const BORDER = '#48C5F4', FILL = '#07304A'   // 與 device/ui.py DialogBox 對齊
    this.fillRoundRect(x, y, w, h, 10, BORDER)
    this.fillRoundRect(x + 2, y + 2, w - 4, h - 4, 8, FILL)
    const ty = y + h
    for (let i = 0; i < TAIL; i++) {
      const hw = TAIL - 2 - i
      if (hw > 0) this.fillRect(tailX - hw, ty + i, hw * 2, 1, BORDER)
      const hwi = TAIL - 5 - i
      if (hwi > 0) this.fillRect(tailX - hwi, ty + i, hwi * 2, 1, FILL)
    }
    this.text(STRINGS[key] ?? key, x + 12, y + 9, C.white, 16)
  }

  // 底部三鍵提示列（ButtonHints）。slot 為 null / 文字 / {arrow:'left'|'right'}。
  hints(a: any, b: any, c: any) {
    const CX = [53, 160, 267]
    const TOP = 216
    const slots = [a, b, c]
    for (let i = 0; i < 3; i++) {
      const slot = slots[i]
      if (slot == null) continue
      if (typeof slot === 'object' && slot.arrow) this.arrow(CX[i], slot.arrow)
      else {
        const s = String(slot)
        const w = this.textWidth(s, 11)
        this.text(s, CX[i] - w / 2, TOP, C.dark, 11)
      }
    }
  }

  private arrow(cx: number, direction: string) {
    const cy = 216 + 7
    const hr = 8, w = 12
    for (let dy = -hr; dy <= hr; dy++) {
      const span = Math.floor((w * (hr - Math.abs(dy))) / hr)
      if (span <= 0) continue
      const x = direction === 'right' ? cx - Math.floor(w / 2) : cx - Math.floor(w / 2) + (w - span)
      this.fillRect(x, cy + dy, span, 1, C.dark)
    }
  }

  // 水平高亮選單（Menu.draw）。
  menu(labels: string[], idx: number, y = 140) {
    const n = labels.length
    const cw = Math.floor(320 / n)
    for (let i = 0; i < n; i++) {
      const x = i * cw
      const sel = i === idx
      const bg = sel ? C.pink : C.dark
      const bx = x + 6
      const bw = cw - 12
      this.fillRoundRect(bx, y, bw, 40, 8, bg)
      const lab = labels[i]
      const tw = this.textWidth(lab, 11)
      this.text(lab, bx + (bw - tw) / 2, y + (40 - 12) / 2, C.white, 11)
    }
  }
}
