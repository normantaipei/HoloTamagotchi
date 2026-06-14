// Feeding.h — STATE_FEEDING：餵食互動（對應 feeding.py）。
//
// 流程：select（甜點 5 選 1，A/C 切換、B 確認）→ eat（食物出現在嘴邊、分 4 口咬掉的
//   咀嚼動畫）→ BasicLifeIndex 增加 → 回普通房間。
//
// 渲染：雙緩衝下每幀全幀重組（背景 + 角色 + 食物 + 選單/提示），不做局部重畫簿記。
#pragma once
#include "State.h"
#include "ui.h"

class Feeding : public State {
public:
    explicit Feeding(Game* g);
    void    onEnter() override;
    StateId update()  override;

private:
    enum class Phase { Select, Eat };
    Menu  menu_;
    Phase phase_;
    int   t_;
    int   foodIdx_;   // 進入 eat 時鎖定玩家選的甜點

    StateId selectPhase();
    StateId eatPhase();
    void    renderSelect();
    void    renderEat();
};
