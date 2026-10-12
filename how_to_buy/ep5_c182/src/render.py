#!/usr/bin/env python3
"""How to Buy a Cessna 182 Skylane (Ep5, N23383) — 1920x1080@30 renderer.
Usage: render.py seg <i> <n>   -> renders segment i of n to seg_i.mp4 (raw frames piped to ffmpeg)
       render.py still <t>      -> writes still_<t>.png"""
import json, math, os, subprocess, sys, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, "/tmp/htb_c182"); sys.path.insert(0, os.path.expanduser("~/kit/lib"))
from timeline import SCENES, OFFS, TOTAL
from beats import BEATS
BID = {sc: b for b, sc, _ in BEATS}
import endcard as EC

ROOT = "/tmp/htb_c182"; FD = f"{ROOT}/fonts"; CAP = f"{ROOT}/cap"; PH = f"{ROOT}/photos"
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
    tw = d.textlength("N23383 · 1998 CESSNA 182S", font=MB(22))
    d.rounded_rectangle([W - 110 - tw, 52, W - 70, 96], radius=10, outline=(*CYAN, 200), width=2, fill=(8, 16, 26, 170))
    d.text((W - 90 - tw, 74), "N23383 · 1998 CESSNA 182S", font=MB(22), fill=OFF, anchor="lm")
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
    for bx in blurs:
        x0, y0, x1, y1 = [int(v * 2) for v in bx]
        reg = im.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(14))
        im.paste(reg, (x0, y0))
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


def rep_label(im, txt="REPRESENTATIVE PHOTO · CESSNA 182S SKYLANE · NOT THE AIRCRAFT FOR SALE"):
    d = ImageDraw.Draw(im, "RGBA"); d.text((70, 925), txt, font=MR(18), fill=(200, 210, 218, 190), anchor="lm")
def big_line(d, y, txt, f=None, fill=OFF, p=1.0):
    f = f or BB(62); d.text((W / 2, y), txt, font=f, fill=(*fill, int(255 * min(max(p, 0), 1))), anchor="mm")
def chip_c(d, y, txt, f=None, fill=CYAN, fg=NAVY):
    f = f or MB(26); tw = d.textlength(txt, font=f); chip(d, W / 2 - tw / 2 - 18, y, txt, fill=fill, fg=fg, f=f)

# ---------- data (from DATA_PACK) ----------
LADDER = [("1956–1971", "classic", 145000, 19, "fifties"), ("1972–1976", "182P", 179900, 29, "mid-seventies"),
          ("1977–1986", "182Q / 182R", 227450, 30, "late"), ("1997–2000", "182S · restart", 319950, 16, "restart"),
          ("2001–2015", "182T", 359900, 17, "thousands"), ("2016–2027", "182T", 649250, 12, "newest")]
S_ASKS = [224500, 240000, 279000, 289900, 300000, 309000, 309900, 314900, 325000, 339500, 339900, 349000, 350000, 369000, 399000, 494900]
PH_HIST = [("Sep 5", 329000), ("Sep 13", 319000), ("Sep 17", 309000), ("Sep 19", 299000), ("Oct 3", 289000), ("Oct 6", 279000)]
BG = "c182s-7.jpg"

def sc_title(im, t, s0, s1):
    im.paste(kb(photo_bg("c182s-1.jpg", dark=0.35, focus=(0.5, 0.45)), (t - s0) / (s1 - s0), 1.0, 1.06))
    d = ImageDraw.Draw(im, "RGBA"); d.rectangle([0, 0, W, H], fill=(8, 16, 26, 140))
    p = ease((t - s0 - 0.2) / 0.8)
    d.text((W / 2, 390), "HOW TO BUY A", font=BB(90), fill=(*OFF, int(255 * p)), anchor="mm")
    d.text((W / 2, 510), "CESSNA 182 SKYLANE", font=BB(160), fill=(*CYAN, int(255 * p)), anchor="mm")
    d.text((W / 2, 640), "ONE REAL AIRCRAFT · ONE REAL REPORT", font=MB(30), fill=(*OFF, int(220 * p)), anchor="mm")
    rep_label(im)

