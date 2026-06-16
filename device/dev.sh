#!/usr/bin/env bash
# dev.sh — HoloTamagotchi 韌體開發小幫手（PlatformIO 包一層，免打一長串）。
#
#   ./dev.sh up      編譯 + 燒錄韌體           （改邏輯後最常用）
#   ./dev.sh mon     看 Serial log
#   ./dev.sh dev     up 完直接接著 mon         （燒完馬上看 log）
#   ./dev.sh build   只編譯不燒
#   ./dev.sh fs      換美術：buildfs + uploadfs（先跑過轉檔工具產 data/）
#   ./dev.sh clean   清掉 build 快取
#
# 為什麼用 `python3 -m platformio`：這台機器 `pio` 不在 PATH，用模組呼叫最穩。
set -euo pipefail
cd "$(dirname "$0")"

PIO="python3 -m platformio"

case "${1:-up}" in
  up|upload)   $PIO run -t upload ;;
  mon|monitor) $PIO device monitor ;;
  dev)         $PIO run -t upload && $PIO device monitor ;;
  build|b)     $PIO run ;;
  fs)          $PIO run -t buildfs && $PIO run -t uploadfs ;;
  clean)       $PIO run -t clean ;;
  *) echo "用法: ./dev.sh [up|mon|dev|build|fs|clean]"; exit 1 ;;
esac
