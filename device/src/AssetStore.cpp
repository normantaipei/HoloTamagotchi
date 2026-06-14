// AssetStore.cpp — LittleFS 素材載入實作。
#include "AssetStore.h"
#include <LittleFS.h>
#include <esp_heap_caps.h>
#include <cstring>
#include <cstdio>
#include <Arduino.h>

bool AssetStore::begin() {
    // 不在掛載失敗時格式化（false）：素材分區由外部 uploadfs 燒入，格式化會清掉。
    mounted_ = LittleFS.begin(false);
    if (!mounted_) Serial.println("[AssetStore] LittleFS 掛載失敗 → 走全佔位");
    return mounted_;
}

bool AssetStore::load(const char* characterId) {
    if (!mounted_) return false;

    char path[64];
    std::snprintf(path, sizeof(path), "/%s/manifest.txt", characterId);
    File mf = LittleFS.open(path, "r");
    if (!mf) {
        Serial.printf("[AssetStore] 找不到 %s\n", path);
        return false;
    }

    count_ = 0;
    while (mf.available() && count_ < MAX_IMAGES) {
        String line = mf.readStringUntil('\n');
        line.trim();
        if (line.length() == 0) continue;

        char key[32];
        int w = 0, h = 0, n = 0;
        unsigned transp = 0xFFFF;
        // manifest 一行：key w h frame_count transp(hex)
        if (std::sscanf(line.c_str(), "%31s %d %d %d %x", key, &w, &h, &n, &transp) != 5)
            continue;
        if (w <= 0 || h <= 0 || n <= 0) continue;
        if (n > MAX_FRAMES) n = MAX_FRAMES;

        const size_t frameBytes = (size_t)w * h * 2;
        bool ok = true;
        int loaded = 0;
        for (int i = 0; i < n; ++i) {
            char fp[80];
            std::snprintf(fp, sizeof(fp), "/%s/%s_%d.565", characterId, key, i);
            File ff = LittleFS.open(fp, "r");
            if (!ff || (size_t)ff.size() != frameBytes) {
                Serial.printf("[AssetStore] %s 第 %d 幀缺檔/尺寸不符\n", key, i);
                if (ff) ff.close();
                ok = false;
                break;
            }
            uint16_t* buf = (uint16_t*)heap_caps_malloc(frameBytes, MALLOC_CAP_SPIRAM);
            if (!buf) {
                Serial.printf("[AssetStore] %s PSRAM 配置失敗\n", key);
                ff.close();
                ok = false;
                break;
            }
            size_t rd = ff.read((uint8_t*)buf, frameBytes);
            ff.close();
            if (rd != frameBytes) {
                heap_caps_free(buf);
                ok = false;
                break;
            }
            framePtrs_[count_][i] = buf;
            loaded++;
        }
        if (!ok) {
            // 部分配置的緩衝回收，該資產整個略過（畫面退回佔位）。
            for (int i = 0; i < loaded; ++i)
                heap_caps_free((void*)framePtrs_[count_][i]);
            continue;
        }

        std::strncpy(keys_[count_], key, sizeof(keys_[count_]) - 1);
        keys_[count_][sizeof(keys_[count_]) - 1] = '\0';

        assets::ImageAsset& a = images_[count_];
        a.key = keys_[count_];
        a.frames = framePtrs_[count_];
        a.frame_count = n;
        a.w = w;
        a.h = h;
        a.transp = (uint16_t)transp;
        count_++;
    }
    mf.close();

    Serial.printf("[AssetStore] 載入 %d 個資產（角色 %s）\n", count_, characterId);
    return count_ > 0;
}
