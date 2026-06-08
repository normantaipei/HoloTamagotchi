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
SLEEP_INIT        = 0        # SleepIndex 初始疲勞
SLEEP_PER_SEC     = 0.3      # 疲勞隨時間累積
SLEEP_YAWN_TH     = 60       # 疲勞超過此值 → 有機率打哈欠
SLEEP_FORCE_TH    = 90       # 疲勞達此值 → 強制進入睡眠
SLEEP_RECOVER_SEC = 2.0      # 睡眠時每秒恢復量

# --- 睡眠時間段（現實時間 / RTC，24h 制）---
NIGHT_START_HOUR  = 23       # 深夜起點（含）
NIGHT_END_HOUR    = 7        # 深夜終點（不含）

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
