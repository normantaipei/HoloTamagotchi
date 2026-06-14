// State.h — 狀態基底類別（對應 states/base.py）。
//
// 每個狀態實作三個鉤子：
//   onEnter() : 進入狀態時呼叫一次（初始化計時器 / 旗標）
//   update()  : 每幀呼叫，負責「更新邏輯 + 把整張畫面畫進 canvas」，
//               回傳下一個狀態 ID 以切換，回 StateId::None 表示停留。
//   onExit()  : 離開狀態時呼叫一次（清理）。
//
// 雙緩衝設計下，update() 每幀重組整張畫面（不再做局部重畫簿記）；
// 主迴圈在 update() 後統一 pushSprite。
#pragma once
#include "config.h"

class Game;

class State {
public:
    Game* game;
    explicit State(Game* g) : game(g) {}
    virtual ~State() {}
    virtual void    onEnter() {}
    virtual StateId update()  { return StateId::None; }
    virtual void    onExit()  {}
};
