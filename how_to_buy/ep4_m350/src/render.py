#!/usr/bin/env python3
"""How to Buy a Piper M350 (Ep4, N333WR) — 1920x1080@30 renderer.
Usage: render.py seg <i> <n>   -> renders segment i of n to seg_i.mp4 (raw frames piped to ffmpeg)
       render.py still <t>      -> writes still_<t>.png"""
import json, math, os, subprocess, sys, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, "/tmp/htb_m350"); sys.path.insert(0, os.path.expanduser("~/kit/lib"))
from timeline import SCENES, OFFS, TOTAL
from beats import BEATS
BID = {sc: b for b, sc, _ in BEATS}
import endcard as EC

ROOT = "/tmp/htb_m350"; FD = f"{ROOT}/fonts"; CAP = f"{ROOT}/cap"; PH = f"{ROOT}/photos"
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
    tw = d.textlength("N333WR · 2022 PIPER M350", font=MB(22))
    d.rounded_rectangle([W - 110 - tw, 52, W - 70, 96], radius=10, outline=(*CYAN, 200), width=2, fill=(8, 16, 26, 170))
    d.text((W - 90 - tw, 74), "N333WR · 2022 PIPER M350", font=MB(22), fill=OFF, anchor="lm")
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


def rep_label(im, txt="REPRESENTATIVE PHOTO · PIPER PA-46-350P · NOT THE AIRCRAFT FOR SALE"):
    d = ImageDraw.Draw(im, "RGBA"); d.text((70, 925), txt, font=MR(18), fill=(200, 210, 218, 190), anchor="lm")
def big_line(d, y, txt, f=None, fill=OFF, p=1.0):
    f = f or BB(62); d.text((W / 2, y), txt, font=f, fill=(*fill, int(255 * min(max(p, 0), 1))), anchor="mm")
def chip_c(d, y, txt, f=None, fill=CYAN, fg=NAVY):
    f = f or MB(26); tw = d.textlength(txt, font=f); chip(d, W / 2 - tw / 2 - 18, y, txt, fill=fill, fg=fg, f=f)

# ---------- data (from DATA_PACK) ----------
LADDER = [("MIRAGE", "1989–2002", 549500, "$549,500", 10, "eighty-nine"), ("MIRAGE", "2011–2014", 824000, "$824,000", 8, "later"),
          ("M350", "2015–2020", 1175000, "$1,175,000", 3, "Early"), ("M350", "2022–2023", 1487450, "$1,475,000–$1,499,900", 2, "twenty-two"),
          ("M350", "2025–2026", 1950000, "$1,950,000", 4, "nearly")]
SHORT = [("N350TZ", 2019, 1175000, 1390, 1315), ("N350W", 2020, 1199000, 1195, 1195), ("N333WR", 2022, 1475000, 688, 444), ("N7377G", 2023, 1499900, 230, 230)]
PH_HIST = [("Jun 11", 1550000), ("Jul 15", 1525000), ("Aug 21", 1475000)]

def sc_title(im, t, s0, s1):
    im.paste(kb(photo_bg("mirage-2.jpg", dark=0.35), (t - s0) / (s1 - s0), 1.0, 1.06))
    d = ImageDraw.Draw(im, "RGBA"); d.rectangle([0, 0, W, H], fill=(8, 16, 26, 150))
    p = ease((t - s0 - 0.2) / 0.8)
    d.text((W / 2, 400), "HOW TO BUY A", font=BB(90), fill=(*OFF, int(255 * p)), anchor="mm")
    d.text((W / 2, 510), "PIPER M350", font=BB(170), fill=(*CYAN, int(255 * p)), anchor="mm")
    d.text((W / 2, 630), "ONE REAL AIRCRAFT · ONE REAL REPORT", font=MB(30), fill=(*OFF, int(220 * p)), anchor="mm")

