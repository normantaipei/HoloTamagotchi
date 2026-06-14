// character.h — 角色 manifest（寶鐘瑪琳 / Houshou Marine）。
//
// 對應原 character.py：定義「一個角色」的資料，不含遊戲邏輯。型別來自 ../character.h。
//   THEME   : 色彩主題（0xRRGGBB）
//   SPRITES : 每個資源的佔位色塊規格 key -> (色, 螢幕標籤, 預設寬, 預設高)
//   IMAGES  : 每個資源對應的 raw RGB565 圖（編譯進韌體，來源 web/demo-assets）。
//
// 美術流程：把新 PNG 換進 web/demo-assets，跑 tools/build_assets.py 重新產生
//           images/*.h 與 images/assets.h（MARINE_IMAGES 巨集），程式邏輯不用改。
//
// 【統一畫布】所有「角色」一律 150x150 正方形畫布置中；食物 95x95；背景 320x240。
#pragma once
#include "../character.h"
#include "images/assets.h"   // 由 build_assets.py 產生：各圖標頭 + MARINE_IMAGES 巨集

namespace assets {
namespace marine {

constexpr int CHAR_W = 150;
constexpr int CHAR_H = 150;

inline const Sprite SPRITES[] = {
    {"egg",         0xF0E6C8, "Egg",          CHAR_W, CHAR_H},
    {"idle",        0xF0405A, "Marine idle",  CHAR_W, CHAR_H},
    {"yawn",        0xC0506A, "ANIM: Yawn",   CHAR_W, CHAR_H},
    {"cheer",       0xFF6080, "ANIM: Cheer",  CHAR_W, CHAR_H},
    {"pet",         0xFF7090, "ANIM: Pet",    CHAR_W, CHAR_H},
    {"eat",         0xF07090, "ANIM: Eat",    CHAR_W, CHAR_H},
    {"sleep",       0x405080, "ANIM: Sleep",  CHAR_W, CHAR_H},
    {"bg_room",     0x2A1020, "BG: Normal Room", 320, 240},
    {"end_good",    0xFFD24A, "END: Good (Idol)",    CHAR_W, CHAR_H},
    {"end_normal",  0x6A86C0, "END: Normal (Office)",CHAR_W, CHAR_H},
    {"end_bad",     0x9A3A3A, "END: Bad (Pirate)",   CHAR_W, CHAR_H},
    {"end_runaway", 0x404048, "END: Run away",       CHAR_W, CHAR_H},
    {"emo_success", 0xFFD24A, "EMO: Success", CHAR_W, CHAR_H},
    {"emo_fail",    0x9A6A6A, "EMO: Fail",    CHAR_W, CHAR_H},
    {"food_0",      0xF0A0B0, "Cake",    95, 95},
    {"food_1",      0xC08050, "Pudding", 95, 95},
    {"food_2",      0xF0D060, "Tart",    95, 95},
    {"food_3",      0xB0E0F0, "Soda",    95, 95},
    {"food_4",      0xE07070, "Parfait", 95, 95},
};

// key -> 圖片。由 MARINE_IMAGES 巨集（images/assets.h）展開，來源 web/demo-assets。
inline const ImageAsset IMAGES[] = {
    MARINE_IMAGES
    {nullptr, nullptr, 0, 0, 0xFFFF},   // 佔位空項（C++ 不允許 0 長度陣列；findImage 會跳過 null）
};

inline const Character CHARACTER = {
    "Houshou Marine",
    0x2A1020,   // bg 深紅房間底
    0xF0405A,   // primary 瑪琳紅
    0xFFC857,   // accent 金
    SPRITES, (int)(sizeof(SPRITES) / sizeof(SPRITES[0])),
    // image_count 用陣列長度；findImage 以 data!=null 過濾佔位空項，故安全。
    IMAGES,  (int)(sizeof(IMAGES) / sizeof(IMAGES[0])),
};

}  // namespace marine
}  // namespace assets
