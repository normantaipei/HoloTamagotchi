#!/usr/bin/env bash
# dev.sh — 安全啟動 HoloTamagotchi dev（mpremote mount run）。
#
# 它幫你處理好整套安全流程，避免「could not enter raw repl」「螢幕全黑」等坑：
#   1) 確認序列埠沒被別的 session 佔住
#   2) 先硬體 reset，清掉上次 mount 殘留的死 /remote
#   3) 等 REPL 真的可用才掛載
#   4) mount + run device/main.py（首幀約需 40 秒，請看板子螢幕）
#   5) 不論 Ctrl-C 或正常結束，收尾再 reset 一次，讓板子回到乾淨 REPL
#
# 用法：./dev.sh [PORT]
#   要停止遊戲：按 Ctrl-C（之後會自動收尾 reset）
set -uo pipefail
cd "$(dirname "$0")"

PORT="${1:-/dev/cu.usbserial-55910039061}"
MPREMOTE=".venv/bin/mpremote"
PY=".venv/bin/python"

reset_board() {
  "$PY" - "$PORT" <<'PY'
import sys, time, serial
s = serial.Serial(sys.argv[1], 115200)
s.dtr = False; s.rts = True; time.sleep(0.2); s.rts = False; time.sleep(1.0); s.close()
PY
}

# 1) 序列埠佔用檢查
if lsof "$PORT" >/dev/null 2>&1; then
  echo "⚠️  $PORT 正被佔用，先關掉那個 mpremote/screen session："
  lsof "$PORT"
  exit 1
fi

# 2) 進場 reset：清掉上次殘留
echo "→ 硬體 reset 板子…"
reset_board

# 3) 等 REPL 可用（板子已停用 flash main.py，開機直接進 REPL）
echo "→ 等待 REPL…"
ok=0
for i in 1 2 3 4 5 6 7 8; do
  if "$MPREMOTE" connect "$PORT" exec "pass" >/dev/null 2>&1; then ok=1; break; fi
done
if [ "$ok" != 1 ]; then
  echo "✗ 連不上 REPL。拔插一次 USB、或確認板子有開機，再重跑 ./dev.sh"
  exit 1
fi

# 4) 收尾 reset：不論怎麼離開都讓板子回乾淨 REPL（下次不一定要先 reset）
cleanup() { echo; echo "→ 收尾 reset…"; reset_board; echo "✓ 板子已回到乾淨 REPL"; }
trap cleanup EXIT

# 5) 掛載執行
echo "→ mount run device/main.py"
echo "   ⏳ 首幀約需 40 秒（模組/素材都透過序列慢慢讀），終端機空白是正常的，請看板子螢幕。"
echo "   要停止：按 Ctrl-C"
"$MPREMOTE" connect "$PORT" mount device run device/main.py