def sc_problem(im, t, s0, s1):
    bid = BID["problem"]
    im.paste(kb(photo_bg("p350-6.jpg", dark=0.5), (t - s0) / (s1 - s0), 1.02, 1.1, dx=-1))
    header_bar(im, "STEP 1", "CHOOSE WHICH ONE"); rep_label(im)
    d = ImageDraw.Draw(im, "RGBA")
    tb = trig(bid, "tracking")
    if t < tb - 0.2:
        if t > trig(bid, "only"): big_line(d, 430, "THE ONLY PRESSURIZED PISTON SINGLE IN PRODUCTION", BB(74), OFF, (t - trig(bid, "only")) / 0.4)
        if t > trig(bid, "replaced"): big_line(d, 540, "M350 (2015–TODAY)  =  THE MALIBU MIRAGE AIRFRAME", MB(34), CYAN, (t - trig(bid, "replaced")) / 0.4)
    else:
        p = (t - tb) / 1.0
        panel(d, [300, 300, 920, 700]); d.text((610, 450), str(int(32 * ease(p))), font=MB(170), fill=WHITE, anchor="mm")
        d.text((610, 590), "MIRAGES & M350s FOR SALE · US", font=MB(26), fill=CYAN, anchor="mm")
        t2 = trig(bid, "Twenty-seven")
        if t > t2:
            p2 = (t - t2) / 0.8
            panel(d, [1000, 300, 1620, 700]); d.text((1310, 450), str(int(27 * ease(p2))), font=MB(170), fill=CYAN, anchor="mm")
            d.text((1310, 590), "SHOW A PUBLISHED PRICE", font=MB(26), fill=OFF, anchor="mm")
        chip_c(d, 760, "NEXTPLANE LISTING PANEL · WEEK OF OCT 5, 2026", fill=(15, 42, 63), fg=OFF, f=MB(22))

