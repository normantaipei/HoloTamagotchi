# asset_manager.py — 資源管理（Asset Manager）
#
# 核心原則：優先載入圖片，找不到圖片就畫「色塊 + 文字標籤」當佔位。
# 這讓「程式邏輯」與「美術資源」完全解耦：
#   - 現在沒有圖 → 全部顯示色塊，程式照跑、流程可測。
#   - 之後美術把圖片丟進角色資料夾、在 manifest 的 IMAGES 補一行 → 自動換成圖片。
#   - 新增角色：複製一份角色資料夾、改 manifest、在 REGISTRY 註冊，邏輯不用動。
#
# 每個資源用一個 key 表示（例如 "idle"/"bg_room"/"end_good"），
# 佔位規格與圖片路徑都由角色 manifest 定義（assets/characters/<id>/character.py）。

import config
from assets.characters import REGISTRY

try:
    import uos as os
except ImportError:
    import os


# ─── 暫時佔位：把「沒有圖片」的角色色塊畫成一隻有表情的小寵物 ───────────────
# 這整段是過渡視覺。之後美術把圖放進角色資料夾、在 manifest 的 IMAGES 補一行，
# 對應 key 就會自動換成圖片，這裡不會再被觸發。
#
# 想完全移除：把 PET_FACE 設成 False（自動退回原本的 [標籤] 色塊），
#             或直接刪掉「PET_FACE / PET_EXPR / _pet / _dot / _arc」與
#             draw() 內標了「<pet-face>」的那段分支即可，其餘程式不受影響。
PET_FACE = True

# 哪些資源 key 要畫成寵物臉、以及對應表情。
# 沒列到的 key（背景 bg_*、食物 food_* 等）維持原本的色塊佔位。
PET_EXPR = {
    "egg":         "neutral",
    "idle":        "happy",
    "yawn":        "sleepy",
    "cheer":       "excited",
    "pet":         "happy",
    "eat":         "eating",
    "sleep":       "sleepy",
    "end_good":    "excited",
    "end_normal":  "neutral",
    "end_bad":     "happy",
    "end_runaway": "sad",
    "emo_success": "excited",
    "emo_fail":    "sad",
}
# ──────────────────────────────────────────────────────────────────────────


def _exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


