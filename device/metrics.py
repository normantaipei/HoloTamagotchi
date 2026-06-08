# metrics.py — 核心數值系統（Core Metrics System）
#
# 維護 4 個關鍵變數：GrowthIndex / BasicLifeIndex / SleepIndex / RhythmGameRate，
# 並提供結局判定的輔助方法。所有閾值都來自 config，這裡只放邏輯。

import config


def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


class Metrics:
    def __init__(self):
        self.reset()

    def reset(self):
        """重新開始一局：所有數值清零 / 回初始值。"""
        self.growth = 0.0                 # GrowthIndex 成長指數 (0~100)
        self.life = config.LIFE_INIT      # BasicLifeIndex 飽食度（允許 <0 觸發壞結局）
        self.sleep = config.SLEEP_INIT    # SleepIndex 疲勞 (0~100)
        # RhythmGameRate 的統計來源
        self.total_interactions = 0       # 總互動次數（餵食 + 音遊…）
        self.rhythm_plays = 0             # 音遊遊玩次數
        self.rhythm_sa = 0                # 音遊取得 S/A 評價次數
        self.days = 1                     # 遊戲天數（之後接 RTC 計算）

    # --- 隨時間推移（每秒呼叫一次）---
    def tick(self, sleeping=False):
        self.growth = clamp(self.growth + config.GROWTH_PER_SEC, 0, config.GROWTH_MAX)
        if sleeping:
            # 睡眠：暫停扣飽食度，疲勞逐漸恢復
            self.sleep = clamp(self.sleep - config.SLEEP_RECOVER_SEC, 0, 100)
        else:
            self.life = self.life + config.LIFE_PER_SEC     # 不設下限，讓它能 <0
            self.sleep = clamp(self.sleep + config.SLEEP_PER_SEC, 0, 100)

    # --- 互動 ---
    def feed(self, amount=None):
        if amount is None:
            amount = config.LIFE_FEED_GAIN
        self.life = clamp(self.life + amount, -20, 100)
        self.total_interactions += 1

    def record_rhythm(self, grade):
        """音遊一局結束後記錄一次。grade 為 'S'/'A'/'C'/'F'。"""
        self.rhythm_plays += 1
        self.total_interactions += 1
        if grade in ("S", "A"):
            self.rhythm_sa += 1

    # --- RhythmGameRate（音遊互動率，%）---
    def rhythm_rate(self):
        # 公式：音遊遊玩次數 / 總互動次數 * 100%
        if self.total_interactions == 0:
            return 0.0
        return self.rhythm_plays * 100.0 / self.total_interactions

    # --- 結局判定輔助 ---
    def is_bad_end(self):
        return self.life < config.LIFE_BAD_END

    def is_growth_end(self):
        return self.growth >= config.GROWTH_MAX
