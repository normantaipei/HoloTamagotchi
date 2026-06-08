# states/init_state.py — STATE_INIT：初始化與重置。
#
# 觸發：首次開機，或前一局結束後重新開始。
# 渲染：播放「蛋裂開」動畫（目前為佔位色塊，隨進度放大）。
# 邏輯：動畫結束後清零所有數值，切到 STATE_NORMAL_ROOM。
#
# 防閃爍：整片只在 on_enter 清一次；每幀只重畫蛋所在的小區塊（而非全螢幕 clear）。

import config
from states.base import State

ANIM_FRAMES = 24
MAXW, MAXH = 110, 140          # 蛋最大尺寸，用來界定每幀要清掉的區塊


class InitState(State):
    def on_enter(self):
        self.t = 0
        self.game.metrics.reset()
        self.game.ending_kind = None
        self.game.lcd.clear(config.BLACK)

    def update(self):
        g = self.game
        frac = self.t / float(ANIM_FRAMES)
        w = int(60 + frac * 40)
        h = int(80 + frac * 50)
        # 只清蛋的最大包圍框（置中），不每幀清整片螢幕
        cx, cy = config.SCREEN_W // 2, config.SCREEN_H // 2
        g.lcd.fillRect(cx - MAXW // 2, cy - MAXH // 2, MAXW, MAXH, config.BLACK)
        g.assets.draw("egg", w=w, h=h)
        g.lcd.font(g.lcd.FONT_DefaultSmall)
        g.lcd.fillRect(60, 213, 200, 14, config.BLACK)
        g.lcd.print("[ANIM: Egg cracking %d%%]" % int(frac * 100), 70, 215, config.WHITE)
        self.t += 1
        if self.t > ANIM_FRAMES:
            return config.STATE_NORMAL_ROOM
        return None
