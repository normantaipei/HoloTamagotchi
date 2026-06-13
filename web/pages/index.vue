<!-- index.vue — 美術動畫 review 模擬器（依手稿重構）。
     版面：上＝動作 List 分頁；中＝該動作的幀序編輯（Pic 01/02 + 新增）+ Anime 輪播；
     下＝Save（工作儲存）/ 模擬（Compile，裝置實機播放）。 -->
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { EDIT_GROUPS } from '~/data/manifest'
import { useAssetStore } from '~/composables/useAssetStore'
import { useI18n } from '~/composables/useI18n'

const store = useAssetStore()
const { t, locale, setLocale } = useI18n()

const groupId = ref('idle')
const group = computed(() => EDIT_GROUPS.find((g) => g.id === groupId.value)!)

// 多部件動作（eat / ending / result / bg）的目前部件。
const partKey = ref('idle')
watch(group, (g) => { partKey.value = g.parts[0] }, { immediate: true })

function selectGroup(id: string) { groupId.value = id }

// 模擬器 modal
const simOpen = ref(false)
const simProps = computed(() => {
  const g = group.value
  const p: any = { actionId: g.actionId || 'idle' }
  if (g.partType === 'food' && partKey.value.startsWith('food_')) p.food = partKey.value
  if (g.partType === 'ending') p.ending = partKey.value.replace('end_', '')
  if (g.partType === 'grade') p.grade = partKey.value.replace('emo_', '') // emo_success → success
  return p
})
function openSim() { simOpen.value = true }

