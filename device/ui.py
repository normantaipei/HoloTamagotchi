# ui.py — 共用 UI 元件：對話筐(DialogBox) 與 選單高亮框(Menu)
#
# 兩者都是「畫面元件」，不持有遊戲狀態，由各 State 建立並驅動。

import config
import i18n


class DialogBox:
    """底部對話筐。文字以 i18n key 傳入，自動依目前語言取字串。"""

    def __init__(self, lcd, x=10, y=185, w=300, h=42):
        self.lcd = lcd
        self.rect = (x, y, w, h)

    def show(self, key):
        lcd = self.lcd
        x, y, w, h = self.rect
        lcd.fillRoundRect(x, y, w, h, 8, config.WHITE)
        lcd.fillRoundRect(x + 2, y + 2, w - 4, h - 4, 6, 0x202030)
        lcd.font(lcd.FONT_DejaVu18)
        lcd.print(i18n.get(key), x + 12, y + 13, config.WHITE)


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
