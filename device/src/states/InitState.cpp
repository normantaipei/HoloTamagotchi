// InitState.cpp — 初始化 / 重置實作（對應 init_state.py）。
#include "InitState.h"
#include <M5Unified.h>
#include "../Game.h"
#include "../config.h"

namespace {
constexpr int ANIM_FRAMES = 24;
constexpr int MAXW = 150, MAXH = 150;   // 蛋最大尺寸（統一 150x150 畫布）
}  // namespace

void InitState::onEnter() {
    t_ = 0;
    game->metrics.reset();
    game->endingKind = EndingKind::None;
}

StateId InitState::update() {
    M5Canvas* cv = game->canvas;
    float frac = (float)t_ / (float)ANIM_FRAMES;
    int cx = config::SCREEN_W / 2, cy = config::SCREEN_H / 2;

    // 全幀重組：黑底 + 蛋由 90 放大到 150 模擬破蛋（圖片 / 佔位皆隨進度縮放，
    // AssetManager 會置中對齊；與 web 模擬器 renderEgg 一致）。
    cv->fillScreen(config::BLACK);
    int s = (int)(90 + frac * 60);
    game->assets.draw("egg", cx - s / 2, cy - s / 2, s, s);
    if (!game->assets.hasImage("egg")) {
        cv->setFont(&fonts::Font0);
        cv->setTextColor(config::WHITE);
        cv->setTextDatum(textdatum_t::top_left);
        char buf[40];
        std::snprintf(buf, sizeof(buf), "[ANIM: Egg cracking %d%%]", (int)(frac * 100));
        cv->drawString(buf, 70, 222);
    }

    t_++;
    if (t_ > ANIM_FRAMES) return StateId::NormalRoom;
    return StateId::None;
}
