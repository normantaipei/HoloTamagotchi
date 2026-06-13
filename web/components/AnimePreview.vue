<!-- AnimePreview.vue — 手稿右下「Anime」框：把目前 part 的多幀圖直接輪播。
     這是「我的幀順起來順不順」的快速預覽（純圖輪播，不含背景 / 程序動畫）；
     要看裝置上的真實播放請按「模擬」。 -->
<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import { useAssetStore } from '~/composables/useAssetStore'
import { useI18n } from '~/composables/useI18n'
import { SPRITES } from '~/data/manifest'

const props = defineProps<{ partKey: string }>()
const store = useAssetStore()
const { t, locale } = useI18n()

const canvas = ref<HTMLCanvasElement | null>(null)
const playing = ref(true)
const loop = ref(true)
const fps = ref(8)
const cur = ref(0)
let raf = 0
let last = 0
let acc = 0

const frames = computed(() => store.getFrames(props.partKey))
const spec = computed(() => SPRITES[props.partKey])

function draw() {
  const c = canvas.value
  if (!c) return
  const ctx = c.getContext('2d')!
  ctx.imageSmoothingEnabled = false
  ctx.clearRect(0, 0, c.width, c.height)
  // 棋盤底，方便看透明 / 邊界
  const t = 8
  for (let y = 0; y < c.height; y += t) for (let x = 0; x < c.width; x += t) {
    ctx.fillStyle = ((x / t + y / t) % 2 === 0) ? '#15121b' : '#1b1722'
    ctx.fillRect(x, y, t, t)
  }
  const fr = frames.value
  if (!fr.length) {
    ctx.fillStyle = '#6f667e'
    ctx.font = '12px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(t('anime.noFrames'), c.width / 2, c.height / 2)
    return
  }
  const idx = Math.min(cur.value, fr.length - 1)
  const img = fr[idx]?.img
  if (!img) return
  // 依角色尺寸比例置中（用 spec 的 w/h 維持長寬比）
  const ar = spec.value.w / spec.value.h
  let dw = c.width * 0.8
  let dh = dw / ar
  if (dh > c.height * 0.8) { dh = c.height * 0.8; dw = dh * ar }
  ctx.drawImage(img, (c.width - dw) / 2, (c.height - dh) / 2, dw, dh)
}

function tick(now: number) {
  if (!playing.value) return
  if (!last) last = now
  acc += now - last
  last = now
  const step = 1000 / Math.max(1, fps.value)
  const n = frames.value.length
  if (n > 0) {
    while (acc >= step) {
      acc -= step
      if (cur.value + 1 >= n) {
        if (loop.value) cur.value = 0
        else { playing.value = false; break }
      } else cur.value++
    }
  }
  draw()
  raf = requestAnimationFrame(tick)
}

function start() { cancelAnimationFrame(raf); last = 0; acc = 0; raf = requestAnimationFrame(tick) }
function stop() { cancelAnimationFrame(raf); raf = 0 }

watch(playing, (p) => (p ? start() : (stop(), draw())))
watch([() => props.partKey, () => store.state.ready], () => { cur.value = 0; draw() })
watch(cur, draw)
watch(locale, draw) // 切換語言時重畫「尚無素材」字樣

onMounted(() => { draw(); if (playing.value) start() })
onBeforeUnmount(stop)
</script>

<template>
  <div class="anime">
    <div class="cap">{{ t('anime.loop') }}</div>
    <canvas ref="canvas" width="288" height="216" class="cv" />
    <div class="bar">
      <button class="b wide" @click="playing = !playing">{{ playing ? t('anime.pause') : t('anime.play') }}</button>
      <button class="b wide" :class="{ on: loop }" :title="t('anime.loopTitle')" @click="loop = !loop">{{ t('anime.loopBtn') }}</button>
    </div>
    <label class="fps" :title="t('anime.speedTitle')">
      {{ t('anime.speed', { n: fps }) }}
      <input type="range" min="1" max="24" step="1" v-model.number="fps" />
    </label>
    <div class="count">{{ frames.length ? t('anime.count', { cur: Math.min(cur, frames.length - 1) + 1, total: frames.length }) : '—' }}</div>
  </div>
</template>

<style scoped>
.anime { display: flex; flex-direction: column; gap: 8px; padding: 12px; background: #120e18; border: 1px solid #2a2333; border-radius: 14px; width: 312px; }
.cap { font-size: 13px; color: #c8bedf; text-align: center; }
.cv { width: 288px; height: 216px; border-radius: 8px; image-rendering: pixelated; align-self: center; background: #000; max-width: 100%; }
.bar { display: flex; align-items: center; gap: 6px; }
.b { padding: 6px 9px; border-radius: 7px; background: #221b2d; border: 1px solid #2f2740; color: #cfc6e0; cursor: pointer; font-size: 12px; }
.b.wide { flex: 1; }
.b:hover { background: #2d2440; }
.b.on { background: #FFC857; color: #1a1018; border-color: #FFC857; }
.fps { display: flex; flex-direction: column; font-size: 10px; color: #8d85a0; gap: 2px; }
.fps input { accent-color: #FFC857; width: 100%; }
.count { font-size: 11px; color: #6f667e; text-align: center; font-family: ui-monospace, monospace; }
</style>
