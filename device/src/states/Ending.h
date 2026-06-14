// Ending.h — STATE_ENDING：結局（對應 ending.py）。
//
// 結局分四類（與角色解耦）：
//   離家出走 end_runaway（endingKind==Runaway）；其餘依 rhythm_rate 分支：
//   好 end_good（>END_GOOD_TH）/ 普通 end_normal / 壞 end_bad（<END_NORMAL_TH）。
// 畫對應結局圖（佔位）+ 互動率，按任意鍵 → 回 Init 重新開始。
#pragma once
#include "State.h"

class Ending : public State {
public:
    explicit Ending(Game* g) : State(g) {}
    void    onEnter() override;
    StateId update()  override;
private:
    const char* key_   = "end_normal";
    const char* title_ = "NORMAL END";
};
