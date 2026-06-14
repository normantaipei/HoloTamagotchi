// Metrics.h — 核心數值系統（對應 metrics.py）。
//
// 維護 4 個關鍵變數：growth / life / sleep / RhythmGameRate，並提供結局判定輔助。
// 所有閾值來自 config，這裡只放邏輯。
#pragma once

class Metrics {
public:
    float growth;              // GrowthIndex 成長指數 (0~100)
    float life;                // BasicLifeIndex 飽食度（允許 <0 觸發壞結局）
    float sleep;               // 精力值 (0~100)：醒著降、睡覺升
    int   total_interactions;  // 總互動次數
    int   rhythm_plays;        // 音遊（摸頭）遊玩次數
    int   rhythm_sa;           // 取得 S/A 評價次數
    int   days;                // 遊戲天數

    Metrics() { reset(); }

    void reset();                       // 重新開始一局：清零 / 回初始值
    void tick(bool sleeping = false);   // 隨時間推移（每秒呼叫一次）
    void feed(float amount = -1.0f);    // 餵食（amount<0 用預設 LIFE_FEED_GAIN）
    void record_rhythm(bool success);   // 摸頭一局結束記錄

    float rhythm_rate() const;          // 音遊互動率 (%)
    bool  is_exhausted() const;         // 精力過低 → 想睡
    bool  is_rested() const;            // 精力已滿 → 睡飽
    bool  is_bad_end() const;           // 飽食度 < 閾值 → 壞結局
    bool  is_growth_end() const;        // 成長滿值 → 正常結局
};
