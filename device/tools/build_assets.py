#!/usr/bin/env python3
"""build_assets.py — 把 web/demo-assets 的 PNG 轉成編進韌體的 RGB565 標頭（支援多幀）。

每個 manifest key 對映到一個「基底檔名」，會自動收集所有 <基底>_NN.png 幀（00,01,02…）
依序轉成 RGB565（alpha<128 寫成洋紅色鍵 0xF81F 做去背），並產出彙整檔 images/assets.h
（含 MARINE_IMAGES 巨集）。裝置端 AssetManager 會依目前幀輪播多幀素材。

用法：python3 build_assets.py    （需 Pillow）
換圖 / 加幀：把 PNG 換進 / 加進 web/demo-assets（檔名照 <基底>_NN.png）重跑即可。
"""
import os
import re
from PIL import Image

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "../../web/demo-assets")
OUT = os.path.join(HERE, "../src/assets/characters/marine/images")
TRANSP = 0xF81F

# manifest key -> (來源基底檔名, 是否不透明)。會收集 <基底>_NN.png 的所有幀。
MAP = [
    ("idle",        "idle",        False),
    ("yawn",        "yawn",        False),
    ("cheer",       "cheer",       False),
    ("pet",         "pet",         False),
    ("eat",         "eat",         False),
    ("sleep",       "sleep",       False),
    ("egg",         "egg",         False),
    ("bg_room",     "bg_room",     True),    # 背景：不透明
    ("end_good",    "end_idol",    False),
    ("end_normal",  "end_office",  False),
    ("end_bad",     "end_pirate",  False),
    ("end_runaway", "end_runaway", False),
    ("emo_success", "emo_success", False),
    ("emo_fail",    "emo_fail",    False),
    ("food_0",      "food_0",      False),
    ("food_1",      "food_1",      False),
    ("food_2",      "food_2",      False),
    ("food_3",      "food_3",      False),
    ("food_4",      "food_4",      False),
]


def to565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def frames_for(base):
    """收集 SRC 下所有 <base>_NN.png，依編號排序。"""
    pat = re.compile(r"^" + re.escape(base) + r"_(\d+)\.png$")
    found = []
    for fn in os.listdir(SRC):
        m = pat.match(fn)
        if m:
            found.append((int(m.group(1)), fn))
    found.sort()
    return [fn for _, fn in found]


def load(path):
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    px = [TRANSP if a < 128 else to565(r, g, b) for (r, g, b, a) in img.getdata()]
    return w, h, px


def fmt_array(name, pixels):
    lines = ["inline const uint16_t %s[%d] = {" % (name, len(pixels))]
    row = []
    for p in pixels:
        row.append("0x%04X," % p)
        if len(row) == 12:
            lines.append("    " + "".join(row)); row = []
    if row:
        lines.append("    " + "".join(row))
    lines.append("};")
    return lines


def emit(key, w, h, frame_pixels):
    """frame_pixels：list of 各幀像素 list。輸出多幀陣列 + 指標陣列。"""
    up = key.upper()
    n = len(frame_pixels)
    lines = ["// 由 tools/build_assets.py 自動產生（來源 web/demo-assets），請勿手改。",
             "#pragma once", "#include <cstdint>", "",
             "constexpr int IMG_%s_W = %d;" % (up, w),
             "constexpr int IMG_%s_H = %d;" % (up, h),
             "constexpr int IMG_%s_N = %d;" % (up, n), ""]
    for i, px in enumerate(frame_pixels):
        lines += fmt_array("img_%s_%d" % (key, i), px)
    # 各幀指標陣列
    ptrs = ", ".join("img_%s_%d" % (key, i) for i in range(n))
    lines.append("inline const uint16_t* const img_%s_frames[%d] = { %s };" % (key, n, ptrs))
    lines.append("")
    with open(os.path.join(OUT, key + ".h"), "w") as f:
        f.write("\n".join(lines))


def main():
    os.makedirs(OUT, exist_ok=True)
    entries = []
    total = 0
    for key, base, opaque in MAP:
        files = frames_for(base)
        if not files:
            print("  SKIP %-12s (找不到 %s_NN.png)" % (key, base)); continue
        w0 = h0 = None
        frame_pixels = []
        for fn in files:
            w, h, px = load(os.path.join(SRC, fn))
            if w0 is None:
                w0, h0 = w, h
            elif (w, h) != (w0, h0):
                print("  WARN %s 幀尺寸不一致 (%s %dx%d != %dx%d)，跳過該幀" % (key, fn, w, h, w0, h0)); continue
            frame_pixels.append(px)
            total += w * h * 2
        emit(key, w0, h0, frame_pixels)
        entries.append((key, "0xFFFF" if opaque else "0xF81F"))
        print("  %-12s <- %-14s x%d 幀  %dx%d" % (key, base, len(frame_pixels), w0, h0))

    agg = ["// 由 tools/build_assets.py 自動產生。include 後用 MARINE_IMAGES 巨集。",
           "#pragma once"]
    for key, _ in entries:
        agg.append('#include "%s.h"' % key)
    agg += ["", "// 展開成 ImageAsset 陣列項（含多幀指標），供 character.h 的 IMAGES[] 使用。",
            "#define MARINE_IMAGES \\"]
    for key, transp in entries:
        up = key.upper()
        agg.append('    {"%s", img_%s_frames, IMG_%s_N, IMG_%s_W, IMG_%s_H, %s}, \\'
                   % (key, key, up, up, up, transp))
    agg.append("")
    with open(os.path.join(OUT, "assets.h"), "w") as f:
        f.write("\n".join(agg))
    print("wrote %d keys + assets.h  (~%.0f KB flash)" % (len(entries), total / 1024.0))


if __name__ == "__main__":
    main()
