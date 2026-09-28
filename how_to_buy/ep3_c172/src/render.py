#!/usr/bin/env python3
"""How to Buy a Cessna 172 (Ep3, N733JE) — 1920x1080@30 renderer.
Usage: render.py seg <i> <n>   -> renders segment i of n to seg_i.mp4 (raw frames piped to ffmpeg)
       render.py still <t>      -> writes still_<t>.png"""
import json, math, os, subprocess, sys, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, "/tmp/htb_c172"); sys.path.insert(0, os.path.expanduser("~/kit/lib"))
from timeline import SCENES, OFFS, TOTAL
from beats import BEATS
BID = {sc: b for b, sc, _ in BEATS}
import endcard as EC

ROOT = "/tmp/htb_c172"; FD = f"{ROOT}/fonts"; CAP = f"{ROOT}/cap3"; PH = f"{ROOT}/photos"
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
    tw = d.textlength("N733JE · 1977 CESSNA 172N", font=MB(22))
    d.rounded_rectangle([W - 110 - tw, 52, W - 70, 96], radius=10, outline=(*CYAN, 200), width=2, fill=(8, 16, 26, 170))
    d.text((W - 90 - tw, 74), "N733JE · 1977 CESSNA 172N", font=MB(22), fill=OFF, anchor="lm")
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
    k = (key, tuple(crop), maxh)
    if k in _rc: return _rc[k]
    im = Image.open(f"{CAP}/{key}.png").convert("RGB")
    for bx in blurs:
        x0, y0, x1, y1 = [int(v * 2) for v in bx]
        reg = im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(14))
        im.paste(reg, (x0, y0))
    x0, y0, x1, y1 = [int(v * 2) for v in crop]
    im = im.crop((x0, y0, x1, y1))
    sc = min(maxw / im.width, maxh / im.height)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    _rc[k] = (im, sc * 2, (x0 / 2, y0 / 2)); return _rc[k]
def report_slide(im, t, key, crop, callouts, blurs=(), cy=540, t0=0, maxh=790):
    rim, sc, (ox, oy) = report_img(key, crop, blurs, maxh=maxh)
    x = (W - rim.width) // 2; y = int(cy - rim.height / 2)
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

# ---------- data (from DATA_PACK) ----------
LADDER = [("172–172L", "1956–72", 94950, "fifty-six"), ("172M", "1973–76", 139000, "M,"), ("172N", "1977–80", 129900, "N,"),
          ("172P", "1981–86", 184000, "P,"), ("172R", "1996–2008", 240000, "R"), ("172S", "1998+", 309900, "S")]
COMPS = [99000, 100000, 109900, 119000, 119900, 119900, 120000, 125000, 129000, 129900, 129900, 134900, 135000, 137000, 137500, 142000, 159900, 165000, 169000]
HERO_IDX = 9
PH_HIST = [("May 16", 150000), ("May 21", 145000), ("May 25", 140000), ("Jul 9", 137500), ("Aug 9", 135000), ("Sep 17", 129900), ("Sep 28", 129900)]

# ---------- scenes ----------
def sc_cold(im, t, s0, s1):
    bg = photo_bg("c172n_sky-0.jpg", dark=0.35)
    im.paste(kb(bg, (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA")
    t_med = trig(BID["pick"], "median"); t_25 = trig(BID["pick"], "twenty-five"); t_today = trig(BID["pick"], "Today")
    if t < t_med - 0.4:
        p = (t - s0 - 0.3) / 1.2
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 70))
        d.text((W / 2, 420), count(129900, p), font=MB(150), fill=WHITE, anchor="mm")
        d.text((W / 2, 530), "ASKING PRICE · 1977 CESSNA 172N · SALISBURY, MD", font=MB(28), fill=CYAN, anchor="mm")
        if t > trig(BID["pick"], "Line"):
            # rank strip
            pa = ease((t - trig(BID["pick"], "Line")) / 0.6)
            x0, x1, yy = 360, 1560, 700
            d.line([x0, yy, x1, yy], fill=(246, 249, 250, int(160 * pa)), width=3)
            for i, v in enumerate(COMPS):
                xx = x0 + (v - 95000) / (175000 - 95000) * (x1 - x0)
                hero = i == HERO_IDX
                r = 16 if hero else 10
                d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(*(CYAN if hero else OFF), int(255 * pa)))
            if t > trig(BID["pick"], "Tenth"):
                d.text((W / 2, 780), "10th OF 19 ACTIVE 172Ns · THE MEDIAN", font=MB(34), fill=CYAN, anchor="mm")
    elif t < t_25 - 0.3:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 120))
        d.text((W / 2, 470), "PRICED AT THE MARKET", font=BB(120), fill=WHITE, anchor="mm")
        d.text((W / 2, 580), "ask $129,900  =  172N median $129,900", font=MB(34), fill=CYAN, anchor="mm")
    elif t < t_today - 0.2:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 120))
        p = (t - t_25) / 0.8
        d.text((W / 2, 440), "+{}%".format(int(25 * ease(p))), font=MB(170), fill=CYAN, anchor="mm")
        d.text((W / 2, 570), "COST PER NAUTICAL MILE VS. THE AVERAGE 172", font=MB(32), fill=WHITE, anchor="mm")
        d.text((W / 2, 625), "$1.73 vs $1.38 · NextPlane Aircraft Report", font=MR(26), fill=GREY, anchor="mm")
    else:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 150))
        p = ease((t - t_today) / 0.6)
        d.text((W / 2, 400), "HOW TO BUY A", font=BB(90), fill=(*OFF, int(255 * p)), anchor="mm")
        d.text((W / 2, 510), "CESSNA 172", font=BB(170), fill=(*CYAN, int(255 * p)), anchor="mm")
        d.text((W / 2, 630), "ONE REAL AIRCRAFT · ONE REAL REPORT", font=MB(30), fill=(*OFF, int(220 * p)), anchor="mm")

