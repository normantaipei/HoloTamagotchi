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
EVENT_FRAMES = 24                       # 哈欠等事件動圖持續幀數（24×50ms≈1.2s）
CHEER_FRAMES = 60                       # 加油話語顯示幀數（60×50ms≈3.0s）
# 角色 / 事件圖位置：水平置中（114+92/2=160）、垂直置中（中點≈122≈螢幕中心120），
# 頭頂上方留給對話泡泡。尺寸較原始放大約 15%（80×74 → 92×85）。
SPR_X, SPR_Y, SPR_W, SPR_H = 114, 80, 92, 85

# 底部按鈕提示列：水平對齊三顆實體鍵（A 左 / B 中 / C 右）。
# 文字走 i18n（保留多語言空間），左右移動則用箭頭圖案（語言無關）。
HINT_CX = (53, 160, 267)                       # 三顆鍵的水平中心
HINT_TOP = 216                                 # 提示文字頂端 y
HINT_CLEAR = (0, 206, config.SCREEN_W, 34)     # 重畫前要清掉的範圍


class NormalRoom(State):
    def on_enter(self):
        self.menu = Menu(self.game.lcd, MENU_ITEMS)
        # 對話泡泡：尾巴指向角色頭頂中心，浮在角色上方（用預設位置即可）。
        self.dialog = DialogBox(self.game.lcd, tail_x=SPR_X + SPR_W // 2)
        self.menu_open = False
        self.event = None               # [kind, frames_left]，kind = "yawn" | "cheer"
        self.frame = 0
        self.idle_frames = 0            # 連續無動作幀數（按鍵 / 搖晃會歸零）
        self._cur_sprite = None         # 目前顯示的角色圖 key（變了才重畫）
        self._menu_sig = (False, 0)      # 選單狀態簽章（開關 + 選項）
        self._hint_open = False          # 目前提示列對應的開關狀態（變了才重畫）
        self._draw_static()

    def _draw_static(self):
        g = self.game
        g.assets.draw("bg_room", 0, 0)
        g.lcd.font(g.lcd.FONT_DejaVu24)
        g.lcd.print(g.assets.char.NAME[:14], 8, 6, config.WHITE)
        self._draw_hints(False)

    def _draw_hints(self, menu_open):
        """底部按鈕提示列。closed：右鍵=開選單；open：左右=箭頭、中間=確認。"""
        g = self.game
        self._bg_fill(*HINT_CLEAR)
        g.lcd.font(g.lcd.FONT_DefaultSmall)
        cy = HINT_TOP + 7
        if menu_open:
            self._hint_arrow(HINT_CX[0], cy, "left")             # A：上一個
            self._hint_text(i18n.get("btn_select"), HINT_CX[1])  # B：確認
            self._hint_arrow(HINT_CX[2], cy, "right")            # C：下一個
        else:
            self._hint_text(i18n.get("btn_menu"), HINT_CX[2])    # C：開選單

    def _hint_text(self, s, cx):
        lcd = self.game.lcd
        try:
            w = lcd.textWidth(s)
        except Exception:
            w = len(s) * 7                       # 韌體無 textWidth 時的粗估
        lcd.print(s, cx - w // 2, HINT_TOP, config.DARK)

    def _hint_arrow(self, cx, cy, direction):
        # 逐列 fillRect 疊出三角形（跨韌體最穩，與 DialogBox 尾巴同手法）。
        lcd = self.game.lcd
        hr, w = 8, 12                            # 半高、底寬
        for dy in range(-hr, hr + 1):
            span = (w * (hr - abs(dy))) // hr    # 該列寬度，往尖端收斂到 0
            if span <= 0:
                continue
            x = cx - w // 2 if direction == "right" else cx - w // 2 + (w - span)
            lcd.fillRect(x, cy + dy, span, 1, config.DARK)

    def _bg_fill(self, x, y, w, h):
        # 用背景色清掉一塊（移除動態元件）。目前背景為純色塊；之後接背景圖再優化成重貼圖。
        self.game.lcd.fillRect(x, y, w, h, self.game.assets.color("bg"))

    def update(self):
        g = self.game
        m = g.metrics

        # 按鍵狀態整幀只讀一次（wasPressed 會清旗標），同時給「閒置偵測」與「選單」用
        pa, pb, pc = g.btnA.wasPressed(), g.btnB.wasPressed(), g.btnC.wasPressed()

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

        # --- 閒置計時：有按鍵或搖晃 → 歸零，否則累加 ---
        if pa or pb or pc or self._motion_active():
            self.idle_frames = 0
        else:
            self.idle_frames += 1

        # --- 睡眠觸發：精力過低（想睡），或閒置過久（1 小時沒動作）---
        idle_limit = config.IDLE_SLEEP_SEC * config.TICKS_PER_SEC
        if m.is_exhausted() or self.idle_frames >= idle_limit:
            return config.STATE_SLEEPING

        # --- 按鍵 ---
        nxt = self._handle_buttons(pa, pb, pc)
        if nxt:
            return nxt

        # --- 繪製（只畫有變動的部分）---
        self._render()
        self.frame += 1
        return None

    def _motion_active(self):
        """陀螺儀偵測到明顯轉動 → 視為「有動作」。IMU 不可用時恆 False。"""
        s = self.game.imu_motion()
        if s is None:
            return False
        _amag, gmag = s
        return gmag > config.IDLE_MOTION_TH

    def _roll_event(self):
        if self.event is not None:
            return
        m = self.game.metrics
        if m.sleep < config.SLEEP_YAWN_TH and _rnd() < config.P_YAWN:
            self.event = ["yawn", EVENT_FRAMES]
        elif _rnd() < config.P_CHEER:
            self.event = ["cheer", CHEER_FRAMES]

    def _handle_buttons(self, pa, pb, pc):
        if not self.menu_open:
            if pc:
                self.menu_open = True
        else:
            if pa:
                self.menu.move(-1)
            if pc:
                self.menu.move(1)
            if pb:
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
                    # 清掉整顆泡泡（含尾巴）。下一幀角色圖由 cheer 換回 idle 會重畫，
                    # 自動補回被尾巴蓋住的頭頂，不會留下殘影。
                    self._bg_fill(*self.dialog.clear_rect)

        # --- 選單：只在開關 / 移動時重畫 ---
        sig = (self.menu_open, self.menu.selected())
        if sig != self._menu_sig:
            if self.menu_open:
                self.menu.draw(150)
            else:
                self._bg_fill(0, 150, config.SCREEN_W, 40)
            self._menu_sig = sig

        # --- 提示列：只在選單開關切換時重畫（選項移動不影響提示）---
        if self.menu_open != self._hint_open:
            self._draw_hints(self.menu_open)
            self._hint_open = self.menu_open
