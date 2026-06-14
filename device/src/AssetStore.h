// AssetStore.h — 開機把素材從 LittleFS 載入 PSRAM。
//
// 素材不再編進韌體：tools/build_fs_assets.py 把 PNG 轉成 raw RGB565 放進 data/<角色>/，
// pio run -t buildfs 打包成 LittleFS 映像燒到獨立 data 分區。本模組開機掛載分區、讀
// manifest.txt，逐資產配 PSRAM 緩衝、把各幀讀進來，組成 ImageAsset 清單交給 AssetManager。
//
// 好處：換美術只要重產素材分區、單獨 uploadfs，不必重編韌體。
// 失敗（掛載失敗 / 缺檔 / PSRAM 不足）→ 該資產略過，AssetManager 自動退回佔位色塊。
#pragma once
#include <cstdint>
#include "assets/characters/character.h"   // assets::ImageAsset

class AssetStore {
public:
    bool begin();                        // 掛載 LittleFS（失敗回 false，不致命）
    bool load(const char* characterId);  // 讀 /<id>/manifest.txt + 各幀 → PSRAM

    const assets::ImageAsset* images() const { return images_; }
    int count() const { return count_; }

private:
    static constexpr int MAX_IMAGES = 32;   // 目前 19 個資產，留餘裕
    static constexpr int MAX_FRAMES = 8;    // 目前最多 egg 4 幀

    assets::ImageAsset images_[MAX_IMAGES];
    const uint16_t*    framePtrs_[MAX_IMAGES][MAX_FRAMES];  // 各資產的幀指標陣列（指向 PSRAM）
    char               keys_[MAX_IMAGES][32];               // key 常駐儲存（ImageAsset.key 指這）
    int                count_ = 0;
    bool               mounted_ = false;
};