def sc_fleet(im, t, s0, s1):
    bg = photo_bg("c172n-0.jpg", dark=0.4)
    im.paste(kb(bg, (t - s0) / (s1 - s0), 1.02, 1.1, dx=-1))
    header_bar(im, "STEP 1", "WHERE THIS AIRCRAFT SITS")
    d = ImageDraw.Draw(im, "RGBA")
    p1 = (t - trig("b02", "forty-four")) / 0.9; p2 = (t - trig("b02", "nineteen")) / 0.9
    if p1 > 0:
        panel(d, [160, 330, 900, 700])
        d.text((530, 470), "~{:,}".format(int(44000 * ease(p1) / 100) * 100), font=MB(110), fill=WHITE, anchor="mm")
        d.text((530, 580), "172s BUILT WORLDWIDE", font=MB(30), fill=CYAN, anchor="mm")
    if p2 > 0:
        panel(d, [1020, 330, 1760, 700])
        d.text((1390, 470), "{:,}".format(int(19447 * ease(p2))), font=MB(110), fill=WHITE, anchor="mm")
        d.text((1390, 580), "STILL ACTIVE ON THE US REGISTRY", font=MB(30), fill=CYAN, anchor="mm")
    if t > trig("b02", "generation"):
        d.text((W / 2, 820), "YOU'RE SHOPPING FOR A GENERATION", font=BB(64), fill=OFF, anchor="mm")

