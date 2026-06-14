// color.h — 顏色轉換。
//
// 全專案的「來源色」一律用人類好讀的 0xRRGGBB（與美術 / 設計稿一致），
// 真正畫到 16bpp canvas 時才用 rgb() 轉成 RGB565。
// constexpr：config 的色票常數可在編譯期就轉好，零執行成本。
#pragma once
#include <cstdint>

// 0xRRGGBB -> RGB565（M5GFX 面板 / canvas 的 16-bit 色）
constexpr uint16_t rgb(uint32_t c) {
    return (uint16_t)(((((c >> 16) & 0xFF) & 0xF8) << 8) |
                      ((((c >> 8) & 0xFF) & 0xFC) << 3) |
                      (((c & 0xFF)) >> 3));
}
