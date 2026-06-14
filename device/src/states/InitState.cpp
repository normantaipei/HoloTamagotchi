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

    // 全幀重組：黑底 + 蛋（佔位色塊由 90 放大到 150 模擬破蛋）。
    cv->fillScreen(config::BLACK);
    if (game->assets.hasImage("egg")) {
        game->assets.draw("egg");                 // 真實蛋圖：原生尺寸置中
    } else {
        int s = (int)(90 + frac * 60);
        game->assets.draw("egg", -1, -1, s, s);   // 佔位：成長中的方塊
        cv->setFont(&fonts::Font0);
        cv->setTextColor(config::WHITE);
        cv->setTextDatum(textdatum_t::top_left);
        char buf[40];
        std::snprintf(buf, sizeof(buf), "[ANIM: Egg cracking %d%%]", (int)(frac * 100));
        cv->drawString(buf, 70, 222);
    }
    (void)cx; (void)cy;

    t_++;
    if (t_ > ANIM_FRAMES) return StateId::NormalRoom;
    return StateId::None;
}
