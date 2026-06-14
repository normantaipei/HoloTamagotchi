# HoloTamagotchi

建構在 **M5Stack Fire** 上的 Hololive 粉絲向電子雞遊戲，語言為 **MicroPython**。

開發方式：Fire 接 USB，用 `mpremote` 把程式推上去跑，**不燒錄、秒級更新**。Fire 出廠的 UIFlow1 韌體已內建 `m5stack` 模組，無須額外燒錄。

---

## 目錄結構

模組化架構，目標：高擴充性（多角色 / 多語言）、邏輯與美術解耦。

```
HoloTamagotchi/
├─ device/                     # 遊戲程式（M5Stack Fire，UIFlow1 m5stack API）
│  ├─ main.py                  #   進入點：Game 情境物件 + 狀態機主迴圈
│  ├─ config.py                #   全域設定（數值閾值、色票、狀態 ID）— 調平衡先動這
│  ├─ dev.py                   #   DEV 覆寫機制（只 config.DEV=True 生效；prod 零開銷）
│  ├─ dev_data.py              #   DEV 設定（CONFIG dict）— 調起始狀態/數值/skip_imu 動這
│  ├─ metrics.py               #   核心數值系統（成長/飽食/疲勞/音遊率）
│  ├─ i18n.py                  #   多國語言字串存取
│  ├─ asset_manager.py         #   資源管理：有圖畫圖，沒圖畫「色塊+標籤」佔位
│  ├─ ui.py                    #   共用 UI（對話筐 DialogBox / 選單 Menu）
│  ├─ states/                  #   狀態機，一狀態一檔
│  │  ├─ base.py               #     State 基底（on_enter/update/on_exit）
│  │  ├─ init_state.py         #     STATE_INIT（蛋裂開）
│  │  ├─ normal_room.py        #     STATE_NORMAL_ROOM（主樞紐 + 結局判定）
│  │  ├─ feeding.py            #     STATE_FEEDING（餵食）
│  │  ├─ sleeping.py           #     STATE_SLEEPING（睡眠）
│  │  ├─ minigame.py           #     STATE_MINI_GAME（音遊）
│  │  └─ ending.py             #     STATE_ENDING（4 種結局）
│  └─ assets/                  #   美術與文案資源（詳見 device/assets/README.md）
│     ├─ strings/              #     i18n 字串（zh_tw / en）
│     └─ characters/marine/    #     角色 manifest + 圖片資料夾
│        ├─ character.py       #       色彩主題 / 佔位規格 / 圖片對應 / 對話
│        ├─ backgrounds/  anim/  portraits/  food/   # ← 美術放圖處（目前空）
├─ dev.sh                      # 安全啟動開發（推薦：自動 reset→等 REPL→mount run→收尾）
├─ reset.sh                    # 硬體 reset 板子（卡住 / 黑屏時用）
├─ .venv/                      # Python 虛擬環境（放 mpremote，已 gitignore）
└─ README.md
```

> **目前沒有任何圖片** → 螢幕全部以「色塊 + 方括號標籤」（如 `[BG: Normal Room]`）顯示，
> 程式照常運行、流程可測。美術把圖丟進上面的資料夾、在 `character.py` 的 `IMAGES`
> 補一行，同位置就自動換成圖片，邏輯程式不用改。詳見 [device/assets/README.md](device/assets/README.md)。

### 核心數值（config.py 可調）

| 變數 | 說明 | 結局關聯 |
|------|------|----------|
| GrowthIndex | 成長指數，隨時間 +，滿 100 | 觸發正常結局 |
| BasicLifeIndex | 飽食度，隨時間 −，餵食 + | < 0 → 壞結局（離家出走） |
| SleepIndex | 疲勞，隨時間 +，睡眠恢復 | 過高打哈欠 / 達標強制睡眠 |
| RhythmGameRate | 音遊互動率 % | >90 偶像 / 30–90 上班族 / <30 海賊 |

---

## 文件

