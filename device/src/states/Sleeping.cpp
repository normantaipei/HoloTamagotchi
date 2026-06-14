// Sleeping.cpp — 睡眠實作（對應 sleeping.py；渲染改雙緩衝全幀重組）。
#include "Sleeping.h"
#include <M5Unified.h>
#include <cmath>
#include <cstdio>
#include "../Game.h"
#include "../config.h"

namespace {
constexpr int SPR_X = 85, SPR_Y = 50, SPR_W = 150, SPR_H = 150;
const uint16_t BG = rgb(0x06141E);   // Cover 夜間深海軍藍
}  // namespace

void Sleeping::onEnter() {
    t_ = 0;
    shake_ = 0.0f;
    hasLast_ = false;
}

bool Sleeping::updateShake() {
    ImuMotion s = game->imuMotion();
    if (!s.ok) return false;
    float inst = s.gmag * config::SHAKE_GYRO_W;
    if (hasLast_) inst += std::fabs(s.amag - lastAmag_);
    lastAmag_ = s.amag;
    hasLast_ = true;
    shake_ = shake_ * config::SHAKE_DECAY + inst;
    return shake_ > config::SHAKE_WAKE_TH;
}

StateId Sleeping::update() {
    M5Canvas* cv = game->canvas;

    if (t_ % config::TICKS_PER_SEC == 0 && t_) game->metrics.tick(true);

    int frame = (t_ / 10) % 2;          // 2 幀輪播（呼吸）
    bool shaken = updateShake();        // 每幀都要更新漏積分（才能正確累積 / 衰減）
    t_++;

    // --- 全幀重組 ---
    cv->fillScreen(BG);
    game->assets.draw("sleep", SPR_X, SPR_Y + frame * 2, SPR_W, SPR_H);   // 上下微移 2px
    cv->setTextDatum(textdatum_t::top_left);
    cv->setFont(&fonts::Font0);
    // 佔位裝飾：美術放好睡覺圖後自動關掉（可把 Zzz 直接畫進素材）。
    if (!game->assets.hasImage("sleep")) {
        cv->setTextColor(config::WHITE);
        cv->drawString("Zzz...", 50, 36);
    }
    cv->setTextColor(config::DARK);
    cv->drawString(game->imuOk ? "Shake or C: wake up" : "C: wake up", 8, 210);
    // DEV：左上角即時顯示搖晃積分值，方便上板校準閾值。
    if (config::DEV && game->imuOk) {
        cv->setTextColor(config::GREEN);
        char buf[32];
        std::snprintf(buf, sizeof(buf), "shake %.1f/%.0f", shake_, config::SHAKE_WAKE_TH);
        cv->drawString(buf, 4, 2);
    }

    // --- 喚醒：按 C 或搖一搖 → 精力回滿、保持清醒；睡飽（精力滿）→ 自然醒 ---
    if (M5.BtnC.wasPressed() || shaken) {
        game->metrics.sleep = config::SLEEP_FULL;
        return StateId::NormalRoom;
    }
    if (game->metrics.is_rested()) return StateId::NormalRoom;
    return StateId::None;
}
