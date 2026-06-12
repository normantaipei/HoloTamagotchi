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

# 嚼食圖位置 / 尺寸（與 draw 參數一致），用來推算嘴巴中心。
EAT_X, EAT_Y, EAT_W, EAT_H = 120, 60, 80, 74
MOUTH = (EAT_X + EAT_W // 2, EAT_Y + EAT_H * 3 // 5)   # 圓嘴中心 ≈ (160, 104)
FOOD_SIZE = 50                                         # 食物起始邊長（同 manifest 預設）
HOLD = (MOUTH[0], MOUTH[1] + 18)                       # 在嘴邊「拿著」的位置（嘴下方一點）

# 動畫節奏：食物直接出現在嘴邊，一口一口咬掉（每咬一口角色低頭咀嚼）。
BITES = 4                                              # 咬幾口（食物分幾塊消失）
BITE_FRAMES = 9                                        # 每一口的幀數（咬下 + 咀嚼）
END_PAD = 6                                            # 吃完後的小停頓
EAT_FRAMES = BITES * BITE_FRAMES + END_PAD             # ~2.1s

CHEW_DIP = 4                                           # 咀嚼時角色上下點頭幅度（px）
CHAR_CLEAR = (EAT_X, EAT_Y, EAT_W, EAT_H + CHEW_DIP)   # 角色重畫前要清掉的範圍（含點頭）


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
            g.assets.draw("eat", EAT_X, EAT_Y, EAT_W, EAT_H)   # 嚼食圖（角色）
            g.lcd.font(g.lcd.FONT_DefaultSmall)
            g.lcd.print("Nom nom...", 130, 216, config.WHITE)  # 在食物路徑下方，整段保留
            self._food_key = FOOD_KEYS[self.menu.selected()]   # 記住玩家選的甜點
            self._food_rect = None                             # 上一格食物殘影範圍
            self._sig = None                                   # 上一幀畫面簽章（相同就不重畫）
            self._eat_started = True
            self.t = 0
        self.t += 1

        if self.t > EAT_FRAMES:
            g.metrics.feed()                          # BasicLifeIndex +
            return config.STATE_NORMAL_ROOM

        self._paint(*self._frame_state(self.t))
        return None

    def _frame_state(self, t):
        """依幀數算出這一幀的 (食物中心x, 中心y, 邊長, 角色點頭位移)。

        食物直接出現在嘴邊，分 BITES 口咬掉：每口先「咬下」缺一塊，再「咀嚼」幾下。
        """
        i = (t - 1) // BITE_FRAMES                           # 第幾口（0-based）
        local = (t - 1) % BITE_FRAMES
        size_after = (FOOD_SIZE * (BITES - i - 1)) // BITES  # 咬掉這口後剩下的大小
        size_before = (FOOD_SIZE * (BITES - i)) // BITES
        if local == 0:
            # 張口咬下：食物頂進嘴裡、角色低頭，這口還沒缺。
            return HOLD[0], MOUTH[1], size_before, CHEW_DIP
        if local == 1:
            # 咬掉一塊：缺一口、角色仍低著頭。
            return HOLD[0], MOUTH[1], size_after, CHEW_DIP
        # 咀嚼：食物回到嘴邊拿著，角色上下小幅點頭。
        return HOLD[0], HOLD[1], size_after, (CHEW_DIP if local % 2 == 0 else 0)

    def _paint(self, cx, cy, size, cdy):
        """重畫角色 + 食物（與上一幀相同則略過，避免靜止時閃爍）。"""
        sig = (cx, cy, size, cdy)
        if sig == self._sig:
            return
        self._sig = sig
        g = self.game
        bg = g.assets.color("bg")
        # 清掉上一格食物殘影 + 角色區（含點頭幅度），再依序重畫。
        if self._food_rect:
            fx, fy, fw, fh = self._food_rect
            g.lcd.fillRect(fx, fy, fw, fh, bg)
        ccx, ccy, ccw, cch = CHAR_CLEAR
        g.lcd.fillRect(ccx, ccy, ccw, cch, bg)
        g.assets.draw("eat", EAT_X, EAT_Y + cdy, EAT_W, EAT_H)   # 角色（咀嚼時低頭）
        if size > 0:
            x, y = cx - size // 2, cy - size // 2
            g.assets.draw(self._food_key, x, y, size, size, show_label=False)  # 無標籤
            self._food_rect = (x, y, size, size)
        else:
            self._food_rect = None