def sc_problem(im, t, s0, s1):
    bid = BID["problem"]
    im.paste(kb(photo_bg("c182s-3.jpg", dark=0.5), (t - s0) / (s1 - s0), 1.02, 1.1, dx=-1))
    header_bar(im, "STEP 1", "CHOOSE WHICH ONE"); rep_label(im)
    d = ImageDraw.Draw(im, "RGBA")
    tb = trig(bid, "tracking")
    if t < tb - 0.2:
        if t > trig(bid, "bigger"): big_line(d, 430, "THE BIGGER, STRONGER SIBLING OF THE 172", BB(80), OFF, (t - trig(bid, "bigger")) / 0.4)
        if t > trig(bid, "seats"): big_line(d, 540, "4 SEATS · BUILT ON AND OFF SINCE 1956", MB(36), CYAN, (t - trig(bid, "seats")) / 0.4)
    else:
        p = (t - tb) / 1.0
        panel(d, [300, 300, 920, 700]); d.text((610, 450), str(int(150 * ease(p))), font=MB(170), fill=WHITE, anchor="mm")
        d.text((610, 590), "SKYLANES FOR SALE · US", font=MB(26), fill=CYAN, anchor="mm")
        t2 = trig(bid, "twenty-three")
        if t > t2:
            p2 = (t - t2) / 0.8
            panel(d, [1000, 300, 1620, 700]); d.text((1310, 450), str(int(123 * ease(p2))), font=MB(170), fill=CYAN, anchor="mm")
            d.text((1310, 590), "SHOW A PUBLISHED PRICE", font=MB(26), fill=OFF, anchor="mm")
        chip_c(d, 760, "NEXTPLANE LISTING PANEL · WEEK OF OCT 12, 2026 · 182 TO 182T, NON-TURBO", fill=(15, 42, 63), fg=OFF, f=MB(22))

