# states/petting.py — STATE_PETTING：摸頭互動（取代原音遊）。
#
# 玩法：在頭頂上方有一隻「摸頭手」，左右交替按 A（往左摸）/ C（往右摸）來撫摸。
#   只有「方向和上一下不同」才算有效一摸（模擬來回撫摸的節奏）；同一邊連按不計、
#   並會斷 Combo。限時一段時間內，把親密度條「摸滿」就成功；時間到還沒滿 → 失敗。
#   結果只有「成功 / 失敗」兩種。被摸時角色露出開心表情、頭兩側冒出愛心。
#
# 結算：以成功與否呼叫 metrics.record_rhythm(success) 更新 RhythmGameRate（結局分支來源）。
#
# 防閃爍（與其它狀態一致）：背景 / 標題只畫一次；摸頭手只在方向改變時重畫，
#   角色只在表情 key 改變時重畫，親密度條 / 時間條 / HUD 只在數字變動時重畫。

import config
from states.base import State

# 角色位置：統一 150×150 畫布，置中。摸頭畫面上下有 HUD（標題 / 時間條 / 親密度條 / HUD 文字），
# 為了容下 150 的角色，時間條上移到 y=30、親密度條下移到 y=190，角色佔 38..188。
SPR_X, SPR_Y, SPR_W, SPR_H = 85, 38, 150, 150
HEAD_CX = SPR_X + SPR_W // 2          # 頭中心 x ≈ 160

# 摸頭手：因角色填滿、頭頂無留白，改在「頭的左右兩側」擺動（A→左、C→右）。
HAND_Y, HAND_W, HAND_H = 54, 44, 24
HAND_DX = 97                          # 手相對頭中心的水平位移（落在角色框外側）

# 被摸時頭兩側冒出的愛心（放在頭左右兩側，不蓋到角色）。
HEART = 20
HEART_Y = 64
HEART_X = (SPR_X - 26, SPR_X + SPR_W + 6)

SESSION_SEC  = 8                      # 一次互動時長（秒）
REACT_FRAMES = 6                      # 每摸一下角色露開心表情 / 愛心的幀數

# 成功門檻（有效摸頭次數）＝親密度條滿格。達標即成功、時間到沒達標即失敗。見 config。