def sc_ladder(im, t, s0, s1):
    bid = BID["ladder"]
    im.paste(kb(photo_bg("mirage-1.jpg", blur=10, dark=0.78), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "THE PRICE LADDER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 140, 1810, 930])
    d.text((160, 190), "MEDIAN ASKING PRICE · ACTIVE US LISTINGS WITH A PRICE · WEEK OF OCT 5, 2026", font=MB(24), fill=GREY, anchor="lm")
    x0, xmax = 640, 1560; vmax = 2150000
    for i, (lab, yrs, v, vtxt, n, key) in enumerate(LADDER):
        ts = trig(bid, key, default=s0 + 2 + i * 6); p = ease((t - ts) / 0.8)
        y = 262 + i * 122; hero = yrs == "2022–2023"
        d.text((160, y + 20), lab, font=BB(52), fill=CYAN if hero else OFF, anchor="lm")
        d.text((370, y + 22), yrs, font=MR(26), fill=GREY, anchor="lm")
        if p > 0:
            bw = (xmax - x0) * v / vmax * p
            d.rounded_rectangle([x0, y, x0 + max(bw, 8), y + 44], radius=8, fill=(*(CYAN if hero else (120, 150, 170)), 255))
            if hero: d.text((x0, y + 72), vtxt + "  (n={})".format(n), font=MB(28), fill=WHITE, anchor="lm")
            else: d.text((x0 + bw + 18, y + 22), vtxt + "  (n={})".format(n), font=MB(28), fill=WHITE, anchor="lm")
    tl = trig(bid, "late-model")
    if t > tl:
        p = ease((t - tl) / 0.5); big_line(d, 885, "LATE-MODEL USED: PRICED CLOSE TO NEW, WITH SOMEONE ELSE'S HOURS", BB(46), CYAN, p)

def sc_shortlist(im, t, s0, s1):
    bid = BID["shortlist"]
    im.paste(kb(photo_bg("mirage-3.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "YOUR SHORTLIST")
    d = ImageDraw.Draw(im, "RGBA")
    rows = [("32", "Mirages & M350s for sale", s0 + 0.2), ("27", "with a published price", s0 + 0.9),
            ("9", "M350 (2015+) with a price", trig(bid, "nine")), ("4", "late-model used · 2019–2023", trig(bid, "leaves"))]
    panel(d, [90, 150, 700, 900]); d.text((130, 195), "THE FUNNEL", font=MB(24), fill=GREY, anchor="lm")
    for i, (n, lab, ts) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 270 + i * 150; w = [520, 440, 300, 210][i]; last = i == 3
        d.rounded_rectangle([130, y, 130 + w * p, y + 70], radius=10, fill=(*(CYAN if last else (60, 90, 112)), 255))
        d.text((150, y + 35), n, font=MB(40), fill=NAVY if last else WHITE, anchor="lm")
        d.text((130, y + 97), lab, font=MR(22), fill=OFF, anchor="lm")
    tl = trig(bid, "leaves")
    if t > tl:
        panel(d, [740, 150, 1830, 900])
        d.text((780, 195), "4 × USED M350 · ASKING $1,175,000 – $1,499,900", font=MB(24), fill=GREY, anchor="lm")
        cols = [(780, "TAIL"), (960, "YEAR"), (1090, "ASK"), (1330, "AIRFRAME"), (1560, "ENGINE")]
        for x, h in cols: d.text((x, 262), h, font=MB(20), fill=GREY, anchor="lm")
        hi = t > trig(bid, "middle")
        keys = ["nineteen,", "twenty,", "twenty-two,", "twenty-three,"]
        for i, (tail, yr, ask, tt, sm) in enumerate(SHORT):
            pr = ease((t - trig(bid, keys[i], default=tl + 0.5 * i)) / 0.4)
            if pr <= 0: continue
            y = 350 + i * 120; hero = tail == "N333WR"
            if hero and hi: d.rounded_rectangle([765, y - 40, 1810, y + 42], radius=8, fill=(*CYAN, 60), outline=CYAN, width=3)
            col = CYAN if hero and hi else WHITE; a = int(255 * pr)
            for x, v in zip([780, 960, 1090, 1330, 1560], [tail, str(yr), money(ask), "{:,} h".format(tt), "{:,} h".format(sm)]):
                d.text((x, y), v, font=MB(30), fill=(*col, a), anchor="lm")
        if t > trig(bid, "apart"):
            d.text((1285, 840), "SAME MODEL · $324,900 APART", font=MB(28), fill=CYAN, anchor="mm")

def sc_pick(im, t, s0, s1):
    bid = BID["pick"]
    im.paste(kb(photo_bg("mirage-2.jpg", dark=0.4), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); rep_label(im)
    t_here = trig(bid, "Here"); t_kept = trig(bid, "while")
    if t < t_here - 0.3:
        p = (t - s0 - 0.3) / 1.2
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 70))
        d.text((W / 2, 440), count(1475000, p), font=MB(150), fill=WHITE, anchor="mm")
        d.text((W / 2, 560), "N333WR · 2022 PIPER M350 · DEALER LISTING, KANSAS", font=MB(30), fill=CYAN, anchor="mm")
    elif t < t_kept - 0.2:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 130))
        tr = trig(bid, "report")
        if t > tr:
            p = (t - tr) / 0.9
            d.text((W / 2 - 430, 380), count(1291765, p), font=MB(84), fill=WHITE, anchor="mm")
            d.text((W / 2 - 430, 465), "NEW IN 2022 · STANDARD EQUIPPED", font=MB(24), fill=GREY, anchor="mm")
            d.text((W / 2 + 430, 380), "$1,475,000", font=MB(84), fill=CYAN, anchor="mm")
            d.text((W / 2 + 430, 465), "ASKING TODAY · 688 HOURS", font=MB(24), fill=GREY, anchor="mm")
        tf = trig(bid, "fourteen")
        if t > tf:
            p = (t - tf) / 0.8
            d.text((W / 2, 640), "+{}%".format(int(round(14 * ease(p)))), font=MB(150), fill=CYAN, anchor="mm")
            d.text((W / 2, 760), "ASK VS. THE 2022 NEW PRICE · NEXTPLANE AIRCRAFT REPORT", font=MB(26), fill=OFF, anchor="mm")
    else:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 130))
        big_line(d, 440, "FOR SALE — AND STILL FLYING", BB(110), WHITE, (t - t_kept) / 0.5)
        if t > trig(bid, "follow"): big_line(d, 600, "SO WHAT IS IT REALLY WORTH?", BB(70), CYAN, (t - trig(bid, "follow")) / 0.4)

