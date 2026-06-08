# states/ending.py — STATE_ENDING：結局。
#
# 來源：normal_room 的 Ending Evaluator 設好 game.ending_kind：
#   "runaway" → 壞結局（離家出走）
#   None      → 正常結局，依 RhythmGameRate 分支：偶像 / 上班族 / 海賊
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
            if r > config.END_IDOL_TH:
                self.key, self.title = "end_idol", "IDOL"
            elif r >= config.END_OFFICE_TH:
                self.key, self.title = "end_office", "OFFICE WORKER"
            else:
                self.key, self.title = "end_pirate", "PIRATE"
        self.game.lcd.clear(config.BLACK)
        self._drawn = False

    def update(self):
        g = self.game
        if not self._drawn:
            g.assets.draw(self.key, 90, 50)
            g.lcd.font(g.lcd.FONT_DejaVu24)
            g.lcd.print("ENDING: " + self.title, 30, 14, config.YELLOW)
            g.lcd.font(g.lcd.FONT_DefaultSmall)
            g.lcd.print("Rhythm rate: %d%%" % int(g.metrics.rhythm_rate()), 100, 196, config.WHITE)
            g.lcd.print("Press any button to restart", 50, 210, config.WHITE)
            self._drawn = True
        if g.btnA.wasPressed() or g.btnB.wasPressed() or g.btnC.wasPressed():
            return config.STATE_INIT
        return None
