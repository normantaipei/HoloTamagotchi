// character.h — 角色資料的「型別定義」（不含任何角色資料）。
//
// 各角色（marine/...）的 character.h include 此檔，填出自己的 THEME/SPRITES/IMAGES。
// AssetManager 只依賴這些型別。
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

// 圖片資源：key -> raw RGB565 資料 + 尺寸 + 透明色鍵（去背）。
struct ImageAsset {
    const char*     key;
    const uint16_t* data;   // 長度 = w*h
    int             w;
    int             h;
    uint16_t        transp; // 透明色鍵（該色像素不畫）；0xFFFF = 不透明
};

struct Character {
    const char*       name;
    uint32_t          theme_bg;
    uint32_t          theme_primary;
    uint32_t          theme_accent;
    const Sprite*     sprites;
    int               sprite_count;
    const ImageAsset* images;
    int               image_count;
};

}  // namespace assets