def sc_header(im, t, s0, s1):
    bid = BID["header"]
    im.paste(kb(photo_bg("mirage-2.jpg", blur=14, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT DOES THE REPORT SAY FIRST?")
    cos = [((10, 150, 280, 212), s0 + 1.2), ((298, 150, 568, 212), trig(bid, "damage")), ((10, 356, 282, 452), trig(bid, "security")),
           ((585, 230, 857, 322), trig(bid, "flagged"))]
    blurs = [(876, 283, 1140, 304), (14, 283, 276, 316)]
    report_slide(im, t, "_headercomb", (0, 0, 1152, 466), cos, blurs=blurs, t0=s0, cy=545)

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
    im.paste(kb(photo_bg("pmir-3.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "IS THE PRICE FAIR?")
    cos = [((44, 228, 500, 298), trig(bid, "ninety-six")), ((44, 332, 470, 376), trig(bid, "middle"))]
    report_slide(im, t, "valuation", (25, 206, 1127, 412), cos, t0=s0, cy=320, maxh=330)
    tiles(im, t, [("ASKING PRICE", "$1,475,000", "published ask", trig(bid, "ask"), False),
                  ("ABOVE THE ESTIMATE", "+$178,500", "ask minus NextPlane estimate", trig(bid, "seventy-eight"), True),
                  ("PREMIUM", "+13.8%", "inside the 25th–75th range", trig(bid, "fourteen"), True)], y=540)

def sc_comps(im, t, s0, s1):
    bid = BID["comps"]
    im.paste(kb(photo_bg("mirage-1.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "FAIR COMPARED WITH WHAT?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 930])
    d.text((160, 200), "THE CLOSEST M350s · LAST ASKING PRICE · NEXTPLANE LISTING PANEL", font=MB(24), fill=GREY, anchor="lm")
    rows = [("2020", "547 h", 1295000, "left the market · Sep", trig(bid, "forty-seven"), False),
            ("2021", "700 h", 1298000, "left the market · Sep", trig(bid, "twenty-one"), False),
            ("2022", "688 h", 1475000, "THIS AIRPLANE · N333WR", s0 + 0.3, True),
            ("2023", "230 h", 1499900, "for sale now", trig(bid, "twenty-three"), False)]
    x0, x1 = 560, 1400
    for i, (yr, hrs, v, note, ts, hero) in enumerate(rows):
        p = ease((t - ts) / 0.6)
        if p <= 0: continue
        y = 280 + i * 118; col = CYAN if hero else (120, 150, 170)
        d.text((160, y + 22), yr, font=BB(56), fill=CYAN if hero else OFF, anchor="lm")
        d.text((300, y + 24), hrs, font=MB(30), fill=OFF, anchor="lm")
        bw = (x1 - x0) * (v - 1000000) / 600000 * p
        d.rounded_rectangle([x0, y, x0 + max(bw, 8), y + 46], radius=8, fill=(*col, 255))
        d.text((x0 + bw + 18, y + 23), money(v), font=MB(32), fill=WHITE, anchor="lm")
        d.text((x0, y + 70), note, font=MR(22), fill=CYAN if hero else GREY, anchor="lm")
    tp = trig(bid, "priced")
    if t > tp: chip(d, 160, 770, "$24,900 UNDER THE 2023, WHICH HAS ONE-THIRD THE HOURS", f=MB(26))
    to = trig(bid, "option")
    if t > to: chip(d, 160, 840, "LISTING: \"EVERY 2023 MODEL YEAR OPTION INSTALLED\"", fill=(15, 42, 63), fg=OFF, f=MB(26))

def sc_engine(im, t, s0, s1):
    bid = BID["engine"]
    im.paste(kb(photo_bg("p350-7.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHY IS THE ENGINE YOUNGER?")
    tr = trig(bid, "report")
    if t < tr - 0.3:
        d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 920])
        d.text((160, 200), "N333WR · TIMES AS LISTED", font=MB(24), fill=GREY, anchor="lm")
        x0, x1 = 480, 1500
        for i, (lab, v, key, col) in enumerate([("AIRFRAME", 688, "eighty-eight", (120, 150, 170)), ("ENGINE", 444, "forty-four", CYAN)]):
            ts = trig(bid, key); p = ease((t - ts) / 0.9)
            y = 330 + i * 190
            d.text((170, y + 30), lab, font=BB(56), fill=OFF, anchor="lm")
            if p > 0:
                d.rounded_rectangle([x0, y, x0 + (x1 - x0) * v / 800 * p, y + 60], radius=10, fill=col)
                d.text((x0 + (x1 - x0) * v / 800 * p + 20, y + 30), "{:,} hrs".format(int(v * p)), font=MB(40), fill=WHITE, anchor="lm")
        tm = trig(bid, "normally")
        if t > tm: big_line(d, 760, "ON A FOUR-YEAR-OLD AIRPLANE, THESE NORMALLY MATCH", BB(60), CYAN, (t - tm) / 0.4)
        if t > trig(bid, "good"): big_line(d, 840, "244 FEWER HOURS ON THE ENGINE", MB(30), OFF, (t - trig(bid, "good")) / 0.4)
    else:
        cos = [((25, 100, 565, 205), trig(bid, "sixty")), ((582, 100, 1127, 205), trig(bid, "sixty-seven")), ((20, 218, 1130, 260), trig(bid, "three"))]
        report_slide(im, t, "cpm", (0, 0, 1152, 420), cos, t0=tr - 0.3, cy=490)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "thirteen"): chip(d, 70, 880, "302 MORE HOURS × $45/HR ($90,000 ÷ 2,000 HR TBO) ≈ $13,590", f=MB(26))
        if t > trig(bid, "Why"): chip(d, 1130, 880, "ASK: WHY? READ THE ENGINE LOGBOOK", fill=(15, 42, 63), fg=OFF, f=MB(26))

def sc_newprice(im, t, s0, s1):
    bid = BID["newprice"]
    im.paste(kb(photo_bg("pmir-3.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHY MORE THAN NEW?")
    t2 = trig(bid, "replacement")
    if t < t2 - 0.3:
        cos = [((392, 66, 760, 122), trig(bid, "nine")), ((764, 66, 1132, 122), trig(bid, "nine") + 1.6)]
        report_slide(im, t, "msrp", (0, 0, 1152, 126), cos, t0=s0, cy=330, maxh=330)
        tz = trig(bid, "zero")
        tiles(im, t, [("NEW · 2022", "$1,291,765", "standard equipped", trig(bid, "nine"), False),
                      ("NEW · 2025", "$2,060,000", "standard equipped", tz, True),
                      ("CHANGE", "+60%", "2022 to 2025", tz + 1.2, True)], y=540)
    else:
        report_slide(im, t, "replacement", (0, 0, 1152, 418), [], t0=t2 - 0.3, cy=500)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "explains"): chip_c(d, 880, "A RISING NEW PRICE LIFTS EVERY USED M350 · IT DOES NOT EXPLAIN THIS ONE'S PREMIUM")

def sc_pricehist(im, t, s0, s1):
    import datetime as dtm
    bid = BID["pricehist"]
    im.paste(kb(photo_bg("mirage-2.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS THE SELLER MOVED?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 920])
    d.text((160, 200), "ASKING PRICE · N333WR · VERIFIED BY NEXTPLANE", font=MB(24), fill=GREY, anchor="lm")
    def dx(s):
        m = {"Jun": 6, "Jul": 7, "Aug": 8}[s.split()[0]]; return dtm.date(2026, m, int(s.split()[1]))
    d0, d1 = dtm.date(2026, 6, 1), dtm.date(2026, 10, 10)
    X = lambda dd: 300 + (dd - d0).days / (d1 - d0).days * 1400
    Y = lambda v: 760 - (v - 1450000) / (1570000 - 1450000) * 440
    for v in (1475000, 1500000, 1525000, 1550000):
        d.line([300, Y(v), 1710, Y(v)], fill=(60, 80, 96), width=1); d.text((285, Y(v)), money(v), font=MR(20), fill=GREY, anchor="rm")
    tcut = [trig(bid, "June"), trig(bid, "July."), trig(bid, "August.")]
    pts = [(X(dx(lab)), Y(v), lab, v) for i, (lab, v) in enumerate(PH_HIST) if t >= tcut[i]]
    if pts:
        path = []
        for i, (x, y, lab, v) in enumerate(pts):
            if i: path.append((x, path[-1][1]))
            path.append((x, y))
        path.append((X(dtm.date(2026, 10, 5)) if len(pts) == 3 else pts[-1][0] + 30, path[-1][1]))
        d.line(path, fill=CYAN, width=5)
        for x, y, lab, v in pts:
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=CYAN)
            d.text((x + 14, y - 30), money(v), font=MB(24), fill=WHITE, anchor="lm"); d.text((x, 800), lab, font=MR(22), fill=GREY, anchor="mm")
        if len(pts) == 3: d.text((X(dtm.date(2026, 10, 5)), 800), "Oct 5", font=MR(22), fill=GREY, anchor="mm")
    if t > trig(bid, "total,"): chip(d, 1180, 250, "2 CUTS · −$75,000 · −4.8%", f=MB(28))
    if t > trig(bid, "ten"): d.text((W / 2, 870), "COMPARABLE LISTINGS: 10 OF 24 CUT · TYPICAL TOTAL CUT 2.8% · THIS ONE 4.8%", font=MB(28), fill=OFF, anchor="mm")
    if t > trig(bid, "nothing"): chip(d, 1180, 320, "NO CHANGE SINCE AUG 21", fill=(15, 42, 63), fg=OFF, f=MB(28))

def sc_owner(im, t, s0, s1):
    bid = BID["owner"]
    im.paste(kb(photo_bg("pa46-4.jpg", blur=14, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHY IS IT FOR SALE SO SOON?")
    blurs = [(22, 116, 300, 144), (56, 204, 400, 230)]
    cos = [((852, 92, 1132, 146), trig(bid, "December")), ((52, 224, 420, 250), trig(bid, "December") + 1.5)]
    report_slide(im, t, "reg", (0, 0, 1152, 278), cos, blurs=blurs, t0=s0, cy=430)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "June"): chip_c(d, 760, "REGISTERED TO THE CURRENT OWNER DEC 5, 2025  →  LISTED FOR SALE JUN 11, 2026")
    if t > trig(bid, "Why"): chip_c(d, 840, "A SHORT HOLD IS NOT A RED FLAG · IT IS A FAIR QUESTION", fill=(15, 42, 63), fg=OFF)

def sc_flight(im, t, s0, s1):
    bid = BID["flight"]
    im.paste(kb(photo_bg("pmir-6.jpg", blur=6, dark=0.75), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "STEP 2", "IS IT STILL FLYING?")
    cos = [((8, 127, 1094, 166), trig(bid, "seventy-two")), ((8, 53, 1094, 92), trig(bid, "Sixty-one"))]
    report_slide(im, t, "fl_period", (0, 0, 1102, 238), cos, t0=s0, cy=320, maxw=1500, maxh=340)
    tn = trig(bid, "November.")
    if t > tn: report_slide(im, t, "fl_monthly", (0, 0, 543, 318), [], t0=tn, cy=715, maxw=660, maxh=390, cx=560)
    d = ImageDraw.Draw(im, "RGBA")
    if t > tn: d.text((1340, 570), "ADS-B TRACKED FLIGHTS", font=MB(24), fill=GREY, anchor="mm")
    if t > trig(bid, "market."):
        d.text((1340, 650), "61.1 HRS", font=MB(84), fill=CYAN, anchor="mm"); d.text((1340, 730), "LAST 3 MONTHS · WHILE LISTED FOR SALE", font=MB(24), fill=OFF, anchor="mm")
    if t > trig(bid, "listing"):
        d.text((1340, 800), "LISTING SAYS 688 HRS TOTAL", font=MB(28), fill=OFF, anchor="mm")
    if t > trig(bid, "Ask"):
        d.text((1340, 865), "ASK: CURRENT TIMES, IN WRITING", font=BB(46), fill=CYAN, anchor="mm")

def sc_ads(im, t, s0, s1):
    bid = BID["ads"]
    im.paste(kb(photo_bg("p350-7.jpg", blur=14, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT SHOULD THE PAPERWORK SHOW?")
    blurs = [(250, 274, 434, 322)]
    cos = [((30, 250, 224, 326), trig(bid, "five"))]
    report_slide(im, t, "ads", (0, 0, 664, 348), cos, blurs=blurs, t0=s0, cy=470, maxh=640)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "three"): chip_c(d, 815, "5 ACTIVE ADs MATCHED · 3 CONDITIONAL ON INSTALLED PARTS")
    if t > trig(bid, "annual"): chip_c(d, 885, "LISTING: ANNUAL \"APRIL 2026\" · DONE, OR DUE? CHECK THE LOGBOOKS", fill=(15, 42, 63), fg=OFF)

def sc_sdr(im, t, s0, s1):
    bid = BID["sdr"]
    im.paste(kb(photo_bg("mirage-1.jpg", blur=14, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS IT EVER BEEN HURT?")
    cos = [((10, 540, 1140, 585), trig(bid, "service"))]
    report_slide(im, t, "sdr", (0, 0, 1152, 598), cos, t0=s0, cy=490, maxh=730)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "record"): chip(d, 70, 885, "NTSB RECORDS FOR THIS AIRCRAFT: NONE", f=MB(26))

def sc_opcost(im, t, s0, s1):
    bid = BID["opcost"]
    im.paste(kb(photo_bg("malibu-0.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT WILL IT COST TO KEEP?")
    cos = [((15, 468, 1137, 502), trig(bid, "fifty-one")), ((15, 502, 1137, 542), trig(bid, "thirty-one")), ((15, 172, 1137, 210), trig(bid, "insurance"))]
    report_slide(im, t, "opcost", (0, 0, 1152, 546), cos, t0=s0, cy=520, maxh=700)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "quote"): chip(d, 70, 905, "GET YOUR OWN INSURANCE QUOTE BEFORE YOU OFFER", f=MB(24))

def sc_seller(im, t, s0, s1):
    bid = BID["seller"]
    im.paste(kb(photo_bg("p350-6.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO AM I DEALING WITH?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [360, 220, 1560, 820])
    d.text((W / 2, 320), "DEALER LISTING", font=BB(96), fill=CYAN, anchor="mm")
    d.text((W / 2, 400), "KANSAS · NOT THE REGISTERED OWNER", font=MB(28), fill=OFF, anchor="mm")
    tf = trig(bid, "fifteen")
    if t > tf: d.text((W / 2, 480), "15 OF 15 CURRENT LISTINGS: PA-46 FAMILY", font=MB(34), fill=WHITE, anchor="mm")
    tc = trig(bid, "come", 2)
    items = [("Come with comps and numbers", tc), ("Independent pre-buy at a shop you choose", tc + 0.5), ("Title search + escrow", tc + 1.0)]
    for i, (s, ts) in enumerate(items):
        if t > ts: bullet(d, 520, 580 + i * 75, s, BS(44))

def sc_offer(im, t, s0, s1):
    bid = BID["offer"]
    im.paste(kb(photo_bg("mirage-2.jpg", blur=12, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 3", "THE OFFER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 140, 1810, 930])
    rows = [("NEXTPLANE ESTIMATE", "$1,296,500", trig(bid, "Start"), OFF), ("ENGINE LIFE CREDIT", "+ $13,590", trig(bid, "Add"), OFF),
            ("ESTIMATE + ENGINE", "≈ $1,310,000", trig(bid, "lands"), CYAN), ("CLOSEST COMPS", "$1.295M–$1.298M", trig(bid, "closest"), OFF)]
    for i, (lab, v, ts, col) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 220 + i * 82
        d.text((170, y), lab, font=MB(26), fill=(*GREY, int(255 * p)), anchor="lm"); d.text((990, y), v, font=MB(36), fill=(*col, int(255 * p)), anchor="rm")
    tt = trig(bid, "timing")
    if t > tt:
        stats = [("115+", "days listed (since Jun 11)", trig(bid, "fifteen")), ("52%", "model odds of another cut in 90 days", trig(bid, "even")),
                 ("47", "days since the last price change", trig(bid, "even") + 1.2)]
        d.line([1040, 190, 1040, 540], fill=(60, 80, 96), width=2)
        for i, (v, lab, ts) in enumerate(stats):
            p = ease((t - ts) / 0.5)
            if p <= 0: continue
            y = 225 + i * 110
            d.text((1080, y + 10), v, font=MB(60), fill=(*CYAN, int(255 * p)), anchor="lm"); d.text((1290, y + 10), lab, font=MR(22), fill=(*OFF, int(255 * p)), anchor="lm")
    to = trig(bid, "reasonable")
    if t > to:
        p = ease((t - to) / 0.5)
        d.rounded_rectangle([180, 590, 1740, 690], radius=18, fill=(*CYAN, int(255 * p)))
        d.text((W / 2, 640), "OPEN AROUND $1.31 MILLION · BACKED BY THE COMPS", font=BB(58), fill=NAVY, anchor="mm")
    ts = trig(bid, "subject")
    for i, s in enumerate(["Current airframe + engine hours, in writing", "The engine logbook", "A pre-buy at a shop you choose"]):
        if t > ts + i * 1.3: bullet(d, 200, 745 + i * 62, s, BS(40))

def sc_watch(im, t, s0, s1):
    bid = BID["watch"]
    im.paste(kb(photo_bg("pmir-3.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 4", "KEEP WATCHING")
    d = ImageDraw.Draw(im, "RGBA")
    items = [(3, "OTHERS ON YOUR SHORTLIST", "2019 · 2020 · 2023", trig(bid, "three")), (6, "NEW MIRAGE / M350 LISTINGS", "last 14 days", trig(bid, "six")),
             (4, "PRICE CUTS", "last 14 days", trig(bid, "four", 2))]
    bw, gap = 520, 40; x = (W - (3 * bw + 2 * gap)) / 2; y = 300
    for v, lab, sub, ts in items:
        p = (t - ts) / 0.8
        if p > 0:
            panel(d, [x, y, x + bw, y + 330])
            d.text((x + bw / 2, y + 130), str(int(round(v * ease(p)))), font=MB(120), fill=WHITE, anchor="mm")
            d.text((x + bw / 2, y + 235), lab, font=MB(26), fill=CYAN, anchor="mm"); d.text((x + bw / 2, y + 280), sub, font=MR(22), fill=GREY, anchor="mm")
        x += bw + gap

def sc_verdict(im, t, s0, s1):
    bid = BID["verdict"]
    im.paste(kb(photo_bg("mirage-2.jpg", dark=0.5), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "VERDICT", "WHO IS THIS AIRPLANE RIGHT FOR?"); rep_label(im)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "buyer"):
        panel(d, [110, 230, 940, 700], a=215); d.text((150, 285), "RIGHT FOR", font=MB(28), fill=CYAN, anchor="lm")
        for i, s in enumerate(["Wants a late-model M350", "A young engine: 444 hrs", "Every option, Garmin G1000 NXi", "Not paying ~$2M for a new one"]):
            bullet(d, 150, 365 + i * 80, s, BS(42))
    if t > trig(bid, "shopping"):
        panel(d, [980, 230, 1810, 700], a=215); d.text((1020, 285), "SHOPPING ON PRICE?", font=MB(28), fill=CYAN, anchor="lm")
        bullet(d, 1020, 365, "The 2019 asks $1,175,000", BS(42), mark="arrow"); bullet(d, 1020, 445, "The 2020 asks $1,199,000", BS(42), mark="arrow")
        bullet(d, 1020, 525, "$276,000–$300,000 less", BS(42), fill=GREY, mark="arrow")
    tq = trig(bid, "Why")
    if t > trig(bid, "Priced"): big_line(d, 770, "PRICED ABOVE THE ESTIMATE · CLEAN HISTORY", BB(54), OFF, (t - trig(bid, "Priced")) / 0.4)
    if t > tq: big_line(d, 850, "WHY SO SOON?  ·  WHY THE YOUNGER ENGINE?  ·  HOURS TODAY?", BB(54), CYAN, (t - tq) / 0.4)

def sc_end(im, t, s0, s1):
    p = Image.new("RGB", (1080, 1920), NAVY)
    EC.draw_endcard(p, t - s0, FD, f"{ROOT}/assets/logo.png")
    p = p.crop((0, 380, 1080, 1480)).resize((1060, 1080), Image.LANCZOS)
    im.paste(NAVY, (0, 0, W, H)); im.paste(p, ((W - 1060) // 2, 0))

SCENE_FN = {"title": sc_title, "problem": sc_problem, "ladder": sc_ladder, "shortlist": sc_shortlist, "pick": sc_pick, "header": sc_header,
            "value": sc_value, "comps": sc_comps, "engine": sc_engine, "newprice": sc_newprice, "pricehist": sc_pricehist, "owner": sc_owner,
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
