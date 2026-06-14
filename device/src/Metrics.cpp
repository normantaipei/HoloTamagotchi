// Metrics.cpp — 核心數值邏輯（對應 metrics.py，行為一對一）。
#include "Metrics.h"
#include "config.h"
#include "dev.h"

namespace {
inline float clampf(float v, float lo, float hi) {
    return v < lo ? lo : (v > hi ? hi : v);
}
}  // namespace

void Metrics::reset() {
    growth = 0.0f;
    life   = config::LIFE_INIT;
    sleep  = config::SLEEP_INIT;
    total_interactions = 0;
    rhythm_plays = 0;
    rhythm_sa = 0;
    days = 1;
    dev::applyMetrics(*this);   // DEV 數值覆寫（POC 為 no-op）
}

void Metrics::tick(bool sleeping) {
    if (dev::FREEZE) return;                 // DEV：凍結數值
    const float s = dev::TIME_SCALE;         // DEV：自然數值倍速（prod 恆為 1）
    growth = clampf(growth + config::GROWTH_PER_SEC * s, 0.0f, config::GROWTH_MAX);
    if (sleeping) {
        // 睡眠：暫停扣飽食度，精力逐漸回復
        sleep = clampf(sleep + config::SLEEP_RECOVER_SEC * s, 0.0f, config::SLEEP_FULL);
    } else {
        life  = life + config::LIFE_PER_SEC * s;   // 不設下限，讓它能 <0
        sleep = clampf(sleep - config::SLEEP_DRAIN_PER_SEC * s, 0.0f, config::SLEEP_FULL);
    }
}

void Metrics::feed(float amount) {
    if (amount < 0.0f) amount = config::LIFE_FEED_GAIN;
    life = clampf(life + amount, -20.0f, 100.0f);
    total_interactions += 1;
}

void Metrics::record_rhythm(bool success) {
    rhythm_plays += 1;
    total_interactions += 1;
    if (success) rhythm_sa += 1;
}

float Metrics::rhythm_rate() const {
    if (total_interactions == 0) return 0.0f;
    return rhythm_plays * 100.0f / total_interactions;
}

bool Metrics::is_exhausted() const { return sleep <= config::SLEEP_LOW_TH; }
bool Metrics::is_rested()    const { return sleep >= config::SLEEP_FULL; }
bool Metrics::is_bad_end()   const { return life < config::LIFE_BAD_END; }
bool Metrics::is_growth_end()const { return growth >= config::GROWTH_MAX; }
