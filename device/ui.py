# ui.py — 共用 UI 元件：對話筐(DialogBox)、選單高亮框(Menu)、底部按鍵提示列(ButtonHints)
#
# 三者都是「畫面元件」，不持有遊戲狀態，由各 State 建立並驅動。

import config
import i18n


class ButtonHints:
    """底部三鍵提示列：對齊三顆實體鍵(A 左 / B 中 / C 右)，每格可放文字或左右箭頭。

    arrow(direction) 用逐列 fillRect 疊出三角形（跨韌體最穩，與 DialogBox 尾巴同手法）。
    clear_rect 對外曝光整列範圍，方便狀態用背景色一次蓋掉再重畫。
    """

    CX = (53, 160, 267)                              # 三顆鍵的水平中心
    TOP = 216                                        # 提示文字頂端 y
    clear_rect = (0, 206, config.SCREEN_W, 34)       # 重畫前要清掉的範圍

    def __init__(self, lcd):
        self.lcd = lcd

    def draw(self, a=None, b=None, c=None):
        """每個 slot 為 None（不畫）/ 文字字串 / ("arrow", "left"|"right")。"""
        lcd = self.lcd
        lcd.font(lcd.FONT_DefaultSmall)
        for cx, slot in zip(self.CX, (a, b, c)):
            if slot is None:
                continue
            if isinstance(slot, tuple):
                self._arrow(cx, slot[1])
            else:
                self._text(slot, cx)

    def _text(self, s, cx):
        lcd = self.lcd
        try:
            w = lcd.textWidth(s)
        except Exception:
            w = len(s) * 7                           # 韌體無 textWidth 時的粗估
        lcd.print(s, cx - w // 2, self.TOP, config.DARK)

    def _arrow(self, cx, direction):
        lcd = self.lcd
        cy = self.TOP + 7
        hr, w = 8, 12                                # 半高、底寬
        for dy in range(-hr, hr + 1):
            span = (w * (hr - abs(dy))) // hr        # 該列寬度，往尖端收斂到 0
            if span <= 0:
                continue
            x = cx - w // 2 if direction == "right" else cx - w // 2 + (w - span)
            lcd.fillRect(x, cy + dy, span, 1, config.DARK)


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

    _FONT_H = 12                         # FONT_DefaultSmall 概略字高（垂直置中用）

    def draw(self, y=140):
        lcd = self.lcd
        n = len(self.labels)
        cw = config.SCREEN_W // n
        # 統一用小字，避免格子寬窄不同造成字型忽大忽小。
        lcd.font(lcd.FONT_DefaultSmall)
        for i, lab in enumerate(self.labels):
            x = i * cw
            sel = (i == self.idx)
            bg = config.PINK if sel else config.DARK
            bx, bw = x + 6, cw - 12
            lcd.fillRoundRect(bx, y, bw, 40, 8, bg)
            try:
                tw = lcd.textWidth(lab)
            except Exception:
                tw = len(lab) * 7        # 韌體無 textWidth 時的粗估
            lcd.print(lab, bx + (bw - tw) // 2, y + (40 - self._FONT_H) // 2, config.WHITE)
