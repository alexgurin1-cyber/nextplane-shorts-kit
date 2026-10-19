#!/usr/bin/env python3
"""Crop the listing-history section (captured at CAP_W=1000) to the stats row + step chart; no source-site names.
usage: report_crop.py <capdir> <out.png>"""
import sys, glob
from PIL import Image
d, out = sys.argv[1], sys.argv[2]
f = sorted(glob.glob(f"{d}/sec_*listing_history*.png"))
src = Image.open(f[0] if f else f"{d}/full.png").convert("RGB")
w = src.width; im = src.crop((20, 0, w-20, int(src.height*0.43)))
im.save(out); print(out, im.size)
