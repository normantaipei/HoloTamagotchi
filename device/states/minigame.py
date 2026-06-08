# states/minigame.py — STATE_MINI_GAME：音樂遊戲（獨立遊戲迴圈）。
#
# 渲染：切到「遊戲房間」背景，上方「唱跳」動圖（佔位）。
# 判定（Hit Detection）：
#   譜面生成器依時間軸生成「方塊物件」，每塊有生命週期：生出(紅) -> 判定窗(綠) -> 消失。
#   方塊在「綠色狀態」時按下對應鍵 → Hit 加分；紅色時按或未按就消失 → Miss 斷 Combo。
# 結算：依命中率給評級 S/A/C/F → 顯示對應情緒圖 → 更新 RhythmGameRate → 等 B 返回。
#
# 三條 lane 對應實體鍵：lane0=A、lane1=B、lane2=C。
# 防閃爍：背景 / 唱跳圖 / 判定線只畫一次；每幀只「擦掉每個方塊的舊位置 + 畫新位置」，
#   不再每幀清空整個音符區；HUD 只在分數/Combo 變動時重畫。
# NOTE: 仍為骨架版（固定譜面、20fps）。要更精準/更高更新率可在此跑獨立內迴圈（TODO）。

import config
from states.base import State

# 譜面：(出現幀, lane)。lane 0=A 1=B 2=C
CHART = [
    (16, 1), (30, 0), (44, 2), (58, 1), (72, 0),
    (86, 2), (100, 1), (114, 0), (128, 2), (142, 1),
]
GREEN_START = 12    # 出現後第幾幀進入判定窗（綠）
GREEN_END   = 20    # 判定窗結束
DESPAWN     = 26    # 方塊消失
LANES_X = [40, 140, 240]
GAME_BG = 0x0C1828


class MiniGame(State):
    def on_enter(self):
        self.t = 0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.hits = 0
        self.notes = [{"spawn": s, "lane": l, "hit": False, "done": False, "py": None}
                      for (s, l) in CHART]
        self.result = None
        self._hud = None
        g = self.game
        lcd = g.lcd
        lcd.clear(GAME_BG)
        g.assets.draw("dance", 130, 8, 60, 36)                       # 唱跳（佔位，畫一次）
        lcd.fillRect(0, 70 + GREEN_START * 5, config.SCREEN_W, 2, config.DARK)  # 判定線

    def update(self):
        if self.result is not None:
            return self._result_screen()
        return self._play()

    # --- 遊玩中 ---
    def _play(self):
        g = self.game
        lcd = g.lcd
        keys = [g.btnA.wasPressed(), g.btnB.wasPressed(), g.btnC.wasPressed()]

        for n in self.notes:
            if n["done"]:
                continue
            age = self.t - n["spawn"]
            if age < 0:
                continue
            x = LANES_X[n["lane"]]
            # 擦掉上一格位置
            if n["py"] is not None:
                lcd.fillRect(x, n["py"], 40, 40, GAME_BG)

            done_now = False
            # 判定：對應 lane 鍵被按
            if keys[n["lane"]] and not n["hit"]:
                if GREEN_START <= age < GREEN_END:
                    n["hit"] = True
                    done_now = True
                    self.hits += 1
                    self.combo += 1
                    self.score += 100 + self.combo * 5
                    if self.combo > self.max_combo:
                        self.max_combo = self.combo
                else:
                    self.combo = 0   # 早按/錯誤時機 → 斷 Combo
            # 超時消失：未命中 → Miss
            if age >= DESPAWN:
                done_now = True
                if not n["hit"]:
                    self.combo = 0

            if done_now:
                n["done"] = True
                n["py"] = None       # 已擦掉、不再畫
                continue

            # 畫新位置
            if age < GREEN_START:
                col = config.RED
            elif age < GREEN_END:
                col = config.GREEN
            else:
                col = config.DARK
            y = 70 + age * 5
            lcd.fillRoundRect(x, y, 40, 40, 6, col)
            n["py"] = y

        # HUD：只在分數/Combo 變動時重畫
        hud = (self.score, self.combo)
        if hud != self._hud:
            lcd.fillRect(0, 212, config.SCREEN_W, 24, GAME_BG)
            lcd.font(lcd.FONT_DejaVu18)
            lcd.print("Score %d   Combo %d" % (self.score, self.combo), 8, 216, config.WHITE)
            self._hud = hud

        self.t += 1
        # 結束：最後一塊消失後
        if self.t > CHART[-1][0] + DESPAWN + 4:
            self.result = self._grade()
            self._drawn = False
        return None

    def _grade(self):
        total = len(CHART)
        acc = self.hits / float(total) if total else 0.0
        if acc >= 0.9:
            return "S"
        if acc >= 0.7:
            return "A"
        if acc >= 0.4:
            return "C"
        return "F"

    # --- 結算畫面（只畫一次）---
    def _result_screen(self):
        g = self.game
        lcd = g.lcd
        if not self._drawn:
            lcd.clear(GAME_BG)
            emo = {"S": "emo_s", "A": "emo_a", "C": "emo_c", "F": "emo_f"}[self.result]
            g.assets.draw(emo, 115, 56)
            lcd.font(lcd.FONT_DejaVu24)
            lcd.print("RESULT: %s" % self.result, 85, 18, config.YELLOW)
            lcd.print("Score %d" % self.score, 95, 172, config.WHITE)
            lcd.font(lcd.FONT_DefaultSmall)
            lcd.print("Max combo %d   B: back" % self.max_combo, 70, 210, config.DARK)
            self._drawn = True
        if g.btnB.wasPressed():
            g.metrics.record_rhythm(self.result)   # 更新 RhythmGameRate 來源
            return config.STATE_NORMAL_ROOM
        return None
