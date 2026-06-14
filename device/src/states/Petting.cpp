// Petting.cpp — 摸頭互動實作（對應 petting.py；渲染改雙緩衝全幀重組）。
#include "Petting.h"
#include <M5Unified.h>
#include <cstdio>
#include "../Game.h"
#include "../config.h"

namespace {
// 角色統一 150x150 畫布，置中；上下留 HUD（時間條 / 親密度條 / 文字）。
constexpr int SPR_X = 85, SPR_Y = 38, SPR_W = 150, SPR_H = 150;
constexpr int HEAD_CX = SPR_X + SPR_W / 2;   // 頭中心 x ≈ 160

// 摸頭手：在頭左右兩側擺動（A→左、C→右），落在角色框外側。
constexpr int HAND_Y = 54, HAND_W = 44, HAND_H = 24, HAND_DX = 97;

// 被摸時頭兩側冒出的愛心。
constexpr int HEART = 20, HEART_Y = 64;
constexpr int HEART_X0 = SPR_X - 26;          // 左側
constexpr int HEART_X1 = SPR_X + SPR_W + 6;   // 右側

constexpr int SESSION_SEC  = 8;
constexpr int REACT_FRAMES = 6;
}  // namespace

void Petting::onEnter() {
    t_ = 0;
    frames_ = SESSION_SEC * config::TICKS_PER_SEC;
    strokes_ = 0;
    combo_ = 0;
    maxCombo_ = 0;
    lastDir_ = 0;
    react_ = 0;
    result_ = Result::None;
    showDeco_ = !game->assets.hasImage("pet");
}

StateId Petting::update() {
    return result_ == Result::None ? play() : resultScreen();
}

StateId Petting::play() {
    // 讀鍵（每幀只讀一次）：A=往左摸、C=往右摸。
    int d = 0;
    if (M5.BtnA.wasPressed()) d = -1;
    else if (M5.BtnC.wasPressed()) d = 1;

    if (d != 0) {
        if (d != lastDir_) {              // 來回交替才算有效一摸
            strokes_++;
            combo_++;
            if (combo_ > maxCombo_) maxCombo_ = combo_;
            react_ = REACT_FRAMES;
        } else {
            combo_ = 0;                   // 同一邊連按 → 斷 Combo
        }
        lastDir_ = d;
    }

    renderPlay();                         // 用目前 react_ 畫表情 / 愛心
    if (react_ > 0) react_--;

    t_++;
    // 摸滿 → 成功（可提前達成）；時間到沒滿 → 失敗。
    if (strokes_ >= config::PET_SUCCESS_STROKES) result_ = Result::Success;
    else if (t_ >= frames_) result_ = Result::Fail;
    return StateId::None;
}

void Petting::renderPlay() {
    AssetManager& a = game->assets;
    M5Canvas* cv = game->canvas;

    a.draw("bg_room", 0, 0);

    // 角色表情：被摸時開心，否則待機。
    a.draw(react_ > 0 ? "pet" : "idle", SPR_X, SPR_Y, SPR_W, SPR_H);

    // 頭上的手 + 兩側愛心（佔位裝飾，美術放好 pet 圖後自動關）。
    if (showDeco_) {
        if (lastDir_ != 0) {
            int hx = HEAD_CX + lastDir_ * HAND_DX - HAND_W / 2;
            cv->fillRoundRect(hx, HAND_Y, HAND_W, HAND_H, 6, config::PINK);
        }
        if (react_ > 0) {
            cv->fillRoundRect(HEART_X0, HEART_Y, HEART, HEART, 4, config::RED);
            cv->fillRoundRect(HEART_X1, HEART_Y, HEART, HEART, 4, config::RED);
        }
    }

    // 標題
    cv->setTextDatum(textdatum_t::top_left);
    cv->setFont(&fonts::Font2);
    cv->setTextColor(config::WHITE);
    cv->drawString("Pet the head!  A <-> C", 20, 14);

    // 時間條（剩餘，y=30）
    int tw = config::SCREEN_W - 40;
    int tf = tw * (frames_ - t_) / frames_;
    cv->fillRect(20, 30, tw, 6, config::DARK);
    if (tf > 0) cv->fillRect(20, 30, tf, 6, config::GREEN);

    // 親密度條（strokes/目標，y=190）
    int bw = config::SCREEN_W - 16;
    float ratio = (float)strokes_ / (float)config::PET_SUCCESS_STROKES;
    if (ratio > 1.0f) ratio = 1.0f;
    int bf = (int)(bw * ratio);
    cv->fillRect(8, 190, bw, 12, config::DARK);
    if (bf > 0) cv->fillRect(8, 190, bf, 12, config::PINK);

    // HUD
    cv->setFont(&fonts::Font2);
    cv->setTextColor(config::WHITE);
    char buf[40];
    std::snprintf(buf, sizeof(buf), "Pets %d   Combo %d", strokes_, combo_);
    cv->drawString(buf, 8, 216);
}

StateId Petting::resultScreen() {
    M5Canvas* cv = game->canvas;
    bool win = (result_ == Result::Success);

    cv->fillScreen(config::BLACK);
    game->assets.draw(win ? "emo_success" : "emo_fail", 85, 36);

    cv->setTextDatum(textdatum_t::top_left);
    cv->setFont(&fonts::Font4);
    cv->setTextColor(win ? config::YELLOW : config::RED);
    cv->drawString(win ? "SUCCESS!" : "FAILED...", 95, 18);

    char buf[40];
    cv->setTextColor(config::WHITE);
    std::snprintf(buf, sizeof(buf), "Pets %d / %d", strokes_, config::PET_SUCCESS_STROKES);
    cv->drawString(buf, 80, 190);

    cv->setFont(&fonts::Font0);
    cv->setTextColor(config::DARK);
    std::snprintf(buf, sizeof(buf), "Max combo %d   B: back", maxCombo_);
    cv->drawString(buf, 70, 214);

    if (M5.BtnB.wasPressed()) {
        game->metrics.record_rhythm(win);   // 更新 RhythmGameRate 來源
        return StateId::NormalRoom;
    }
    return StateId::None;
}
