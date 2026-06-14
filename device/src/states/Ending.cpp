// Ending.cpp — 結局實作（對應 ending.py；渲染雙緩衝全幀重組）。
#include "Ending.h"
#include <M5Unified.h>
#include <cstdio>
#include "../Game.h"
#include "../config.h"

void Ending::onEnter() {
    Metrics& m = game->metrics;
    if (game->endingKind == EndingKind::Runaway) {
        key_ = "end_runaway"; title_ = "RUN AWAY";
    } else {
        float r = m.rhythm_rate();
        if (r > config::END_GOOD_TH)         { key_ = "end_good";   title_ = "GOOD END"; }
        else if (r >= config::END_NORMAL_TH) { key_ = "end_normal"; title_ = "NORMAL END"; }
        else                                 { key_ = "end_bad";    title_ = "BAD END"; }
    }
}

StateId Ending::update() {
    M5Canvas* cv = game->canvas;
    cv->fillScreen(config::BLACK);
    game->assets.draw(key_, 85, 36);

    cv->setTextDatum(textdatum_t::top_left);
    cv->setFont(&fonts::Font4);
    cv->setTextColor(config::YELLOW);
    char buf[48];
    std::snprintf(buf, sizeof(buf), "ENDING: %s", title_);
    cv->drawString(buf, 30, 14);

    cv->setFont(&fonts::Font0);
    cv->setTextColor(config::WHITE);
    std::snprintf(buf, sizeof(buf), "Rhythm rate: %d%%", (int)game->metrics.rhythm_rate());
    cv->drawString(buf, 100, 196);
    cv->drawString("Press any button to restart", 50, 210);

    if (M5.BtnA.wasPressed() || M5.BtnB.wasPressed() || M5.BtnC.wasPressed())
        return StateId::Init;
    return StateId::None;
}
