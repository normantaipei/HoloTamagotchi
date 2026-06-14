// config.h — 全域設定（螢幕、色票、節奏、核心數值閾值、結局規則、狀態 ID）
//
// 對應原 config.py：所有「可調參數」集中在這裡。程式邏輯不寫死數字，一律從這裡讀，
// 達成「換角色 / 改平衡只動設定」。色票以 0xRRGGBB 經 rgb() 轉 RGB565（編譯期）。
#pragma once
#include "color.h"

namespace config {

// --- 執行模式 ---
// DEV=true：螢幕疊一層 debug overlay（狀態名 + 核心數值）。DEV=false：乾淨展示介面。
constexpr bool DEV = true;

// --- 螢幕 ---
constexpr int SCREEN_W = 320;
constexpr int SCREEN_H = 240;
constexpr int FRAME_MS = 50;                       // 主迴圈每幀間隔（~20fps）
constexpr int TICKS_PER_SEC = 1000 / FRAME_MS;     // 幾幀算一秒

// --- 預設角色 / 語言 ---
constexpr const char* DEFAULT_CHARACTER = "marine";
// 螢幕對話語言。M5GFX 支援 CJK 字型，zh_tw 之後可真的上螢幕（UIFlow1 做不到）；
// POC 先用 en，與原行為一致。
constexpr const char* DEFAULT_LANG = "en";

// --- 通用色票（已轉 RGB565）— Cover Corp 風格：白 + 天藍 accent ---
constexpr uint16_t WHITE      = rgb(0xFFFFFF);
constexpr uint16_t BLACK      = rgb(0x000000);
constexpr uint16_t DARK       = rgb(0x12303D);     // 冷調深板岩
constexpr uint16_t GREEN      = rgb(0x78E682);     // 飽食度
constexpr uint16_t YELLOW     = rgb(0xFFDC50);     // 精力
constexpr uint16_t RED        = rgb(0xF05A5A);     // 警示 / 愛心
constexpr uint16_t PINK       = rgb(0x48C5F4);     // 主互動 accent（Cover 亮天藍，沿用 PINK 名）
constexpr uint16_t CYAN       = rgb(0x51CCE8);     // Cover 淺青
constexpr uint16_t BRAND_DEEP = rgb(0x0099EB);
constexpr uint16_t BRAND_MID  = rgb(0x38ABE0);
constexpr uint16_t BRAND_LITE = rgb(0x51CCE8);
constexpr uint16_t ACCENT     = rgb(0x48C5F4);

// --- 核心數值：初始值與每秒變化量 ---
constexpr float GROWTH_MAX        = 100.0f;
constexpr float GROWTH_PER_SEC    = 0.0001f;
constexpr float LIFE_INIT         = 80.0f;
constexpr float LIFE_PER_SEC      = -0.0003f;
constexpr float LIFE_FEED_GAIN    = 18.0f;
constexpr float LIFE_BAD_END      = 0.0f;
constexpr float SLEEP_INIT          = 100.0f;
constexpr float SLEEP_FULL          = 100.0f;
constexpr float SLEEP_DRAIN_PER_SEC = 0.02f;
constexpr float SLEEP_RECOVER_SEC   = 2.0f;
constexpr float SLEEP_LOW_TH        = 10.0f;
constexpr float SLEEP_YAWN_TH       = 30.0f;

// --- 普通房間：閒置自動睡眠 ---
constexpr int   IDLE_SLEEP_SEC = 20;       // 【驗證用，正式請改回 3600】閒置這麼久 → 睡眠
constexpr float IDLE_MOTION_TH = 30.0f;    // 角速度(°/s)超過此值算「有動作」

// --- 睡眠時間段（Fire 無 RTC，目前不強制觸發，保留）---
constexpr int NIGHT_START_HOUR = 23;
constexpr int NIGHT_END_HOUR   = 7;

// --- IMU 體感：睡覺時「搖一搖」喚醒 ---
constexpr float SHAKE_WAKE_TH = 4.0f;
constexpr float SHAKE_DECAY   = 0.75f;
constexpr float SHAKE_GYRO_W  = 0.02f;

// --- 隨機事件機率（每秒判定一次，0~1）---
constexpr float P_YAWN  = 0.15f;
constexpr float P_CHEER = 0.10f;

// --- 摸頭遊戲 ---
constexpr int PET_SUCCESS_STROKES = 28;

// --- 結局：互動率分支閾值（%）---
constexpr float END_GOOD_TH   = 90.0f;
constexpr float END_NORMAL_TH = 30.0f;

}  // namespace config

// --- 狀態 ID（取代原本的字串鍵；None = 停留在當前狀態）---
enum class StateId {
    None,
    Init,
    NormalRoom,
    Feeding,
    Sleeping,
    Petting,
    Ending,
};

// 結局種類（取代原 game.ending_kind 字串："runaway" / None）
enum class EndingKind { None, Runaway };
