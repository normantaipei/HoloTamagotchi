// Sleeping.h — STATE_SLEEPING：睡眠（對應 sleeping.py）。
//
// 渲染：背景變暗，「蓋被子睡覺」2 幀輪播（上下微移模擬呼吸）。
// 邏輯：暫停扣飽食度、精力逐漸回復；按 C 或「搖一搖」喚醒，睡飽自然醒。
//
// 搖一搖：每幀讀 IMU 動量（陀螺儀為主 + 加速度變化）丟進漏積分器，持續搖到
//   超過閾值才醒，輕碰 / 放桌上不會誤觸（閾值見 config::SHAKE_*）。IMU 不可用自動停用。
#pragma once
#include "State.h"

class Sleeping : public State {
public:
    explicit Sleeping(Game* g) : State(g) {}
    void    onEnter() override;
    StateId update()  override;

private:
    int   t_ = 0;
    float shake_ = 0.0f;        // 搖晃漏積分值
    float lastAmag_ = 0.0f;     // 上一幀加速度大小
    bool  hasLast_ = false;     // 首幀無前值，先不累積差分

    bool updateShake();         // 更新漏積分，回傳是否超過喚醒閾值
};
