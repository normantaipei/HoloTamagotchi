# 美術動畫 Review 模擬器（web/）

給**美術**用的瀏覽器工具：上傳素材後，逐一檢查每個動作在 **M5Stack Fire（320×240）** 上的動畫播放是否符合預期 —— 不用接板子、不用燒錄。

> 播放速度依**真機實測**：有背景的畫面（待機 / 餵食 / 摸頭…）真機約 **14fps**（每幀要把整張背景寫進 canvas 再整張推到面板）、其餘約 20fps。模擬器照各動作的 `deviceFrameMs` 播，所以這裡的「快慢與頓感」就是真機體驗。

模擬器把裝置端的繪圖邏輯（C++ 韌體 `device/src/AssetManager.cpp`、`device/src/ui.cpp`、`device/src/states/*`）搬到 canvas，所以**你在這裡看到的播放，就是真機上的播放**：位置、縮放、點頭、呼吸、一口一口咬、摸頭手擺動、佔位色塊與小寵物臉都一致。

> 右上角的**電量指示**（小電池圖示 + 百分比）也與真機對齊——真機由 `device/src/Game.cpp` 的 `drawBattery()` 每幀疊在所有畫面上，依電量綠 / 黃 / 紅、充電中轉亮天藍 + 閃電。模擬器無真實電池，固定顯示展示值（80%）。

## 啟動

```bash
cd web
npm install
npm run dev      # 開 http://localhost:3000
```

其他指令：`npm run build`（正式打包）、`npm run generate`（輸出純靜態，可丟任何靜態空間）、`npm run preview`。

### 一鍵安裝（乾淨 VM，一行命令，免先 clone repo）

在一台全新的 Linux / macOS VM 上，**貼一行就好**：

```bash
curl -fsSL https://raw.githubusercontent.com/normantaipei/HoloTamagotchi/main/web/install.sh | bash
```

它會自動：裝 git → 裝 Node（NodeSource / nvm / brew）→ sparse-checkout 只抓 `web/` → `npm ci` + `npm run build` → 用 node 起 production server（預設對外 `0.0.0.0:3000`）。跑完直接開 `http://<VM-IP>:3000`。

想客製化就在 `bash` 前面塞環境變數：

```bash
# 換對外埠：
curl -fsSL https://raw.githubusercontent.com/normantaipei/HoloTamagotchi/main/web/install.sh | PORT=8080 bash

# 只裝＋build、先不啟動：
curl -fsSL https://raw.githubusercontent.com/normantaipei/HoloTamagotchi/main/web/install.sh | NO_START=1 bash
```

> 也可以把 [`install.sh`](install.sh) 下載下來用 `bash install.sh` 跑，效果相同。

### 用 Docker 管理（推薦：主機免裝 node、好起好停）

同一支腳本加 `DOCKER=1` 就改走容器流程：自動裝 git、（缺的話用官方腳本裝）Docker → 抓 `web/` → `docker compose up -d --build` 背景起容器（`restart: unless-stopped`）。

```bash
curl -fsSL https://raw.githubusercontent.com/normantaipei/HoloTamagotchi/main/web/install.sh | DOCKER=1 bash
# 換埠：
curl -fsSL https://raw.githubusercontent.com/normantaipei/HoloTamagotchi/main/web/install.sh | DOCKER=1 PORT=8080 bash
```

跑完用標準 compose 指令管理（在 `holotamagotchi-web/web` 下）：

```bash
docker compose ps              # 看狀態
docker compose logs -f         # 看 log
docker compose down            # 停止並移除容器
docker compose up -d --build   # 更新原始碼後重建
```

已經 clone 過 repo 的話也可以直接進 `web/` 跑 `docker compose up -d --build`。容器多階段打包，runtime 映像只含 `.output`（不含原始碼）。

常用環境變數（皆可選）：`PORT`（預設 3000）、`HOST`（預設 0.0.0.0）、`INSTALL_DIR`（預設 `./holotamagotchi-web`）、`REPO_BRANCH`（預設 main）、`NODE_VERSION`（預設 22）、`NO_START=1`（只裝＋build 不啟動）。

啟動後本機開 `http://localhost:3000`，VM 對外開 `http://<VM-IP>:3000`（記得在防火牆 / 安全群組放行該埠）。重跑同目錄會自動更新到最新 branch。免重新 build 直接啟動：`cd holotamagotchi-web/web && node .output/server/index.mjs`。

## 怎麼用

版面參考手稿，分成三段：

