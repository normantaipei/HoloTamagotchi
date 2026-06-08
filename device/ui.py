# ui.py — 共用 UI 元件：對話筐(DialogBox) 與 選單高亮框(Menu)
#
# 兩者都是「畫面元件」，不持有遊戲狀態，由各 State 建立並驅動。

import config
import i18n


class DialogBox:
    """漫畫對話泡泡：圓角白框 + 朝下小尾巴，浮在角色頭頂上方。

    文字以 i18n key 傳入，自動依目前語言取字串。tail_x 指向角色頭頂中心。
    clear_rect 對外曝光「含尾巴」的完整範圍，方便狀態用背景色一次蓋掉。
    """

    _TAIL = 12                       # 尾巴高度（px）

    def __init__(self, lcd, x=12, y=34, w=296, h=36, tail_x=160):
        self.lcd = lcd
        self.rect = (x, y, w, h)
        self.tail_x = tail_x
        self.clear_rect = (x, y, w, h + self._TAIL)

    def show(self, key):
        lcd = self.lcd
        x, y, w, h = self.rect
        # 泡泡本體：外白框 + 內深色
        lcd.fillRoundRect(x, y, w, h, 10, config.WHITE)
        lcd.fillRoundRect(x + 2, y + 2, w - 4, h - 4, 8, 0x202030)
        # 朝下小尾巴：用一排遞減寬度的橫條堆出三角形（只靠 fillRect，跨韌體最穩）。
        # 先畫較寬的白色當描邊，再疊較窄的深色當內側，做出帶白邊的尖角。
        ty = y + h
        for i in range(self._TAIL):
            hw = (self._TAIL - 2) - i            # 白色半寬：由寬遞減到尖
            if hw > 0:
                lcd.fillRect(self.tail_x - hw, ty + i, hw * 2, 1, config.WHITE)
            hwi = (self._TAIL - 5) - i           # 深色半寬：比白色窄，留出白邊
            if hwi > 0:
                lcd.fillRect(self.tail_x - hwi, ty + i, hwi * 2, 1, 0x202030)
        # 文字
        lcd.font(lcd.FONT_DejaVu18)
        lcd.print(i18n.get(key), x + 12, y + 9, config.WHITE)


class Menu:
    """水平高亮選單：左右移動高亮框、確認鍵送出。labels 為螢幕字串清單。"""

    def __init__(self, lcd, labels):
        self.lcd = lcd
        self.labels = labels
        self.idx = 0

    def move(self, d):
        self.idx = (self.idx + d) % len(self.labels)

    def selected(self):
        return self.idx

    def draw(self, y=140):
        lcd = self.lcd
        n = len(self.labels)
        cw = config.SCREEN_W // n
        lcd.font(lcd.FONT_DejaVu18)
        for i, lab in enumerate(self.labels):
            x = i * cw
            sel = (i == self.idx)
            bg = config.PINK if sel else config.DARK
            lcd.fillRoundRect(x + 6, y, cw - 12, 40, 8, bg)
            lcd.print(lab, x + 14, y + 12, config.WHITE)
