// Feeding.cpp — 餵食互動實作（對應 feeding.py；渲染改為雙緩衝全幀重組）。
#include "Feeding.h"
#include <M5Unified.h>
#include <cstdio>
#include "../Game.h"
#include "../config.h"
#include "../i18n.h"

namespace {
const char* const FOOD_KEYS[]   = {"food_0", "food_1", "food_2", "food_3", "food_4"};
const char* const FOOD_LABELS[] = {"Cake", "Pudd", "Tart", "Soda", "Parf"};
constexpr int FOOD_COUNT = 5;

// 嚼食圖位置 / 尺寸（角色統一 150x150 畫布）。
constexpr int EAT_X = 85, EAT_Y = 34, EAT_W = 150, EAT_H = 150;
constexpr int MOUTH_X = EAT_X + EAT_W / 2;             // 嘴中心 x ≈ 160
constexpr int MOUTH_Y = EAT_Y + EAT_H * 3 / 5;         // 圓嘴 y ≈ 124
constexpr int HOLD_Y  = MOUTH_Y + 34;                  // 在嘴邊「拿著」的 y ≈ 158
constexpr int FOOD_DY = -(EAT_H * 20 / 100);           // 食物整體上移 20%（以 150px 角色高為基準 = 30px）
constexpr int FOOD_SIZE = 95;                          // 食物起始邊長

// 動畫節奏：食物分 BITES 口咬掉，每口先咬下、再咀嚼。
constexpr int BITES = 4;
constexpr int BITE_FRAMES = 9;
constexpr int END_PAD = 6;
constexpr int EAT_FRAMES = BITES * BITE_FRAMES + END_PAD;   // ~2.1s
}  // namespace

Feeding::Feeding(Game* g)
    : State(g), menu_(g->canvas, FOOD_LABELS, FOOD_COUNT),
      phase_(Phase::Select), t_(0), foodIdx_(0) {}

void Feeding::onEnter() {
    phase_ = Phase::Select;
    t_ = 0;
    foodIdx_ = 0;
}

StateId Feeding::update() {
    return phase_ == Phase::Select ? selectPhase() : eatPhase();
}

// --- select：甜點 5 選 1 ---
StateId Feeding::selectPhase() {
    if (M5.BtnA.wasPressed()) menu_.move(-1);
    if (M5.BtnC.wasPressed()) menu_.move(1);
    if (M5.BtnB.wasPressed()) {            // 確認 → 進 eat
        foodIdx_ = menu_.selected();
        phase_ = Phase::Eat;
        t_ = 0;
    }
    renderSelect();
    return StateId::None;
}

// --- eat：咀嚼動畫 ---
StateId Feeding::eatPhase() {
    t_++;
    if (t_ > EAT_FRAMES) {
        game->metrics.feed();              // BasicLifeIndex +
        return StateId::NormalRoom;
    }
    renderEat();
    return StateId::None;
}

void Feeding::renderSelect() {
    AssetManager& a = game->assets;
    M5Canvas* cv = game->canvas;
    a.draw("bg_room", 0, 0);

    cv->setFont(&fonts::Font2);
    cv->setTextColor(config::WHITE);
    cv->setTextDatum(textdatum_t::top_left);
    cv->drawString("Choose a sweet", 20, 18);

    a.draw(FOOD_KEYS[menu_.selected()], 112, 38);   // 預覽選中的甜點（95x95 置中偏上）
    menu_.draw(150);

    ButtonHints hints(cv);
    hints.draw(Hint::arrowL(), Hint::txt(i18n::get("btn_eat")), Hint::arrowR());
}

void Feeding::renderEat() {
    AssetManager& a = game->assets;
    M5Canvas* cv = game->canvas;

    // 依幀數算出這一幀的食物 (中心 y, 邊長)：每口先咬下（在嘴上）、再咀嚼（回嘴邊拿著）。
    int i = (t_ - 1) / BITE_FRAMES;                  // 第幾口（0-based）
    int local = (t_ - 1) % BITE_FRAMES;
    int sizeAfter  = FOOD_SIZE * (BITES - i - 1) / BITES;
    int sizeBefore = FOOD_SIZE * (BITES - i) / BITES;
    int fy, size;
    if (local == 0)      { fy = MOUTH_Y + FOOD_DY; size = sizeBefore; }   // 張口咬下（還沒缺）
    else if (local == 1) { fy = MOUTH_Y + FOOD_DY; size = sizeAfter;  }   // 咬掉一塊
    else                 { fy = HOLD_Y  + FOOD_DY; size = sizeAfter;  }   // 咀嚼：回嘴邊拿著

    a.draw("bg_room", 0, 0);
    a.draw("eat", EAT_X, EAT_Y, EAT_W, EAT_H);       // 角色（嚼食）

    // 佔位裝飾：美術放好嚼食圖後自動關掉（可把 Nom nom 直接畫進素材）。
    if (!a.hasImage("eat")) {
        cv->setFont(&fonts::Font0);
        cv->setTextColor(config::WHITE);
        cv->setTextDatum(textdatum_t::top_left);
        cv->drawString("Nom nom...", 130, 216);
    }

    if (size > 0)
        a.draw(FOOD_KEYS[foodIdx_], MOUTH_X - size / 2, fy - size / 2, size, size, /*showLabel=*/false);
}
