// NormalRoom.cpp — 普通房間實作（對應 normal_room.py，邏輯一對一；渲染改全幀重組）。
#include "NormalRoom.h"
#include <M5Unified.h>
#include "../Game.h"
#include "../config.h"
#include "../i18n.h"
#include "../rng.h"

namespace {
// 角色 / 事件圖位置：統一 150x150 畫布，水平置中。
constexpr int SPR_X = 85, SPR_Y = 38, SPR_W = 150, SPR_H = 150;
constexpr int EVENT_FRAMES = 24;   // 哈欠等事件動圖持續幀數（~1.2s）
constexpr int CHEER_FRAMES = 60;   // 加油話語顯示幀數（~3.0s）

const char* const MENU_ITEMS[] = {"FEED", "PET"};
constexpr int MENU_COUNT = 2;
}  // namespace

NormalRoom::NormalRoom(Game* g)
    : State(g),
      menu_(g->canvas, MENU_ITEMS, MENU_COUNT),
      menuOpen_(false), event_(Ev::None), eventFrames_(0),
      frame_(0), idleFrames_(0) {}

void NormalRoom::onEnter() {
    menuOpen_ = false;
    event_ = Ev::None;
    eventFrames_ = 0;
    frame_ = 0;
    idleFrames_ = 0;
}

StateId NormalRoom::update() {
    Metrics& m = game->metrics;

    // 按鍵整幀只讀一次（wasPressed 會清旗標），給「閒置偵測」與「選單」共用。
    bool pa = M5.BtnA.wasPressed();
    bool pb = M5.BtnB.wasPressed();
    bool pc = M5.BtnC.wasPressed();

    // --- 每秒一次：更新數值 + 擲隨機事件 ---
    if (frame_ % config::TICKS_PER_SEC == 0 && frame_) {
        m.tick(false);
        rollEvent();
    }

    // --- 閒置計時：有按鍵或搖晃 → 歸零，否則累加 ---
    if (pa || pb || pc || motionActive()) idleFrames_ = 0;
    else idleFrames_++;

    // --- 按鍵（選單開關 / 移動 / 確認）---
    StateId btnNext = handleButtons(pa, pb, pc);

    // --- 事件倒數 ---
    if (event_ != Ev::None) {
        if (--eventFrames_ <= 0) event_ = Ev::None;
    }

    // --- 全幀重組畫面（off-screen，主迴圈統一 push）---
    renderScene();
    frame_++;

    // --- 轉場判定（壞結局優先 → 成長結局 → 睡眠 → 選單選擇）---
    if (m.is_bad_end())    { game->endingKind = EndingKind::Runaway; return StateId::Ending; }
    if (m.is_growth_end()) { game->endingKind = EndingKind::None;    return StateId::Ending; }
    int idleLimit = config::IDLE_SLEEP_SEC * config::TICKS_PER_SEC;
    if (m.is_exhausted() || idleFrames_ >= idleLimit) return StateId::Sleeping;
    if (btnNext != StateId::None) return btnNext;
    return StateId::None;
}

bool NormalRoom::motionActive() {
    ImuMotion s = game->imuMotion();
    return s.ok && s.gmag > config::IDLE_MOTION_TH;
}

void NormalRoom::rollEvent() {
    if (event_ != Ev::None) return;
    Metrics& m = game->metrics;
    if (m.sleep < config::SLEEP_YAWN_TH && rnd() < config::P_YAWN) {
        event_ = Ev::Yawn;  eventFrames_ = EVENT_FRAMES;
    } else if (rnd() < config::P_CHEER) {
        event_ = Ev::Cheer; eventFrames_ = CHEER_FRAMES;
    }
}

StateId NormalRoom::handleButtons(bool pa, bool pb, bool pc) {
    if (!menuOpen_) {
        if (pc) menuOpen_ = true;       // C：開選單
    } else {
        if (pa) menu_.move(-1);         // A：上一個
        if (pc) menu_.move(1);          // C：下一個
        if (pb) {                       // B：確認
            menuOpen_ = false;
            return menu_.selected() == 0 ? StateId::Feeding : StateId::Petting;
        }
    }
    return StateId::None;
}

void NormalRoom::renderScene() {
    AssetManager& a = game->assets;
    M5Canvas* cv = game->canvas;

    // 背景
    a.draw("bg_room", 0, 0);

    // 角色 / 事件動圖
    const char* key = (event_ == Ev::Yawn)  ? "yawn"
                    : (event_ == Ev::Cheer) ? "cheer"
                                            : "idle";
    a.draw(key, SPR_X, SPR_Y, SPR_W, SPR_H);

    // 加油事件：頭頂上方對話泡泡
    if (event_ == Ev::Cheer) {
        DialogBox dialog(cv, 12, 12, 296, 36, SPR_X + SPR_W / 2);
        dialog.show("cheer_msg_01");
    }

    // 選單（開啟時）
    if (menuOpen_) menu_.draw(150);

    // 底部按鍵提示列
    ButtonHints hints(cv);
    if (menuOpen_)
        hints.draw(Hint::arrowL(), Hint::txt(i18n::get("btn_select")), Hint::arrowR());
    else
        hints.draw(Hint::none(), Hint::none(), Hint::txt(i18n::get("btn_menu")));
}
