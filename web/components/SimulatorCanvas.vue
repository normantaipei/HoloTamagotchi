<!-- SimulatorCanvas.vue — 把指定動作的第 N 幀畫到放大後的螢幕。
     - 320×240 離屏 canvas 作畫（裝置原生解析度），再以最近鄰放大到可視 canvas，
       忠實呈現小螢幕顆粒感。
     - 播放迴圈（requestAnimationFrame + 累加器）依「該動作的真機實測幀時間」步進
       （deviceFrameMs；有背景的畫面 ~70ms≈14fps，其餘 50ms=20fps）× 速度。
     - frame 用 v-model 雙向綁定，方便外層拖時間軸。 -->
<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import { Renderer } from '~/utils/renderer'
import type { ActionDef, ActionOpts } from '~/utils/animations'
import { FPS, SCREEN_W, SCREEN_H } from '~/data/manifest'
import { useAssetStore } from '~/composables/useAssetStore'

const props = defineProps<{
  action: ActionDef
  opts: ActionOpts
  playing: boolean
  speed: number
  frameHold: number
  scale: number
}>()

const frame = defineModel<number>('frame', { default: 0 })

const store = useAssetStore()
const canvas = ref<HTMLCanvasElement | null>(null)
let offscreen: HTMLCanvasElement | null = null
let renderer: Renderer | null = null
let raf = 0
let acc = 0
let last = 0

const W = computed(() => SCREEN_W * props.scale)
const H = computed(() => SCREEN_H * props.scale)

function ensure() {
  if (!canvas.value) return
  if (!offscreen) {
    offscreen = document.createElement('canvas')
    offscreen.width = SCREEN_W
    offscreen.height = SCREEN_H
    const octx = offscreen.getContext('2d')!
    renderer = new Renderer(octx, (key) => store.getImages(key))
  }
}

function draw() {
  ensure()
  if (!renderer || !offscreen || !canvas.value) return
  renderer.frame = frame.value
  renderer.frameHold = props.frameHold
  // 清成黑底再交給動作腳本（多數 state 自己會鋪滿背景）。
  renderer.clear('#000000')
  props.action.render(renderer, props.opts)

  const vctx = canvas.value.getContext('2d')!
  vctx.imageSmoothingEnabled = false
  vctx.clearRect(0, 0, W.value, H.value)
  vctx.drawImage(offscreen, 0, 0, SCREEN_W, SCREEN_H, 0, 0, W.value, H.value)
}

function tick(now: number) {
  if (!props.playing) return
  if (!last) last = now
  const dt = now - last
  last = now
  acc += dt
  // 每幀步進用「該動作的真機實測幀時間」（deviceFrameMs，未填即 50ms = 20fps），
  // 讓播放速度與真機一致：有背景的畫面真機 ~70ms（~14fps），會比 20fps 慢且較頓。
  const deviceMs = props.action.deviceFrameMs ?? 1000 / FPS
  const step = deviceMs / Math.max(0.05, props.speed)
  let advanced = false
  while (acc >= step) {
    acc -= step
    let next = frame.value + 1
    if (next >= props.action.frames) {
      if (props.action.loop) next = 0
      else {
        next = props.action.frames - 1
        frame.value = next
        advanced = true
        // 非循環播到底 → 停在最後一幀並通知外層暫停。
        emit('ended')
        break
      }
    }
    frame.value = next
    advanced = true
  }
  if (advanced) draw()
  raf = requestAnimationFrame(tick)
}

const emit = defineEmits<{ ended: [] }>()

function start() {
  cancelAnimationFrame(raf)
  last = 0
  acc = 0
  raf = requestAnimationFrame(tick)
}
function stop() {
  cancelAnimationFrame(raf)
  raf = 0
}

watch(() => props.playing, (p) => (p ? start() : stop()))
// 任一影響畫面的輸入變動 → 立即重畫（暫停時也要更新）。
watch([frame, () => props.action, () => props.opts, () => props.frameHold, () => props.scale, () => store.state.ready], () => {
  if (canvas.value) {
    canvas.value.width = W.value
    canvas.value.height = H.value
  }
  draw()
}, { deep: true })

onMounted(() => {
  if (canvas.value) {
    canvas.value.width = W.value
    canvas.value.height = H.value
  }
  draw()
  if (props.playing) start()
})
onBeforeUnmount(stop)
</script>

<template>
  <div class="screen-wrap">
    <canvas ref="canvas" class="screen" />
  </div>
</template>

<style scoped>
.screen-wrap {
  display: inline-block;
  padding: 14px;
  background: #14101a;
  border-radius: 18px;
  border: 3px solid #2a2333;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), inset 0 0 0 6px #0a0810;
}
.screen {
  display: block;
  image-rendering: pixelated;
  border-radius: 4px;
  background: #000;
  max-width: 100%;
  height: auto;
}
</style>
