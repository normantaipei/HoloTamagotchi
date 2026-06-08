# assets/strings — 多國語言字串。新增語言：建一個 <lang>.py（內含 STRINGS dict），
# 在這裡 import 並加進 TABLES 即可。i18n 模組只依賴 TABLES。

from . import zh_tw, en

TABLES = {
    "zh_tw": zh_tw.STRINGS,
    "en":    en.STRINGS,
}
