# HoloTamagotchi

建構在 **M5Stack Fire** 上的 Hololive 粉絲向電子雞遊戲，語言為 **MicroPython**。

開發方式：Fire 接 USB，用 `mpremote` 把程式推上去跑，**不燒錄、秒級更新**。Fire 出廠的 UIFlow1 韌體已內建 `m5stack` 模組，無須額外燒錄。

---

## 目錄結構

```
HoloTamagotchi/
├─ device/                  # 遊戲程式（M5Stack Fire，UIFlow1 m5stack API）
│  └─ main.py               #   ← 主程式，平常改這支
├─ .venv/                   # Python 虛擬環境（放 mpremote，已 gitignore）
└─ README.md
```

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

**② 把程式推上去跑**（改完 `device/main.py` 後重複這步，秒級、不燒錄）
```bash
.venv/bin/mpremote connect /dev/cu.usbserial-XXXX run device/main.py
```
- `run` 只是「執行」，不寫進 flash → 快且不傷 flash。
- 程式裡的 `print()` 會回傳到終端機；按 **Ctrl-C** 中斷。
- 真機按鍵：**A=餵食　B=玩耍　C=睡覺**。

**③（可選）開機自動跑** — 存進 flash 的 `main.py`：
```bash
.venv/bin/mpremote connect /dev/cu.usbserial-XXXX fs cp device/main.py :main.py
```
> 會覆蓋 Fire 上原本的 `main.py`。平常 debug 用步驟 ② 的 `run` 就好。

**開發循環**：改 [device/main.py](device/main.py) → 跑步驟 ② → 看畫面 / 終端機輸出 → 重複。

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
| `could not enter raw repl` | 板子正在跑 flash 上的程式或剛開機 —— `mpremote run` 會自動中斷它，等幾秒重跑即可 |
| 按鍵有爆音/底噪 | M5 喇叭 DAC 殘留噪音；`device/main.py` 啟動會 `mute_speaker()` 靜音 |
| `mpremote: command not found` | 用完整路徑 `.venv/bin/mpremote ...`，或先 `source .venv/bin/activate` |
| 找不到序列埠 | 確認 USB 線可傳輸資料、Fire 已開機；重插或換線 |
