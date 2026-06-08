# main.py — HoloTamagotchi 進入點（M5Stack Fire / UIFlow1 m5stack API）
#
# 架構總覽（模組化、可擴充）：
#   config.py        全域設定（數值閾值、色票、狀態 ID）
#   metrics.py       核心數值系統（成長/飽食/疲勞/音遊率）
#   i18n.py          多國語言字串（assets/strings/<lang>.py）
#   asset_manager.py 資源管理：有圖畫圖，沒圖畫「色塊 + 標籤」佔位
#   ui.py            共用 UI（對話筐 / 選單高亮框）
#   states/          狀態機，一狀態一檔（init / normal_room / feeding /
#                    sleeping / minigame / ending）
#   assets/          美術與文案資源（角色 manifest、圖片資料夾、字串表）
#
# 開發（多檔需用 mount，讓本機模組直接載入、免燒錄、秒級更新）：
#   .venv/bin/mpremote connect /dev/cu.usbserial-XXXX mount device run device/main.py
#
# 按鍵：A / B / C（各狀態內定義；普通房間 B=選單，選單內 A/C 移動、B 確認）。

import time
import config
import i18n
from m5stack import lcd, btnA, btnB, btnC

from metrics import Metrics
from asset_manager import AssetManager
from states.init_state import InitState
from states.normal_room import NormalRoom
from states.feeding import Feeding
from states.sleeping import Sleeping
from states.minigame import MiniGame
from states.ending import Ending


def mute_speaker():
    """靜音 M5 喇叭，消除 DAC 底噪/爆音。"""
    try:
        from m5stack import speaker
        speaker.setVolume(0)
        speaker.stop()
    except Exception:
        pass


def init_imu():
    """初始化 M5 Fire 內建 IMU（MPU6886，含加速度計 + 陀螺儀）。

    不同 UIFlow1 韌體匯入路徑不一，逐一嘗試；取不到（如 mount 開發、無此硬體）
    回 None，呼叫端需自行容錯（搖一搖功能靜默停用，不影響其它玩法）。
    """
    try:
        from imu import IMU
        return IMU()
    except Exception:
        pass
    try:
        from m5stack import imu
        return imu.IMU()
    except Exception:
        return None


class Game:
    """共用情境物件：硬體 + 子系統，傳給各 State 使用，避免到處 import。"""

    def __init__(self):
        self.lcd = lcd
        self.btnA = btnA
        self.btnB = btnB
        self.btnC = btnC
        self.metrics = Metrics()
        i18n.set_lang(config.DEFAULT_LANG)
        self.assets = AssetManager(lcd, config.DEFAULT_CHARACTER)
        self.imu = init_imu()     # 內建 IMU；None 代表不可用（搖一搖會靜默停用）
        self.ending_kind = None   # 結局種類，由 Ending Evaluator 設定
        self._dbg_sig = None      # DEV overlay 上次畫的內容簽章（用來避免每幀重畫）

    def imu_motion(self):
        """回傳 (加速度大小 g, 角速度大小 °/s)；IMU 不可用或讀取失敗回 None。

        搖一搖判定只關心「總動量」，故回傳兩者的向量大小、與方向無關。
        靜止：加速度 ≈ 1.0、角速度 ≈ 3。
        """
        if self.imu is None:
            return None
        try:
            ax, ay, az = self.imu.acceleration
            gx, gy, gz = self.imu.gyro
            amag = (ax * ax + ay * ay + az * az) ** 0.5
            gmag = (gx * gx + gy * gy + gz * gz) ** 0.5
            return (amag, gmag)
        except Exception:
            return None

    def is_night(self):
        """是否為深夜（依現實時間 / RTC）。time 取不到時回 False。"""
        try:
            h = time.localtime()[3]
        except Exception:
            return False
        s, e = config.NIGHT_START_HOUR, config.NIGHT_END_HOUR
        return (h >= s or h < e) if s > e else (s <= h < e)

    def draw_metric_bars(self):
        """畫三條核心數值條（成長 / 飽食 / 疲勞）。"""
        m = self.metrics
        rows = [
            ("GROW",  m.growth,           config.CYAN),
            ("LIFE",  max(0, m.life),     config.GREEN),
            ("ENRGY", m.sleep,            config.YELLOW),
        ]
        self.lcd.font(self.lcd.FONT_DefaultSmall)
        bx, bw = 70, 130
        for i, (name, val, col) in enumerate(rows):
            y = 128 + i * 15
            self.lcd.print(name, 8, y, config.WHITE)
            self.lcd.fillRect(bx, y, bw, 10, config.DARK)
            f = int(bw * min(100, max(0, val)) / 100)
            if f > 0:
                self.lcd.fillRect(bx, y, f, 10, col)

    def draw_debug_overlay(self, state_id, force=False):
        """DEV 模式專用：螢幕最下方一行顯示「狀態名 + 核心數值」。

        關鍵：只有在數值/狀態實際變動時才重畫（簽章比對），避免每幀重畫造成閃爍。
        force=True 用於剛切換狀態、畫面被重畫後強制補上這一行。
        prod 模式（config.DEV=False）由主迴圈完全跳過，畫面保持乾淨。
        """
        m = self.metrics
        sig = (state_id, int(m.growth), int(m.life), int(m.sleep), int(m.rhythm_rate()))
        if not force and sig == self._dbg_sig:
            return
        self._dbg_sig = sig
        lcd = self.lcd
        lcd.fillRect(0, 226, config.SCREEN_W, 14, 0x101018)
        lcd.font(lcd.FONT_DefaultSmall)
        lcd.print(
            "DEV %s  G%d L%d E%d R%d%%" % (state_id, sig[1], sig[2], sig[3], sig[4]),
            4, 228, config.GREEN,
        )


def build_states(game):
    return {
        config.STATE_INIT:        InitState(game),
        config.STATE_NORMAL_ROOM: NormalRoom(game),
        config.STATE_FEEDING:     Feeding(game),
        config.STATE_SLEEPING:    Sleeping(game),
        config.STATE_MINI_GAME:   MiniGame(game),
        config.STATE_ENDING:      Ending(game),
    }


def main():
    mute_speaker()
    game = Game()
    states = build_states(game)

    current = config.STATE_INIT
    state = states[current]
    state.on_enter()
    if config.DEV:
        game.draw_debug_overlay(current, force=True)
    print("HoloTamagotchi started @", current)

    while True:
        nxt = state.update()
        transitioned = False
        if nxt and nxt != current:
            state.on_exit()
            current = nxt
            state = states[current]
            state.on_enter()
            transitioned = True
            print("-> state", current)
        # DEV 疊圖：只在數值變動或剛切換狀態時重畫（避免閃爍）；prod 完全不畫
        if config.DEV:
            game.draw_debug_overlay(current, force=transitioned)
        time.sleep_ms(config.FRAME_MS)


if __name__ == "__main__":
    main()
