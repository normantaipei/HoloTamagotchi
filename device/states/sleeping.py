# states/sleeping.py — STATE_SLEEPING：睡眠。
#
# 觸發：現實時間進入深夜（RTC / time.localtime），或 SleepIndex 達標。
# 渲染：背景變暗，「蓋被子睡覺」2 幀輪播（佔位）。
# 邏輯：暫停扣飽食度，SleepIndex 逐漸恢復；忽略多數按鍵。
#       喚醒：按 C，或「搖一搖」機體（IMU 加速度）。
#
# 搖一搖：每幀讀加速度大小，把相鄰幀變化量丟進漏積分器，持續搖到超過閾值才醒，
#         輕碰/放桌上不會誤觸（閾值與衰減見 config.SHAKE_*）。IMU 不可用時自動停用。
#
# 防閃爍：背景 / 文字只在 on_enter 畫一次；睡覺圖只在「換幀」時重畫該區塊。

import config
from states.base import State

SPR_X, SPR_Y, SPR_W, SPR_H = 110, 80, 100, 70
BG = 0x0A0814


class Sleeping(State):
    def on_enter(self):
        self.t = 0
        self._frame = -1
        self._shake = 0.0           # 搖晃漏積分值
        self._last_amag = None      # 上一幀加速度大小（首幀無前值，先不累積）
        self._dbg_shake = -1        # DEV 搖晃量顯示快取（避免每幀重畫）
        g = self.game
        g.lcd.clear(BG)
        g.lcd.font(g.lcd.FONT_DefaultSmall)
        g.lcd.print("Zzz...", 70, 56, config.WHITE)
        hint = "Shake or C: wake up" if g.imu is not None else "C: wake up"
        g.lcd.print(hint, 8, 210, config.DARK)

    def _shaken(self):
        """讀 IMU 累積動量（陀螺儀為主 + 加速度變化），超過閾值回 True。

        IMU 不可用時恆 False（搖一搖靜默停用，不影響按 C 喚醒）。
        """
        s = self.game.imu_motion()
        if s is None:
            return False
        amag, gmag = s
        inst = gmag * config.SHAKE_GYRO_W
        if self._last_amag is not None:
            inst += abs(amag - self._last_amag)
        self._last_amag = amag
        self._shake = self._shake * config.SHAKE_DECAY + inst
        return self._shake > config.SHAKE_WAKE_TH

    def _draw_shake_meter(self):
        """DEV 專用：左上角即時顯示搖晃積分值，方便上板校準閾值。"""
        v = int(self._shake * 10)
        if v == self._dbg_shake:
            return
        self._dbg_shake = v
        g = self.game
        g.lcd.fillRect(0, 0, 130, 14, BG)
        g.lcd.font(g.lcd.FONT_DefaultSmall)
        g.lcd.print("shake %.1f/%.0f" % (self._shake, config.SHAKE_WAKE_TH), 4, 2, config.GREEN)

    def update(self):
        g = self.game
        if self.t % config.TICKS_PER_SEC == 0 and self.t:
            g.metrics.tick(sleeping=True)

        frame = (self.t // 10) % 2      # 2 幀輪播
        if frame != self._frame:
            # 只在換幀時重畫睡覺圖（上下微移 2px 模擬呼吸），不每幀重畫整片
            g.lcd.fillRect(SPR_X, SPR_Y - 2, SPR_W, SPR_H + 4, BG)
            g.assets.draw("sleep", SPR_X, SPR_Y + frame * 2, SPR_W, SPR_H)
            self._frame = frame

        self.t += 1
        # 先更新搖晃積分（每幀都要讀，才能正確累積/衰減），再判斷喚醒
        shaken = self._shaken()
        if config.DEV and g.imu is not None:
            self._draw_shake_meter()
        # 主動喚醒（按 C 或搖一搖）：精力回滿，醒來後保持清醒、不會馬上又睡
        if g.btnC.wasPressed() or shaken:
            g.metrics.sleep = config.SLEEP_FULL
            return config.STATE_NORMAL_ROOM
        # 睡飽（精力回滿）→ 自然醒
        if g.metrics.is_rested():
            return config.STATE_NORMAL_ROOM
        return None
