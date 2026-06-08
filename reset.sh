#!/usr/bin/env bash
# reset.sh — 硬體 reset M5 板（透過 RTS=EN 線，不用按實體鍵）。
#
# 用途：清掉 mpremote mount 中斷後殘留的「死 /remote」狀態。症狀是下次連線出現
#       `could not enter raw repl`。跑這個就能讓板子重開、回到乾淨 REPL。
#
# 用法：./reset.sh [PORT]   （PORT 預設見下方）
set -euo pipefail
cd "$(dirname "$0")"

PORT="${1:-/dev/cu.usbserial-55910039061}"

if lsof "$PORT" >/dev/null 2>&1; then
  echo "⚠️  $PORT 正被佔用，先關掉那個 session 再 reset："
  lsof "$PORT"
  exit 1
fi

.venv/bin/python - "$PORT" <<'PY'
import sys, time, serial
port = sys.argv[1]
s = serial.Serial(port, 115200)
# classic ESP32 reset：RTS 拉 EN 低→放開，DTR(GPIO0) 保持高 → 正常開機（非下載模式）
s.dtr = False; s.rts = True
time.sleep(0.2)
s.rts = False
time.sleep(1.0)
s.close()
print("✓ reset", port)
PY
