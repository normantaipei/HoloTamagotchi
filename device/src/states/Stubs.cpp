// Stubs.cpp — POC 最小狀態實作。每幀全幀重組畫面（雙緩衝，主迴圈統一 push）。
#include "Stubs.h"
#include <M5Unified.h>
#include <cstdio>
#include "../Game.h"
#include "../config.h"

namespace {
// 共用：畫底色 + 置中標題 + 一行提示（佔位畫面）。
void drawStub(M5Canvas* cv, const char* title, const char* hint, uint16_t bg) {
    cv->fillScreen(bg);
    cv->setTextDatum(textdatum_t::middle_center);
    cv->setFont(&fonts::Font4);
    cv->setTextColor(config::WHITE);
    cv->drawString(title, config::SCREEN_W / 2, 90);
    cv->setFont(&fonts::Font2);
    cv->setTextColor(config::CYAN);
    cv->drawString(hint, config::SCREEN_W / 2, 150);
}
}  // namespace

StateId Feeding::update() {
    drawStub(game->canvas, "FEEDING", "B: feed & back (stub)", config::DARK);
    if (M5.BtnB.wasPressed()) {
        game->metrics.feed();                    // 維持原效果：飽食度 +
        return StateId::NormalRoom;
    }
    return StateId::None;
}

StateId Petting::update() {
    drawStub(game->canvas, "PETTING", "B: success & back (stub)", config::DARK);
    if (M5.BtnB.wasPressed()) {
        game->metrics.record_rhythm(true);       // 維持原效果：記錄一局（成功）
        return StateId::NormalRoom;
    }
    return StateId::None;
}

StateId Sleeping::update() {
    // 睡眠：暫停扣飽食度、精力回復；按 C 喚醒（搖一搖留待交付物 2）。
    game->metrics.tick(true);
    drawStub(game->canvas, "SLEEPING", "C: wake up (stub)", rgb(0x06141E));
    if (M5.BtnC.wasPressed() || game->metrics.is_rested()) {
        game->metrics.sleep = config::SLEEP_FULL;
        return StateId::NormalRoom;
    }
    return StateId::None;
}

void Ending::onEnter() {
    Metrics& m = game->metrics;
    if (game->endingKind == EndingKind::Runaway) {
        key_ = "end_runaway"; title_ = "RUN AWAY";
    } else {
        float r = m.rhythm_rate();
        if (r > config::END_GOOD_TH)        { key_ = "end_good";   title_ = "GOOD END"; }
        else if (r >= config::END_NORMAL_TH){ key_ = "end_normal"; title_ = "NORMAL END"; }
        else                                { key_ = "end_bad";    title_ = "BAD END"; }
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