def sc_ladder(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n_sky-1.jpg", blur=10, dark=0.78), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "THE 172 PRICE LADDER")
    d = ImageDraw.Draw(im, "RGBA")
    panel(d, [110, 140, 1810, 930])
    d.text((160, 190), "MEDIAN ASKING PRICE · ACTIVE US LISTINGS · WEEK OF SEP 28, 2026", font=MB(24), fill=GREY, anchor="lm")
    x0, xmax = 520, 1640; vmax = 320000
    for i, (lab, yrs, v, key) in enumerate(LADDER):
        ts = trig(BID["ladder"], key, default=s0 + 2 + i * 6)
        if key == "R": ts = trig(BID["ladder"], "fuel-injected")
        if key == "S": ts = trig(BID["ladder"], "S", 2) if trig(BID["ladder"], "S", 2) > trig(BID["ladder"], "fuel-injected") else ts
        p = ease((t - ts) / 0.8)
        y = 255 + i * 108
        hero = lab == "172N"
        col = CYAN if hero else (120, 150, 170)
        d.text((160, y + 20), lab, font=BB(52), fill=CYAN if hero else OFF, anchor="lm")
        d.text((345, y + 22), yrs, font=MR(24), fill=GREY, anchor="lm")
        if p > 0:
            bw = (xmax - x0) * v / vmax * p
            d.rounded_rectangle([x0, y, x0 + max(bw, 8), y + 44], radius=8, fill=(*col, 255))
            d.text((x0 + bw + 18, y + 22), money(v) + (" (n=5)" if lab == "172R" else ""), font=MB(30), fill=WHITE, anchor="lm")
    if t > trig(BID["ladder"], "sweet"):
        p = ease((t - trig(BID["ladder"], "sweet")) / 0.5)
        d.rounded_rectangle([140, 350, 1790, 568], radius=16, outline=(*CYAN, int(255 * p)), width=4)
        d.text((1780, 330), "THE SWEET SPOT: MOST AIRPLANES, MOST COMPS", font=MB(24), fill=(*CYAN, int(255 * p)), anchor="rm")

def sc_header(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n_sky-0.jpg", blur=14, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT DOES THE REPORT SAY FIRST?")
    # header (220) + verdict strip (first 236 css px)
    tb = [("$129,900", (0, 150, 290, 215), "Asking"), ("None", (290, 150, 575, 215), "damage"),
          ("6.9", (575, 220 + 10, 865, 220 + 100), "same"), ("nolien", (0, 220 + 122, 290, 220 + 230), "security")]
    cos = [((b[0], b[1], b[2], b[3]), trig(BID["header"], k)) for _, b, k in tb]
    report_slide(im, t, "_headercomb", (0, 0, 1152, 456), cos, t0=s0, cy=560)

def big3(im, t, s0, items, y=330):
    d = ImageDraw.Draw(im, "RGBA")
    n = len(items); bw = 520; gap = 40; x = (W - (n * bw + (n - 1) * gap)) / 2
    for i, (lab, v, sub, ts, hi) in enumerate(items):
        p = (t - ts) / 0.9
        if p <= 0: continue
        panel(d, [x, y, x + bw, y + 330])
        d.text((x + bw / 2, y + 70), lab, font=MB(24), fill=CYAN if hi else GREY, anchor="mm")
        d.text((x + bw / 2, y + 165), count(v, p), font=MB(78), fill=CYAN if hi else WHITE, anchor="mm")
        d.text((x + bw / 2, y + 255), sub, font=MR(22), fill=GREY, anchor="mm")
        x += bw + gap

def sc_value(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n_sky-2.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "IS THE PRICE FAIR?")
    big3(im, t, s0, [("ASKING PRICE", 129900, "published ask", s0 + 0.3, False),
                     ("172N ACTIVE MEDIAN", 129900, "19 listings · outliers removed", trig(BID["value"], "nineteen"), False),
                     ("NEXTPLANE FAIR VALUE", 121187, "price model · scored Sep 16", trig(BID["value"], "fair-value"), True)])
    d = ImageDraw.Draw(im, "RGBA")
    tv = trig(BID["value"], "About")
    if t > tv:
        p = ease((t - tv) / 0.5); txt = "THE MARKET SAYS FAIR · THE MODEL SAYS ~7% RICH"
        tw = d.textlength(txt, font=BB(60))
        d.rounded_rectangle([W / 2 - tw / 2 - 40, 760, W / 2 + tw / 2 + 40, 860], radius=18, fill=(*CYAN, int(255 * p)))
        d.text((W / 2, 810), txt, font=BB(60), fill=NAVY, anchor="mm")

def sc_comps(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n_sky-1.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT MAKES ONE 172N WORTH MORE?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 920])
    d.text((160, 200), "19 ACTIVE CESSNA 172Ns · ASKING PRICE · IQR OUTLIER GATE APPLIED", font=MB(24), fill=GREY, anchor="lm")
    x0, x1, yy = 220, 1700, 560
    d.line([x0, yy, x1, yy], fill=(*GREY, 255), width=2)
    for v in (100000, 120000, 140000, 160000):
        xx = x0 + (v - 95000) / (175000 - 95000) * (x1 - x0)
        d.line([xx, yy - 8, xx, yy + 8], fill=GREY, width=2); d.text((xx, yy + 40), money(v), font=MR(22), fill=GREY, anchor="mm")
    order = sorted(range(len(COMPS)), key=lambda i: COMPS[i])
    stack = {}
    for k, i in enumerate(order):
        p = ease((t - s0 - 0.3 - k * 0.12) / 0.4)
        if p <= 0: continue
        v = COMPS[i]; xx = x0 + (v - 95000) / (175000 - 95000) * (x1 - x0)
        b = round(xx / 22); lvl = stack.get(b, 0); stack[b] = lvl + 1
        yc = yy - 40 - lvl * 40
        hero = i == HERO_IDX; r = 17 if hero else 13
        d.ellipse([xx - r, yc - r, xx + r, yc + r], fill=(*(CYAN if hero else OFF), int(255 * p)))
        if hero:
            d.line([xx, yc - 24, xx, 300], fill=CYAN, width=3)
            d.text((xx, 280), "N733JE · $129,900", font=MB(30), fill=CYAN, anchor="mm")
    if t > trig(BID["comps"], "cheap"):
        d.text((x0, 720), "← HIGH AIRFRAME TIME / TIRED ENGINES", font=MB(26), fill=OFF, anchor="lm")
    if t > trig(BID["comps"], "expensive"):
        d.text((x1, 780), "FRESH ENGINES →", font=MB(26), fill=OFF, anchor="rm")
    if t > trig(BID["comps"], "condition"):
        d.text((W / 2, 860), "MIDDLE ON PRICE. MIDDLE ON CONDITION?", font=BB(54), fill=CYAN, anchor="mm")