| 文件 | 內容 |
|------|------|
| [docs/character-states-for-art.md](docs/character-states-for-art.md) | **角色狀態總覽（給美術看的白話版）** — 六大場景、心情、美術交付清單，含範例圖流程圖 |
| [docs/character-states-for-art.en.md](docs/character-states-for-art.en.md) | 同上英文版 / Artist-friendly states overview (English) |
| [docs/character-state-machine.md](docs/character-state-machine.md) | 角色狀態機（給工程的技術版）— 觸發條件、數值規則、config 常數 |
| [web/README.md](web/README.md) | 動畫模擬器（瀏覽器預覽真機播放） |
| [device/assets/README.md](device/assets/README.md) | 美術放圖規格與流程 |

![角色狀態流程圖](docs/character-states-for-art.png)

---

## 環境準備（只做一次）

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

---

## 開發流程

Fire 用 USB 接上 Mac 即可，**不需要燒錄**。

**① 找出 Fire 的序列埠**
```bash
ls /dev/cu.* | grep usbserial      # 例如 /dev/cu.usbserial-55910039061
```

**② 把程式推上去跑**（改完任何 `device/` 下的檔後重複這步，秒級、不燒錄）

**推薦：用安全啟動腳本**——幫你處理好埠佔用檢查、進場/收尾硬體 reset、等 REPL：
```bash
./dev.sh                      # port 預設 /dev/cu.usbserial-55910039061
./dev.sh /dev/cu.usbserial-XXXX   # 換 port 時這樣傳
```

底層其實是這條（`dev.sh` 就是把它包起來 + 前後 reset）：
```bash
.venv/bin/mpremote connect /dev/cu.usbserial-XXXX mount device run device/main.py
```

- 專案已拆成多個模組，**必須用 `mount`**：它把本機 `device/` 掛載成裝置檔案系統，
  `import config` / `import states...` 等才找得到。`mount` 不寫進 flash → 快且不傷 flash。
- 只想跑單檔的舊式 `run device/main.py`（不加 `mount`）會因找不到模組而失敗。
- ⏳ **首幀約需 40 秒**：模組與素材都透過序列線一個 byte 一個 byte 讀，很慢。**終端機空白是正常的，看板子螢幕為準**，別誤判當機。
- 程式裡的 `print()` 會回傳到終端機；按 **Ctrl-C** 中斷（用 `dev.sh` 會在中斷後自動收尾 reset，把板子留在乾淨 REPL）。
- ⚠️ **mount 開發每次中斷後通常要硬體 reset 一次**：中斷掛載會殘留指向已消失 `/remote` 的死狀態，下次連線就 `could not enter raw repl`。`dev.sh` 已自動處理；手動跑底層指令時，卡住就 `./reset.sh`。
- 真機按鍵（普通房間）：**B=叫出選單**；選單內 **A/C=左右移動、B=確認**（FEED 餵食 / GAME 音遊）。

**③（可選）開機自動跑** — 把整個 `device/` 樹複製進 flash（多模組，需整包複製，非只 main.py）：
```bash
.venv/bin/mpremote connect /dev/cu.usbserial-XXXX cp -r device/. :
```
> 會覆蓋 Fire 上原本的 `main.py` 及同名檔。平常 debug 用步驟 ② 的 `mount` 就好，不必複製。

**開發循環**：改 [device/](device/) 下任一檔 → 跑步驟 ②（`mount … run`）→ 看畫面 / 終端機輸出 → 重複。

### DEV / PROD 模式

由 [config.py](device/config.py) 的 `DEV` 旗標切換（改完重跑步驟 ②）：

| `DEV` | 畫面 | 用途 |
|-------|------|------|
| `True`（預設） | 疊一層 debug overlay：底部 `DEV <state> G.. L.. S.. R..%` 文字 + 三條核心數值條 | 上 Fire 開發時即時看背景數值 / 目前狀態 |
| `False` | 乾淨遊戲介面，不顯示任何數值或狀態文字（靠角色動作表現） | 正式展示 / 給玩家 |

