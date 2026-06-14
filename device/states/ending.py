# states/ending.py — STATE_ENDING：結局。
#
# 結局分四類（與角色解耦，方便未來換遊戲沿用）：
#   離家出走 end_runaway → game.ending_kind == "runaway"（飽食度歸零的壞收場）
#   其餘依互動率 rhythm_rate 分支：
#     好結局   end_good   （rate >  END_GOOD_TH）
#     普通結局 end_normal （END_NORMAL_TH ≤ rate ≤ END_GOOD_TH）
#     壞結局   end_bad    （rate <  END_NORMAL_TH）
# 渲染對應結局圖（佔位），按任意鍵 → 回 STATE_INIT 重新開始。

import config
from states.base import State


class Ending(State):
    def on_enter(self):
        m = self.game.metrics
        kind = self.game.ending_kind
        if kind == "runaway":
            self.key, self.title = "end_runaway", "RUN AWAY"
        else:
            r = m.rhythm_rate()
            if r > config.END_GOOD_TH:
                self.key, self.title = "end_good", "GOOD END"
            elif r >= config.END_NORMAL_TH:
                self.key, self.title = "end_normal", "NORMAL END"
            else:
                self.key, self.title = "end_bad", "BAD END"
        self.game.lcd.clear(config.BLACK)
        self._drawn = False

    def update(self):
        g = self.game
        if not self._drawn:
            g.assets.draw(self.key, 85, 36)
            g.lcd.font(g.lcd.FONT_DejaVu24)
            g.lcd.print("ENDING: " + self.title, 30, 14, config.YELLOW)
            g.lcd.font(g.lcd.FONT_DefaultSmall)
            g.lcd.print("Rhythm rate: %d%%" % int(g.metrics.rhythm_rate()), 100, 196, config.WHITE)
            g.lcd.print("Press any button to restart", 50, 210, config.WHITE)
            self._drawn = True
        if g.btnA.wasPressed() or g.btnB.wasPressed() or g.btnC.wasPressed():
            return config.STATE_INIT
        return None
