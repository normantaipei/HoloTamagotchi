<!-- FrameEditor.vue — 某個 sprite key 的「幀序編輯」。
     對應手稿中間區：Pic 01 / Pic 02 ... + （Frame 新增）。
     每張卡片可：點圖換圖（Frame 上傳）、左右移動排序、刪除。
     末端「+」新增一或多幀（多選依檔名排序）。 -->
<script setup lang="ts">
import { computed } from 'vue'
import { SPRITES } from '~/data/manifest'
import { useAssetStore } from '~/composables/useAssetStore'

const props = defineProps<{ partKey: string }>()
const store = useAssetStore()
const spec = computed(() => SPRITES[props.partKey])
const frames = computed(() => store.getFrames(props.partKey))

async function onAdd(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.length) await store.addFiles(props.partKey, Array.from(input.files))
  input.value = ''
}
async function onReplace(idx: number, e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) await store.replaceFrame(props.partKey, idx, input.files[0])
  input.value = ''
}
</script>

<template>
  <div class="editor">
    <div class="ed-head">
      <div class="ed-title">
        <span class="key">{{ partKey }}</span>
        <span class="desc">{{ spec.desc }}</span>
      </div>
      <div class="ed-meta">建議 Suggested {{ spec.w }}×{{ spec.h }} · {{ spec.folder }}/{{ spec.suggested }} · {{ frames.length }} 幀 frames</div>
    </div>

    <div class="strip">
      <!-- 已有的幀 -->
      <div v-for="(f, i) in frames" :key="i" class="card">
        <div class="idx">{{ String(i + 1).padStart(2, '0') }}</div>
        <label class="pic" :title="'點擊換圖 Click to replace：' + f.name">
          <img v-if="f.img" :src="f.dataUrl" :alt="f.name" />
          <span v-else class="loading">載入中 Loading…</span>
          <input type="file" accept="image/*" @change="onReplace(i, $event)" />
          <span class="replace-hint">換圖 Replace</span>
        </label>
        <!-- 手稿的三個小框：往前移 / 刪除 / 往後移 -->
        <div class="ctrls">
          <button class="ctrl" :disabled="i === 0" title="往前移 Move left" @click="store.moveFrame(partKey, i, i - 1)">◀</button>
          <button class="ctrl del" title="刪除這幀 Delete frame" @click="store.removeFrame(partKey, i)">✕</button>
          <button class="ctrl" :disabled="i === frames.length - 1" title="往後移 Move right" @click="store.moveFrame(partKey, i, i + 1)">▶</button>
        </div>
        <div class="fname">{{ f.name }}</div>
      </div>

      <!-- + 新增 Frame -->
      <label class="card add" :class="{ empty: frames.length === 0 }">
        <div class="plus">＋</div>
        <div class="add-label">{{ frames.length === 0 ? '上傳第一幀 Upload first' : '新增幀 Add frame' }}</div>
        <div class="add-sub">可多選 Multi-select</div>
        <input type="file" accept="image/*" multiple @change="onAdd($event)" />
      </label>
    </div>

    <p v-if="frames.length === 0" class="tip">
      此格使用<strong>佔位</strong>顯示（{{ SPRITES[partKey].label }}）。上傳一張＝靜圖；上傳多張＝多幀動畫，下方 Anime 會輪播。
    </p>
    <p v-else-if="frames.length === 1" class="tip">
      單張＝裝置現行行為（靜圖 + 程序動畫）。想做逐幀動畫就按「＋」繼續加。
    </p>
    <p v-else class="tip">
      {{ frames.length }} 幀逐幀動畫。Anime 預覽輪播，「模擬」可看裝置上的實際播放。
    </p>
  </div>
</template>

<style scoped>
.editor { display: flex; flex-direction: column; gap: 10px; }
.ed-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.ed-title { display: flex; align-items: baseline; gap: 10px; }
.key { font-family: ui-monospace, monospace; font-size: 15px; color: #fff; font-weight: 700; }
.desc { font-size: 13px; color: #b8b0c8; }
.ed-meta { font-size: 11px; color: #6f667e; font-family: ui-monospace, monospace; }

.strip { display: flex; gap: 14px; align-items: stretch; overflow-x: auto; padding: 6px 2px 14px; }
.card {
  position: relative; flex: 0 0 auto; width: 168px; display: flex; flex-direction: column; gap: 7px;
  padding: 10px; background: #17131f; border: 1px solid #2a2333; border-radius: 12px;
}
.idx { position: absolute; top: 8px; left: 10px; z-index: 2; font-family: ui-monospace, monospace; font-size: 12px; color: #FFC857; background: rgba(0,0,0,.55); padding: 1px 6px; border-radius: 6px; }
.pic {
  position: relative; aspect-ratio: 1; background: #000; border-radius: 8px; overflow: hidden;
  display: flex; align-items: center; justify-content: center; cursor: pointer; border: 1px solid #241d30;
}
.pic img { width: 100%; height: 100%; object-fit: contain; image-rendering: pixelated; }
.pic input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
.loading { font-size: 11px; color: #6f667e; }
.replace-hint { position: absolute; bottom: 0; left: 0; right: 0; text-align: center; font-size: 11px; padding: 3px; background: rgba(0,0,0,.6); color: #d8d2e4; opacity: 0; transition: opacity .15s; }
.pic:hover .replace-hint { opacity: 1; }

.ctrls { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
.ctrl { padding: 6px 0; border-radius: 7px; background: #221b2d; border: 1px solid #2f2740; color: #cfc6e0; cursor: pointer; font-size: 13px; line-height: 1; }
.ctrl:hover:not(:disabled) { background: #2d2440; }
.ctrl:disabled { opacity: .3; cursor: default; }
.ctrl.del:hover { background: #4a2230; border-color: #6a2c3e; color: #ffb3c4; }
.fname { font-size: 10px; color: #6f667e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.card.add {
  width: 132px; align-items: center; justify-content: center; gap: 4px; cursor: pointer;
  border-style: dashed; border-color: #3a3048; background: #14101a; text-align: center;
}
.card.add:hover { border-color: #F0405A; background: #1b1422; }
.card.add.empty { border-color: #F0405A; }
.card.add input { display: none; }
.plus { font-size: 38px; color: #F0405A; line-height: 1; }
.add-label { font-size: 12px; color: #d8d2e4; }
.add-sub { font-size: 10px; color: #6f667e; }

.tip { margin: 0; font-size: 12px; color: #8d85a0; line-height: 1.5; }
.tip strong { color: #c8bedf; }
</style>
