# i18n.py — 多國語言字串對應表
#
# 用法：i18n.get("cheer_msg_01") → 依目前語言回字串；找不到鍵就回鍵本身。
# 字串表放在 assets/strings/<lang>.py（各自一個 STRINGS dict），
# 由 assets/strings/__init__.py 彙整成 TABLES。新增語言只要加一個檔 + 註冊一行。

import config
from assets.strings import TABLES

_lang = config.DEFAULT_LANG


def set_lang(lang):
    global _lang
    if lang in TABLES:
        _lang = lang
    else:
        print("i18n: unknown lang", lang, "-> keep", _lang)


def get(key):
    return TABLES.get(_lang, {}).get(key, key)


def lang():
    return _lang
