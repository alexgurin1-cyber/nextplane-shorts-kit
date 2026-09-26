#!/usr/bin/env python3
"""Rebuild NextPlane logo (dark-bg variant) from nextplane_logo.svg geometry with PIL. 800x800 RGBA."""
import math
from PIL import Image, ImageDraw
S = 8
N = 800; U = N / 120.0
OFF = (246, 249, 250, 255); CYAN = (37, 197, 203, 255)
im = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
def P(x, y): return (x * U * S, y * U * S)
cx, cy, r, w = 60, 60, 48, 5
d.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], outline=OFF, width=int(w * U * S))
d.ellipse([P(56, 8), P(64, 16)], fill=CYAN)
d.rectangle([P(58.5, 108), P(61.5, 114)], fill=OFF)
d.rectangle([P(108, 58.5), P(114, 61.5)], fill=OFF)
d.rectangle([P(6, 58.5), P(12, 61.5)], fill=OFF)
def rot(x, y, a=22):
    t = math.radians(a); dx, dy = x - 60, y - 60
    return (60 + dx * math.cos(t) - dy * math.sin(t), 60 + dx * math.sin(t) + dy * math.cos(t))
def tri(pts, col):
    d.polygon([P(*rot(x, y)) for x, y in pts], fill=col)
tri([(60, 24), (70, 60), (60, 60)], CYAN)
tri([(60, 24), (50, 60), (60, 60)], (37, 197, 203, 217))
tri([(60, 96), (70, 60), (60, 60)], OFF)
tri([(60, 96), (50, 60), (60, 60)], (246, 249, 250, 224))
d.ellipse([P(57, 57), P(63, 63)], fill=OFF)
im = im.resize((N, N), Image.LANCZOS)
im.save("/tmp/bw/assets/logo.png")
print("logo ok", im.size)