class AssetManager:
    def __init__(self, lcd, character_id):
        self.lcd = lcd
        self.set_character(character_id)

    def set_character(self, character_id):
        self.char = REGISTRY[character_id]
        self.id = character_id
        self.base = "assets/characters/%s/" % character_id
        self.theme = getattr(self.char, "THEME", {})
        self.sprites = getattr(self.char, "SPRITES", {})
        self.images = getattr(self.char, "IMAGES", {})

    def color(self, name, default=config.DARK):
        return self.theme.get(name, default)

    def has_image(self, key):
        """這個 key 是否已有可用的圖片素材（美術已在 IMAGES 補上路徑且檔案存在）。

        給各 state 判斷要不要畫「佔位用的裝飾」——例如睡覺的 Zzz、吃東西的
        Nom nom、摸頭時頭上的手與愛心。一旦美術放好對應角色圖，這些就自動關掉，
        讓美術能把這些元素直接畫進素材裡、完全自由發揮（與佔位色塊同套退場邏輯）。
        """
        rel = self.images.get(key)
        return bool(rel) and _exists(self.base + rel)

    def draw(self, key, x=None, y=None, w=None, h=None, show_label=True):
        """畫一個資源。有圖片就畫圖片，否則畫佔位色塊 + 標籤文字。

        x/y/w/h 省略時，採用 manifest 的預設尺寸並置中。
        show_label=False：佔位色塊不畫標籤文字（例如動畫中移動的小物件）。
        """
        spec = self.sprites.get(key)
        if spec is None:
            # 未定義的 key：畫一塊洋紅警示，方便開發時一眼看出漏定義
            self.lcd.fillRect(x or 0, y or 0, w or 40, h or 20, 0xFF00FF)
            return
        color, label, dw, dh = spec
        if w is None:
            w = dw
        if h is None:
            h = dh
        if x is None:
            x = (config.SCREEN_W - w) // 2
        if y is None:
            y = (config.SCREEN_H - h) // 2
        # 1) 有對應圖片檔就畫圖片
        rel = self.images.get(key)
        if rel and self._try_image(self.base + rel, x, y):
            return
        # 2) 否則畫佔位。<pet-face> 角色類 key 畫成小寵物，其餘維持色塊 + 標籤。
        if PET_FACE and key in PET_EXPR:
            self._pet(x, y, w, h, color, PET_EXPR[key])
        else:
            self._placeholder(x, y, w, h, color, label if show_label else None)

    def _try_image(self, path, x, y):
        if not _exists(path):
            return False
        try:
            self.lcd.image(x, y, path)   # UIFlow1: lcd.image(x, y, file)
            return True
        except Exception as e:
            print("asset: image draw fail", path, e)
            return False

    def _placeholder(self, x, y, w, h, color, label):
        lcd = self.lcd
        lcd.fillRect(x, y, w, h, color)
        if not label:                        # show_label=False：只畫色塊，不畫文字
            return
        lcd.font(lcd.FONT_DefaultSmall)
        # 標籤大致置中（粗略估字寬，夠用即可）
        tx = x + 3
        ty = y + h // 2 - 6
        lcd.print("[" + label + "]", tx, ty, config.WHITE)

    # ─── <pet-face> 暫時佔位用的小寵物（全程只用 fillRect/fillRoundRect，跨韌體最穩）───
    def _dot(self, x, y, s, col):
        self.lcd.fillRect(x, y, s, s, col)

    def _arc(self, cx, my, half_w, sag, t, col):
        """用一排小方點堆出拋物線嘴。sag>0：中間下凹（微笑）；sag<0：中間上凸（嘟嘴）。"""
        n = 4
        step = max(1, half_w // n)
        for i in range(-n, n + 1):
            px = cx + i * step
            f = 1.0 - (i * i) / float(n * n)
            py = my + int(sag * f)
            self.lcd.fillRect(px - t // 2, py - t // 2, t, t, col)

    def _pet(self, x, y, w, h, color, expr):
        lcd = self.lcd
        DARK, WHITE = config.BLACK, config.WHITE

        # 身體：圓角色塊
        lcd.fillRoundRect(x, y, w, h, min(w, h) // 4, color)

        cx = x + w // 2
        eye_y = y + h * 2 // 5
        eye_dx = w // 4
        es = max(4, w // 8)              # 眼睛大小
        t = max(2, w // 18)             # 線條粗細
        mouth_y = y + h * 3 // 5
        half = w // 5
        lx, rx = cx - eye_dx, cx + eye_dx

        # 眼睛：sleepy/eating 閉眼（彎彎橫槓），其餘睜眼（白底黑眼珠）
        if expr in ("sleepy", "eating"):
            for ex in (lx, rx):
                lcd.fillRect(ex - es // 2, eye_y, es, t, DARK)
        else:
            for ex in (lx, rx):
                lcd.fillRoundRect(ex - es // 2, eye_y - es // 2, es, es, es // 3, WHITE)
                lcd.fillRect(ex - t, eye_y - t, t * 2, t * 2, DARK)

        # 嘴巴 + 表情點綴
        if expr == "happy":
            self._arc(cx, mouth_y, half, es // 2, t, DARK)              # 微笑
        elif expr == "excited":
            mw, mh = w // 3, h // 6
            lcd.fillRoundRect(cx - mw // 2, mouth_y - mh // 2, mw, mh, mh // 2, DARK)  # 張嘴笑
            self._dot(x + w - es, y + es, t * 2, config.YELLOW)        # 火花
        elif expr == "eating":
            mw = w // 5
            lcd.fillRoundRect(cx - mw // 2, mouth_y - mw // 2, mw, mw, mw // 2, DARK)  # 圓嘴
        elif expr == "sad":
            self._arc(cx, mouth_y + es // 2, half, -(es // 2), t, DARK)  # 嘟嘴
            self._dot(lx, eye_y + es, t, config.CYAN)                   # 淚滴
        elif expr == "sleepy":
            zx, zy = x + w - es * 2, y + es                             # 小 z
            lcd.fillRect(zx, zy, es, t, WHITE)
            lcd.fillRect(zx, zy + es, es, t, WHITE)
            self._arc(cx, mouth_y, half // 2, t, t, DARK)              # 小嘴
        else:  # neutral
            lcd.fillRect(cx - half // 2, mouth_y, half, t, DARK)        # 直線嘴
    # ─── </pet-face> ───
