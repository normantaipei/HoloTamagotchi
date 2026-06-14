// character.h — 角色資料的「型別定義」（不含任何角色資料）。
//
// 各角色（marine/...）的 character.h include 此檔，填出自己的 THEME/SPRITES。
// 圖片(IMAGES)已不在這裡：改由 AssetStore 開機從 LittleFS 載入。AssetManager 只依賴這些型別。
#pragma once
#include <cstdint>

namespace assets {

// 佔位色塊規格：key -> (0xRRGGBB 色, 螢幕標籤, 預設寬, 預設高)
struct Sprite {
    const char* key;
    uint32_t    color;
    const char* label;
    int         w;
    int         h;
};

// 圖片資源：key -> 多幀 raw RGB565 資料 + 尺寸 + 透明色鍵（去背）。
// frames 指向各幀資料的指標陣列；單張素材 frame_count=1。各幀共用 w/h。
// 注意：圖片資料已不編進韌體——由 AssetStore 開機從 LittleFS 載入 PSRAM 後填這個結構，
// 故 frames 指向 runtime 配置的緩衝（非編譯期 const）。
struct ImageAsset {
    const char*      key;
    const uint16_t** frames;      // frames[i] 長度 = w*h（指向 PSRAM）
    int              frame_count;
    int              w;
    int              h;
    uint16_t         transp;      // 透明色鍵（該色像素不畫）；0xFFFF = 不透明
};

// 角色「靜態」資料：名稱 / 主題色 / 佔位色塊規格。圖片已外移到 LittleFS，
// 不再屬於 Character——由 AssetStore 載入後注入 AssetManager。
struct Character {
    const char*   name;
    uint32_t      theme_bg;
    uint32_t      theme_primary;
    uint32_t      theme_accent;
    const Sprite* sprites;
    int           sprite_count;
};

}  // namespace assets
