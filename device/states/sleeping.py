# states/sleeping.py — STATE_SLEEPING：睡眠。
#
# 觸發：現實時間進入深夜（RTC / time.localtime），或 SleepIndex 達標。
# 渲染：背景變暗，「蓋被子睡覺」2 幀輪播（佔位）。
# 邏輯：暫停扣飽食度，SleepIndex 逐漸恢復；忽略多數按鍵，C 可喚醒。
#
# 防閃爍：背景 / 文字只在 on_enter 畫一次；睡覺圖只在「換幀」時重畫該區塊。

import config
from states.base import State

SPR_X, SPR_Y, SPR_W, SPR_H = 110, 80, 100, 70
BG = 0x0A0814


class Sleeping(State):
    def on_enter(self):
        self.t = 0
        self._frame = -1
        g = self.game
        g.lcd.clear(BG)
        g.lcd.font(g.lcd.FONT_DefaultSmall)
        g.lcd.print("Zzz...", 70, 56, config.WHITE)
        g.lcd.print("C: wake up", 8, 210, config.DARK)

    def update(self):
        g = self.game
        if self.t % config.TICKS_PER_SEC == 0 and self.t:
            g.metrics.tick(sleeping=True)

        frame = (self.t // 10) % 2      # 2 幀輪播
        if frame != self._frame:
            # 只在換幀時重畫睡覺圖（上下微移 2px 模擬呼吸），不每幀重畫整片
            g.lcd.fillRect(SPR_X, SPR_Y - 2, SPR_W, SPR_H + 4, BG)
            g.assets.draw("sleep", SPR_X, SPR_Y + frame * 2, SPR_W, SPR_H)
            self._frame = frame

        self.t += 1
        # 睡飽且非深夜，或主動按 C 喚醒 → 回普通房間
        if (g.metrics.sleep <= 0 and not g.is_night()) or g.btnC.wasPressed():
            return config.STATE_NORMAL_ROOM
        return None
