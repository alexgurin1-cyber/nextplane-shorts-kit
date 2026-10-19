#!/usr/bin/env python3
"""How to Buy a TBM 930 (Ep6, N24MY) — 1920x1080@30 renderer.
Usage: render.py seg <i> <n>   -> renders segment i of n to seg_i.mp4 (raw frames piped to ffmpeg)
       render.py still <t>      -> writes still_<t>.png"""
import json, math, os, subprocess, sys, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, "/tmp/htb_tbm"); sys.path.insert(0, os.path.expanduser("~/kit/lib"))
from timeline import SCENES, OFFS, TOTAL
from beats import BEATS
BID = {sc: b for b, sc, _ in BEATS}
import endcard as EC

ROOT = "/tmp/htb_tbm"; FD = f"{ROOT}/fonts"; CAP = f"{ROOT}/cap"; PH = f"{ROOT}/photos"
W, H, FPS = 1920, 1080, 30
NAVY = (8, 16, 26); NAVY2 = (15, 42, 63); CYAN = (37, 197, 203); OFF = (246, 249, 250); WHITE = (255, 255, 255)
GREY = (150, 165, 178); DIM = (70, 92, 110)
_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(f"{FD}/{name}", size)
    return _fc[k]
BB = lambda s: F("BarlowCondensed-Bold.ttf", s)
BS = lambda s: F("BarlowCondensed-SemiBold.ttf", s)
MB = lambda s: F("SpaceMono-Bold.ttf", s)
MR = lambda s: F("SpaceMono-Regular.ttf", s)
def ease(p): p = min(max(p, 0.0), 1.0); return p * p * (3 - 2 * p)
def lerp(a, b, p): return a + (b - a) * p

# ---------- word timing ----------
WORDS = []  # (global_start, global_end, word, bid)
for bid, _, _ in BEATS:
    for w in json.load(open(f"{ROOT}/vo/{bid}.json"))["words"]:
        WORDS.append((OFFS[bid] + w["s"], OFFS[bid] + w["e"], w["w"], bid))
def trig(bid, sub, n=1, default=None):
    k = 0
    for s, e, w, b in WORDS:
        if b == bid and sub.lower() in w.lower():
            k += 1
            if k == n: return s
    return default if default is not None else OFFS[bid]

# ---------- captions (phrase chunks) ----------
CHUNKS = []
cur = []
for i, (s, e, w, b) in enumerate(WORDS):
    cur.append((s, e, w, b))
    nxt = WORDS[i + 1] if i + 1 < len(WORDS) else None
    brk = w[-1] in ".,?:;!" or len(cur) >= 7 or nxt is None or nxt[3] != b or (nxt[0] - e) > 0.6
    if brk:
        CHUNKS.append([cur[0][0], cur[-1][1], " ".join(x[2] for x in cur), b]); cur = []
for i in range(len(CHUNKS) - 1):
    if CHUNKS[i + 1][3] == CHUNKS[i][3]:
        CHUNKS[i][1] = max(CHUNKS[i][1], min(CHUNKS[i + 1][0], CHUNKS[i][1] + 0.35))
def caption(im, t):
    for s, e, txt, b in CHUNKS:
        if b == BID["end"]: continue
        if s - 0.05 <= t <= e + 0.12:
            d = ImageDraw.Draw(im, "RGBA"); f = BS(46)
            tw = d.textlength(txt, font=f)
            x0, y0 = W / 2 - tw / 2 - 26, 968
            d.rounded_rectangle([x0, y0, W / 2 + tw / 2 + 26, y0 + 70], radius=14, fill=(5, 10, 16, 200))
            d.text((W / 2, y0 + 35), txt, font=f, fill=WHITE, anchor="mm")
            return

# ---------- shared drawing ----------
_bgc = {}
def photo_bg(name, blur=0, dark=0.55, focus=(0.5, 0.5)):
    k = (name, blur, dark, focus)
    if k in _bgc: return _bgc[k]
    im = Image.open(f"{PH}/{name}").convert("RGB")
    sc = max(W * 1.1 / im.width, H * 1.1 / im.height)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    x = int((im.width - W * 1.1) * focus[0]); y = int((im.height - H * 1.1) * focus[1])
    im = im.crop((x, y, x + int(W * 1.1), y + int(H * 1.1)))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    ov = Image.new("RGBA", im.size, (*NAVY, int(255 * dark)))
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    _bgc[k] = im; return im
def kb(bg, p, z0=1.0, z1=1.06, dx=0.0):
    """Ken Burns crop from a 1.1x plate."""
    z = lerp(z0, z1, p); cw, ch = bg.width / 1.1 / z * 1.0, bg.height / 1.1 / z
    cx = bg.width / 2 + dx * p * 40; cy = bg.height / 2
    box = (int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))
    return bg.crop(box).resize((W, H), Image.BILINEAR)
