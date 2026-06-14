#!/usr/bin/env python3
"""png2rgb565.py — 把 PNG 轉成「編譯進韌體」的 raw RGB565 C 標頭。

為什麼存 raw RGB565（而非燒 JPG/PNG 上板再解碼）：原 UIFlow1 用 lcd.image 邊解碼
邊逐列貼到面板，肉眼看得到「掃描線」。改走 raw RGB565 + canvas.pushImage，整塊一次
貼進 off-screen canvas，再一次 pushSprite，畫面瞬間更新、無掃描線。

去背：PNG 的全透明像素（alpha<128）寫成「透明色鍵」（預設洋紅 0xF81F），
上板用 canvas.pushImage(x,y,w,h,data, transp) 時該色不畫，達成去背。

用法：
  # 需要 Pillow：pip install pillow
  python3 png2rgb565.py idle.png --name marine_idle -o ../src/assets/characters/marine/images/idle.h

  # 不需任何套件：產生一張 150x150 測試圖（驗證 raw RGB565 路徑無掃描線）
  python3 png2rgb565.py --test -o ../src/assets/characters/marine/images/test_pattern.h
"""
import argparse
import os
import sys

TRANSP_DEFAULT = 0xF81F  # 洋紅當透明色鍵


def to565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def emit_header(path, name, w, h, pixels):
    """pixels：長度 w*h 的 uint16 list，輸出成 C 標頭。"""
    guard = name.upper() + "_H"
    lines = []
    lines.append("// 由 tools/png2rgb565.py 自動產生，請勿手改。")
    lines.append("#pragma once")
    lines.append("#include <cstdint>")
    lines.append("")
    lines.append("constexpr int %s_W = %d;" % (name.upper(), w))
    lines.append("constexpr int %s_H = %d;" % (name.upper(), h))
    lines.append("inline const uint16_t %s[%d] = {" % (name, w * h))
    row = []
    for i, p in enumerate(pixels):
        row.append("0x%04X," % p)
        if len(row) == 12:
            lines.append("    " + "".join(row))
            row = []
    if row:
        lines.append("    " + "".join(row))
    lines.append("};")
    lines.append("")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print("wrote %s  (%dx%d, %d px, %.1f KB)" % (path, w, h, w * h, w * h * 2 / 1024.0))


def gen_test(w=150, h=150, transp=TRANSP_DEFAULT):
    """純 Python 測試圖：對角漸層 + 圓角外的透明色鍵（驗證去背 + 整張一次貼）。"""
    px = []
    cx, cy = w / 2.0, h / 2.0
    rad = min(w, h) / 2.0
    for y in range(h):
        for x in range(w):
            # 圓形外面設透明（示範去背疊在房間背景上）
            if ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 > rad:
                px.append(transp)
                continue
            r = int(255 * x / (w - 1))
            g = int(255 * y / (h - 1))
            b = int(255 * (1 - (x + y) / (w + h - 2)))
            px.append(to565(r, g, b))
    return w, h, px


def from_png(path, transp=TRANSP_DEFAULT):
    try:
        from PIL import Image
    except ImportError:
        sys.exit("需要 Pillow：pip install pillow（或改用 --test 產生測試圖）")
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    px = []
    for (r, g, b, a) in img.getdata():
        px.append(transp if a < 128 else to565(r, g, b))
    return w, h, px


def main():
    ap = argparse.ArgumentParser(description="PNG -> raw RGB565 C 標頭")
    ap.add_argument("png", nargs="?", help="來源 PNG（--test 時可省略）")
    ap.add_argument("-o", "--out", required=True, help="輸出 .h 路徑")
    ap.add_argument("--name", default=None, help="C 陣列名（預設用檔名）")
    ap.add_argument("--transp", default=hex(TRANSP_DEFAULT), help="透明色鍵（RGB565，hex）")
    ap.add_argument("--test", action="store_true", help="不讀 PNG，產生 150x150 測試圖")
    args = ap.parse_args()

    transp = int(args.transp, 16)
    if args.test:
        name = args.name or "test_pattern"
        w, h, px = gen_test(transp=transp)
    else:
        if not args.png:
            ap.error("需要 PNG 路徑，或加 --test")
        name = args.name or os.path.splitext(os.path.basename(args.png))[0]
        w, h, px = from_png(args.png, transp=transp)

    emit_header(args.out, name, w, h, px)


if __name__ == "__main__":
    main()
