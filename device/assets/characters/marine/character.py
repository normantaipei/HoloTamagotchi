# character.py — 角色 manifest（寶鐘瑪琳 / Houshou Marine）
#
# 這支檔案「定義一個角色」，不含遊戲邏輯。包含三塊：
#   THEME   : 色彩主題（背景 / 主色 / 點綴）
#   SPRITES : 每個資源的「佔位色塊規格」 key -> (顏色, 螢幕標籤, 預設寬, 預設高)
#   IMAGES  : 每個資源對應的圖片檔（相對角色資料夾）。檔案存在才用，否則回退色塊。
#
# 美術流程：把圖片放進對應子資料夾（backgrounds/ anim/ portraits/ food/），
#           再到 IMAGES 補上 "key": "相對路徑" 即可，程式邏輯完全不用改。
# 詳見 device/assets/README.md。

NAME = "Houshou Marine"

# 色彩主題（0xRRGGBB）
THEME = {
    "bg":      0x2A1020,   # 深紅房間底
    "primary": 0xF0405A,   # 瑪琳紅
    "accent":  0xFFC857,   # 金
}

# key -> (佔位色塊顏色, 螢幕標籤, 預設寬, 預設高)
# 標籤文字同時也是「給美術看的這格要放什麼圖」的說明。
SPRITES = {
    # 初始 / 待機 / 動作
    "egg":          (0xF0E6C8, "Egg",            70,  90),
    "idle":         (0xF0405A, "Marine idle",    80,  74),
    "yawn":         (0xC0506A, "ANIM: Yawn",     80,  74),
    "cheer":        (0xFF6080, "ANIM: Cheer",    80,  74),
    "pet":          (0xFF7090, "ANIM: Pet",      92,  85),
    "eat":          (0xF07090, "ANIM: Eat",      80,  74),
    "sleep":        (0x405080, "ANIM: Sleep",   100,  70),
    # 背景
    "bg_room":      (0x2A1020, "BG: Normal Room", 320, 240),
    "bg_game":      (0x0C1828, "BG: Game Room",   320, 240),
    # 結局圖（4 種）
    "end_idol":     (0xFFD24A, "END: Idol",      140, 150),
    "end_office":   (0x6A86C0, "END: Office",    140, 150),
    "end_pirate":   (0x9A3A3A, "END: Pirate",    140, 150),
    "end_runaway":  (0x404048, "END: Run away",  140, 150),
    # 摸頭遊戲結算情緒圖（成功 / 失敗 2 張）
    "emo_success":  (0xFFD24A, "EMO: Success",    90, 100),
    "emo_fail":     (0x9A6A6A, "EMO: Fail",       90, 100),
    # 食物 / 甜點（5 種）
    "food_0":       (0xF0A0B0, "Cake",     50, 50),
    "food_1":       (0xC08050, "Pudding",  50, 50),
    "food_2":       (0xF0D060, "Tart",     50, 50),
    "food_3":       (0xB0E0F0, "Soda",     50, 50),
    "food_4":       (0xE07070, "Parfait",  50, 50),
}

# key -> 圖片相對路徑（相對於本角色資料夾）。
# 目前留空 → 全部走佔位色塊。美術放好圖後，把對應行取消註解並改檔名即可。
IMAGES = {
    # "bg_room":   "backgrounds/room.jpg",
    # "bg_game":   "backgrounds/game_room.jpg",
    # "idle":      "anim/idle_00.jpg",
    # "end_idol":  "portraits/idol.jpg",
    # "food_0":    "food/cake.jpg",
}

# 此角色用到的對話字串 key（對應 assets/strings/<lang>.py）。
DIALOG = ["cheer_msg_01", "cheer_msg_02", "yawn_msg_01"]
