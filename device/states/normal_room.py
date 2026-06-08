# states/normal_room.py — STATE_NORMAL_ROOM：普通房間 / 待機（遊戲主樞紐）。
#
# 職責：
#   - Main Loop：每秒更新核心數值。
#   - 隨機事件：疲勞高 → 打哈欠；一般 → 機率「加油」並叫出對話筐。
#   - 按鍵：B 叫出選單（FEED / GAME），選 FEED→餵食、GAME→音遊。
#   - 結局判定（Ending Evaluator）：壞結局優先，再判成長結局。
#   - 睡眠觸發：疲勞達標或進入深夜 → 睡眠。
#
# 渲染原則（防閃爍）：背景與標題只在 on_enter 畫一次；角色 / 對話筐 / 選單
#   只有在「內容改變」時才重畫該區塊，不每幀重畫整個畫面。

import config
import i18n
from states.base import State
from ui import Menu, DialogBox

# 隨機數（MicroPython 用 urandom；桌機測試 fallback 到 random）
try:
    from urandom import getrandbits
    def _rnd():
        return getrandbits(16) / 65535.0
except ImportError:
    import random
    def _rnd():
        return random.random()

MENU_ITEMS = ["FEED", "GAME"]
EVENT_FRAMES = 24                       # 單次事件動圖持續幀數
SPR_X, SPR_Y, SPR_W, SPR_H = 120, 40, 80, 74   # 角色 / 事件圖位置


class NormalRoom(State):
    def on_enter(self):
        self.menu = Menu(self.game.lcd, MENU_ITEMS)
        self.dialog = DialogBox(self.game.lcd, y=150, h=40)
        self.menu_open = False
        self.event = None               # [kind, frames_left]，kind = "yawn" | "cheer"
        self.frame = 0
        self._cur_sprite = None         # 目前顯示的角色圖 key（變了才重畫）
        self._menu_sig = (False, 0)      # 選單狀態簽章（開關 + 選項）
        self._draw_static()

    def _draw_static(self):
        g = self.game
        g.assets.draw("bg_room", 0, 0)
        g.lcd.font(g.lcd.FONT_DejaVu24)
        g.lcd.print(g.assets.char.NAME[:14], 8, 6, config.WHITE)
        g.lcd.font(g.lcd.FONT_DefaultSmall)
        g.lcd.print("B: Menu", 8, 210, config.DARK)

    def _bg_fill(self, x, y, w, h):
        # 用背景色清掉一塊（移除動態元件）。目前背景為純色塊；之後接背景圖再優化成重貼圖。
        self.game.lcd.fillRect(x, y, w, h, self.game.assets.color("bg"))

    def update(self):
        g = self.game
        m = g.metrics

        # --- 每秒一次：更新數值 + 擲隨機事件 ---
        if self.frame % config.TICKS_PER_SEC == 0 and self.frame:
            m.tick(sleeping=False)
            self._roll_event()

        # --- 結局判定（壞結局優先）---
        if m.is_bad_end():
            g.ending_kind = "runaway"
            return config.STATE_ENDING
        if m.is_growth_end():
            g.ending_kind = None
            return config.STATE_ENDING

        # --- 睡眠觸發 ---
        if m.sleep >= config.SLEEP_FORCE_TH or g.is_night():
            return config.STATE_SLEEPING

        # --- 按鍵 ---
        nxt = self._handle_buttons()
        if nxt:
            return nxt

        # --- 繪製（只畫有變動的部分）---
        self._render()
        self.frame += 1
        return None

    def _roll_event(self):
        if self.event is not None:
            return
        m = self.game.metrics
        if m.sleep > config.SLEEP_YAWN_TH and _rnd() < config.P_YAWN:
            self.event = ["yawn", EVENT_FRAMES]
        elif _rnd() < config.P_CHEER:
            self.event = ["cheer", EVENT_FRAMES]

    def _handle_buttons(self):
        g = self.game
        if not self.menu_open:
            if g.btnB.wasPressed():
                self.menu_open = True
        else:
            if g.btnA.wasPressed():
                self.menu.move(-1)
            if g.btnC.wasPressed():
                self.menu.move(1)
            if g.btnB.wasPressed():
                self.menu_open = False
                return config.STATE_FEEDING if self.menu.selected() == 0 else config.STATE_MINI_GAME
        return None

    def _render(self):
        g = self.game

        # --- 角色 / 事件動圖：只在 key 改變時重畫（避免每幀重畫造成閃爍）---
        key = self.event[0] if self.event else "idle"
        if key != self._cur_sprite:
            g.assets.draw(key, SPR_X, SPR_Y, SPR_W, SPR_H)
            if key == "cheer":
                self.dialog.show("cheer_msg_01")
            self._cur_sprite = key

        # 事件倒數結束 → 清掉對話筐（角色圖下一輪會換回 idle 蓋掉事件圖）
        if self.event:
            self.event[1] -= 1
            if self.event[1] <= 0:
                was_cheer = (self.event[0] == "cheer")
                self.event = None
                if was_cheer:
                    self._bg_fill(*self.dialog.rect)

        # --- 選單：只在開關 / 移動時重畫 ---
        sig = (self.menu_open, self.menu.selected())
        if sig != self._menu_sig:
            if self.menu_open:
                self.menu.draw(150)
            else:
                self._bg_fill(0, 150, config.SCREEN_W, 40)
            self._menu_sig = sig