class Petting(State):
    def on_enter(self):
        self.t = 0
        self.frames = SESSION_SEC * config.TICKS_PER_SEC
        self.strokes = 0
        self.combo = 0
        self.max_combo = 0
        self.last_dir = 0             # 上一下方向：-1 左 / +1 右 / 0 尚未開始
        self.react = 0               # 剩餘「開心反應」幀數
        self.result = None
        self._cur_sprite = None      # 目前角色表情 key（變了才重畫）
        self._hand_dir = None        # 目前畫出的手方向（變了才重畫）
        self._hearts_on = False      # 愛心目前是否顯示
        self._bar_fill = -1          # 親密度條目前填滿寬度
        self._time_fill = -1         # 時間條目前剩餘寬度
        self._hud = None
        self._drawn = False
        g = self.game
        # 佔位裝飾（頭上的摸頭手 + 兩側愛心）：美術放好摸頭圖後自動關掉，
        # 可把手 / 愛心等頭上元素直接畫進素材裡，完全自由發揮。
        self._show_deco = not g.assets.has_image("pet")
        lcd = g.lcd
        g.assets.draw("bg_room", 0, 0)
        lcd.font(lcd.FONT_DejaVu18)
        lcd.print("Pet the head!  A <-> C", 20, 14, config.WHITE)

    def update(self):
        if self.result is not None:
            return self._result_screen()
        return self._play()

    # --- 互動中 ---
    def _play(self):
        g = self.game
        lcd = g.lcd
        bg = g.assets.color("bg")

        # 讀鍵（每幀只讀一次）：A=往左摸、C=往右摸。
        d = 0
        if g.btnA.wasPressed():
            d = -1
        elif g.btnC.wasPressed():
            d = 1

        if d != 0:
            if d != self.last_dir:            # 來回交替才算有效一摸
                self.strokes += 1
                self.combo += 1
                if self.combo > self.max_combo:
                    self.max_combo = self.combo
                self.react = REACT_FRAMES
            else:
                self.combo = 0                # 同一邊連按 → 斷 Combo
            self.last_dir = d

        # 摸頭手：方向改變時重畫（擦掉另一邊、畫新一邊）。美術放圖後關掉。
        if self._show_deco and d != 0 and d != self._hand_dir:
            self._draw_hand(d, bg)
            self._hand_dir = d

        # 角色表情：被摸時開心，否則待機；只在 key 改變時重畫。
        key = "pet" if self.react > 0 else "idle"
        if key != self._cur_sprite:
            g.assets.draw(key, SPR_X, SPR_Y, SPR_W, SPR_H)
            self._cur_sprite = key

        # 愛心：開心反應期間顯示，結束擦掉（只在切換時重畫）。美術放圖後關掉。
        show = self._show_deco and self.react > 0
        if show != self._hearts_on:
            for hx in HEART_X:
                if show:
                    lcd.fillRoundRect(hx, HEART_Y, HEART, HEART, 4, config.RED)
                else:
                    lcd.fillRect(hx, HEART_Y, HEART, HEART, bg)
            self._hearts_on = show

        if self.react > 0:
            self.react -= 1

        # 親密度條 / 時間條 / HUD：只在數字變動時重畫。
        self._draw_bar()
        self._draw_time()
        hud = (self.strokes, self.combo)
        if hud != self._hud:
            lcd.fillRect(0, 212, config.SCREEN_W, 24, bg)
            lcd.font(lcd.FONT_DejaVu18)
            lcd.print("Pets %d   Combo %d" % (self.strokes, self.combo), 8, 216, config.WHITE)
            self._hud = hud

        self.t += 1
        # 摸滿親密度條 → 成功（可在時間內提前達成）；時間到還沒滿 → 失敗。
        if self.strokes >= config.PET_SUCCESS_STROKES:
            self.result = "success"
            self._drawn = False
        elif self.t >= self.frames:
            self.result = "fail"
            self._drawn = False
        return None

    def _draw_hand(self, d, bg):
        x_other = HEAD_CX - d * HAND_DX - HAND_W // 2
        self.game.lcd.fillRect(x_other, HAND_Y, HAND_W, HAND_H, bg)   # 擦掉另一邊
        x = HEAD_CX + d * HAND_DX - HAND_W // 2
        self.game.lcd.fillRoundRect(x, HAND_Y, HAND_W, HAND_H, 6, config.PINK)

    def _draw_bar(self):
        target = config.PET_SUCCESS_STROKES
        w = config.SCREEN_W - 16
        f = int(w * min(1.0, self.strokes / float(target)))
        if f == self._bar_fill:
            return
        lcd = self.game.lcd
        lcd.fillRect(8, 190, w, 12, config.DARK)
        if f > 0:
            lcd.fillRect(8, 190, f, 12, config.PINK)
        self._bar_fill = f

    def _draw_time(self):
        w = config.SCREEN_W - 40
        f = int(w * (self.frames - self.t) / float(self.frames))
        if f == self._time_fill:
            return
        lcd = self.game.lcd
        lcd.fillRect(20, 30, w, 6, config.DARK)
        if f > 0:
            lcd.fillRect(20, 30, f, 6, config.GREEN)
        self._time_fill = f

    # --- 結算畫面（只畫一次）：成功 / 失敗兩種 ---
    def _result_screen(self):
        g = self.game
        lcd = g.lcd
        if not self._drawn:
            lcd.clear(config.BLACK)
            win = (self.result == "success")
            emo = "emo_success" if win else "emo_fail"
            g.assets.draw(emo, 85, 36)
            lcd.font(lcd.FONT_DejaVu24)
            lcd.print("SUCCESS!" if win else "FAILED...", 95, 18,
                      config.YELLOW if win else config.RED)
            lcd.print("Pets %d / %d" % (self.strokes, config.PET_SUCCESS_STROKES), 80, 190, config.WHITE)
            lcd.font(lcd.FONT_DefaultSmall)
            lcd.print("Max combo %d   B: back" % self.max_combo, 70, 210, config.DARK)
            self._drawn = True
        if g.btnB.wasPressed():
            g.metrics.record_rhythm(self.result == "success")   # 更新 RhythmGameRate 來源
            return config.STATE_NORMAL_ROOM
        return None
