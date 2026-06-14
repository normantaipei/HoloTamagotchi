// AssetManager.cpp — 資源管理實作（對應 asset_manager.py，含過渡用寵物臉佔位）。
#include "AssetManager.h"
#include <M5Unified.h>
#include <cstring>
#include <cstdio>
#include "config.h"
#include "assets/characters/registry.h"

namespace {

// ─── <pet-face> 過渡視覺：把「沒有圖片」的角色色塊畫成一隻有表情的小寵物 ───
// 美術把圖放進 manifest IMAGES 後，對應 key 走 pushImage、這裡不再觸發。
// 哪些 key 畫成寵物臉、對應表情；沒列到的（bg_*/food_* 等）維持色塊 + 標籤。
struct ExprMap { const char* key; const char* expr; };
const ExprMap PET_EXPR[] = {
    {"egg", "neutral"},   {"idle", "happy"},      {"yawn", "sleepy"},
    {"cheer", "excited"}, {"pet", "happy"},       {"eat", "eating"},
    {"sleep", "sleepy"},  {"end_good", "excited"},{"end_normal", "neutral"},
    {"end_bad", "happy"}, {"end_runaway", "sad"}, {"emo_success", "excited"},
    {"emo_fail", "sad"},
};
const char* petExpr(const char* key) {
    for (const auto& e : PET_EXPR) if (std::strcmp(e.key, key) == 0) return e.expr;
    return nullptr;
}

}  // namespace

void AssetManager::setCharacter(const char* characterId) {
    char_ = assets::getCharacter(characterId);
}

const assets::Sprite* AssetManager::findSprite(const char* key) const {
    if (!char_) return nullptr;
    for (int i = 0; i < char_->sprite_count; ++i)
        if (std::strcmp(char_->sprites[i].key, key) == 0) return &char_->sprites[i];
    return nullptr;
}

const assets::ImageAsset* AssetManager::findImage(const char* key) const {
    if (!char_) return nullptr;
    for (int i = 0; i < char_->image_count; ++i)
        if (char_->images[i].frames && std::strcmp(char_->images[i].key, key) == 0)
            return &char_->images[i];
    return nullptr;
}

uint16_t AssetManager::color(const char* name) const {
    if (char_) {
        if (std::strcmp(name, "bg") == 0)      return rgb(char_->theme_bg);
        if (std::strcmp(name, "primary") == 0) return rgb(char_->theme_primary);
        if (std::strcmp(name, "accent") == 0)  return rgb(char_->theme_accent);
    }
    return config::DARK;
}

bool AssetManager::hasImage(const char* key) const { return findImage(key) != nullptr; }

void AssetManager::draw(const char* key, int x, int y, int w, int h, bool showLabel) {
    if (!canvas_) return;
    const assets::Sprite* spec = findSprite(key);
    if (!spec) {
        // 未定義 key：畫洋紅警示，開發時一眼看出漏定義（對應 0xFF00FF）。
        canvas_->fillRect(x < 0 ? 0 : x, y < 0 ? 0 : y,
                          w < 0 ? 40 : w, h < 0 ? 20 : h, rgb(0xFF00FF));
        return;
    }
    if (w < 0) w = spec->w;
    if (h < 0) h = spec->h;
    if (x < 0) x = (config::SCREEN_W - w) / 2;
    if (y < 0) y = (config::SCREEN_H - h) / 2;

    // 1) 有對應圖片就畫圖片（raw RGB565，整塊一次貼到 canvas），一律以方框中心對齊。
    const assets::ImageAsset* img = findImage(key);
    if (img) {
        // 多幀輪播：顯示幀 = (frame / HOLD) % 幀數（與 web 模擬器 pickImage 一致）。
        int idx = img->frame_count > 1
                      ? (frame_ / config::ANIM_FRAME_HOLD) % img->frame_count : 0;
        const uint16_t* data = img->frames[idx];
        if (w == img->w && h == img->h) {
            // 尺寸相符：直接貼（最快、最銳利）；置中對齊此時等同貼左上角。
            int ix = x + (w - img->w) / 2;
            int iy = y + (h - img->h) / 2;
            if (img->transp == 0xFFFF) canvas_->pushImage(ix, iy, img->w, img->h, data);
            else canvas_->pushImage(ix, iy, img->w, img->h, data, img->transp);
        } else {
            // 尺寸不同：以方框中心為基準縮放（餵食食物縮小、破殼蛋長大）。
            // pushImageRotateZoom 用最近鄰取樣，邊緣會略鋸齒、但透明色鍵仍精確比對（去背正常）。
            float zx = (float)w / img->w, zy = (float)h / img->h;
            float cx = x + w / 2.0f, cy = y + h / 2.0f;
            if (img->transp == 0xFFFF)
                canvas_->pushImageRotateZoom(cx, cy, img->w / 2.0f, img->h / 2.0f,
                                             0.0f, zx, zy, img->w, img->h, data);
            else
                canvas_->pushImageRotateZoom(cx, cy, img->w / 2.0f, img->h / 2.0f,
                                             0.0f, zx, zy, img->w, img->h, data, img->transp);
        }
        return;
    }
    // 2) 否則畫佔位。角色類 key 畫寵物臉，其餘色塊 + 標籤。
    const char* expr = petExpr(key);
    if (expr)
        pet(x, y, w, h, rgb(spec->color), expr);
    else
        placeholder(x, y, w, h, rgb(spec->color), showLabel ? spec->label : nullptr);
}