// Save / 載入：匯出整份工作為 JSON 檔（含所有幀的 dataURL），可備份 / 交接。
const toast = ref('')
let toastTimer: any = null
function flash(msg: string) {
  toast.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toast.value = ''), 2200)
}
function save() {
  const data = store.exportJSON()
  const blob = new Blob([JSON.stringify(data)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `holo-art-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
  flash(t('toast.exported'))
}
async function loadFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    const obj = JSON.parse(await file.text())
    store.importJSON(obj)
    flash(t('toast.loaded'))
  } catch {
    flash(t('toast.loadFailed'))
  }
  input.value = ''
}

const total = computed(() => store.totalCount())
const partLabel = (k: string) => t('sprite.' + k)
</script>

<template>
  <div class="app">
    <!-- 頂部：動作 List -->
    <header class="topbar">
      <div class="brand">
        <span class="title">{{ t('app.title') }}</span>
      </div>
      <nav class="tabs">
        <button v-for="g in EDIT_GROUPS" :key="g.id" class="tab" :class="{ on: g.id === groupId }" @click="selectGroup(g.id)">
          {{ t('group.' + g.id) }}
        </button>
      </nav>
      <label class="lang" :title="t('lang.label')">
        <select :value="locale" @change="setLocale(($event.target as HTMLSelectElement).value as any)">
          <option value="zh">{{ t('lang.zh') }}</option>
          <option value="en">{{ t('lang.en') }}</option>
        </select>
      </label>
    </header>

    <main class="work">
      <!-- 多部件動作的部件選擇（單部件不顯示）-->
      <div v-if="group.parts.length > 1" class="parts">
        <span class="parts-label">{{ t('parts.label') }}：</span>
        <button v-for="k in group.parts" :key="k" class="part" :class="{ on: k === partKey, has: store.count(k) > 0 }" @click="partKey = k">
          {{ partLabel(k) }}<span v-if="store.count(k)" class="badge">{{ store.count(k) }}</span>
        </button>
      </div>

      <!-- 中段：幀序編輯 + Anime 輪播 -->
      <div class="stage-row">
        <section class="ed-panel">
          <FrameEditor :part-key="partKey" />
        </section>
        <aside class="anime-panel">
          <AnimePreview :part-key="partKey" />
          <button class="sim-btn" @click="openSim">{{ t('sim.onDevice') }}</button>
        </aside>
      </div>

      <!-- 底部：Save / Compile -->
      <footer class="actionbar">
        <button class="bar-btn save" @click="save">{{ t('bar.save') }}</button>
        <label class="bar-btn ghost">
          {{ t('bar.load') }}
          <input type="file" accept="application/json" @change="loadFile" />
        </label>
        <button class="bar-btn compile" @click="openSim">{{ t('bar.simulate') }}</button>
        <span class="spacer" />
        <span class="stat">{{ t('bar.assetCount', { n: total }) }}</span>
        <button class="bar-btn ghost danger" @click="store.clearAll()">{{ t('bar.clearAll') }}</button>
      </footer>
    </main>

    <Transition name="fade">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </Transition>

    <SimulatorModal v-if="simOpen" v-bind="simProps" @close="simOpen = false" />
  </div>
</template>

<style scoped>
.app { min-height: 100vh; display: flex; flex-direction: column; }

.topbar { display: flex; align-items: center; gap: 18px; padding: 12px 20px; border-bottom: 1px solid #241d30; background: #120e18; position: sticky; top: 0; z-index: 10; flex-wrap: wrap; }
.brand { display: flex; align-items: center; gap: 10px; }
.logo { font-size: 22px; }
.title { font-size: 15px; font-weight: 700; white-space: nowrap; }
.tabs { display: flex; gap: 6px; flex-wrap: wrap; }
.tab { font-size: 13px; padding: 7px 13px; border-radius: 9px; background: #1b1722; color: #d8d2e4; border: 1px solid #2a2333; cursor: pointer; }
.tab:hover { background: #251f30; }
.tab.on { background: #F0405A; color: #fff; border-color: #F0405A; }

.lang { margin-left: auto; }
.lang select { font-size: 13px; padding: 7px 28px 7px 12px; border-radius: 9px; background: #1b1722; color: #d8d2e4; border: 1px solid #2a2333; cursor: pointer; appearance: none; -webkit-appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath fill='%238d85a0' d='M0 0l5 6 5-6z'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 10px center; }
.lang select:hover { background-color: #251f30; }

.work { flex: 1; display: flex; flex-direction: column; gap: 16px; padding: 18px 20px 90px; max-width: 1200px; width: 100%; margin: 0 auto; }

.parts { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.parts-label { font-size: 12px; color: #8d85a0; }
.part { position: relative; font-size: 12px; padding: 6px 12px; border-radius: 14px; background: #1b1722; color: #d8d2e4; border: 1px solid #2a2333; cursor: pointer; }
.part.has { border-color: #38492a; }
.part.on { background: #FFC857; color: #1a1018; border-color: #FFC857; font-weight: 600; }
.badge { margin-left: 6px; font-size: 10px; background: rgba(0,0,0,.35); padding: 0 5px; border-radius: 6px; }
.part.on .badge { background: rgba(0,0,0,.18); }

.stage-row { display: flex; gap: 18px; align-items: flex-start; }
.ed-panel { flex: 1; min-width: 0; padding: 16px; background: #14101a; border: 1px solid #241d30; border-radius: 16px; }
.anime-panel { flex: 0 0 auto; width: 312px; display: flex; flex-direction: column; gap: 10px; align-items: center; }
.sim-btn { width: 100%; padding: 11px; border-radius: 10px; background: #F0405A; color: #fff; border: none; font-weight: 600; cursor: pointer; font-size: 13px; }
.sim-btn:hover { background: #ff516b; }

.actionbar { position: fixed; left: 0; right: 0; bottom: 0; display: flex; align-items: center; gap: 10px; padding: 12px 20px; background: #120e18ee; border-top: 1px solid #241d30; backdrop-filter: blur(6px); z-index: 20; }
.bar-btn { position: relative; font-size: 13px; padding: 9px 16px; border-radius: 10px; cursor: pointer; border: 1px solid #2a2333; }
.bar-btn.save { background: #2a4a2e; color: #c8f0cc; border-color: #38592e; }
.bar-btn.save:hover { background: #335a38; }
.bar-btn.compile { background: #F0405A; color: #fff; border-color: #F0405A; font-weight: 600; }
.bar-btn.compile:hover { background: #ff516b; }
.bar-btn.ghost { background: #1b1722; color: #d8d2e4; }
.bar-btn.ghost:hover { background: #251f30; }
.bar-btn.ghost input { display: none; }
.bar-btn.danger { color: #c89; }
.bar-btn.danger:hover { background: #3a1c24; color: #ffb3c4; }
.spacer { flex: 1; }
.stat { font-size: 12px; color: #8d85a0; font-family: ui-monospace, monospace; }

.toast { position: fixed; bottom: 76px; left: 50%; transform: translateX(-50%); background: #2a2333; color: #fff; padding: 10px 18px; border-radius: 10px; font-size: 13px; z-index: 50; box-shadow: 0 8px 30px rgba(0,0,0,.5); border: 1px solid #3a3048; }
.fade-enter-active, .fade-leave-active { transition: opacity .2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 880px) {
  .stage-row { flex-direction: column; }
  .anime-panel { width: auto; flex-direction: row; align-self: stretch; align-items: flex-start; }
  .sim-btn { width: auto; flex: 1; }
}
</style>
