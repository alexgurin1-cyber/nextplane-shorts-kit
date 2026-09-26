#!/usr/bin/env python3
"""NextPlane "The Rent Line" QUIZ Short renderer (quiz #7, guess-the-gap A/B/C mechanic).
Usage: render_rl.py <start> <end> [step]  -> /tmp/qz/frames/f%05d.jpg (1080x1920@30). Resumable; step interleaves procs."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, "/tmp/qz")
from endcard import draw_endcard

ROOT = "/tmp/qz"
W, H, FPS = 1080, 1920, 30
NAVY = (10, 22, 34); NAVY2 = (16, 34, 52); INK = (13, 27, 38)
CYAN = (37, 197, 203); OFF = (246, 249, 250); WHITE = (255, 255, 255)
MUTE = (128, 148, 162); AMBER = (245, 166, 35); DIM = (70, 92, 108); GREEN = (86, 214, 140); RED = (232, 88, 88)
FD = f"{ROOT}/fonts"
_f = {}
def F(name, size):
    k = (name, size)
    if k not in _f: _f[k] = ImageFont.truetype(f"{FD}/{name}", size)
    return _f[k]
BCB = lambda s: F("BarlowCondensed-Bold.ttf", s)
BCS = lambda s: F("BarlowCondensed-SemiBold.ttf", s)
SMB = lambda s: F("SpaceMono-Bold.ttf", s)
SMR = lambda s: F("SpaceMono-Regular.ttf", s)

def ease(p): p = min(max(p, 0.0), 1.0); return p*p*(3-2*p)
def easeo(p): p = min(max(p, 0.0), 1.0); return 1-(1-p)**3

BEATS = ["b1","b2","b3","b4","b5","b6"]
VO = {b: json.load(open(f"{ROOT}/vo/{b}.json")) for b in BEATS}
OFFS = {}
t = 0.4; GAP = 0.22
for b in BEATS:
    OFFS[b] = t; t += VO[b]["dur"] + GAP + (0.3 if b == "b1" else 0)
TOTAL = OFFS["b6"] + VO["b6"]["dur"] + 1.3
NF = int(TOTAL * FPS)

def wt(b, idx): w = VO[b]["words"][idx]; return OFFS[b] + w["s"]
def anchor(b, text, occ=1):
    n = 0
    for i, w in enumerate(VO[b]["words"]):
        if w["w"].strip(".,?!'’:").lower() == text.lower():
            n += 1
            if n == occ: return wt(b, i)
    return 1e9

SC = []
edges = [0.0]
for b in BEATS[1:]: edges.append(OFFS[b] - GAP/2)
edges.append(TOTAL)
for i, b in enumerate(BEATS): SC.append((b, edges[i], edges[i+1]))
T0 = {b: SC[i][1] for i, b in enumerate(BEATS)}

_ph = {}
def photo(slug, dark=0.42, tint=0.55):
    k = (slug, dark, tint)
    if k in _ph: return _ph[k]
    cache = f"{ROOT}/assets/bg_{slug}_{int(dark*100)}_{int(tint*100)}.jpg"
    if os.path.exists(cache):
        try:
            _ph[k] = Image.open(cache).convert("RGB"); return _ph[k]
        except Exception: pass
    im = Image.open(f"{ROOT}/photos/{slug}-0.jpg").convert("RGB")
    tw, th = int(W*1.12), int(H*1.12)
    r = max(tw/im.width, th/im.height)
    im = im.resize((int(im.width*r)+1, int(im.height*r)+1), Image.LANCZOS)
    x = (im.width - tw)//2; y = (im.height - th)//2
    im = im.crop((x, y, x+tw, y+th))
    im = ImageEnhance.Color(im).enhance(0.55)
    im = ImageEnhance.Brightness(im).enhance(dark)
    ov = Image.new("RGB", im.size, NAVY)
    im = Image.blend(im, ov, tint)
    tmp = cache + f".{os.getpid()}.tmp"
    im.save(tmp, quality=90, format="JPEG"); os.replace(tmp, cache)
    _ph[k] = im; return im

def bg_photo(slug, p, zoom0=1.10, zoom1=1.0, dark=0.42, tint=0.55):
    src = photo(slug, dark, tint)
    z = zoom0 + (zoom1 - zoom0) * p
    cw, ch = int(W*z), int(H*z)
    cw, ch = min(cw, src.width), min(ch, src.height)
    x = (src.width - cw)//2; y = (src.height - ch)//2
    return src.crop((x, y, x+cw, y+ch)).resize((W, H), Image.BILINEAR)

def bg_grad(top=NAVY, bot=NAVY2):
    k = ("grad", top, bot)
    if k not in _ph:
        im = Image.new("RGB", (1, H)); px = im.load()
        for y in range(H):
            a = y / H
            px[0, y] = tuple(int(top[i]*(1-a)+bot[i]*a) for i in range(3))
        _ph[k] = im.resize((W, H))
    return _ph[k].copy()

def vignette(im):
    k = "vig"
    if k not in _ph:
        m = Image.new("L", (W//4, H//4), 0)
        d = ImageDraw.Draw(m)
        d.ellipse([-W//16, -H//16, W//4+W//16, H//4+H//16], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(40)).resize((W, H))
        _ph[k] = m.point(lambda v: 185 + (v*70)//255)
    black = Image.new("RGB", (W, H), (4, 10, 16))
    return Image.composite(im, black, _ph[k])

def glass(d, box, a=1.0, fill=(13,27,38,200), line=CYAN, lw=2, r=22):
    if a <= 0: return
    f = (fill[0], fill[1], fill[2], int(fill[3]*a))
    d.rounded_rectangle(box, radius=r, fill=f, outline=(*line, int(210*a)), width=lw)

def sh(d, xy, s, f, fill, a=1.0, anch="mm", shad=3):
    if a <= 0: return
    col = tuple(int(v*min(a,1)) for v in fill)
    if shad: d.text((xy[0]+shad, xy[1]+shad), s, font=f, fill=(0,0,0), anchor=anch)
    d.text(xy, s, font=f, fill=col, anchor=anch)

def chip(d, cx, cy, txt, f, a, fg=CYAN, w_pad=34, h_pad=20, fill=(13,27,38,190)):
    if a <= 0: return
    tw = d.textlength(txt, font=f)
    hh = f.size//2
    box = [cx-tw/2-w_pad, cy-hh-h_pad, cx+tw/2+w_pad, cy+hh+h_pad]
    d.rounded_rectangle(box, radius=18, fill=(fill[0],fill[1],fill[2],int(fill[3]*a)), outline=(*fg, int(200*a)), width=2)
    sh(d, (cx, cy), txt, f, fg if fg != CYAN else OFF, a)

def counter(v0, v1, t0, dur, t, fmt="{:,.0f}"):
    p = easeo((t - t0) / dur)
    return fmt.format(v0 + (v1 - v0) * p)

def stamp(im, cx, cy, txt, color, a, size=74, angle=-9):
    if a <= 0: return
    f = BCB(size)
    tmp = Image.new("RGBA", (900, 220), (0,0,0,0))
    td = ImageDraw.Draw(tmp)
    tw = td.textlength(txt, font=f)
    hh = size*0.75
    box = [450-tw/2-28, 110-hh, 450+tw/2+28, 110+hh]
    td.rounded_rectangle(box, radius=14, outline=(*color, 255), width=6)
    td.text((450, 110), txt, font=f, fill=(*color, 255), anchor="mm")
    tmp = tmp.rotate(angle, expand=True, resample=Image.BICUBIC)
    sc = 0.85 + 0.15*ease(a)
    tmp = tmp.resize((int(tmp.width*sc), int(tmp.height*sc)), Image.BILINEAR)
    if a < 1:
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v*a)))
    im.paste(tmp, (int(cx-tmp.width/2), int(cy-tmp.height/2)), tmp)

_th = {}
def thumb(slug, w, h):
    k = (slug, w, h)
    if k not in _th:
        im = Image.open(f"{ROOT}/photos/{slug}-0.jpg").convert("RGB")
        r = max(w/im.width, h/im.height)
        im = im.resize((int(im.width*r)+1, int(im.height*r)+1), Image.LANCZOS)
        x = (im.width-w)//2; y = (im.height-h)//2
        im = im.crop((x, y, x+w, y+h))
        im = ImageEnhance.Color(im).enhance(0.8)
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0,0,w-1,h-1], radius=14, fill=255)
        _th[k] = (im, m)
    return _th[k]

def paste_thumb(im, slug, box, a):
    if a <= 0: return
    x0, y0, x1, y1 = box
    th, m = thumb(slug, x1-x0, y1-y0)
    if a < 1: m = m.point(lambda v: int(v*a))
    im.paste(th, (x0, y0), m)

CHUNKS = []
for b in BEATS[:-1]:
    ws = VO[b]["words"]; cur = []
    for i, w in enumerate(ws):
        cur.append((w["w"], OFFS[b]+w["s"], OFFS[b]+w["e"]))
        if len(cur) >= 4 or w["w"].rstrip().endswith((".", "?", "!", ",", ":")):
            CHUNKS.append(cur); cur = []
    if cur: CHUNKS.append(cur)

def draw_captions(d, t):
    for ch in CHUNKS:
        if ch[0][1] - 0.05 <= t <= ch[-1][2] + 0.12:
            f = BCS(58)
            words = [w for w, s, e in ch]
            widths = [d.textlength(w+" ", font=f) for w in words]
            tot = sum(widths)
            scale = min(1.0, 980/tot)
            f2 = BCS(int(58*scale)) if scale < 1 else f
            widths = [d.textlength(w+" ", font=f2) for w in words]
            tot = sum(widths)
            x = W/2 - tot/2; y = 1575
            d.rounded_rectangle([W/2-tot/2-30, y-52, W/2+tot/2+30, y+52], radius=16, fill=(5, 12, 18, 165))
            for (w, s, e), wd in zip(ch, widths):
                col = CYAN if s <= t <= e else OFF
                d.text((x+3, y+3), w, font=f2, fill=(0,0,0), anchor="lm")
                d.text((x, y), w, font=f2, fill=col, anchor="lm")
                x += wd
            return

def topline(d, t, txt, t0):
    a = ease((t - t0)/0.4)
    sh(d, (W/2, 150), txt, SMB(32), MUTE, a)
    if a > 0:
        lw = int(300*a)
        d.rectangle([W/2-lw/2, 190, W/2+lw/2, 193], fill=(*CYAN, int(160*a)))

# ---------- the two ad cards ----------
CARD_A = [70, 240, 1010, 640]
CARD_B = [70, 680, 1010, 1080]
def ad_card(im, d, box, a, label, title, sub, hours_txt, price_txt, slug, hot, tag=None, tag_col=MUTE, line=None, line_col=GREEN):
    if a <= 0: return
    x0, y0, x1, y1 = box
    glass(d, box, a, line=CYAN if hot else DIM, lw=3 if hot else 2, r=18)
    paste_thumb(im, slug, (x0+18, y0+18, x0+400, y0+300), a)
    d2 = ImageDraw.Draw(im, "RGBA")
    sh(d2, (x0+430, y0+50), label, SMB(24), CYAN if hot else MUTE, a, anch="lm")
    sh(d2, (x0+430, y0+108), title, BCB(46), OFF, a, anch="lm")
    sh(d2, (x0+430, y0+155), sub, SMR(19), MUTE, a, anch="lm")
    if hours_txt: sh(d2, (x0+430, y0+215), hours_txt, BCB(44), OFF, a, anch="lm")
    if price_txt:
        sh(d2, (x0+430, y0+278), price_txt, SMB(50), CYAN if hot else WHITE, a, anch="lm")
        sh(d2, (x1-28, y0+278), "ASKING", BCB(24), MUTE, a, anch="rm")
    if line is not None:
        sy = y0+335
        d2.rounded_rectangle([x0+18, sy, x1-18, sy+48], radius=10, fill=(18, 36, 52, int(225*a)), outline=(*line_col, int(220*a)), width=2)
        sh(d2, (x0+34, sy+24), line, BCS(26), OFF, a, anch="lm")
    if tag:
        chip(d2, x1-120, y0+215, tag, BCB(28), a, fg=tag_col, w_pad=16, h_pad=9)

# ---------- scenes ----------
def s_hook(im, d, t):
    topline(d, t, "GUESS THE GAP · TWO 2005 CIRRUS SR22-G2 · $30K APART", 0.3)
    ca = ease((t-(anchor("b1","Ad",1)-0.2))/0.45)
    cb = ease((t-(anchor("b1","Ad",2)-0.2))/0.45)
    ha = ease((t-(anchor("b1","six")-0.1))/0.35); hb = ease((t-(anchor("b1","four")-0.1))/0.35)
    ad_card(im, d, CARD_A, ca, "AD A · 2005 · CONTROLLER", "CIRRUS SR22-G2", "N2428E · S/N 1307 · BEND OR · DEALER",
            (counter(0, 630, anchor("b1","six")-0.1, 0.6, t) + " HOURS" if ha > 0 else ""), "$325,000", "sr22_g2", False,
            line="\"LOWEST TOTAL TIME SR22 G2 ON THE MARKET\"", line_col=CYAN)
    ad_card(im, d, CARD_B, cb, "AD B · 2005 · CONTROLLER", "CIRRUS SR22-G2 GTS", "N25ML · S/N 1571 · RUSTON LA · DEALER",
            (counter(0, 4030, anchor("b1","four")-0.1, 0.7, t) + " HOURS" if hb > 0 else ""), "$294,900", "sr22_n147vc", False,
            line="\"FULLY LOADED · FRESH CAPS REPACK · A/C\"", line_col=DIM)
    d2 = ImageDraw.Draw(im, "RGBA")
    qa = ease((t-(anchor("b1","Per")-0.1))/0.4)
    if qa > 0:
        glass(d2, [70, 1120, 1010, 1215], qa, line=AMBER, lw=3)
        sh(d2, (W/2, 1167), "COST PER HOUR TO OWN · WHO PAID MORE?", BCB(44), AMBER, qa)
    # vote tiles
    tiles = [("A", "SAME", "same"), ("B", "DOUBLE", "double"), ("C", "TRIPLE", "triple")]
    for i, (L, txt, word) in enumerate(tiles):
        ta = ease((t-(anchor("b1", word)-0.15))/0.35)
        if ta <= 0: continue
        x0 = 70 + i*320; x1 = x0 + 300
        glass(d2, [x0, 1240, x1, 1400], ta, line=DIM, lw=2, fill=(13,27,38,215))
        sh(d2, (x0+40, 1320), L, BCB(74), CYAN, ta, anch="lm")
        sh(d2, (x0+120, 1320), txt, BCB(46), OFF, ta, anch="lm")
    for word, n, occ in (("Three", "3", 1), ("Two", "2", 3), ("One", "1", 1)):
        at = anchor("b1", word, occ) - 0.05
        if at <= t < at + 0.95:
            a = ease((t-at)/0.15) * (1 - ease((t-at-0.7)/0.25))
            sc = 1.0 + 0.25*ease((t-at)/0.9)
            sh(d2, (W/2, 1450), n, BCB(int(130*sc)), CYAN, a)

def s_reveal(im, d, t):
    topline(d, t, "THE ANSWER · NEXTPLANE COST ESTIMATE · PER HOUR FLOWN", T0["b2"]+0.15)
    ca = ease((t-(anchor("b2","c")-0.05))/0.3)
    stamp(im, W/2, 300, "C · TRIPLE", CYAN, ca, size=86, angle=-6)
    d = ImageDraw.Draw(im, "RGBA")
    cols = [("AD A · N2428E", "sr22_g2", 29, 20978, 723, "twenty", 1, "Twenty", 2, "seven", 1, CYAN, 70),
            ("AD B · N25ML", "sr22_n147vc", 187, 44217, 236, "B", 1, "Forty", 1, "two", 1, AMBER, 560)]
    for lab, slug, hpy, yr, ph, w1, o1, w2, o2, w3, o3, col, x0 in cols:
        a1 = ease((t-(anchor("b2", w1, o1)-0.15))/0.4)
        if a1 <= 0: continue
        x1 = x0 + 450
        glass(d, [x0, 420, x1, 1180], a1, fill=(11,24,36,215), line=col, lw=3)
        paste_thumb(im, slug, (x0+20, 440, x1-20, 640), a1)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (x0+30, 690), lab, SMB(24), col, a1, anch="lm")
        sh(d, (x0+30, 760), counter(0, hpy, anchor("b2", w1, o1)-0.15, 0.7, t) + " H/YR", BCB(64), OFF, a1, anch="lm")
        sh(d, (x0+30, 805), "LIFETIME AVERAGE", SMR(18), MUTE, a1, anch="lm")
        a2 = ease((t-(anchor("b2", w2, o2)-0.15))/0.4)
        if a2 > 0:
            sh(d, (x0+30, 880), counter(0, yr, anchor("b2", w2, o2)-0.15, 0.8, t, "${:,.0f}"), BCB(54), OFF, a2, anch="lm")
            sh(d, (x0+30, 925), "PER YEAR TO OWN", SMR(18), MUTE, a2, anch="lm")
        a3 = ease((t-(anchor("b2", w3, o3)-0.15))/0.4)
        if a3 > 0:
            g = easeo((t-(anchor("b2", w3, o3)-0.15))/0.8)
            d.rounded_rectangle([x0+30, 1090, x0+30+int(390*ph/760*g), 1150], radius=10, fill=(*col, 235))
            sh(d, (x0+30, 1040), counter(0, ph, anchor("b2", w3, o3)-0.15, 0.8, t, "${:,.0f}") + "/H", SMB(60), WHITE, a3, anch="lm")
    ra = ease((t-(anchor("b2","Same")-0.1))/0.4)
    chip(d, W/2, 1260, "SAME AIRPLANE · 3.06× THE COST PER HOUR", BCB(44), ra)
    d2 = ImageDraw.Draw(im, "RGBA")
    ta = ease((t-(anchor("b2","times")-0.1))/0.4)
    chip(d2, W/2, 1370, "ESTIMATES · REGION ADJUSTED · OR vs LA", BCB(26), ta, fg=MUTE, w_pad=16, h_pad=8)

FIXED = [("INSURANCE", 5230, "Insurance"), ("HANGAR", 4200, "hangar"), ("ANNUAL", 2500, "annual"), ("SUBSCRIPTIONS", 2900, "subscriptions")]
def s_why(im, d, t):
    topline(d, t, "WHY · THE FIXED FLOOR · 2005 SR22 · NATIONAL ESTIMATE", T0["b3"]+0.15)
    a0 = ease((t-(anchor("b3","Why")-0.1))/0.4)
    glass(d, [60, 240, 1020, 720], a0, fill=(11,24,36,215), line=DIM)
    sh(d, (90, 285), "EVERY YEAR · WHETHER YOU FLY OR NOT", SMR(22), MUTE, a0, anch="lm")
    for i, (lab, v, word) in enumerate(FIXED):
        at = anchor("b3", word) - 0.1; ra = ease((t-at)/0.35)
        if ra <= 0: continue
        y = 330 + i*70
        g = easeo((t-at)/0.7)
        d.rounded_rectangle([90, y, 90+int(560*v/5230*g), y+50], radius=8, fill=(78,118,138,230))
        sh(d, (100, y+25), lab, BCB(32), OFF, ra, anch="lm")
        sh(d, (990, y+25), counter(0, v, at, 0.7, t, "${:,.0f}"), SMB(30), OFF, ra, anch="rm")
    fa = ease((t-(anchor("b3","Fifteen")-0.15))/0.4)
    if fa > 0:
        d.line([90, 620, 990, 620], fill=(*CYAN, int(200*fa)), width=3)
        sh(d, (90, 670), counter(0, 14830, anchor("b3","Fifteen")-0.15, 0.8, t, "${:,.0f}") + " / YEAR", BCB(54), CYAN, fa, anch="lm")
        sh(d, (990, 670), "BEFORE THE PROP TURNS", BCB(30), AMBER, fa, anch="rm")
    va = ease((t-(anchor("b3","Fuel")-0.1))/0.4)
    chip(d, W/2, 790, "+ $161 / HOUR · FUEL · ENGINE · MAINTENANCE RESERVES", BCB(34), va, fg=AMBER, w_pad=24, h_pad=12)
    # ladder
    la = ease((t-(anchor("b3","Twenty")-0.1))/0.4)
    if la > 0:
        glass(d, [60, 860, 1020, 1340], la, fill=(11,24,36,215), line=CYAN, lw=3)
        sh(d, (90, 905), "COST PER HOUR FLOWN · BY HOURS PER YEAR", SMR(22), MUTE, la, anch="lm")
        rows = [("25 H/YR", 755, "Twenty", 1), ("50 H/YR", 458, "Twenty", 1), ("100 H/YR", 310, "hundred", 2), ("200 H/YR", 236, "Two", 1)]
        for i, (lab, v, word, occ) in enumerate(rows):
            at = anchor("b3", word, occ) - 0.1 + (0.35 if lab.startswith("50") else 0)
            ra = ease((t-at)/0.35)
            if ra <= 0: continue
            y = 950 + i*95
            g = easeo((t-at)/0.8)
            col = AMBER if v > 450 else CYAN
            d.rounded_rectangle([250, y+10, 250+int(560*v/755*g), y+60], radius=8, fill=(*col, 225))
            sh(d, (90, y+35), lab, BCB(36), OFF, ra, anch="lm")
            sh(d, (990, y+35), counter(0, v, at, 0.8, t, "${:,.0f}"), SMB(40), WHITE, ra, anch="rm")

def s_rent(im, d, t):
    topline(d, t, "THE RENT LINE · OWN vs RENT · 2005 SR22", T0["b4"]+0.15)
    a0 = ease((t-(anchor("b4","rented")-0.2))/0.4)
    if a0 > 0:
        glass(d, [60, 240, 1020, 900], a0, fill=(11,24,36,215), line=DIM)
        # chart: x hours 0..200, y $/h 0..800
        X0, X1, Y0, Y1 = 150, 980, 820, 300
        def px(h): return X0 + (X1-X0)*h/200
        def py(v): return Y0 - (Y0-Y1)*min(v, 800)/800
        d.line([X0, Y0, X1, Y0], fill=(*MUTE, int(200*a0)), width=2)
        d.line([X0, Y0, X0, Y1], fill=(*MUTE, int(200*a0)), width=2)
        for h in (50, 100, 150, 200):
            sh(d, (px(h), Y0+28), str(h), SMR(20), MUTE, a0)
        sh(d, (W/2, Y0+62), "HOURS FLOWN PER YEAR", SMR(20), MUTE, a0)
        for v in (200, 400, 600, 800):
            sh(d, (X0-12, py(v)), f"${v}", SMR(18), MUTE, a0, anch="rm")
        # rent band
        ba = ease((t-(anchor("b4","four")-0.1))/0.5)
        if ba > 0:
            d.rectangle([X0, py(500), X1, py(400)], fill=(*AMBER, int(70*ba)))
            d.line([X0, py(400), X1, py(400)], fill=(*AMBER, int(230*ba)), width=3)
            d.line([X0, py(500), X1, py(500)], fill=(*AMBER, int(230*ba)), width=3)
            sh(d, (X1-10, py(450)), "RENT $400–500/H WET", BCB(30), AMBER, ba, anch="rm")
        # own curve
        g = easeo((t-(anchor("b4","rented")-0.1))/1.4)
        pts = []
        hmax = 8 + 192*g
        h = 18
        while h <= hmax:
            pts.append((px(h), py(14830/h + 161.5))); h += 2
        if len(pts) > 1:
            d.line(pts, fill=(*CYAN, int(240*a0)), width=6)
            sh(d, (pts[-1][0]+10, pts[-1][1]-30), "OWN", BCB(30), CYAN, a0, anch="lm")
        sa = ease((t-(anchor("b4","Shop")-0.1))/0.4)
        chip(d, 330, 290, "SHOP RATES · NOT OUR DATA", BCB(24), sa, fg=MUTE, w_pad=14, h_pad=8)
        ka = ease((t-(anchor("b4","fifty")-0.15))/0.4)
        if ka > 0:
            xk = px(51)
            d.line([xk, Y0, xk, py(600)], fill=(*OFF, int(220*ka)), width=3)
            d.ellipse([xk-14, py(451)-14, xk+14, py(451)+14], fill=(*OFF, int(240*ka)))
            chip(d, xk+40, py(720), "≈ 50 H/YR", BCB(40), ka, w_pad=18, h_pad=10)
            sh(d, (xk-16, py(590)), "RENT WINS", BCB(28), AMBER, ka, anch="rm")
            sh(d, (xk+16, py(590)), "OWN WINS", BCB(28), CYAN, ka, anch="lm")
    # market strip
    ma = ease((t-(anchor("b4","Of")-0.1))/0.4)
    if ma > 0:
        glass(d, [60, 940, 1020, 1400], ma, fill=(11,24,36,215), line=CYAN, lw=3)
        sh(d, (90, 985), "477 CIRRUS SR22 FOR SALE · US · LIFETIME HOURS PER YEAR", SMR(22), MUTE, ma, anch="lm")
        # dot grid 477 dots: 53 x 9
        oa = ease((t-(anchor("b4","one")-0.1))/0.5)
        ha = ease((t-(anchor("b4","half")-0.1))/0.5)
        n_lt60 = 41; n_lt100 = 226
        for i in range(477):
            r, c = divmod(i, 53)
            x = 90 + c*16.6; y = 1020 + r*17
            if i < n_lt60 and oa > 0: col = (*AMBER, int(240*oa))
            elif i < n_lt100 and ha > 0: col = (*CYAN, int(220*ha))
            else: col = (78, 118, 138, int(200*ma))
            d.ellipse([x, y, x+11, y+11], fill=col)
        if oa > 0:
            sh(d, (90, 1230), counter(0, 41, anchor("b4","one")-0.1, 0.7, t) + " UNDER 60 H/YR", BCB(44), AMBER, oa, anch="lm")
            sh(d, (990, 1230), "1 IN 12", BCB(44), AMBER, oa, anch="rm")
        if ha > 0:
            sh(d, (90, 1300), counter(0, 226, anchor("b4","half")-0.1, 0.7, t) + " UNDER 100 H/YR", BCB(44), CYAN, ha, anch="lm")
            sh(d, (990, 1300), "47%", BCB(44), CYAN, ha, anch="rm")
        sh(d, (90, 1360), "MEDIAN 103 H/YR · TTAF ÷ AGE · ASKING, NOT SOLD", SMR(20), DIM, ma, anch="lm")

def s_report(im, d, t):
    topline(d, t, "THE CATCH · THEN THE REPORT", T0["b5"]+0.15)
    a3 = ease((t-(anchor("b5","catch")-0.1))/0.4)
    if a3 > 0:
        glass(d, [80, 240, 1000, 470], a3, line=AMBER, lw=3, fill=(11,24,36,215))
        sh(d, (110, 280), "THE CATCH", SMB(22), AMBER, a3, anch="lm")
        rows = [("ESTIMATES · REGION ADJUSTED · YOUR HANGAR DIFFERS", "Estimates"),
                ("NO INTEREST, NO DEPRECIATION · THE REAL LINE IS HIGHER", "interest"),
                ("HOURS/YR = LIFETIME AVERAGE · NOT THIS SELLER'S", "Hours")]
        for j, (txt, word) in enumerate(rows):
            ra = ease((t-(anchor("b5", word)-0.1))/0.35)
            sh(d, (110, 330+j*45), txt, BCS(28), OFF, ra, anch="lm")
    ca = ease((t-(anchor("b5","Count")-0.1))/0.4)
    chip(d, W/2, 540, "COUNT YOUR REAL HOURS BEFORE YOU BUY", BCB(44), ca, fg=GREEN)
    ga = ease((t-(anchor("b5","NextPlane")-0.3))/0.5)
    if ga > 0:
        glass(d, [80, 620, 1000, 1400], ga, fill=(11, 24, 36, 235))
        lg = Image.open(f"{ROOT}/assets/logo.png").resize((64, 64), Image.LANCZOS)
        if ga > 0.5: im.paste(lg, (120, 655), lg)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (200, 688), "NEXTPLANE REPORT", BCB(44), OFF, ga, anch="lm")
        sh(d, (960, 688), "N2428E", SMB(34), CYAN, ga, anch="rm")
        d.line([120, 740, 960, 740], fill=(*DIM, int(160*ga)), width=2)
        sh(d, (120, 775), "COST OF OWNERSHIP · 2005 CIRRUS SR22-G2 · BEND OR · $325,000", SMR(19), MUTE, ga, anch="lm")
        rows = [("AT THIS AIRPLANE'S 29 H/YR", "$20,978 / YEAR · $723 / HOUR", "INSURANCE · HANGAR · ANNUAL · FUEL · RESERVES", AMBER, anchor("b5","NextPlane")-0.2),
                ("AT 100 H/YR", "$32,747 / YEAR · $327 / HOUR", "SAME AIRPLANE · SAME HANGAR · OREGON RATES", CYAN, anchor("b5","every")-0.1),
                ("RENT LINE", "≈ 50 HOURS A YEAR", "BELOW IT, RENTING IS THE CHEAPER SR22", AMBER, anchor("b5","tail")-0.2)]
        for j, (lab, val, sub, cc, at) in enumerate(rows):
            ra = ease((t-at)/0.4)
            if ra <= 0: continue
            y = 810 + j*180
            d.rounded_rectangle([120, y, 960, y+160], radius=16, fill=(18, 36, 52, int(220*ra)), outline=(*cc, int(200*ra)), width=2)
            sh(d, (150, y+38), lab, SMR(20), MUTE, ra, anch="lm")
            sh(d, (150, y+82), val, BCB(36), OFF, ra, anch="lm")
            sh(d, (150, y+128), sub, SMR(21), cc, ra, anch="lm")
    d = ImageDraw.Draw(im, "RGBA")
    ca2 = ease((t-(anchor("b5","tail")-0.1))/0.4)
    chip(d, W/2, 1470, "EVERY LISTING · ANY TAIL NUMBER", BCB(42), ca2)

def s_end(im, d, t):
    return draw_endcard(im, t - T0["b6"], FD, f"{ROOT}/assets/logo.png")

def end_bg():
    k = "endbg"
    if k not in _ph:
        im = bg_grad((15, 32, 48), (11, 24, 38))
        gl = Image.new("L", (W//4, H//4), 0)
        dg = ImageDraw.Draw(gl)
        dg.ellipse([W//8-160, 100, W//8+160, 420], fill=70)
        gl = gl.filter(ImageFilter.GaussianBlur(60)).resize((W, H))
        cy = Image.new("RGB", (W, H), (24, 60, 70))
        _ph[k] = Image.composite(cy, im, gl)
    return _ph[k].copy()

SCENE_FN = {"b1": s_hook, "b2": s_reveal, "b3": s_why, "b4": s_rent, "b5": s_report, "b6": s_end}

def frame(i):
    t = i / FPS
    name, t0, t1 = next(s for s in SC if s[1] <= t < s[2] or s is SC[-1] and t >= s[1])
    p = (t - t0) / max(t1 - t0, 0.01)
    if name == "b1":
        im = bg_photo("sr22_g2b", p, zoom0=1.0, zoom1=1.12, dark=0.40, tint=0.58)
    elif name == "b2":
        im = bg_photo("sr22_ramp", p, zoom0=1.12, zoom1=1.0, dark=0.42, tint=0.58)
    elif name == "b3":
        im = bg_photo("sr22_cockpit", p, dark=0.36, tint=0.64)
    elif name == "b4":
        im = bg_photo("sr22_chicago", p, zoom0=1.0, zoom1=1.10, dark=0.34, tint=0.66)
    elif name == "b5":
        im = bg_photo("sr22_n68gt", p, dark=0.32, tint=0.70)
    else:
        im = end_bg()
    if name not in ("b5", "b6"):
        im = vignette(im)
    d = ImageDraw.Draw(im, "RGBA")
    SCENE_FN[name](im, d, t)
    d = ImageDraw.Draw(im, "RGBA")
    if name != "b6":
        draw_captions(d, t)
    return im

if __name__ == "__main__":
    a, b = int(sys.argv[1]), min(int(sys.argv[2]), NF)
    step = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    os.makedirs(f"{ROOT}/frames", exist_ok=True)
    if a == 0 and step == 1:
        print(f"TOTAL {TOTAL:.2f}s NF={NF}")
        print(json.dumps({k: round(v,2) for k,v in OFFS.items()}))
    n = 0
    for i in range(a, b, step):
        fn = f"{ROOT}/frames/f{i:05d}.jpg"
        if os.path.exists(fn): continue
        tmp = fn + f".{os.getpid()}.tmp"
        frame(i).save(tmp, quality=91, format="JPEG"); os.replace(tmp, fn)
        n += 1
    print(f"rendered {n} frames [{a},{b}) step {step}")