1. **頂部「動作 List」**：選一個動作分頁（Idle / Eat / Sleep / Yawn / Cheer / Pet / Egg / Sing / Ending / Result / BG）。
2. **中段「幀序編輯」**：該動作的逐幀列（Frame 01、02…）。
   - 每張卡片點圖可**換圖**（Frame 上傳）；下方三顆鈕 = **◀ 往前移 / 🗑 刪除 / ▶ 往後移**。
   - 末端「**＋**」= **Frame 新增**（可多選，依檔名數字排序）。
   - 多部件動作（Eat / Ending / Result / BG）上方會多一排「部件」可切（角色 / 各甜點 / 各結局圖…）。
3. **右側「Anime」**：把目前部件的多幀直接**輪播**，快速看順不順（play/pause、循環、fps）。
4. **底部按鈕**：
   - **💾 Save 工作儲存**：把整份工作匯出成 `.json`（含所有幀），可備份 / 交接；平常也會自動存在瀏覽器。**📂 載入**可讀回。
   - **⚙ Compile 模擬**（或右側「▶ 模擬」）：開**裝置實機模擬器**，在 320×240 螢幕上用與真機相同的繪圖邏輯重播（含背景、程序動畫、佔位行為）。內含暫停 / 逐幀 / 時間軸 / 速度 / 放大。

### 單幀 vs 多幀
- **一格放一張**：重現「裝置目前的行為」——靜圖 + 程序動畫（蛋會放大、睡覺上下呼吸、吃東西食物一口口變小）。
- **一格放多張**：逐幀動畫。Anime 即時輪播，「模擬」可看裝置上的實際播放。這是 `device/assets/README.md` 標記為 TODO 的未來方向，先在這裡驗證效果。

## 動作 ↔ 裝置 state 對照

| 動作 | 來源 | 重點 |
|------|------|------|
| 破殼 Egg | `states/init_state.py` | 蛋隨進度放大（24 幀 ≈ 1.2s，一次性） |
| 待機 Idle | `states/normal_room.py` | 主畫面門面 |
| 打哈欠 Yawn | `states/normal_room.py` | 疲勞高隨機觸發（24 幀）→ 回待機 |
| 加油 Cheer | `states/normal_room.py` | 隨機觸發（60 幀）+ 對話泡泡 |
| 餵食 Eat | `states/feeding.py` | 4 口 × 9 幀 + 6 收尾；食物逐口變小、角色點頭。可換 5 種甜點 |
| 睡覺 Sleep | `states/sleeping.py` | 2 幀呼吸輪播（每 10 幀換 + 上下 2px） |
| 摸頭 Pet | `states/petting.py` | 時間內摸滿親密度條＝成功、沒滿＝失敗；手左右擺、開心 + 愛心（自動示範） |
| 結局 Ending | `states/ending.py` | 4 種結局圖，可切分支 |
| 摸頭結算 Result | `states/petting.py` | 成功 / 失敗 2 張情緒圖，可切換 |

## 對應裝置端素材

格子的命名、建議資料夾與尺寸，完全對齊 `device/data/marine/manifest.txt`：
- `backgrounds/`：`bg_room`（320×240）
- `anim/`：`egg` `idle` `yawn` `cheer` `pet` `eat` `sleep`（皆 150×150）
- `portraits/`：`end_*`、`emo_success` / `emo_fail`（皆 150×150）
- `food/`：`food_0`~`food_4`（95×95）

**檔案規格**（`device/tools/build_fs_assets.py` 轉檔規則）：
- **PNG 去背**。轉檔時 `alpha < 128` 會變成透明色鍵（0xF81F 洋紅），`alpha ≥ 128` 一律不透明——**沒有半透明**，也請避免在圖裡用純洋紅 `#FF00FF`。
- **不縮放**：裝置端貼圖照原尺寸畫，上傳尺寸＝上機顯示尺寸。
- **多幀**：同一 key 交多張即可（`idle_0.png`、`idle_1.png`…），裝置照 `manifest.txt` 的幀數輪播。

驗收滿意後，把 PNG 依 `<key>_NN.png` 命名放進 `web/demo-assets/`，再跑
`python3 device/tools/build_fs_assets.py` 轉成 RGB565 素材、`pio run -t buildfs -t uploadfs` 燒進裝置的 LittleFS 分區即可（不必重編韌體）。

## 備註
- 純前端、無後端：圖片只存在瀏覽器（`localStorage`），重整不會掉，也**不會上傳到任何伺服器**。
- 規格若有更新，請同步 `web/data/manifest.ts`（sprite 清單 / 色票）與 `web/utils/animations.ts`（動畫腳本），來源為 `device/` 對應檔案。
