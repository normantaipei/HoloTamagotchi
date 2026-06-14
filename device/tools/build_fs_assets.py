#!/usr/bin/env python3
"""build_fs_assets.py — 把 web/demo-assets 的 PNG 轉成「LittleFS 素材分區」的內容。

過去（build_assets.py）是把圖轉成 C 標頭、編譯期焊進韌體。現在改成：圖轉成 raw RGB565
檔放進 data/<角色>/，由 pio run -t buildfs 打包成 LittleFS 映像、燒到獨立 data 分區，
韌體開機由 AssetStore 載入 PSRAM。好處：換美術只要重跑本工具 + buildfs + uploadfs，
不必重編韌體。

每個 manifest key 對映到一個「基底檔名」，自動收集所有 <基底>_NN.png 幀（00,01,02…）
依序轉 RGB565（alpha<128 寫成洋紅色鍵 0xF81F 去背；背景不透明）。

輸出（預設 ../data/marine/）：
  <key>_<i>.565   每幀一個 little-endian raw RGB565 檔（長度 = w*h*2 bytes）
  manifest.txt    一行一資產：  key w h frame_count transp(hex)
                  （純文字，裝置端 sscanf 即可解，不需 JSON 函式庫）

用法：python3 build_fs_assets.py        （需 Pillow）
換圖 / 加幀：把 PNG 換進 / 加進 web/demo-assets（檔名照 <基底>_NN.png）重跑即可。
"""
import os
import re
import struct
import shutil
from PIL import Image

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "../../web/demo-assets")
CHARACTER = "marine"
OUT = os.path.join(HERE, "../data", CHARACTER)
TRANSP = 0xF81F

# manifest key -> (來源基底檔名, 是否不透明)。會收集 <基底>_NN.png 的所有幀。
# 與舊 build_assets.py 一致；新增一種圖在這加一行即可。
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
    """讀 PNG -> (w, h, [uint16 RGB565...])，alpha<128 寫成透明色鍵。"""
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    px = [TRANSP if a < 128 else to565(r, g, b) for (r, g, b, a) in img.getdata()]
    return w, h, px


def write_frame(path, pixels):
    """把 uint16 list 以 little-endian 寫成 raw .565（ESP32 為小端，裝置直接記憶體載入）。"""
    with open(path, "wb") as f:
        f.write(struct.pack("<%dH" % len(pixels), *pixels))


def main():
    # 整個重建，避免殘留舊幀（例如某資產幀數變少）。
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

    lines = []
    total = 0
    for key, base, opaque in MAP:
        files = frames_for(base)
        if not files:
            print("  SKIP %-12s (找不到 %s_NN.png)" % (key, base))
            continue
        w0 = h0 = None
        n = 0
        for fn in files:
            w, h, px = load(os.path.join(SRC, fn))
            if w0 is None:
                w0, h0 = w, h
            elif (w, h) != (w0, h0):
                print("  WARN %s 幀尺寸不一致 (%s %dx%d != %dx%d)，跳過該幀"
                      % (key, fn, w, h, w0, h0))
                continue
            write_frame(os.path.join(OUT, "%s_%d.565" % (key, n)), px)
            total += w * h * 2
            n += 1
        if n == 0:
            continue
        transp = 0xFFFF if opaque else TRANSP
        lines.append("%s %d %d %d 0x%04X" % (key, w0, h0, n, transp))
        print("  %-12s <- %-14s x%d 幀  %dx%d" % (key, base, n, w0, h0))

    with open(os.path.join(OUT, "manifest.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote %d 資產 + manifest.txt 到 %s  (~%.0f KB 素材分區)"
          % (len(lines), os.path.relpath(OUT, HERE), total / 1024.0))


if __name__ == "__main__":
    main()
