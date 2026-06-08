# config.py — 全域設定（螢幕、色票、節奏、核心數值閾值、結局規則、狀態 ID）
#
# 所有「可調參數」集中在這裡，方便調整與社群 fork。
# 程式邏輯不寫死數字，一律從這裡讀，達成「換角色 / 改平衡只動設定」的目標。

# --- 執行模式 ---
# DEV  = True ：開發模式。螢幕疊一層 debug overlay（狀態名 + 核心數值條 + 數字），
#               方便在 Fire 上即時看背景數值。
# DEV  = False：正式模式（prod）。乾淨遊戲介面，不顯示任何數值/狀態文字。
# 上板測試切 True，要乾淨展示就切 False。
DEV = True

# --- 螢幕 ---
SCREEN_W = 320
SCREEN_H = 240
FRAME_MS = 50                       # 主迴圈每幀間隔（~20fps）
TICKS_PER_SEC = 1000 // FRAME_MS    # 幾幀算一秒（給「每秒一次」的數值更新用）

# --- 預設角色 / 語言 ---
DEFAULT_CHARACTER = "marine"        # 預設角色（寶鐘瑪琳）
# 螢幕對話語言。注意：UIFlow1 內建字型無法顯示中文，
# 想在螢幕上顯示中文需另外燒錄 CJK 字型（TODO）。預設用 en 確保可見；
# zh_tw 字串仍備妥，之後接上中文字型即可切換。
DEFAULT_LANG = "en"

# --- 通用色票 (0xRRGGBB) ---
WHITE  = 0xFFFFFF
BLACK  = 0x000000
DARK   = 0x3C3250
GREEN  = 0x78E682
YELLOW = 0xFFDC50
RED    = 0xF05A5A
PINK   = 0xFF80C4
CYAN   = 0x78DCFF

# --- 核心數值：初始值與每秒變化量 ---
GROWTH_MAX        = 100      # GrowthIndex 滿值 → 觸發正常結局
GROWTH_PER_SEC    = 0.05     # 成長指數隨時間自然增加
LIFE_INIT         = 80       # BasicLifeIndex 初始飽食度
LIFE_PER_SEC      = -0.4     # 飽食度隨時間下降
LIFE_FEED_GAIN    = 18       # 餵食一次增加量
LIFE_BAD_END      = 0        # BasicLifeIndex < 此值 → 壞結局
# SleepIndex 改為「精力值」：醒著時下降、睡覺回復；過低就想睡，睡飽自然醒。
SLEEP_INIT          = 100    # 精力初始值（滿）
SLEEP_FULL          = 100    # 精力上限（睡飽 = 回到此值 → 自然醒）
SLEEP_DRAIN_PER_SEC = 0.02   # 醒著時精力每秒下降（~75 分鐘從滿掉到想睡）
SLEEP_RECOVER_SEC   = 2.0    # 睡眠時每秒回復精力
SLEEP_LOW_TH        = 10     # 精力 ≤ 此值 → 想睡（普通房間 → 睡眠）
SLEEP_YAWN_TH       = 30     # 精力 < 此值 → 有機率打哈欠

# --- 普通房間：閒置自動睡眠 ---
# 連續 IDLE_SLEEP_SEC 秒「沒有動作」（沒按鍵、沒搖晃）→ 進入睡眠。
# 任一按鍵，或陀螺儀偵測到動作，都會把閒置計時歸零。
IDLE_SLEEP_SEC    = 3600     # 閒置這麼久沒動作 → 睡眠（1 小時）
IDLE_MOTION_TH    = 30       # 角速度(°/s)超過此值算「有動作」，重置閒置計時

# --- 睡眠時間段（現實時間 / RTC，24h 制；目前不強制觸發睡眠，保留備用）---
NIGHT_START_HOUR  = 23       # 深夜起點（含）
NIGHT_END_HOUR    = 7        # 深夜終點（不含）

# --- IMU 體感：睡覺時「搖一搖」喚醒 ---
# 偵測「動量」：每幀把 (角速度大小×權重 + 加速度變化量) 丟進漏積分器
#   shake = shake*DECAY + (gyro_mag*GYRO_W + |Δaccel|)
# 持續晃動才會累積過閾值；靜止 / 輕碰 / 放桌上不會誤觸。
# 陀螺儀(gyro)對「轉動 / 揮動」最敏感（靜止≈3°/s，搖一搖可達數百），是主力訊號；
# 加速度變化量補捉「直線甩動」。實測：靜止時 shake 穩定 < 0.5。
SHAKE_WAKE_TH = 4.0          # 動量積分超過此值 → 喚醒（越大越難搖醒）
SHAKE_DECAY   = 0.75         # 每幀衰減係數 0~1（越小越需要「連續」搖，越大越靈敏）
SHAKE_GYRO_W  = 0.02         # 角速度(°/s)換算權重；靜止 3→0.06，揮動數百→好幾分

# --- 隨機事件機率（每秒判定一次，範圍 0~1）---
P_YAWN   = 0.15
P_CHEER  = 0.10

# --- 結局：RhythmGameRate 分支閾值（%）---
END_IDOL_TH   = 90    # > 90% → 偶像（結局1）
END_OFFICE_TH = 30    # 30%~90% → 上班族（結局2）；< 30% → 海賊（結局3）

# --- 狀態 ID（狀態機用字串當鍵，可讀性高、易擴充）---
STATE_INIT        = "init"          # 初始化 / 重置（蛋裂開）
STATE_NORMAL_ROOM = "normal_room"   # 普通房間 / 待機
STATE_FEEDING     = "feeding"       # 餵食互動
STATE_SLEEPING    = "sleeping"      # 睡眠
STATE_MINI_GAME   = "mini_game"     # 音樂遊戲
STATE_ENDING      = "ending"        # 結局
