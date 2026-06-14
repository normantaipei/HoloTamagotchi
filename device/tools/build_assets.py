#!/usr/bin/env python3
"""build_assets.py — 把 web/demo-assets 的 PNG 轉成編進韌體的 RGB565 標頭。

把每個 manifest key 對映到一張來源 PNG，轉成 const uint16_t[]（RGB565，alpha<128 的
像素寫成洋紅色鍵 0xF81F 做去背），並產出彙整檔 images/assets.h（含 MARINE_IMAGES 巨集，
供 character.h 的 IMAGES[] 使用）。

來源多幀的（idle_00/01/02…）目前先取第 0 幀（單張）；逐幀動畫待之後做。

用法：python3 build_assets.py    （需 Pillow）
真美術更新：把新 PNG 換進 web/demo-assets 重跑即可。
"""
import os
from PIL import Image

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "../../web/demo-assets")
OUT = os.path.join(HERE, "../src/assets/characters/marine/images")
TRANSP = 0xF81F

# manifest key -> (來源 PNG 檔名, 是否不透明)
MAP = [
    ("idle",        "idle_00.png",        False),
    ("yawn",        "yawn_00.png",        False),
    ("cheer",       "cheer_00.png",       False),
    ("pet",         "pet_00.png",         False),
    ("eat",         "eat_00.png",         False),
    ("sleep",       "sleep_00.png",       False),
    ("egg",         "egg_00.png",         False),
    ("bg_room",     "bg_room_00.png",     True),    # 背景：不透明
    ("end_good",    "end_idol_00.png",    False),
    ("end_normal",  "end_office_00.png",  False),
    ("end_bad",     "end_pirate_00.png",  False),
    ("end_runaway", "end_runaway_00.png", False),
    ("emo_success", "emo_success_00.png", False),
    ("emo_fail",    "emo_fail_00.png",    False),
    ("food_0",      "food_0_00.png",      False),
    ("food_1",      "food_1_00.png",      False),
    ("food_2",      "food_2_00.png",      False),
    ("food_3",      "food_3_00.png",      False),
    ("food_4",      "food_4_00.png",      False),
]


def to565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def load(path):
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    px = [TRANSP if a < 128 else to565(r, g, b) for (r, g, b, a) in img.getdata()]
    return w, h, px


def emit(key, w, h, pixels):
    up = key.upper()
    lines = ["// 由 tools/build_assets.py 自動產生（來源 web/demo-assets），請勿手改。",
             "#pragma once", "#include <cstdint>", "",
             "constexpr int IMG_%s_W = %d;" % (up, w),
             "constexpr int IMG_%s_H = %d;" % (up, h),
             "inline const uint16_t img_%s[%d] = {" % (key, w * h)]
    row = []
    for p in pixels:
        row.append("0x%04X," % p)
        if len(row) == 12:
            lines.append("    " + "".join(row)); row = []
    if row:
        lines.append("    " + "".join(row))
    lines.append("};\n")
    with open(os.path.join(OUT, key + ".h"), "w") as f:
        f.write("\n".join(lines))


def main():
    os.makedirs(OUT, exist_ok=True)
    entries = []
    total = 0
    for key, fname, opaque in MAP:
        path = os.path.join(SRC, fname)
        if not os.path.exists(path):
            print("  SKIP %-12s (找不到 %s)" % (key, fname)); continue
        w, h, px = load(path)
        emit(key, w, h, px)
        entries.append((key, "0xFFFF" if opaque else "0xF81F"))
        total += w * h * 2
        print("  %-12s <- %-20s %dx%d" % (key, fname, w, h))

    agg = ["// 由 tools/build_assets.py 自動產生。include 後用 MARINE_IMAGES 巨集。",
           "#pragma once"]
    for key, _ in entries:
        agg.append('#include "%s.h"' % key)
    agg += ["", "// 展開成 ImageAsset 陣列項，供 character.h 的 IMAGES[] 使用。",
            "#define MARINE_IMAGES \\"]
    for key, transp in entries:
        up = key.upper()
        agg.append('    {"%s", img_%s, IMG_%s_W, IMG_%s_H, %s}, \\'
                   % (key, key, up, up, transp))
    agg.append("")
    with open(os.path.join(OUT, "assets.h"), "w") as f:
        f.write("\n".join(agg))
    print("wrote %d images + assets.h  (~%.0f KB flash)" % (len(entries), total / 1024.0))


if __name__ == "__main__":
    main()