def bar2(d, y, lab, v, ref, vmax, p, unit, sub):
    x0, x1 = 480, 1500
    d.text((170, y + 10), lab, font=BB(46), fill=OFF, anchor="lm")
    d.rounded_rectangle([x0, y - 16, x0 + (x1 - x0) * v / vmax * ease(p), y + 30], radius=8, fill=CYAN)
    d.rounded_rectangle([x0, y + 44, x0 + (x1 - x0) * ref / vmax * ease(p), y + 84], radius=8, fill=(110, 140, 160))
    d.text((x0 + (x1 - x0) * v / vmax * ease(p) + 16, y + 7), "{:,} {}".format(int(v * ease(p)), unit), font=MB(28), fill=WHITE, anchor="lm")
    d.text((x0 + (x1 - x0) * ref / vmax * ease(p) + 16, y + 64), "{:,} {}".format(int(ref * ease(p)), sub), font=MR(24), fill=GREY, anchor="lm")

def sc_hours(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n-1.jpg", blur=10, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHERE DOES OURS FALL?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 920])
    d.text((160, 200), "N733JE (CYAN) VS. MEDIAN OF ACTIVE 172Ns (GREY)", font=MB(24), fill=GREY, anchor="lm")
    bar2(d, 320, "AIRFRAME TT", 5500, 7512, 8500, (t - s0 - 0.3) / 0.9, "hrs", "hrs · 172N median")
    te = trig(BID["hours"], "engine")
    if t > te:
        p = ease((t - te) / 1.0)
        d.text((170, 560), "ENGINE", font=BB(46), fill=OFF, anchor="lm")
        x0, x1 = 480, 1500
        d.rounded_rectangle([x0, 540, x1, 600], radius=10, fill=(40, 60, 76))
        d.rounded_rectangle([x0, 540, x0 + (x1 - x0) * 0.75 * p, 600], radius=10, fill=CYAN)
        d.text((x1, 640), "TBO 2,000 hrs", font=MR(24), fill=GREY, anchor="rm")
        d.text((x0, 640), "{:,} hrs SMOH".format(int(1500 * p)), font=MB(28), fill=WHITE, anchor="lm")
        if t > trig(BID["hours"], "quarters"):
            d.text((W / 2, 790), "75% OF THE WAY TO OVERHAUL · 500 HOURS LEFT", font=BB(60), fill=CYAN, anchor="mm")

def sc_pricehist(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n_sky-0.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS THE SELLER NOTICED?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 920])
    d.text((160, 200), "ASKING PRICE · N733JE · VERIFIED BY NEXTPLANE", font=MB(24), fill=GREY, anchor="lm")
    import datetime as dtm
    def dx(s):
        m = {"May": 5, "Jul": 7, "Aug": 8, "Sep": 9}[s.split()[0]]; return dtm.date(2026, m, int(s.split()[1]))
    d0, d1 = dtm.date(2026, 5, 10), dtm.date(2026, 10, 1)
    X = lambda dd: 230 + (dd - d0).days / (d1 - d0).days * 1480
    Y = lambda v: 780 - (v - 125000) / (152000 - 125000) * 480
    for v in (130000, 140000, 150000):
        d.line([230, Y(v), 1710, Y(v)], fill=(60, 80, 96), width=1); d.text((215, Y(v)), money(v), font=MR(20), fill=GREY, anchor="rm")
    cut_words = [("Five", 1), ("Another", 1), ("July", 1), ("August", 1), ("fifty-one", 1)]
    tcut = [trig(BID["pricehist"], "mid-May")] + [trig(BID["pricehist"], w, n) for w, n in cut_words]
    pts = []
    for i, (lab, v) in enumerate(PH_HIST[:-1]):
        if t < tcut[i]: break
        pts.append((X(dx(lab)), Y(v), lab, v))
    if pts:
        path = []
        for i, (x, y, lab, v) in enumerate(pts):
            if i: path.append((x, path[-1][1]))
            path.append((x, y))
        path.append((X(dtm.date(2026, 9, 28)) if len(pts) == 6 else pts[-1][0] + 20, path[-1][1]))
        d.line(path, fill=CYAN, width=5)
        for x, y, lab, v in pts:
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=CYAN)
            d.text((x, y - 30), money(v), font=MB(22), fill=WHITE, anchor="mm")
            if lab not in ("May 21", "May 25"): d.text((x, 815), lab, font=MR(20), fill=GREY, anchor="mm")
    if t > trig(BID["pricehist"], "thirteen"):
        chip(d, 1200, 250, "5 CUTS · −$20,100 · −13.4%", f=MB(26))
    if t > trig(BID["pricehist"], "Most"):
        d.text((W / 2, 880), "MOST 172 SELLERS NEVER CUT · TYPICAL TOTAL CUT 8% · THIS ONE: 13.4%", font=MB(28), fill=OFF, anchor="mm")

