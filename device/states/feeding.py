# states/feeding.py — STATE_FEEDING：餵食互動。
#
# 渲染：普通房間上疊「甜點 5 選 1」選單。
# 按鍵：A/C 左右切換高亮，B 確認。
# 邏輯：確認 → 隱藏選單 → 播「拿起食物嚼」動圖 → BasicLifeIndex 增加 → 回普通房間。
#
# 防閃爍：背景 / 提示只在進入時畫一次；選單只在「移動」時重畫；嚼食圖畫一次後計時。

import config
import i18n
from states.base import State
from ui import Menu, ButtonHints

FOOD_KEYS = ["food_0", "food_1", "food_2", "food_3", "food_4"]
FOOD_LABELS = ["Cake", "Pudd", "Tart", "Soda", "Parf"]
EAT_FRAMES = 18


class Feeding(State):
    def on_enter(self):
        self.menu = Menu(self.game.lcd, FOOD_LABELS)
        self.phase = "select"   # select -> eat
        self.t = 0
        self._menu_idx = -1
        self._eat_started = False
        g = self.game
        g.assets.draw("bg_room", 0, 0)
        g.lcd.font(g.lcd.FONT_DejaVu18)
        g.lcd.print("Choose a sweet", 20, 18, config.WHITE)
        # 底部提示：A/C 左右箭頭切換、B 確認餵食（與普通房間選單同款）。
        ButtonHints(g.lcd).draw(("arrow", "left"),
                                i18n.get("btn_eat"),
                                ("arrow", "right"))

    def update(self):
        if self.phase == "select":
            return self._select()
        return self._eat()

    def _select(self):
        g = self.game
        if g.btnA.wasPressed():
            self.menu.move(-1)
        if g.btnC.wasPressed():
            self.menu.move(1)
        if g.btnB.wasPressed():
            self.phase = "eat"
            return None
        idx = self.menu.selected()
        if idx != self._menu_idx:                 # 只在移動時重畫
            g.assets.draw(FOOD_KEYS[idx], 135, 60)   # 預覽選中的甜點
            self.menu.draw(150)
            self._menu_idx = idx
        return None

    def _eat(self):
        g = self.game
        if not self._eat_started:
            g.assets.draw("bg_room", 0, 0)
            g.assets.draw("eat", 120, 60, 80, 74)    # 嚼食圖（佔位，畫一次）
            g.lcd.font(g.lcd.FONT_DefaultSmall)
            g.lcd.print("Nom nom...", 122, 150, config.WHITE)
            self._eat_started = True
            self.t = 0
        self.t += 1
        if self.t > EAT_FRAMES:
            g.metrics.feed()                          # BasicLifeIndex +
            return config.STATE_NORMAL_ROOM
        return None
