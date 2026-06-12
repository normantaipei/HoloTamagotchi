// nuxt.config.ts — 純前端工具（無後端）。
// 這個 web 介面只在瀏覽器跑：美術上傳圖片 → canvas 重現裝置端動畫播放，
// 所有狀態都在記憶體 / localStorage，不需要伺服器。
//
// 註：刻意「不」設 ssr:false。Nuxt 3.21.8 在 ssr:false 時，dev server 會把 client
// server 誤傳進 resolveServerEntry 而丟 "No entry found in rollupOptions.input"。
// 本 app 全部在 client 端繪製（canvas 在 onMounted、localStorage 以 import.meta.client
// 包住），維持預設 SSR（prerender + hydrate）即可正常運作；要純靜態用 `npm run generate`。
export default defineNuxtConfig({
  devtools: { enabled: false },
  app: {
    head: {
      title: 'HoloTamagotchi — 美術動畫 Review 模擬器',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '上傳美術素材，逐一檢查每個動作在 M5Stack Fire (320×240) 上的動畫播放是否符合預期。' },
      ],
    },
  },
  css: ['~/assets/css/main.css'],
  compatibilityDate: '2024-11-01',
})