def sc_owner(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n-4.jpg", blur=14, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO OWNED IT, AND HOW WAS IT USED?")
    blurs = [(20, 114, 300, 144), (55, 203, 700, 232)]
    cos = [((20, 100, 1130, 150), trig(BID["owner"], "registered")), ((20, 245, 1130, 278), trig(BID["owner"], "Almost"))]
    report_slide(im, t, "reg", (0, 88, 1152, 480), cos, blurs=blurs, t0=s0, cy=530)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(BID["owner"], "Training"):
        chip(d, 70, 880, "TRAINING HISTORY ≠ BAD · MORE LANDINGS, MORE WEAR ON SEATS, DOORS, BRAKES", fill=(15, 42, 63), fg=OFF, f=MB(24))

def sc_flight(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n-11.jpg", blur=6, dark=0.72), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "STEP 2", "IS IT STILL FLYING?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [460, 300, 1460, 760])
    p = ease((t - trig(BID["flight"], "one")) / 0.6)
    d.text((W / 2, 440), "1", font=MB(170), fill=(*CYAN, int(255 * p)), anchor="mm")
    d.text((W / 2, 560), "TRACKED FLIGHT · LAST 12 MONTHS (ADS-B)", font=MB(28), fill=OFF, anchor="mm")
    if t > trig(BID["flight"], "ask"):
        d.text((W / 2, 670), "ASK: LOGBOOK HOURS, LAST 12 MONTHS", font=BB(52), fill=CYAN, anchor="mm")

def sc_ads(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n-1.jpg", blur=14, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT SHOULD THE PAPERWORK SHOW?")
    t2 = trig(BID["ads"], "Two")
    if t < t2 - 0.2:
        blurs = [(250, 270, 440, 340), (680, 350, 1120, 395)]
        cos = [((30, 250, 230, 330), trig(BID["ads"], "twelve"))]
        report_slide(im, t, "ads", (0, 0, 1152, 345), cos, blurs=blurs, t0=s0, cy=520)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(BID["ads"], "Seven"):
            chip(d, 360, 860, "12 MATCHED · 7 CONDITIONAL ON INSTALLED EQUIPMENT · 5 APPLY OUTRIGHT", f=MB(26))
    else:
        cos = [((20, 1850, 1140, 1905), trig(BID["ads"], "seat-rail")), ((20, 1926, 1140, 1995), trig(BID["ads"], "doorpost"))]
        report_slide(im, t, "ads", (0, 1846, 1152, 2110), cos, t0=t2 - 0.2, cy=500)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(BID["ads"], "logbooks"):
            chip(d, 480, 860, "PRE-BUY: AD 2011-10-09 (SEAT RAILS) · AD 2020-18-01 (DOORPOST)", f=MB(26))

def sc_sdr(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n_sky-1.jpg", blur=14, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS IT EVER BEEN HURT?")
    cos = [((10, 540, 1140, 585), trig(BID["sdr"], "service"))]
    report_slide(im, t, "sdr", (0, 0, 1152, 598), cos, t0=s0, cy=490, maxh=730)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(BID["sdr"], "N"):
        chip(d, 70, 885, "NTSB RECORDS FOR THIS AIRCRAFT: NONE", f=MB(26))

