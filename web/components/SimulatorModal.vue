<!-- SimulatorModal.vue — 「模擬 / Compile」：用裝置端忠實引擎，在 320×240 螢幕上
     重播選定動作（含背景、程序動畫、佔位行為）。對應手稿 Compilar → 模擬。 -->
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ACTIONS } from '~/utils/animations'
import type { ActionOpts } from '~/utils/animations'
import { FOODS, ENDINGS, GRADES, FPS } from '~/data/manifest'
import { useI18n } from '~/composables/useI18n'

const { t } = useI18n()

const props = defineProps<{
  actionId: string
  // 進場時若是多部件動作（食物 / 結局 / 評級），帶入目前選的部件。
  food?: string
  ending?: string
  grade?: string
}>()
const emit = defineEmits<{ close: [] }>()

const actionId = ref(props.actionId)
const action = computed(() => ACTIONS.find((a) => a.id === actionId.value) || ACTIONS[0])

const food = ref(props.food || 'food_0')
const ending = ref(props.ending || 'good')
const grade = ref(props.grade || 'success')
const opts = computed<ActionOpts>(() => ({ food: food.value, ending: ending.value, grade: grade.value }))

const frame = ref(0)
const playing = ref(true)
const speed = ref(1)
const frameHold = ref(5)
const scale = ref(3)

watch(action, () => { frame.value = 0; playing.value = true })
function onEnded() { playing.value = false }

const durLabel = computed(() => (action.value.frames / FPS / speed.value).toFixed(1))
</script>

<template>
  <div class="overlay" @click.self="emit('close')">
    <div class="modal">
      <header class="m-head">
        <div>
          <div class="m-title">{{ t('sim.title') }}</div>
          <div class="m-sub">{{ t('sim.sub') }}</div>
        </div>
        <button class="x" :title="t('sim.close')" @click="emit('close')">✕</button>
      </header>

      <div class="m-body">
        <!-- 動作快速切換 -->
        <div class="acts">
          <button v-for="a in ACTIONS" :key="a.id" class="act" :class="{ on: a.id === actionId }" @click="actionId = a.id">{{ t('action.' + a.id) }}</button>
        </div>

        <div class="stage">
          <SimulatorCanvas
            v-model:frame="frame"
            :action="action"
            :opts="opts"
            :playing="playing"
            :speed="speed"
            :frame-hold="frameHold"
            :scale="scale"
            @ended="onEnded"
          />
        </div>

        <div class="note">{{ t('actionNote.' + action.id) }}</div>

        <div v-if="action.picker" class="picker">
          <template v-if="action.picker === 'food'">
            <button v-for="f in FOODS" :key="f.key" class="chip" :class="{ on: food === f.key }" @click="food = f.key">{{ t('food.' + f.key) }}</button>
          </template>
          <template v-else-if="action.picker === 'ending'">
            <button v-for="e in ENDINGS" :key="e.id" class="chip" :class="{ on: ending === e.id }" @click="ending = e.id">{{ t('ending.' + e.id) }}</button>
          </template>
          <template v-else-if="action.picker === 'grade'">
            <button v-for="g in GRADES" :key="g.id" class="chip" :class="{ on: grade === g.id }" @click="grade = g.id">{{ t('grade.' + g.id) }}</button>
          </template>
        </div>

        <div class="controls">
          <button class="play" @click="playing = !playing">{{ playing ? t('anime.pause') : t('anime.play') }}</button>
          <button class="step" :title="t('sim.prevFrame')" @click="playing = false; frame = Math.max(0, frame - 1)">◀</button>
          <button class="step" :title="t('sim.nextFrame')" @click="playing = false; frame = Math.min(action.frames - 1, frame + 1)">▶</button>
          <button class="step" :title="t('sim.replay')" @click="frame = 0">⟲</button>
          <span class="ro">{{ t('sim.frameRO', { cur: frame + 1, total: action.frames, dur: durLabel }) }}</span>
        </div>
        <input class="scrub" type="range" min="0" :max="action.frames - 1" v-model.number="frame" @input="playing = false" />

        <div class="sliders">
          <label>{{ t('sim.speed', { v: speed.toFixed(2) }) }} <input type="range" min="0.1" max="2" step="0.05" v-model.number="speed" /></label>
          <label>{{ t('sim.frameHold', { n: frameHold }) }} <input type="range" min="1" max="20" step="1" v-model.number="frameHold" /></label>
          <label>{{ t('sim.zoom', { n: scale }) }} <input type="range" min="1" max="4" step="1" v-model.number="scale" /></label>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(5, 3, 8, 0.78); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 20px; backdrop-filter: blur(3px); }
.modal { background: #100c16; border: 1px solid #2a2333; border-radius: 18px; width: min(720px, 100%); max-height: 92vh; overflow-y: auto; box-shadow: 0 20px 70px rgba(0,0,0,.6); }
.m-head { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #241d30; position: sticky; top: 0; background: #100c16; }
.m-title { font-size: 15px; font-weight: 700; }
.m-sub { font-size: 12px; color: #8d85a0; }
.x { background: #1b1722; border: 1px solid #2a2333; color: #cfc6e0; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; font-size: 14px; }
.x:hover { background: #2a2333; }
.m-body { padding: 16px 20px 22px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.acts { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
.act { font-size: 12px; padding: 5px 10px; border-radius: 8px; background: #1b1722; color: #d8d2e4; border: 1px solid #2a2333; cursor: pointer; }
.act.on { background: #F0405A; color: #fff; border-color: #F0405A; }
.note { font-size: 12px; color: #b8b0c8; text-align: center; max-width: 520px; line-height: 1.5; }
.picker { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
.chip { font-size: 12px; padding: 5px 11px; border-radius: 14px; background: #1b1722; color: #d8d2e4; border: 1px solid #2a2333; cursor: pointer; }
.chip.on { background: #FFC857; color: #1a1018; border-color: #FFC857; font-weight: 600; }
.controls { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; justify-content: center; }
.play { font-size: 13px; padding: 8px 16px; border-radius: 8px; background: #F0405A; color: #fff; border: none; cursor: pointer; font-weight: 600; }
.step { font-size: 13px; padding: 8px 12px; border-radius: 8px; background: #1b1722; color: #d8d2e4; border: 1px solid #2a2333; cursor: pointer; }
.ro { font-size: 12px; color: #8d85a0; font-family: ui-monospace, monospace; }
.scrub { width: 100%; max-width: 520px; accent-color: #F0405A; }
.sliders { display: flex; flex-wrap: wrap; gap: 14px; justify-content: center; }
.sliders label { font-size: 11px; color: #9a93a8; display: flex; flex-direction: column; gap: 3px; }
.sliders input { accent-color: #FFC857; }
</style>