def chip(d, x, y, txt, fill=CYAN, fg=NAVY, f=None):
    f = f or MB(24); tw = d.textlength(txt, font=f)
    d.rounded_rectangle([x, y, x + tw + 36, y + 46], radius=10, fill=fill)
    d.text((x + 18, y + 23), txt, font=f, fill=fg, anchor="lm"); return x + tw + 36
def header_bar(im, step, title):
    d = ImageDraw.Draw(im, "RGBA")
    x = chip(d, 70, 50, step)
    d.text((x + 22, 73), title, font=BB(46), fill=OFF, anchor="lm")
    tw = d.textlength("N24MY · 2016 DAHER TBM 930", font=MB(22))
    d.rounded_rectangle([W - 110 - tw, 52, W - 70, 96], radius=10, outline=(*CYAN, 200), width=2, fill=(8, 16, 26, 170))
    d.text((W - 90 - tw, 74), "N24MY · 2016 DAHER TBM 930", font=MB(22), fill=OFF, anchor="lm")
def bullet(d, x, y, txt, f, fill=WHITE, mark="ok"):
    col = CYAN if mark == "ok" else (230, 120, 110) if mark == "no" else GREY
    if mark == "ok":
        d.line([(x, y), (x + 9, y + 10), (x + 26, y - 12)], fill=col, width=6, joint="curve")
    elif mark == "no":
        d.line([(x, y - 11), (x + 22, y + 11)], fill=col, width=6); d.line([(x, y + 11), (x + 22, y - 11)], fill=col, width=6)
    else:
        d.line([(x, y), (x + 22, y)], fill=col, width=5); d.line([(x + 12, y - 9), (x + 22, y), (x + 12, y + 9)], fill=col, width=5)
    d.text((x + 46, y), txt, font=f, fill=fill, anchor="lm")
def panel(d, box, a=235):
    d.rounded_rectangle(box, radius=22, fill=(10, 22, 34, a), outline=(37, 197, 203, 90), width=2)
def money(v): return "${:,.0f}".format(v)
def count(v, p): return money(round(v * ease(p) / 100) * 100 if p < 1 else v)

# ---------- report slide ----------
_rc = {}
def report_img(key, crop, blurs, maxw=1720, maxh=790):
    k = (key, tuple(crop), maxw, maxh)
    if k in _rc: return _rc[k]
    im = Image.open(f"{CAP}/{key}.png").convert("RGB")
    for bx in list(blurs) + EXTRA_BLUR.get(key, []):
        x0, y0, x1, y1 = [int(v * 2) for v in bx]
        reg = im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(14))
        im.paste(reg, (x0, y0))
    for bx, txt in RELABEL.get(key, []):
        x0, y0, x1, y1 = [int(v * 2) for v in bx]
        col = im.getpixel((max(x0 - 3, 0), y0 + 2))
        dd = ImageDraw.Draw(im); dd.rectangle([x0, y0, x1, y1], fill=col)
        dd.text((x0, (y0 + y1) / 2), txt, font=MR(int((y1 - y0) * 0.8)), fill=(150, 165, 178), anchor="lm")
    x0, y0, x1, y1 = [int(v * 2) for v in crop]
    im = im.crop((x0, y0, x1, y1))
    sc = min(maxw / im.width, maxh / im.height)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    _rc[k] = (im, sc * 2, (x0 / 2, y0 / 2)); return _rc[k]
def report_slide(im, t, key, crop, callouts, blurs=(), cy=540, t0=0, maxh=790, maxw=1720, cx=960):
    rim, sc, (ox, oy) = report_img(key, crop, blurs, maxw=maxw, maxh=maxh)
    x = int(cx - rim.width / 2); y = int(cy - rim.height / 2)
    a = ease((t - t0) / 0.5)
    sh = Image.new("RGBA", (rim.width + 60, rim.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([30, 30, rim.width + 30, rim.height + 30], radius=12, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    im.paste(sh, (x - 30, y - 20), sh)
    if a < 1:
        r2 = rim.copy(); r2.putalpha(int(255 * a)); im.paste(r2, (x, y + int((1 - a) * 30)), r2)
    else:
        im.paste(rim, (x, y))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([x - 2, y - 2, x + rim.width + 2, y + rim.height + 2], radius=6, outline=(37, 197, 203, 120), width=2)
    for (bx, ts) in callouts:
        p = ease((t - ts) / 0.35)
        if p <= 0: continue
        bx0 = x + (bx[0] - ox) * sc; by0 = y + (bx[1] - oy) * sc
        bx1 = x + (bx[2] - ox) * sc; by1 = y + (bx[3] - oy) * sc
        g = (1 - p) * 18
        d.rounded_rectangle([bx0 - 8 - g, by0 - 8 - g, bx1 + 8 + g, by1 + 8 + g], radius=10, outline=(*CYAN, int(255 * p)), width=5)
    return x, y, rim