overlay 由主迴圈統一畫在最上層，對所有狀態生效（餵食 / 睡眠 / 音遊也看得到）。

### DEV 快速情境（dev_data.py）

不必苦等數值自然跑到特殊狀態——編輯 [device/dev_data.py](device/dev_data.py) 的 `CONFIG`，存檔重跑步驟 ② 即生效（免燒錄）。只在 `config.DEV=True` 時讀取，prod 零開銷。

| 欄位 | 作用 |
|------|------|
| `start_state` | 強制起始狀態，跳過開場蛋動畫（`"normal_room"` / `"feeding"` / `"sleeping"` / `"mini_game"` / `"ending"`） |
| `metrics` | 直接設核心數值，一開機重現情境（`sleep=5` 馬上想睡 / `growth=100` 馬上結局 / `life=-1` 壞結局）；`None`=不覆寫 |
| `skip_imu` | 跳過 IMU 初始化（mount 開發 / 無此硬體時設 `True`，搖一搖靜默停用） |
| `freeze_metrics` | 凍結數值，畫面停住方便觀察 |
| `time_scale` | 自然數值倍速（如 `60` → 1 秒當 1 分鐘跑），快速驗證自然轉場 |
| `enabled` | `False` 一鍵停用所有覆寫，不必刪檔 |

> ⚠️ **設定一定要放 `.py`、走 `import` 載入，不要用 `dev.json` + `open()`**。在 mpremote mount 下，模組 import 完之後再 `open()` 讀資料檔會卡死序列協定 → 開機永遠停在讀檔、**螢幕全黑**。這是曾經的真實坑，故設定改成 Python 模組。

---

## 畫面 / 按鍵 API 速查（`m5stack` 模組）

```python
from m5stack import lcd, btnA, btnB, btnC

# 繪圖（顏色用 0xRRGGBB）
lcd.clear(0x181226)                       # 清螢幕
lcd.fillRect(x, y, w, h, color)           # 實心矩形
lcd.fillRoundRect(x, y, w, h, r, color)   # 圓角矩形
lcd.fillCircle(x, y, r, color)            # 實心圓
lcd.font(lcd.FONT_DejaVu24)               # 設字型
lcd.print("TEXT", x, y, color)            # 印文字

# 按鍵（邊緣偵測，按下瞬間 True 一次）
if btnA.wasPressed(): ...                  # btnA / btnB / btnC

# 喇叭（以 SOUND_ON 開關控制；目前預設關閉）
from m5stack import speaker
speaker.tone(freq, ms)
```

座標系：左上角 (0,0)，橫向 320(寬)×240(高)。

> **螢幕文字用英文**：內建字型對中文支援有限，中文放在註解或 `print()`。

---

## 疑難排解

| 症狀 | 處理 |
|------|------|
| **螢幕全黑 / 卡開機**（終端機無輸出超過 1 分鐘） | 先確認不是「首幀 ~40 秒還在載入」（看步驟 ②）。若真的卡住：**設定檔別用 `open()` 讀**（見「DEV 快速情境」的警告），並 `./reset.sh` 後重跑 `./dev.sh` |
| `could not enter raw repl` | 多半是上次 mount 中斷殘留的死 `/remote`，或板子正在跑程式。**`./reset.sh`** 硬體 reset 最快（用 `dev.sh` 已自動處理）；或先 `pkill -9 -f mpremote` 釋放序列埠再重試 |
| 卡在 raw repl 重試多次仍失敗 | `./reset.sh`（RTS 線硬重置，免按鍵），或直接按 Fire 側邊 RESET 鍵 |
| 按鍵有爆音/底噪 | M5 喇叭 DAC 殘留噪音；`device/main.py` 啟動會 `mute_speaker()` 靜音 |
| `mpremote: command not found` | 用完整路徑 `.venv/bin/mpremote ...`，或先 `source .venv/bin/activate` |
| 找不到序列埠 | 確認 USB 線可傳輸資料、Fire 已開機；重插或換線 |
