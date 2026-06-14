// Petting.h — STATE_PETTING：摸頭互動（對應 petting.py）。
//
// 玩法：左右交替按 A（往左摸）/ C（往右摸）撫摸；只有「方向和上一下不同」才算
//   有效一摸（同一邊連按斷 Combo）。限時內把親密度條摸滿 → 成功；時間到沒滿 → 失敗。
//   被摸時角色露開心表情、頭兩側冒愛心。結算以成功與否更新 RhythmGameRate。
//
// 渲染：雙緩衝全幀重組（不再做局部重畫簿記）。
#pragma once
#include "State.h"

class Petting : public State {
public:
    explicit Petting(Game* g) : State(g) {}
    void    onEnter() override;
    StateId update()  override;

private:
    enum class Result { None, Success, Fail };

    int     t_;
    int     frames_;       // 一局總幀數
    int     strokes_;      // 有效摸頭次數
    int     combo_;
    int     maxCombo_;
    int     lastDir_;      // 上一下方向：-1 左 / +1 右 / 0 尚未開始
    int     react_;        // 剩餘「開心反應」幀數
    Result  result_;
    bool    showDeco_;     // 無 pet 圖時才畫頭上的手 + 愛心（美術放圖後自動關）

    StateId play();
    StateId resultScreen();
    void    renderPlay();
};