void AssetManager::placeholder(int x, int y, int w, int h, uint16_t col, const char* label) {
    canvas_->fillRect(x, y, w, h, col);
    if (!label) return;
    char buf[40];
    std::snprintf(buf, sizeof(buf), "[%s]", label);
    canvas_->setFont(&fonts::Font0);
    canvas_->setTextColor(config::WHITE);
    canvas_->setTextDatum(textdatum_t::top_left);
    canvas_->drawString(buf, x + 3, y + h / 2 - 6);   // 大致置中（夠用即可）
}

// ─── 寵物臉佔位（全程 fillRect/fillRoundRect，與原 Python 一對一）───
void AssetManager::dot(int x, int y, int s, uint16_t col) {
    canvas_->fillRect(x, y, s, s, col);
}

void AssetManager::arc(int cx, int my, int halfW, int sag, int t, uint16_t col) {
    // 用一排小方點堆出拋物線嘴。sag>0 中間下凹（微笑）；sag<0 中間上凸（嘟嘴）。
    const int n = 4;
    int step = halfW / n; if (step < 1) step = 1;
    for (int i = -n; i <= n; ++i) {
        int px = cx + i * step;
        float f = 1.0f - (float)(i * i) / (float)(n * n);
        int py = my + (int)(sag * f);
        canvas_->fillRect(px - t / 2, py - t / 2, t, t, col);
    }
}

void AssetManager::pet(int x, int y, int w, int h, uint16_t color, const char* expr) {
    const uint16_t DARK = config::BLACK, WHITE = config::WHITE;
    int rr = (w < h ? w : h) / 4;
    canvas_->fillRoundRect(x, y, w, h, rr, color);   // 身體：圓角色塊

    int cx = x + w / 2;
    int eye_y = y + h * 2 / 5;
    int eye_dx = w / 4;
    int es = w / 8; if (es < 4) es = 4;              // 眼睛大小
    int t = w / 18; if (t < 2) t = 2;                // 線條粗細
    int mouth_y = y + h * 3 / 5;
    int half = w / 5;
    int lx = cx - eye_dx, rx = cx + eye_dx;

    bool closed = (std::strcmp(expr, "sleepy") == 0 || std::strcmp(expr, "eating") == 0);
    if (closed) {
        for (int ex : {lx, rx}) canvas_->fillRect(ex - es / 2, eye_y, es, t, DARK);
    } else {
        for (int ex : {lx, rx}) {
            canvas_->fillRoundRect(ex - es / 2, eye_y - es / 2, es, es, es / 3, WHITE);
            canvas_->fillRect(ex - t, eye_y - t, t * 2, t * 2, DARK);
        }
    }

    if (std::strcmp(expr, "happy") == 0) {
        arc(cx, mouth_y, half, es / 2, t, DARK);                 // 微笑
    } else if (std::strcmp(expr, "excited") == 0) {
        int mw = w / 3, mh = h / 6;
        canvas_->fillRoundRect(cx - mw / 2, mouth_y - mh / 2, mw, mh, mh / 2, DARK);  // 張嘴笑
        dot(x + w - es, y + es, t * 2, config::YELLOW);          // 火花
    } else if (std::strcmp(expr, "eating") == 0) {
        int mw = w / 5;
        canvas_->fillRoundRect(cx - mw / 2, mouth_y - mw / 2, mw, mw, mw / 2, DARK);  // 圓嘴
    } else if (std::strcmp(expr, "sad") == 0) {
        arc(cx, mouth_y + es / 2, half, -(es / 2), t, DARK);     // 嘟嘴
        dot(lx, eye_y + es, t, config::CYAN);                    // 淚滴
    } else if (std::strcmp(expr, "sleepy") == 0) {
        int zx = x + w - es * 2, zy = y + es;                    // 小 z
        canvas_->fillRect(zx, zy, es, t, WHITE);
        canvas_->fillRect(zx, zy + es, es, t, WHITE);
        arc(cx, mouth_y, half / 2, t, t, DARK);                  // 小嘴
    } else {  // neutral
        canvas_->fillRect(cx - half / 2, mouth_y, half, t, DARK);// 直線嘴
    }
}
