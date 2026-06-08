# HoloTamagotchi - M5Stack Fire 真機版 (UIFlow1 韌體 / m5stack 模組)
#
# 開發方式（不燒錄，秒級更新）：
#   mpremote connect /dev/cu.usbserial-XXXX run device/main.py
# 改完存檔再跑一次即可。按 Ctrl-C 可中斷。
#
# 按鍵：A = 餵食   B = 玩耍   C = 睡覺

from m5stack import lcd, btnA, btnB, btnC
import time

# --- 顏色 (0xRRGGBB) ---
BG     = 0x181226   # 深紫背景
WHITE  = 0xFFFFFF
PINK   = 0xFF80C4   # 主色
CYAN   = 0x78DCFF
GREEN  = 0x78E682
YELLOW = 0xFFDC50
RED    = 0xF05A5A
DARK   = 0x3C3250

# --- 寵物狀態 (0~100) ---
# 螢幕用英文（UIFlow1 字型對中文支援有限），中文放註解。
stats = {"FOOD": 80, "MOOD": 70, "STAM": 90}

PET_X, PET_Y, PET_W, PET_H = 120, 70, 80, 80   # 寵物身體位置


SOUND_ON = False   # 暫時關閉聲音；要恢復改成 True


def mute_speaker():
    """把喇叭硬體靜音，消除 M5 喇叭的 DAC 底噪/爆音。"""
    try:
        from m5stack import speaker
        speaker.setVolume(0)
        speaker.stop()
    except Exception:
        pass


def beep(freq, ms=120):
    if not SOUND_ON:
        return
    try:
        from m5stack import speaker
        speaker.tone(freq, ms)
    except Exception:
        pass


def draw_static():
    """畫一次就好：背景、標題、底部按鍵提示。"""
    lcd.clear(BG)
    lcd.font(lcd.FONT_DejaVu24)
    lcd.print("HoloTama", 95, 12, PINK)
    lcd.font(lcd.FONT_DefaultSmall)
    lcd.print("A:Feed   B:Play   C:Sleep", 70, 224, DARK)


def draw_face(blink, mood):
    """重畫寵物臉，做眨眼/表情。"""
    lcd.fillRoundRect(PET_X, PET_Y, PET_W, PET_H, 14, PINK)
    eye_y = PET_Y + 30
    lx, rx = PET_X + 24, PET_X + 56
    if blink:
        lcd.fillRect(lx - 6, eye_y, 12, 3, DARK)
        lcd.fillRect(rx - 6, eye_y, 12, 3, DARK)
    else:
        lcd.fillCircle(lx, eye_y, 7, WHITE)
        lcd.fillCircle(rx, eye_y, 7, WHITE)
        lcd.fillCircle(lx + 2, eye_y + 1, 3, DARK)
        lcd.fillCircle(rx + 2, eye_y + 1, 3, DARK)
    # 嘴巴依心情
    my = PET_Y + 56
    if mood == "happy":
        lcd.fillRoundRect(PET_X + 26, my - 4, 28, 8, 4, DARK)
    elif mood == "sad":
        lcd.fillRoundRect(PET_X + 26, my, 28, 8, 4, DARK)
        lcd.fillRect(PET_X + 26, my, 28, 4, PINK)
    else:
        lcd.fillRect(PET_X + 34, my, 12, 5, DARK)


def draw_bars():
    """三條狀態條。"""
    lcd.font(lcd.FONT_DejaVu18)
    bar_x, bar_w = 110, 150
    for i, name in enumerate(stats.keys()):
        y = 150 + i * 22
        val = stats[name]
        lcd.print(name, 16, y, WHITE)
        lcd.fillRect(bar_x, y, bar_w, 12, DARK)          # 底槽
        col = GREEN if val > 50 else (YELLOW if val > 25 else RED)
        fill = int(bar_w * val / 100)
        if fill > 0:
            lcd.fillRect(bar_x, y, fill, 12, col)


def current_mood():
    avg = sum(stats.values()) / 3
    if avg > 60:
        return "happy"
    if avg > 30:
        return "neutral"
    return "sad"


def clamp(v):
    return max(0, min(100, v))


# --- 動作 ---
def feed():
    stats["FOOD"] = clamp(stats["FOOD"] + 18)
    stats["MOOD"] = clamp(stats["MOOD"] + 4)
    beep(880)
    print("Feed ->", stats["FOOD"])


def play():
    stats["MOOD"] = clamp(stats["MOOD"] + 18)
    stats["STAM"] = clamp(stats["STAM"] - 8)
    beep(660)
    print("Play ->", stats["MOOD"])


def sleep_action():
    stats["STAM"] = clamp(stats["STAM"] + 25)
    beep(440)
    print("Sleep ->", stats["STAM"])


# --- 主迴圈 ---
mute_speaker()
draw_static()
draw_bars()
frame = 0
print("HoloTamagotchi running on Fire. A=Feed B=Play C=Sleep")

while True:
    # 邊緣偵測：按下瞬間觸發一次
    if btnA.wasPressed():
        feed();         draw_bars()
    if btnB.wasPressed():
        play();         draw_bars()
    if btnC.wasPressed():
        sleep_action(); draw_bars()

    # 每秒 (~20幀) 衰減狀態
    if frame % 20 == 0 and frame > 0:
        stats["FOOD"] = clamp(stats["FOOD"] - 2)
        stats["MOOD"] = clamp(stats["MOOD"] - 1)
        stats["STAM"] = clamp(stats["STAM"] - 1)
        draw_bars()

    blink = (frame % 40) < 3
    draw_face(blink, current_mood())

    frame += 1
    time.sleep_ms(50)
