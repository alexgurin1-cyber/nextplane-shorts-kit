#!/usr/bin/env python3
"""Canonical NextPlane end card (reference-approved 2026-07-23).
draw_endcard(im, t, fonts_dir, logo_path) -> PIL Image. t = seconds since scene start."""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
W, H = 1080, 1920
CYAN = (37, 197, 203); OFF = (246, 249, 250); WHITE = (255, 255, 255)
_cache = {}
def _font(fd, name, size):
    k = (name, size)
    if k not in _cache: _cache[k] = ImageFont.truetype(os.path.join(fd, name), size)
    return _cache[k]
def _logo(path, dpx):
    k = ("logo", dpx)
    if k not in _cache:
        lg = Image.open(path).convert("RGBA")
        _cache[k] = lg.resize((dpx, dpx), Image.LANCZOS)
    return _cache[k]
def _ease(p):
    p = min(max(p, 0.0), 1.0)
    return p * p * (3 - 2 * p)
def _paste_fade(im, sp, xy, a):
    if a <= 0: return
    if a < 1:
        sp = sp.copy(); sp.putalpha(sp.getchannel("A").point(lambda v: int(v * a)))
    im.paste(sp, xy, sp)
def _sh_center(d, y, s, f, fill, a, sh=3):
    col = tuple(int(v * a) for v in fill)
    d.text((W//2 + sh, y + sh), s, font=f, fill=(0, 0, 0), anchor="mm")
    d.text((W//2, y), s, font=f, fill=col, anchor="mm")
def _tracked_w(d, s, f, tr):
    return sum(d.textlength(c, font=f) for c in s) + tr * (len(s) - 1)
def _tracked_center(d, y, s, f, fill, a, tr=8, sh=3):
    col = tuple(int(v * a) for v in fill)
    tw = _tracked_w(d, s, f, tr)
    x = W/2 - tw/2
    for c in s:
        d.text((x + sh, y + sh), c, font=f, fill=(0, 0, 0), anchor="lm")
        d.text((x, y), c, font=f, fill=col, anchor="lm")
        x += d.textlength(c, font=f) + tr
    return tw
def draw_endcard(im, t, fonts_dir, logo_path):
    d = ImageDraw.Draw(im, "RGBA")
    BC_B = lambda s: _font(fonts_dir, "BarlowCondensed-Bold.ttf", s)
    SM_B = lambda s: _font(fonts_dir, "SpaceMono-Bold.ttf", s)
    # logo
    a0 = _ease(t / 0.15)
    lg = _logo(logo_path, 270)
    _paste_fade(im, lg, (W//2 - 135, 430), a0)
    d = ImageDraw.Draw(im, "RGBA")
    # wordmark + underline
    a1 = _ease((t - 0.2) / 0.4)
    if a1 > 0:
        tw = _tracked_center(d, 830, "NEXTPLANE", BC_B(150), OFF, a1, tr=10)
        a1b = _ease((t - 0.55) / 0.4)
        if a1b > 0:
            uw = int(tw * a1b)
            d.rounded_rectangle([W/2 - uw/2, 930, W/2 + uw/2, 937],
                                radius=3, fill=(*CYAN, int(255 * a1b)))
    # tagline
    a2 = _ease((t - 0.85) / 0.45)
    if a2 > 0: _sh_center(d, 1055, "DON'T BUY THE STORY.", BC_B(92), OFF, a2)
    a3 = _ease((t - 1.35) / 0.45)
    if a3 > 0: _sh_center(d, 1165, "BUY THE DATA.", BC_B(92), CYAN, a3)
    # pill
    a4 = _ease((t - 2.0) / 0.5)
    if a4 > 0:
        f = SM_B(58)
        txt = "NEXTPLANE.US"
        tw = d.textlength(txt, font=f)
        x0, x1 = W/2 - tw/2 - 46, W/2 + tw/2 + 46
        y0, y1 = 1315, 1435
        d.rounded_rectangle([x0, y0, x1, y1], radius=26,
                            outline=(*CYAN, int(230 * a4)), width=3,
                            fill=(13, 27, 38, int(120 * a4)))
        _sh_center(d, (y0 + y1)//2, txt, f, WHITE, a4)
    return im