def sc_cpm(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n-3.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT WILL THAT ENGINE COST ME?")
    cos = [((25, 100, 565, 215), trig(BID["cpm"], "seventy-three")), ((582, 100, 1127, 215), trig(BID["cpm"], "thirty-eight")),
           ((20, 225, 1130, 262), trig(BID["cpm"], "twenty-five"))]
    report_slide(im, t, "cpm", (0, 0, 1152, 440), cos, t0=s0, cy=500)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(BID["cpm"], "eighty"):
        chip(d, 70, 880, "$40,000 OVERHAUL ÷ 500 HRS LEFT = $80/HR RESERVE", f=MB(26))
    if t > trig(BID["cpm"], "Compared"):
        chip(d, 1020, 880, "≈ $9,520 MORE ENGINE LIFE USED", f=MB(26))

def sc_seller(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n_sky-2.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO AM I DEALING WITH?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [360, 220, 1560, 800])
    d.text((W / 2, 320), "PRIVATE SELLER", font=BB(96), fill=CYAN, anchor="mm")
    d.text((W / 2, 400), "SALISBURY, MD", font=MB(30), fill=OFF, anchor="mm")
    items = ["Verify the registered owner matches the seller", "Title search + escrow", "Budget for an independent pre-buy"]
    for i, s in enumerate(items):
        if t > s0 + 2 + i * 1.5 or t > trig(BID["seller"], "budget"):
            bullet(d, 470, 500 + i * 80, s, BS(44))
    d.text((W / 2, 760), "FROM THE REPORT'S 'BEFORE YOU CALL' CHECKLIST", font=MR(20), fill=GREY, anchor="mm")

def sc_offer(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n_sky-0.jpg", blur=12, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 3", "THE OFFER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 140, 1810, 930])
    rows = [("ASKING PRICE", "$129,900", trig(BID["offer"], "Start"), OFF),
            ("ENGINE GAP VS. MARKET", "− $9,520", trig(BID["offer"], "Take"), OFF),
            ("ENGINE-ADJUSTED", "≈ $120,400", trig(BID["offer"], "lands"), CYAN),
            ("NEXTPLANE FAIR VALUE", "$121,187", trig(BID["offer"], "exactly"), OFF)]
    for i, (lab, v, ts, col) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 220 + i * 78
        d.text((180, y), lab, font=MB(28), fill=(*GREY, int(255 * p)), anchor="lm")
        d.text((900, y), v, font=MB(40), fill=(*col, int(255 * p)), anchor="rm")
    tt = trig(BID["offer"], "timing")
    if t > tt:
        stats = [("137", "days listed (since May 16)", trig(BID["offer"], "timing")), ("18%", "of spring 172s still listed >90 days", trig(BID["offer"], "eighteen", 1)),
                 ("61%", "model odds of another cut in 90 days", trig(BID["offer"], "sixty-one"))]
        for i, (v, lab, ts) in enumerate(stats):
            p = ease((t - ts) / 0.5)
            if p <= 0: continue
            y = 220 + i * 110
            d.text((1060, y + 10), v, font=MB(64), fill=(*CYAN, int(255 * p)), anchor="lm")
            d.text((1260, y + 10), lab, font=MR(24), fill=(*OFF, int(255 * p)), anchor="lm")
        d.line([1000, 190, 1000, 560], fill=(60, 80, 96), width=2)
    to = trig(BID["offer"], "reasonable")
    if t > to:
        p = ease((t - to) / 0.5)
        d.rounded_rectangle([180, 600, 1740, 700], radius=18, fill=(*CYAN, int(255 * p)))
        d.text((W / 2, 650), "OPEN AROUND $120,000 · BACKED BY THE ENGINE MATH", font=BB(58), fill=NAVY, anchor="mm")
    if t > trig(BID["offer"], "annual"):
        bullet(d, 200, 760, "Ask for the current annual (listing: \"current thru 12/2025\")", BS(40))
    if t > trig(BID["offer"], "condition"):
        bullet(d, 200, 830, "Seat-rail + doorpost ADs as a pre-buy condition", BS(40))

def sc_verdict(im, t, s0, s1):
    bg = photo_bg("c172n-0.jpg", dark=0.45, focus=(0.5, 0.5))
    im.paste(kb(bg, (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "VERDICT", "WHO IS THIS AIRPLANE RIGHT FOR?")
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(BID["verdict"], "buyer"):
        panel(d, [110, 250, 940, 700], a=215)
        d.text((150, 300), "RIGHT FOR", font=MB(28), fill=CYAN, anchor="lm")
        for i, s in enumerate(["~100 hrs/yr flyer", "Plans the overhaul on their schedule", "Wants two G5s + ADS-B out, done"]):
            bullet(d, 150, 380 + i * 85, s, BS(42))
    if t > trig(BID["verdict"], "not"):
        panel(d, [980, 250, 1810, 700], a=215)
        d.text((1020, 300), "NOT FOR", font=MB(28), fill=CYAN, anchor="lm")
        bullet(d, 1020, 380, "Five years with no engine bill", BS(42), mark="no")
        bullet(d, 1020, 465, "Pay up for a fresher engine", BS(42), fill=GREY, mark="arrow")
    if t > trig(BID["verdict"], "Priced"):
        d.text((W / 2, 820), "PRICED AT MARKET · HONEST HISTORY · THE ENGINE IS THE NEGOTIATION", font=BB(54), fill=CYAN, anchor="mm")


def title_card(im, t, s0, p_img=0.0):
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 0, W, H], fill=(8, 16, 26, 150))
    p = ease((t - s0 - 0.2) / 0.8)
    d.text((W / 2, 400), "HOW TO BUY A", font=BB(90), fill=(*OFF, int(255 * p)), anchor="mm")
    d.text((W / 2, 510), "CESSNA 172", font=BB(170), fill=(*CYAN, int(255 * p)), anchor="mm")
    d.text((W / 2, 630), "ONE REAL AIRCRAFT · ONE REAL REPORT", font=MB(30), fill=(*OFF, int(220 * p)), anchor="mm")

def sc_title(im, t, s0, s1):
    im.paste(kb(photo_bg("c172n_sky-0.jpg", dark=0.35), (t - s0) / (s1 - s0), 1.0, 1.06))
    title_card(im, t, s0)

def sc_problem(im, t, s0, s1):
    bid = BID["problem"]
    im.paste(kb(photo_bg("c172n-0.jpg", dark=0.45), (t - s0) / (s1 - s0), 1.02, 1.1, dx=-1))
    header_bar(im, "STEP 1", "CHOOSE WHICH ONE")
    d = ImageDraw.Draw(im, "RGBA")
    tb = trig(bid, "tracking")
    if t > tb:
        p = (t - tb) / 1.2
        panel(d, [560, 300, 1360, 700])
        d.text((W / 2, 450), str(int(205 * ease(p))), font=MB(170), fill=WHITE, anchor="mm")
        d.text((W / 2, 590), "CESSNA 172s FOR SALE IN THE US · THIS WEEK", font=MB(28), fill=CYAN, anchor="mm")
    if t > trig(bid, "alike"):
        d.text((W / 2, 820), "ON THE LISTING SITE, MOST OF THEM LOOK ALIKE", font=BB(62), fill=OFF, anchor="mm")

SHORT = [("N3306E", 1978, 119000, 1783, 321), ("N733EN", 1977, 119900, 8386, 1864), ("N833CB", 1976, 120000, 3719, 1806),
         ("N73864", 1976, 125000, 2882, 1544), ("N738PV", 1977, 129000, 10946, 1223), ("N733JE", 1977, 129900, 5500, 1500),
         ("N1591E", 1978, 129900, 7617, 2420), ("N739NT", 1978, 134900, 7512, 1502), ("N173SK", 1979, 135000, 14573, 1984),
         ("N6212G", 1980, 137500, 9831, 1373)]
def sc_shortlist(im, t, s0, s1):
    bid = BID["shortlist"]
    im.paste(kb(photo_bg("c172n_sky-1.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "YOUR SHORTLIST")
    d = ImageDraw.Draw(im, "RGBA")
    rows = [("205", "Cessna 172s for sale", s0 + 0.2), ("44", "172M & 172N with a price", s0 + 0.9),
            ("21", "172N (1977–80) with a price", trig(bid, "Just")), ("12", "asking $115K–$140K", trig(bid, "Between")),
            ("10", "not already sold or pending", trig(bid, "leaves"))]
    panel(d, [90, 150, 700, 900])
    d.text((130, 195), "THE FUNNEL", font=MB(24), fill=GREY, anchor="lm")
    for i, (n, lab, ts) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 270 + i * 125; w = [520, 430, 340, 260, 210][i]
        last = i == 4
        d.rounded_rectangle([130, y, 130 + w * p, y + 70], radius=10, fill=(*(CYAN if last else (60, 90, 112)), 255))
        d.text((150, y + 35), n, font=MB(40), fill=NAVY if last else WHITE, anchor="lm")
        d.text((130, y + 95), lab, font=MR(22), fill=OFF, anchor="lm")
    tl = trig(bid, "listing")
    if t > tl:
        p = ease((t - tl) / 0.6)
        panel(d, [740, 150, 1830, 900])
        d.text((780, 195), "ON THE LISTING SITE: 10 × 172N, $119K–$138K", font=MB(24), fill=GREY, anchor="lm")
        cols = [(780, "TAIL"), (960, "YEAR"), (1090, "ASK"), (1300, "AIRFRAME"), (1500, "ENGINE SMOH")]
        for x, h in cols: d.text((x, 245), h, font=MB(20), fill=GREY, anchor="lm")
        hi = t > trig(bid, "middle")
        for i, (tail, yr, ask, tt, sm) in enumerate(SHORT):
            pr = ease((t - tl - 0.1 * i) / 0.4)
            if pr <= 0: continue
            y = 290 + i * 58; hero = tail == "N733JE"
            if hero and hi: d.rounded_rectangle([765, y - 24, 1810, y + 26], radius=8, fill=(*CYAN, 60), outline=CYAN, width=3)
            col = (CYAN if hero and hi else WHITE)
            a = int(255 * pr)
            for x, v in zip([780, 960, 1090, 1300, 1500], [tail, str(yr), money(ask), "{:,} h".format(tt), "{:,} h".format(sm)]):
                d.text((x, y), v, font=MB(28), fill=(*col, a), anchor="lm")

def sc_pick(im, t, s0, s1):
    bid = BID["pick"]
    bg = photo_bg("c172n_sky-0.jpg", dark=0.35)
    im.paste(kb(bg, (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA")
    t_on = trig(bid, "paper"); t_yet = trig(bid, "Yet")
    if t < t_on - 0.3:
        p = (t - s0 - 0.3) / 1.2
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 70))
        d.text((W / 2, 420), count(129900, p), font=MB(150), fill=WHITE, anchor="mm")
        d.text((W / 2, 530), "N733JE · 1977 CESSNA 172N · SALISBURY, MD", font=MB(28), fill=CYAN, anchor="mm")
        tl = trig(bid, "Line")
        if t > tl:
            pa = ease((t - tl) / 0.6)
            x0, x1, yy = 360, 1560, 700
            d.line([x0, yy, x1, yy], fill=(246, 249, 250, int(160 * pa)), width=3)
            for i, v in enumerate(COMPS):
                xx = x0 + (v - 95000) / (175000 - 95000) * (x1 - x0)
                hero = i == HERO_IDX; r = 16 if hero else 10
                d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(*(CYAN if hero else OFF), int(255 * pa)))
            if t > trig(bid, "Tenth"):
                d.text((W / 2, 780), "10th OF 19 ACTIVE 172Ns · THE MEDIAN", font=MB(34), fill=CYAN, anchor="mm")
    elif t < t_yet - 0.2:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 120))
        d.text((W / 2, 470), "THE MOST TYPICAL 172N", font=BB(120), fill=WHITE, anchor="mm")
        d.text((W / 2, 580), "ask $129,900  =  172N median $129,900", font=MB(34), fill=CYAN, anchor="mm")
    else:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 130))
        p = (t - t_yet - 0.5) / 0.8
        d.text((W / 2, 420), "+{}%".format(int(25 * ease(p))), font=MB(170), fill=CYAN, anchor="mm")
        d.text((W / 2, 550), "COST PER NAUTICAL MILE VS. THE AVERAGE 172", font=MB(32), fill=WHITE, anchor="mm")
        if t > trig(bid, "follow"):
            d.text((W / 2, 690), "SO WHY? LET'S FOLLOW THE DATA.", font=BB(70), fill=OFF, anchor="mm")

def sc_watch(im, t, s0, s1):
    bid = BID["watch"]
    im.paste(kb(photo_bg("c172n_sky-2.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 4", "KEEP WATCHING")
    d = ImageDraw.Draw(im, "RGBA")
    items = [(27, "NEW 172 LISTINGS", "last 14 days", trig(bid, "twenty-seven")), (8, "OF THEM M OR N", "the sweet-spot models", trig(bid, "eight")),
             (22, "PRICE CUTS", "last 14 days", trig(bid, "twenty-two"))]
    bw, gap = 520, 40; x = (W - (3 * bw + 2 * gap)) / 2; y = 300
    for v, lab, sub, ts in items:
        p = (t - ts) / 0.8
        if p > 0:
            panel(d, [x, y, x + bw, y + 330])
            d.text((x + bw / 2, y + 130), str(int(round(v * ease(p)))), font=MB(120), fill=WHITE, anchor="mm")
            d.text((x + bw / 2, y + 235), lab, font=MB(28), fill=CYAN, anchor="mm")
            d.text((x + bw / 2, y + 280), sub, font=MR(22), fill=GREY, anchor="mm")
        x += bw + gap
    if t > trig(bid, "pass"):
        d.text((W / 2, 780), "KEEP THE OTHER NINE ON YOUR LIST", font=BB(64), fill=CYAN, anchor="mm")

_ecbase = {}
def sc_end(im, t, s0, s1):
    p = Image.new("RGB", (1080, 1920), NAVY)
    EC.draw_endcard(p, t - s0, FD, f"{ROOT}/assets/logo.png")
    p = p.crop((0, 380, 1080, 1480)).resize((1060, 1080), Image.LANCZOS)
    im.paste(NAVY, (0, 0, W, H)); im.paste(p, ((W - 1060) // 2, 0))

SCENE_FN = {"title": sc_title, "problem": sc_problem, "ladder": sc_ladder, "shortlist": sc_shortlist, "pick": sc_pick,
            "header": sc_header, "value": sc_value, "comps": sc_comps, "hours": sc_hours, "pricehist": sc_pricehist,
            "owner": sc_owner, "flight": sc_flight, "ads": sc_ads, "sdr": sc_sdr, "cpm": sc_cpm, "seller": sc_seller,
            "offer": sc_offer, "watch": sc_watch, "verdict": sc_verdict, "end": sc_end}
SC = [list(s) for s in SCENES]
for i in range(1, len(SC)): SC[i][2] = SC[i - 1][3]
SC[-1][3] = TOTAL + 1

def frame(t):
    im = Image.new("RGB", (W, H), NAVY)
    for bid, scene, s0, s1 in SC:
        if s0 <= t < s1:
            SCENE_FN[scene](im, t, s0, s1)
            # scene crossfade-in from black over 0.25s
            if t - s0 < 0.25 and bid != BID["title"]:
                a = 1 - (t - s0) / 0.25
                im = Image.blend(im, Image.new("RGB", (W, H), NAVY), a * 0.6)
            break
    caption(im, t)
    return im

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f"{ROOT}/stills3/still_{float(ts):07.2f}.png")
    elif sys.argv[1] == "seg":
        i, n = int(sys.argv[2]), int(sys.argv[3])
        NF = int(math.ceil(TOTAL * FPS)); a, b = NF * i // n, NF * (i + 1) // n
        out = f"{ROOT}/segs/seg_{i:02d}.mp4"
        pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out + ".part.mp4"], stdin=subprocess.PIPE)
        for f in range(a, b):
            pr.stdin.write(frame(f / FPS).tobytes())
        pr.stdin.close(); pr.wait(); os.replace(out + ".part.mp4", out); print("seg", i, "frames", a, b, "done")
