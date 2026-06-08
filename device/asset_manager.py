# asset_manager.py — 資源管理（Asset Manager）
#
# 核心原則：優先載入圖片，找不到圖片就畫「色塊 + 文字標籤」當佔位。
# 這讓「程式邏輯」與「美術資源」完全解耦：
#   - 現在沒有圖 → 全部顯示色塊，程式照跑、流程可測。
#   - 之後美術把圖片丟進角色資料夾、在 manifest 的 IMAGES 補一行 → 自動換成圖片。
#   - 新增角色：複製一份角色資料夾、改 manifest、在 REGISTRY 註冊，邏輯不用動。
#
# 每個資源用一個 key 表示（例如 "idle"/"bg_room"/"end_idol"），
# 佔位規格與圖片路徑都由角色 manifest 定義（assets/characters/<id>/character.py）。

import config
from assets.characters import REGISTRY

try:
    import uos as os
except ImportError:
    import os


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

    def draw(self, key, x=None, y=None, w=None, h=None):
        """畫一個資源。有圖片就畫圖片，否則畫佔位色塊 + 標籤文字。

        x/y/w/h 省略時，採用 manifest 的預設尺寸並置中。
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
        # 2) 否則畫佔位色塊 + 標籤
        self._placeholder(x, y, w, h, color, label)

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
        lcd.font(lcd.FONT_DefaultSmall)
        # 標籤大致置中（粗略估字寬，夠用即可）
        tx = x + 3
        ty = y + h // 2 - 6
        lcd.print("[" + label + "]", tx, ty, config.WHITE)
