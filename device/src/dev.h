// dev.h — 開發用覆寫（Dev Override）
//
// 只在 config::DEV=true 時有意義。原 Python 版透過 dev_data.py + 延遲載入來避開
// mpremote mount 的巢狀讀檔死鎖——那是 MicroPython 專屬問題，C++ 沒有，
// 故簡化為「編譯期常數」。要快速重現某情境，改這裡重燒即可。
#pragma once
#include "config.h"

class Metrics;  // 前向宣告，避免循環 include

namespace dev {

// 熱路徑（Metrics::tick）會讀這兩個：凍結數值 / 自然數值倍速。
constexpr bool  FREEZE     = false;
constexpr float TIME_SCALE = 1.0f;

// 跳過 IMU 初始化（某些開機情境 IMU 會卡 I²C）。true 時搖一搖靜默停用。
constexpr bool  SKIP_IMU   = false;

// 強制起始狀態（跳過開場蛋動畫直接除錯）；None = 照正常 Init 流程。
constexpr StateId START_STATE = StateId::None;

// 套用數值覆寫到 Metrics（在 reset() 末尾呼叫）。POC 無覆寫 → no-op。
// 要覆寫時在這裡 setattr 對應欄位（見 .cpp）。
void applyMetrics(Metrics& m);

}  // namespace dev
