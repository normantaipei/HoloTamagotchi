// InitState.h — STATE_INIT：初始化與重置（對應 init_state.py）。
//
// 觸發：首次開機，或前一局結束後重新開始。
// 邏輯：清零所有數值，播放「蛋裂開」動畫（佔位色塊隨進度放大），結束切到普通房間。
#pragma once
#include "State.h"

class InitState : public State {
public:
    explicit InitState(Game* g) : State(g) {}
    void    onEnter() override;
    StateId update()  override;
private:
    int t_ = 0;
};
