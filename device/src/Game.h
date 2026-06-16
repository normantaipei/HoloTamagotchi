// Game.h — 共用情境物件（對應 main.py 的 Game class）。
//
// 持有硬體 + 子系統，傳給各 State 使用，避免到處 include。
// 按鍵直接用 M5.BtnA/B/C（M5Unified），不另存於此。
#pragma once
#include <M5GFX.h>   // M5Canvas（LGFX_Sprite 別名，需完整定義）
#include "config.h"
#include "Metrics.h"
#include "AssetManager.h"
#include "AssetStore.h"

// IMU 一次讀數：加速度大小(g) + 角速度大小(°/s)。ok=false 表示 IMU 不可用 / 讀取失敗。
struct ImuMotion { bool ok; float amag; float gmag; };

class Game {
public:
    M5Canvas*    canvas = nullptr;
    Metrics      metrics;
    AssetManager assets;
    AssetStore   assetStore;               // LittleFS 素材載入（開機填 assets）
    bool         imuOk = false;            // IMU 是否可用（搖一搖 / 動作偵測據此）
    EndingKind   endingKind = EndingKind::None;

    void begin(M5Canvas* cv);              // 綁定 canvas、初始化子系統

    ImuMotion imuMotion();                 // 讀 IMU 動量（方向無關，只回大小）
    bool      isNight();                   // Fire 無 RTC → 恆 false（保留介面）

    // DEV 疊圖：螢幕最下方一行「狀態名 + 核心數值」。雙緩衝下每幀直接畫，無需簽章快取。
    void drawDebugOverlay(StateId stateId);

    // 電量指示：螢幕右上角小電池圖示（綠/黃/紅＋充電閃電）。每幀疊在場景之上。
    void drawBattery();
};

const char* stateName(StateId id);         // 狀態 ID → 顯示名（DEV 疊圖 / log 用）
