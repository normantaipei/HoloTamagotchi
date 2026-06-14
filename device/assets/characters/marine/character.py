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
#
# 【統一畫布】所有「角色」一律用同一塊 150×150 正方形畫布，方便美術作業：
#   每個動作 / 表情 / 結局都畫在 150×150 裡置中，留白即可。
#   裝置端是用 lcd.image(x,y) 原生尺寸貼圖（不縮放），所以「畫布大小＝上機顯示大小」；
#   各畫面只決定「貼在哪」，不會把同一張圖顯示成不同尺寸。
#   150 是能塞進最擠畫面（摸頭，上下有 HUD）的最大正方形。
# 食物是道具、背景是背景，各自一套尺寸，不屬於「角色畫布」。
CHAR_W = CHAR_H = 150           # 角色統一畫布邊長

SPRITES = {
    # 初始 / 待機 / 動作（皆 150×150 統一畫布）
    "egg":          (0xF0E6C8, "Egg",           CHAR_W, CHAR_H),
    "idle":         (0xF0405A, "Marine idle",   CHAR_W, CHAR_H),
    "yawn":         (0xC0506A, "ANIM: Yawn",    CHAR_W, CHAR_H),
    "cheer":        (0xFF6080, "ANIM: Cheer",   CHAR_W, CHAR_H),
    "pet":          (0xFF7090, "ANIM: Pet",     CHAR_W, CHAR_H),
    "eat":          (0xF07090, "ANIM: Eat",     CHAR_W, CHAR_H),
    "sleep":        (0x405080, "ANIM: Sleep",   CHAR_W, CHAR_H),
    # 背景
    "bg_room":      (0x2A1020, "BG: Normal Room", 320, 240),
    # 結局圖（4 類，150×150 統一畫布）。key 為通用類別，marine 各自對應自己的角色圖。
    "end_good":     (0xFFD24A, "END: Good (Idol)",     CHAR_W, CHAR_H),
    "end_normal":   (0x6A86C0, "END: Normal (Office)",  CHAR_W, CHAR_H),
    "end_bad":      (0x9A3A3A, "END: Bad (Pirate)",     CHAR_W, CHAR_H),
    "end_runaway":  (0x404048, "END: Run away",         CHAR_W, CHAR_H),
    # 摸頭遊戲結算情緒圖（成功 / 失敗 2 張，150×150 統一畫布）
    "emo_success":  (0xFFD24A, "EMO: Success",   CHAR_W, CHAR_H),
    "emo_fail":     (0x9A6A6A, "EMO: Fail",      CHAR_W, CHAR_H),
    # 食物 / 甜點（5 種，道具自成一套 95×95）
    "food_0":       (0xF0A0B0, "Cake",     95, 95),
    "food_1":       (0xC08050, "Pudding",  95, 95),
    "food_2":       (0xF0D060, "Tart",     95, 95),
    "food_3":       (0xB0E0F0, "Soda",     95, 95),
    "food_4":       (0xE07070, "Parfait",  95, 95),
}

# key -> 圖片相對路徑（相對於本角色資料夾）。
# 目前留空 → 全部走佔位色塊。美術放好圖後，把對應行取消註解並改檔名即可。
IMAGES = {
    # "bg_room":   "backgrounds/room.jpg",
    # "idle":      "anim/idle_00.jpg",
    # "end_good":  "portraits/idol.jpg",
    # "food_0":    "food/cake.jpg",
}

# 此角色用到的對話字串 key（對應 assets/strings/<lang>.py）。
DIALOG = ["cheer_msg_01", "cheer_msg_02", "yawn_msg_01"]
