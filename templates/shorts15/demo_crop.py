#!/usr/bin/env python3
"""REPORT DEMO helper: cut one panel out of a captured report section (lib/report_capture.py, 1600x900 PNG),
mask what must not be shown, and scale it to the vertical frame width.

  demo_crop.py SECTION.png OUT.png x0,y0,x1,y1 [--blur x0,y0,x1,y1 ...] [--width 940]

Blur boxes are in SECTION coordinates (before the crop). Mask seller and dealer names and logos, owner names
(people and LLCs), phone numbers and addresses, and data-source labels / fine print (ADS-B, FlightRadar24,
FAA document index, NTSB, SDR). The subject tail may stay: it is what the viewer types in.
Always look at OUT.png after masking."""
import sys
from PIL import Image, ImageFilter


def crop(sec, out, box, blurs=(), width=940):
    im = Image.open(sec).convert("RGB")
    for b in blurs:
        x0, y0, x1, y1 = b
        reg = im.crop(b)
        # pixelate + blur so no letter shape survives
        small = reg.resize((max(1, (x1 - x0) // 14), max(1, (y1 - y0) // 10)), Image.BILINEAR)
        im.paste(small.resize(reg.size, Image.NEAREST).filter(ImageFilter.GaussianBlur(6)), (x0, y0))
    c = im.crop(box)
    sc = width / c.width
    c = c.resize((width, int(c.height * sc)), Image.LANCZOS)
    c.save(out)
    print(out, c.size, f"scale {sc:.2f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    sec, out, box = a[0], a[1], tuple(int(v) for v in a[2].split(","))
    blurs, width, i = [], 940, 3
    while i < len(a):
        if a[i] == "--blur":
            blurs.append(tuple(int(v) for v in a[i + 1].split(","))); i += 2
        elif a[i] == "--width":
            width = int(a[i + 1]); i += 2
        else:
            raise SystemExit("unknown arg " + a[i])
    crop(sec, out, box, blurs, width)