def sc_ladder(im, t, s0, s1):
    bid = BID["ladder"]
    im.paste(kb(photo_bg("c182s-0.jpg", blur=10, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "THE PRICE LADDER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 140, 1810, 940])
    d.text((160, 185), "TYPICAL (MEDIAN) ASKING PRICE · ACTIVE US LISTINGS WITH A PRICE · OCT 12, 2026", font=MB(24), fill=GREY, anchor="lm")
    x0, xmax = 700, 1560; vmax = 700000
    for i, (yrs, lab, v, n, key) in enumerate(LADDER):
        ts = trig(bid, key, default=s0 + 2 + i * 5); p = ease((t - ts) / 0.8)
        y = 245 + i * 108 + (40 if i >= 3 else 0); hero = lab.startswith("182S")
        d.text((160, y + 22), yrs, font=BB(50), fill=CYAN if hero else OFF, anchor="lm")
        d.text((420, y + 24), lab, font=MR(24), fill=CYAN if hero else GREY, anchor="lm")
        if p > 0:
            bw = (xmax - x0) * v / vmax * p
            d.rounded_rectangle([x0, y, x0 + max(bw, 8), y + 44], radius=8, fill=(*(CYAN if hero else (120, 150, 170)), 255))
            d.text((x0 + bw + 18, y + 22), money(round(v * ease(p))) + "  (n={})".format(n), font=MB(28), fill=WHITE, anchor="lm")
    tg = trig(bid, "stopped")
    if t > tg:
        p = ease((t - tg) / 0.5)
        d.text((W / 2, 245 + 3 * 108 + 6), "1987–1996 · CESSNA BUILT NO NEW PISTON SINGLES", font=MB(26), fill=(230, 120, 110, int(255 * p)), anchor="mm")

def sc_shortlist(im, t, s0, s1):
    bid = BID["shortlist"]
    im.paste(kb(photo_bg("c182s-6.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "YOUR SHORTLIST")
    d = ImageDraw.Draw(im, "RGBA")
    rows = [("150", "Skylanes for sale", s0 + 0.2), ("123", "with a published price", s0 + 0.9),
            ("17", "182S · 1997–2000", trig(bid, "Seventeen")), ("16", "182S with a price", trig(bid, "sixteen"))]
    panel(d, [90, 150, 640, 900]); d.text((130, 195), "THE FUNNEL", font=MB(24), fill=GREY, anchor="lm")
    for i, (n, lab, ts) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 270 + i * 150; w = [460, 400, 220, 200][i]; last = i == 3
        d.rounded_rectangle([130, y, 130 + w * p, y + 70], radius=10, fill=(*(CYAN if last else (60, 90, 112)), 255))
        d.text((150, y + 35), n, font=MB(40), fill=NAVY if last else WHITE, anchor="lm")
        d.text((130, y + 97), lab, font=MR(22), fill=OFF, anchor="lm")
    tr = trig(bid, "run")
    if t > tr - 0.2:
        panel(d, [680, 150, 1830, 900])
        d.text((720, 195), "THE 16 ASKING PRICES · 182S · ACTIVE US LISTINGS", font=MB(24), fill=GREY, anchor="lm")
        X = lambda v: 760 + (v - 200000) / 320000 * 1000
        d.line([760, 520, 1760, 520], fill=(90, 110, 128), width=3)
        for v in (200000, 300000, 400000, 500000):
            d.line([X(v), 505, X(v), 535], fill=(90, 110, 128), width=3); d.text((X(v), 570), "${}K".format(v // 1000), font=MR(24), fill=GREY, anchor="mm")
        hi = t > trig(bid, "cheapest")
        for i, v in enumerate(S_ASKS):
            p = ease((t - tr - i * 0.08) / 0.4)
            if p <= 0: continue
            hero = v == 279000 and hi
            yy = 520 - (i % 3) * 0
            r = 16 if hero else 12
            d.ellipse([X(v) - r, yy - r - (1 - p) * 40, X(v) + r, yy + r - (1 - p) * 40], fill=(*(CYAN if hero else OFF), int(255 * p)))
        if t > trig(bid, "double"):
            d.text((1260, 680), "$224,500 – $494,900", font=MB(52), fill=WHITE, anchor="mm")
            d.text((1260, 750), "SAME MODEL · MORE THAN DOUBLE THE MONEY", font=MB(26), fill=CYAN, anchor="mm")
        if hi:
            d.text((X(279000), 440), "THIS ONE · $279,000", font=MB(26), fill=CYAN, anchor="mm")

def sc_pick(im, t, s0, s1):
    bid = BID["pick"]
    im.paste(kb(photo_bg("c182s-8.jpg", dark=0.4), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); rep_label(im)
    t_here = trig(bid, "Here")
    if t < t_here - 0.3:
        p = (t - s0 - 0.3) / 1.2
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 90))
        d.text((W / 2, 420), count(279000, p), font=MB(150), fill=WHITE, anchor="mm")
        d.text((W / 2, 540), "N23383 · 1998 CESSNA 182S · PRIVATE SELLER, NORTH CAROLINA", font=MB(30), fill=CYAN, anchor="mm")
        tf = trig(bid, "forty")
        if t > tf: big_line(d, 650, "$40,000 UNDER NEXTPLANE'S ESTIMATE ($319,000)", MB(36), OFF, (t - tf) / 0.4)
        if t > trig(bid, "bargain?"): big_line(d, 750, "A BARGAIN?", BB(90), CYAN, (t - trig(bid, "bargain?")) / 0.4)
    else:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 150))
        tr = trig(bid, "sixty-seven")
        if t > tr - 0.5:
            p = ease((t - tr + 0.5) / 0.6)
            panel(d, [260, 300, 900, 700]); d.text((580, 380), "THIS AIRPLANE", font=MB(26), fill=CYAN, anchor="mm")
            d.text((580, 500), "$2.67", font=MB(150), fill=(*CYAN, int(255 * p)), anchor="mm"); d.text((580, 620), "PER NAUTICAL MILE", font=MB(24), fill=GREY, anchor="mm")
        ta = trig(bid, "average")
        if t > ta:
            p = ease((t - ta) / 0.6)
            panel(d, [1020, 300, 1660, 700]); d.text((1340, 380), "AVERAGE 182S FOR SALE", font=MB(26), fill=GREY, anchor="mm")
            d.text((1340, 500), "$1.51", font=MB(150), fill=(*WHITE, int(255 * p)), anchor="mm"); d.text((1340, 620), "PER NAUTICAL MILE", font=MB(24), fill=GREY, anchor="mm")
        chip_c(d, 780, "NEXTPLANE AIRCRAFT REPORT · TRUE COST PER MILE", fill=(15, 42, 63), fg=OFF, f=MB(24))

def sc_header(im, t, s0, s1):
    bid = BID["header"]
    im.paste(kb(photo_bg(BG, blur=14, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT DOES THE REPORT SAY FIRST?")
    cos = [((300, 200, 565, 238), trig(bid, "accident")), ((12, 408, 278, 470), trig(bid, "loan")),
           ((588, 283, 852, 335), trig(bid, "company")), ((278, 580, 398, 606), trig(bid, "warning:"))]
    blurs = [(876, 314, 1140, 350), (876, 200, 1140, 238)]
    report_slide(im, t, "_headercomb", (0, 0, 1152, 615), cos, blurs=blurs, t0=s0, cy=535, maxh=800)

def tiles(im, t, items, y=560, bw=520, h=300):
    d = ImageDraw.Draw(im, "RGBA"); n = len(items); gap = 40; x = (W - (n * bw + (n - 1) * gap)) / 2
    for lab, vtxt, sub, ts, hi in items:
        p = ease((t - ts) / 0.6)
        if p > 0:
            panel(d, [x, y, x + bw, y + h])
            d.text((x + bw / 2, y + 60), lab, font=MB(24), fill=CYAN if hi else GREY, anchor="mm")
            d.text((x + bw / 2, y + 150), vtxt, font=MB(72), fill=(*(CYAN if hi else WHITE), int(255 * p)), anchor="mm")
            d.text((x + bw / 2, y + 235), sub, font=MR(22), fill=GREY, anchor="mm")
        x += bw + gap

def sc_value(im, t, s0, s1):
    bid = BID["value"]
    im.paste(kb(photo_bg(BG, blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "IS THE PRICE FAIR?")
    cos = [((34, 110, 282, 162), trig(bid, "nineteen")), ((46, 330, 574, 376), trig(bid, "middle"))]
    report_slide(im, t, "valuation", (25, 100, 1127, 385), cos, blurs=[(312, 110, 560, 162)], t0=s0, cy=320, maxh=330)
    tiles(im, t, [("ASKING PRICE", "$279,000", "published ask", trig(bid, "asks", 1), False),
                  ("UNDER THE ESTIMATE", "−$40,000", "ask minus NextPlane estimate", trig(bid, "less,"), True),
                  ("DISCOUNT", "−12.5%", "below the middle half", trig(bid, "twelve"), True)], y=540)
    if t > trig(bid, "why?"): chip_c(d=ImageDraw.Draw(im, "RGBA"), y=880, txt="A CAREFUL BUYER ASKS: WHY?", f=MB(30))

def sc_engine(im, t, s0, s1):
    bid = BID["engine"]
    im.paste(kb(photo_bg("c182ck-0.jpg", blur=12, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHY IS IT CHEAPER? THE ENGINE")
    cos = [((30, 98, 565, 205), trig(bid, "listing")), ((587, 98, 1122, 205), trig(bid, "average")), ((38, 165, 560, 190), trig(bid, "remain."))]
    report_slide(im, t, "cpm", (0, 0, 1152, 420), cos, t0=s0, cy=420, maxh=560)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "recommends"): chip(d, 70, 760, "OVERHAUL = A FULL ENGINE REBUILD · RECOMMENDED EVERY 2,000 HRS", f=MB(26))
    if t > trig(bid, "prices"): chip(d, 70, 830, "OVERHAUL ≈ $65,000 ÷ 2,000 HRS = $32.50 PER HOUR OF ENGINE LIFE", fill=(15, 42, 63), fg=OFF, f=MB(26))
    if t > trig(bid, "missing"): chip(d, 70, 900, "894 FEWER HOURS LEFT THAN AVERAGE × $32.50 ≈ $29,055", f=MB(26))

def sc_adjust(im, t, s0, s1):
    bid = BID["adjust"]
    im.paste(kb(photo_bg("c182s-3.jpg", blur=12, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "PRICED FOR ITS ENGINE")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 930])
    d.text((160, 200), "WHAT THIS 182S IS WORTH, ONCE THE ENGINE IS COUNTED", font=MB(24), fill=GREY, anchor="lm")
    rows = [("NEXTPLANE ESTIMATE", 319000, "$319,000", trig(bid, "estimate,"), (120, 150, 170)),
            ("MINUS THE ENGINE", 29055, "−$29,055", trig(bid, "Take", 2), (230, 120, 110)),
            ("ENGINE-ADJUSTED VALUE", 289945, "≈ $290,000", trig(bid, "leaves"), CYAN),
            ("NEXTPLANE PRICE MODEL (OCT 7)", 289524, "$289,524", trig(bid, "model,"), CYAN),
            ("5 × 182S, ENGINE 1,400+ HRS", 282000, "$282,000 typical", trig(bid, "fourteen"), (120, 150, 170)),
            ("THIS AIRPLANE'S ASK", 279000, "$279,000", trig(bid, "bargain."), OFF)]
    x0, x1 = 760, 1560
    for i, (lab, v, vt, ts, col) in enumerate(rows):
        p = ease((t - ts) / 0.6)
        if p <= 0: continue
        y = 260 + i * 100
        d.text((160, y + 22), lab, font=MB(26), fill=OFF, anchor="lm")
        if i == 1:
            xa = x0 + (x1 - x0) * 289945 / 340000; xb = x0 + (x1 - x0) * 319000 / 340000
            d.rounded_rectangle([xa + (xb - xa) * (1 - p), y, xb, y + 44], radius=8, fill=col)
            d.text((xa - 18, y + 22), vt, font=MB(28), fill=WHITE, anchor="rm")
        else:
            bw = (x1 - x0) * v / 340000 * p
            d.rounded_rectangle([x0, y, x0 + bw, y + 44], radius=8, fill=col)
            d.text((x0 + bw + 18, y + 22), vt, font=MB(28), fill=WHITE, anchor="lm")
    if t > trig(bid, "right,"): chip_c(d, 865, "NOT A BARGAIN · PRICED ABOUT RIGHT FOR AN ENGINE THAT IS NEARLY DUE", f=MB(28))

def sc_overhaul(im, t, s0, s1):
    bid = BID["overhaul"]
    im.paste(kb(photo_bg("c182s-9.jpg", blur=10, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "THE OVERHAUL MATH")
    d = ImageDraw.Draw(im, "RGBA")
    ta = trig(bid, "Buy")
    if t > ta:
        panel(d, [160, 220, 920, 760]); d.text((540, 280), "THIS 182S, THEN OVERHAUL", font=MB(28), fill=CYAN, anchor="mm")
        d.text((540, 380), "$279,000", font=MB(60), fill=WHITE, anchor="mm"); d.text((540, 460), "+ $65,000 overhaul", font=MB(40), fill=OFF, anchor="mm")
        d.line([300, 520, 780, 520], fill=(90, 110, 128), width=3)
        if t > trig(bid, "forty-four"): d.text((540, 610), "≈ $344,000", font=MB(84), fill=CYAN, anchor="mm")
    tb = trig(bid, "freshly")
    if t > tb - 0.3:
        panel(d, [1000, 220, 1760, 760]); d.text((1380, 280), "1999 182S · FRESH OVERHAUL", font=MB(28), fill=CYAN, anchor="mm")
        d.text((1380, 380), "0 HRS ON ENGINE", font=MB(40), fill=OFF, anchor="mm"); d.text((1380, 460), "for sale now", font=MR(28), fill=GREY, anchor="mm")
        d.line([1140, 520, 1620, 520], fill=(90, 110, 128), width=3)
        if t > trig(bid, "hundred.") - 0.8: d.text((1380, 610), "$339,900", font=MB(84), fill=WHITE, anchor="mm")
    if t > trig(bid, "difference"): chip_c(d, 840, "NEARLY THE SAME MONEY · THE DIFFERENCE IS WHO PICKS THE SHOP, AND WHEN", f=MB(28))

def sc_pricehist(im, t, s0, s1):
    import datetime as dtm
    bid = BID["pricehist"]
    im.paste(kb(photo_bg(BG, blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS THE SELLER MOVED?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 930])
    d.text((160, 200), "ASKING PRICE · N23383 · EVERY CHANGE RECORDED BY NEXTPLANE", font=MB(24), fill=GREY, anchor="lm")
    mon = {"Sep": 9, "Oct": 10}
    dx = lambda s: dtm.date(2026, mon[s.split()[0]], int(s.split()[1]))
    d0, d1 = dtm.date(2026, 9, 1), dtm.date(2026, 10, 14)
    X = lambda dd: 300 + (dd - d0).days / (d1 - d0).days * 1400
    Y = lambda v: 720 - (v - 270000) / (335000 - 270000) * 430
    for v in (280000, 300000, 320000):
        d.line([300, Y(v), 1710, Y(v)], fill=(60, 80, 96), width=1); d.text((285, Y(v)), money(v), font=MR(20), fill=GREY, anchor="rm")
    tl = trig(bid, "Listed"); tt = trig(bid, "times,")
    show = 0
    if t > tl: show = 1
    if t > trig(bid, "ten"): show = 1 + min(5, int((t - trig(bid, "ten")) / 0.5) + 1)
    pts = [(X(dx(lab)), Y(v), lab, v) for lab, v in PH_HIST[:show]]
    if pts:
        path = []
        for i, (x, y, lab, v) in enumerate(pts):
            if i: path.append((x, path[-1][1]))
            path.append((x, y))
        path.append((X(dtm.date(2026, 10, 12)) if len(pts) == 6 else pts[-1][0] + 30, path[-1][1]))
        d.line(path, fill=CYAN, width=5)
        for i, (x, y, lab, v) in enumerate(pts):
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=CYAN)
            d.text((x + 12, y - 28), money(v), font=MB(22), fill=WHITE, anchor="lm"); d.text((x, 765 + (i % 2) * 30), lab, font=MR(22), fill=GREY, anchor="mm")
    if t > trig(bid, "all,"): chip(d, 1150, 250, "5 CUTS · −$50,000 · −15.2%", f=MB(28))
    if t > trig(bid, "four"): d.text((W / 2, 870), "SKYLANES LISTED APR 26–JUL 7: 54 OF 143 CUT · TYPICAL TOTAL CUT 6.7% · THIS ONE 15.2%", font=MB(25), fill=OFF, anchor="mm")
    if t > trig(bid, "Ask."): chip(d, 1150, 320, "WE DON'T KNOW WHY · ASK", fill=(15, 42, 63), fg=OFF, f=MB(28))

def sc_owner(im, t, s0, s1):
    bid = BID["owner"]
    im.paste(kb(photo_bg("c182s-6.jpg", blur=14, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO OWNS IT?")
    blurs = [(22, 116, 300, 144), (56, 204, 420, 230)]
    cos = [((856, 92, 1132, 144), trig(bid, "April")), ((38, 350, 372, 400), trig(bid, "loans.") if trig(bid, "loans.") else s0 + 3)]
    report_slide(im, t, "reg", (0, 0, 1152, 410), cos, blurs=blurs, t0=s0, cy=430, maxh=560)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "person."): chip_c(d, 755, "REGISTERED OWNER: A NORTH CAROLINA COMPANY  ·  SELLER: A PRIVATE PERSON")
    ts = trig(bid, "Confirm")
    items = [("Seller can sign for the company", ts), ("Title search · claims against it", trig(bid, "title")), ("Escrow · a neutral party holds the money", trig(bid, "escrow,"))]
    x = 60
    for s, tt in items:
        if t > tt:
            f = BS(32); tw = d.textlength(s, font=f)
            d.rounded_rectangle([x, 830, x + tw + 80, 900], radius=12, fill=(10, 22, 34, 230), outline=(37, 197, 203, 120), width=2)
            bullet(d, x + 20, 865, s, f)
            x += tw + 100

def sc_flight(im, t, s0, s1):
    bid = BID["flight"]
    im.paste(kb(photo_bg("c182s-2.jpg", blur=6, dark=0.75), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "STEP 2", "IS IT FLYING?")
    cos = [((30, 120, 330, 175), trig(bid, "forty-four"))]
    report_slide(im, t, "flight", (0, 80, 1152, 200), cos, t0=s0, cy=245, maxw=1600, maxh=200)
    tw = trig(bid, "winter,")
    if t > tw - 0.5: report_slide(im, t, "fl_monthly", (0, 0, 543, 318), [], t0=tw - 0.5, cy=640, maxw=760, maxh=450, cx=560)
    d = ImageDraw.Draw(im, "RGBA")
    if t > tw - 0.5: d.text((560, 900), "TRACKED FLIGHTS PER MONTH · ADS-B", font=MR(22), fill=GREY, anchor="mm")
    if t > tw:
        panel(d, [1010, 420, 1810, 560]); d.text((1040, 455), "NOV 2024 – MAR 2025", font=MB(24), fill=GREY, anchor="lm"); d.text((1040, 515), "32 HRS TRACKED", font=MB(48), fill=WHITE, anchor="lm")
    if t > trig(bid, "eleven"):
        panel(d, [1010, 580, 1810, 720]); d.text((1040, 615), "APR 2025 – SEP 2026", font=MB(24), fill=GREY, anchor="lm"); d.text((1040, 675), "11 HRS TRACKED", font=MB(48), fill=CYAN, anchor="lm")
    if t > trig(bid, "measured."): d.text((1410, 760), "\"SITTING AGES AN ENGINE\" = A COMMON SHOP VIEW, NOT A NEXTPLANE MEASUREMENT", font=MR(16), fill=GREY, anchor="mm")
    if t > trig(bid, "oil"):
        bullet(d, 1030, 815, "Oil analysis", BS(42));
    if t > trig(bid, "camera"): bullet(d, 1030, 880, "Camera look inside the cylinders", BS(42))

def sc_ads(im, t, s0, s1):
    bid = BID["ads"]
    im.paste(kb(photo_bg("c182ck-2.jpg", blur=14, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT SHOULD THE LOGBOOKS SHOW?")
    blurs = [(250, 250, 434, 345)]
    cos = [((30, 250, 224, 326), trig(bid, "eleven"))]
    report_slide(im, t, "ads", (0, 100, 664, 350), cos, blurs=blurs, t0=s0, cy=330, maxh=400, maxw=1100)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "Seven"): chip_c(d, 560, "11 MATCHED · 7 APPLY ONLY IF CERTAIN PARTS ARE INSTALLED")
    tf = trig(bid, "Four")
    if t > tf:
        panel(d, [360, 630, 1560, 900]); d.text((400, 665), "APPLY TO EVERY 182S · CONFIRM EACH IS SIGNED OFF", font=MB(22), fill=CYAN, anchor="lm")
        for i, s in enumerate(["Oil pressure switch · AD 2000-04-01 and AD 2013-11-11", "Crew seat locks · AD 2007-05-10", "Exhaust mufflers · AD 98-01-14"]):
            if t > tf + 0.6 + i * 0.8: bullet(d, 410, 725 + i * 58, s, BS(38))
    if t > trig(bid, "annual"): d.text((W / 2, 935), "LISTING: \"FRESH ANNUAL INSPECTION 09/01/26\" · CHECK THE LOGBOOK ENTRY", font=MB(24), fill=OFF, anchor="mm")

def sc_sdr(im, t, s0, s1):
    bid = BID["sdr"]
    im.paste(kb(photo_bg(BG, blur=14, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS IT EVER BEEN HURT?")
    cos = [((20, 596, 1132, 688), trig(bid, "entry,"))]
    report_slide(im, t, "sdr", (0, 0, 1152, 700), cos, t0=s0, cy=480, maxh=700)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "accident"): chip(d, 70, 880, "NTSB ACCIDENT RECORDS FOR THIS AIRCRAFT: NONE", f=MB(26))
    if t > trig(bid, "minor,"): chip(d, 1180, 880, "2000 · AUTOPILOT PART · ONE QUESTION", fill=(15, 42, 63), fg=OFF, f=MB(26))

def sc_opcost(im, t, s0, s1):
    bid = BID["opcost"]
    im.paste(kb(photo_bg("c182s-7.jpg", blur=12, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT WILL IT COST TO KEEP?")
    cos = [((15, 468, 1137, 502), trig(bid, "twenty-seven")), ((15, 502, 1137, 540), trig(bid, "thirty-one")), ((15, 132, 1137, 166), trig(bid, "Fuel"))]
    report_slide(im, t, "opcost", (0, 0, 1152, 580), cos, t0=s0, cy=490, maxh=700)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "add"): chip(d, 70, 890, "ON THIS AIRPLANE, ADD: OVERHAUL ≈ $65,000 · ~300 HRS LEFT ≈ 2.5 YEARS AT 120 HRS/YR", f=MB(26))

def sc_seller(im, t, s0, s1):
    bid = BID["seller"]
    im.paste(kb(photo_bg("c182s-8.jpg", blur=12, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO AM I DEALING WITH?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [360, 200, 1560, 840])
    d.text((W / 2, 300), "PRIVATE SELLER", font=BB(100), fill=CYAN, anchor="mm")
    d.text((W / 2, 385), "ERWIN, NC · LISTED SEP 5, 2026 · ORIGINALLY $329,000", font=MB(28), fill=OFF, anchor="mm")
    items = [("Often more flexible on price", trig(bid, "flexible")), ("No dealer warranty to lean on", trig(bid, "warranty")),
             ("Independent pre-buy at a shop you choose", trig(bid, "budget"))]
    for i, (s, ts) in enumerate(items):
        if t > ts: bullet(d, 470, 500 + i * 85, s, BS(46), mark="ok" if i != 1 else "no")

def sc_offer(im, t, s0, s1):
    bid = BID["offer"]
    im.paste(kb(photo_bg("c182s-1.jpg", blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 3", "THE OFFER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 140, 1810, 940])
    rows = [("ENGINE-ADJUSTED VALUE", "≈ $290,000", trig(bid, "Start"), OFF),
            ("CLOSEST MATCH · 1999 · ENGINE 1,822 HRS", "$240,000", trig(bid, "forty"), OFF),
            ("…LISTED FOR", "100+ DAYS", trig(bid, "days."), OFF),
            ("THIS SELLER'S STEPS", "5 × −$10,000", trig(bid, "cutting"), OFF),
            ("MODEL ODDS OF ANOTHER CUT, 90 DAYS", "≈ 3 IN 4 (75%)", trig(bid, "three", 2), OFF)]
    for i, (lab, v, ts, col) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 210 + i * 72
        d.text((170, y), lab, font=MB(26), fill=(*GREY, int(255 * p)), anchor="lm"); d.text((1740, y), v, font=MB(36), fill=(*col, int(255 * p)), anchor="rm")
    to = trig(bid, "reasonable")
    if t > to:
        p = ease((t - to) / 0.5)
        d.rounded_rectangle([180, 580, 1740, 680], radius=18, fill=(*CYAN, int(255 * p)))
        d.text((W / 2, 630), "OPEN AROUND $265,000 · ABOUT 5% UNDER THE ASK", font=BB(58), fill=NAVY, anchor="mm")
    ts = trig(bid, "subject")
    for i, s in enumerate(["Subject to a pre-buy inspection", "An oil analysis", "A camera look inside the cylinders"]):
        if t > ts + i * 1.0: bullet(d, 200, 740 + i * 58, s, BS(40))
    tw = trig(bid, "fails")
    if t > tw:
        panel(d, [1000, 710, 1760, 900], a=200)
        d.text((1380, 760), "IF THE ENGINE FAILS THOSE CHECKS", font=MB(24), fill=(230, 120, 110), anchor="mm")
        d.text((1380, 815), "ASK FOR ≈ $65,000 OFF", font=BB(52), fill=WHITE, anchor="mm")
        if t > trig(bid, "walk"): d.text((1380, 865), "OR WALK AWAY", font=BB(44), fill=CYAN, anchor="mm")

def sc_watch(im, t, s0, s1):
    bid = BID["watch"]
    im.paste(kb(photo_bg("c182s-4.jpg", blur=8, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 4", "KEEP WATCHING")
    d = ImageDraw.Draw(im, "RGBA")
    items = [(14, "NEW SKYLANE LISTINGS", "last 14 days", trig(bid, "fourteen")), (22, "PRICE CUTS", "last 14 days", trig(bid, "twenty-two")),
             (2, "PRICE INCREASES", "last 14 days", trig(bid, "increases."))]
    bw, gap = 520, 40; x = (W - (3 * bw + 2 * gap)) / 2; y = 300
    for v, lab, sub, ts in items:
        p = (t - ts) / 0.8
        if p > 0:
            panel(d, [x, y, x + bw, y + 330])
            d.text((x + bw / 2, y + 130), str(int(round(v * ease(p)))), font=MB(120), fill=WHITE, anchor="mm")
            d.text((x + bw / 2, y + 235), lab, font=MB(26), fill=CYAN, anchor="mm"); d.text((x + bw / 2, y + 280), sub, font=MR(22), fill=GREY, anchor="mm")
        x += bw + gap
    if t > trig(bid, "Right"): chip_c(d, 720, "RIGHT NOW, SELLERS ARE THE ONES ADJUSTING", f=MB(30))

def sc_verdict(im, t, s0, s1):
    bid = BID["verdict"]
    im.paste(kb(photo_bg("c182s-7.jpg", dark=0.5), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "VERDICT", "WHO IS THIS AIRPLANE RIGHT FOR?"); rep_label(im)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "buyer"):
        panel(d, [110, 200, 940, 690], a=215); d.text((150, 255), "RIGHT FOR", font=MB(28), fill=CYAN, anchor="lm")
        for i, (s, k) in enumerate([("Plans to overhaul soon", "buyer"), ("Wants to choose the shop", "choose"), ("Airframe: 1,699 hrs", "low-time"), ("Average for sale: 3,584 hrs", "average")]):
            if t > trig(bid, k): bullet(d, 150, 335 + i * 80, s, BS(42), fill=WHITE if i < 3 else GREY, mark="ok" if i < 3 else "arrow")
    if t > trig(bid, "not"):
        panel(d, [980, 200, 1810, 690], a=215); d.text((1020, 255), "NOT RIGHT IF", font=MB(28), fill=(230, 120, 110), anchor="lm")
        bullet(d, 1020, 335, "You want 300 hrs of flying", BS(42), mark="no"); bullet(d, 1020, 415, "before spending on the engine", BS(42), fill=GREY, mark="arrow")
    if t > trig(bid, "Priced"): big_line(d, 760, "PRICED ABOUT RIGHT FOR ITS ENGINE · CLEAN HISTORY", BB(54), OFF, (t - trig(bid, "Priced")) / 0.4)
    tq = trig(bid, "Check")
    if t > tq: big_line(d, 845, "ENGINE CONDITION  ·  WHO SIGNS FOR THE COMPANY  ·  THE SEPTEMBER ANNUAL", BB(50), CYAN, (t - tq) / 0.4)

def sc_end(im, t, s0, s1):
    p = Image.new("RGB", (1080, 1920), NAVY)
    EC.draw_endcard(p, t - s0, FD, f"{ROOT}/assets/logo.png")
    p = p.crop((0, 380, 1080, 1480)).resize((1060, 1080), Image.LANCZOS)
    im.paste(NAVY, (0, 0, W, H)); im.paste(p, ((W - 1060) // 2, 0))

SCENE_FN = {"title": sc_title, "problem": sc_problem, "ladder": sc_ladder, "shortlist": sc_shortlist, "pick": sc_pick, "header": sc_header,
            "value": sc_value, "engine": sc_engine, "adjust": sc_adjust, "overhaul": sc_overhaul, "pricehist": sc_pricehist, "owner": sc_owner,
            "flight": sc_flight, "ads": sc_ads, "sdr": sc_sdr, "opcost": sc_opcost, "seller": sc_seller, "offer": sc_offer, "watch": sc_watch,
            "verdict": sc_verdict, "end": sc_end}
SC = [list(s) for s in SCENES]
for i in range(1, len(SC)): SC[i][2] = SC[i - 1][3]
SC[-1][3] = TOTAL + 1

def frame(t):
    im = Image.new("RGB", (W, H), NAVY)
    for bid, scene, s0, s1 in SC:
        if s0 <= t < s1:
            SCENE_FN[scene](im, t, s0, s1)
            if t - s0 < 0.25 and bid != BID["title"]:
                a = 1 - (t - s0) / 0.25
                im = Image.blend(im, Image.new("RGB", (W, H), NAVY), a * 0.6)
            break
    caption(im, t)
    return im

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f"{ROOT}/stills/still_{float(ts):07.2f}.png")
    elif sys.argv[1] == "words":
        for s, e, w, b in WORDS:
            if b == sys.argv[2]: print(round(s, 2), w)
    elif sys.argv[1] == "seg":
        i, n = int(sys.argv[2]), int(sys.argv[3])
        NF = int(math.ceil(TOTAL * FPS)); a, b = NF * i // n, NF * (i + 1) // n
        out = f"{ROOT}/segs/seg_{i:02d}.mp4"
        pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out + ".part.mp4"], stdin=subprocess.PIPE)
        for f in range(a, b):
            pr.stdin.write(frame(f / FPS).tobytes())
        pr.stdin.close(); pr.wait(); os.replace(out + ".part.mp4", out); print("seg", i, "frames", a, b, "done")
