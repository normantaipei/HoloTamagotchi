// NormalRoom.h — STATE_NORMAL_ROOM：普通房間 / 待機（遊戲主樞紐）。
//
// 對應 states/normal_room.py。職責：每秒更新數值、隨機事件（哈欠 / 加油）、
// B 開選單（FEED/PET）、結局判定、睡眠觸發。
//
// 渲染：雙緩衝下每幀由 renderScene() 重組整張畫面（背景 + 角色 + 選單 + 提示），
//   不再做「只重畫變動區塊」的簿記——這正是 C++ 版相對 Python 版的簡化。
#pragma once
#include "State.h"
#include "ui.h"

class NormalRoom : public State {
public:
    explicit NormalRoom(Game* g);
    void    onEnter() override;
    StateId update()  override;

private:
    enum class Ev { None, Yawn, Cheer };

    Menu menu_;
    bool menuOpen_;
    Ev   event_;
    int  eventFrames_;
    int  frame_;
    int  idleFrames_;

    void    rollEvent();
    StateId handleButtons(bool pa, bool pb, bool pc);
    bool    motionActive();
    void    renderScene();
};
