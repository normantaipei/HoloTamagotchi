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
MAXW, MAXH = 150, 150          # 蛋最大尺寸（統一 150×150 畫布），界定每幀要清掉的區塊


class InitState(State):
    def on_enter(self):
        self.t = 0
        self.game.metrics.reset()
        self.game.ending_kind = None
        self.game.lcd.clear(config.BLACK)

    def update(self):
        g = self.game
        frac = self.t / float(ANIM_FRAMES)
        cx, cy = config.SCREEN_W // 2, config.SCREEN_H // 2
        if g.assets.has_image("egg"):
            # 真實蛋圖：lcd.image 不縮放（忽略 w/h），逐幀重畫只是把同一張 PNG 重新解碼
            # 24 次、徒增卡頓且看不出成長。改成只畫一次、靜置等動畫時間到。
            if self.t == 0:
                g.assets.draw("egg")
        else:
            # 佔位色塊：fillRect 會吃 w/h，所以維持「正方形成長 90→150」的破蛋動畫。
            w = h = int(90 + frac * 60)
            g.lcd.fillRect(cx - MAXW // 2, cy - MAXH // 2, MAXW, MAXH, config.BLACK)
            g.assets.draw("egg", w=w, h=h)
            g.lcd.font(g.lcd.FONT_DefaultSmall)
            g.lcd.fillRect(60, 220, 200, 16, config.BLACK)
            g.lcd.print("[ANIM: Egg cracking %d%%]" % int(frac * 100), 70, 222, config.WHITE)
        self.t += 1
        if self.t > ANIM_FRAMES:
            return config.STATE_NORMAL_ROOM
        return None
