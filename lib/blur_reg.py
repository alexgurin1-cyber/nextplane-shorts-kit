#!/usr/bin/env python3
"""Blur registrations (or any region) in a photo with a feathered mask, so other aircraft's
N-numbers never appear on screen (PILOTS.md / RUNBOOK_SHORTS15 photo rule).

Usage: blur_reg.py IN.jpg OUT.jpg x0,y0,x1,y1 [x0,y0,x1,y1 ...]   (boxes in source-pixel coords)
       blur_reg.py --strong IN.jpg OUT.jpg BOX ...  pixelate + blur (use for large, high-contrast lettering:
       the plain feathered blur left "C-GSCY" and a tail logo readable on 2026-11-22)
Tip: make a ~800px preview first, read the box off it, scale by src_width/800, pad ~15 px.
"""
import sys
from PIL import Image, ImageDraw, ImageFilter


def blur_regions(src, boxes, radius=14, feather=10):
    im = Image.open(src).convert("RGB")
    bl = im.filter(ImageFilter.GaussianBlur(radius))
    m = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(m)
    for b in boxes:
        d.rounded_rectangle(b, radius=feather, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather))
    im.paste(bl, (0, 0), m)
    return im


def pixelate_regions(src, boxes, cell=14):
    im = Image.open(src).convert("RGB")
    for (x0, y0, x1, y1) in boxes:
        r = im.crop((x0, y0, x1, y1)); w, h = r.size
        r = r.resize((max(1, w // cell), max(1, h // cell)), Image.BILINEAR).resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((4, 4, w - 4, h - 4), radius=10, fill=255)
        im.paste(r, (x0, y0), m.filter(ImageFilter.GaussianBlur(4)))
    return im


if __name__ == "__main__":
    if sys.argv[1] == "--strong":
        boxes = [tuple(int(v) for v in a.split(",")) for a in sys.argv[4:]]
        pixelate_regions(sys.argv[2], boxes).save(sys.argv[3], quality=95)
        print(sys.argv[3], len(boxes), "region(s) pixelated"); sys.exit(0)
    boxes = [tuple(int(v) for v in a.split(",")) for a in sys.argv[3:]]
    blur_regions(sys.argv[1], boxes).save(sys.argv[2], quality=95)
    print(sys.argv[2], len(boxes), "region(s) blurred")
