// AssetManager.h — 資源管理（對應 asset_manager.py）。
//
// 核心原則：優先畫圖片，找不到圖片就畫「色塊 + 文字標籤」佔位（讓邏輯與美術解耦）。
// 全部畫到傳入的 M5Canvas（off-screen），由主迴圈最後一次 pushSprite——這就是
// 根治掃描線的關鍵：圖片不再邊解碼邊逐列貼到面板。
#pragma once
#include <cstdint>
#include <M5GFX.h>   // M5Canvas（M5GFX 裡是 LGFX_Sprite 的別名，需完整定義，不能前向宣告）
#include "assets/characters/character.h"

class AssetManager {
public:
    AssetManager() : canvas_(nullptr), char_(nullptr) {}

    void setCanvas(M5Canvas* canvas) { canvas_ = canvas; }
    void setCharacter(const char* characterId);

    // 目前動畫幀計數（由主迴圈每幀設定，狀態切換時歸零）。多幀素材據此輪播：
    // 顯示幀 = (frame / ANIM_FRAME_HOLD) % 幀數，與 web 模擬器一致。
    void setFrame(int f) { frame_ = f; }

    // 主題色（"bg"/"primary"/"accent"）→ RGB565；未知回 config::DARK。
    uint16_t color(const char* name) const;

    // 這個 key 是否已有可用圖片（美術放好圖且編進韌體）。
    bool hasImage(const char* key) const;

    // 畫一個資源。x/y<0 表示用 manifest 預設尺寸並置中；w/h<0 用預設尺寸。
    // showLabel=false：佔位色塊不畫標籤文字。
    void draw(const char* key, int x = -1, int y = -1,
              int w = -1, int h = -1, bool showLabel = true);

private:
    M5Canvas* canvas_;
    const assets::Character* char_;
    int frame_ = 0;

    const assets::Sprite*     findSprite(const char* key) const;
    const assets::ImageAsset* findImage(const char* key) const;

    // ─── 佔位繪圖（對應 asset_manager.py 的 _placeholder / _pet / _dot / _arc）───
    void placeholder(int x, int y, int w, int h, uint16_t color, const char* label);
    void pet(int x, int y, int w, int h, uint16_t color, const char* expr);
    void dot(int x, int y, int s, uint16_t col);
    void arc(int cx, int my, int halfW, int sag, int t, uint16_t col);
};
