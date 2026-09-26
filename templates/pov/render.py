#!/usr/bin/env python3
"""NextPlane "Six-Seat Tax" POV-BUYER Short renderer. Usage: render_six.py <start> <end> [step]
Writes /tmp/six/frames/f%05d.jpg (1080x1920@30). Resumable; step lets N procs interleave."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, "/tmp/six")
from endcard import draw_endcard

ROOT = "/tmp/six"
W, H, FPS = 1080, 1920, 30
NAVY = (10, 22, 34); NAVY2 = (16, 34, 52); INK = (13, 27, 38)
CYAN = (37, 197, 203); OFF = (246, 249, 250); WHITE = (255, 255, 255)
MUTE = (128, 148, 162); AMBER = (245, 166, 35); DIM = (70, 92, 108); GREEN = (86, 214, 140); RED = (232, 96, 88)
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

BEATS = ["b1","b2","b3","b4","b5","b6","b7","b8"]
VO = {b: json.load(open(f"{ROOT}/vo/{b}.json")) for b in BEATS}
OFFS = {}
t = 0.4; GAP = 0.25
for b in BEATS:
    OFFS[b] = t; t += VO[b]["dur"] + GAP + (0.3 if b == "b1" else 0)
TOTAL = OFFS["b8"] + VO["b8"]["dur"] + 1.6
NF = int(TOTAL * FPS)

def wt(b, idx): w = VO[b]["words"][idx]; return OFFS[b] + w["s"]
def anchor(b, text, occ=1):
    n = 0
    for i, w in enumerate(VO[b]["words"]):
        if w["w"].strip(".,?!:;'’").lower() == text.lower():
            n += 1
            if n == occ: return wt(b, i)
    raise KeyError(f"{b}:{text}:{occ}")

SC = []
edges = [0.0]
for b in BEATS[1:]: edges.append(OFFS[b] - GAP/2)
edges.append(TOTAL)
for i, b in enumerate(BEATS): SC.append((b, edges[i], edges[i+1]))

_ph = {}
def photo(slug, dark=0.42, tint=0.55):
    k = (slug, dark, tint)
    if k in _ph: return _ph[k]
    cache = f"{ROOT}/assets/bg_{slug}_{int(dark*100)}_{int(tint*100)}.jpg"
    if os.path.exists(cache):
        _ph[k] = Image.open(cache).convert("RGB"); return _ph[k]
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
    im.save(cache, quality=90)
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
    tmp = Image.new("RGBA", (1000, 200), (0,0,0,0))
    td = ImageDraw.Draw(tmp)
    tw = td.textlength(txt, font=f)
    box = [500-tw/2-28, 20, 500+tw/2+28, 180]
    td.rounded_rectangle(box, radius=14, outline=(*color, 255), width=6)
    td.text((500, 100), txt, font=f, fill=(*color, 255), anchor="mm")
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
    sh(d, (W/2, 150), txt, SMB(34), MUTE, a)
    if a > 0:
        lw = int(300*a)
        d.rectangle([W/2-lw/2, 190, W/2+lw/2, 193], fill=(*CYAN, int(160*a)))

def line_tag(d, t, n, txt, t0):
    """Teardown 'LINE n' ribbon under the topline."""
    a = ease((t - t0)/0.35)
    if a <= 0: return
    f = BCB(40); s = f"LINE {n}  ·  {txt}"
    tw = d.textlength(s, font=f)
    d.rounded_rectangle([W/2-tw/2-30, 215, W/2+tw/2+30, 282], radius=12, fill=(*CYAN, int(235*a)))
    sh(d, (W/2, 248), s, f, (5,12,18), a, shad=0)

def hbar(d, y, x0, x1, v, vmax, at, t, col, txt, f=None, lab=None):
    """horizontal bar growing from x0"""
    a = ease((t-at)/0.4)
    if a <= 0: return
    g = easeo((t-at)/0.8)
    bw = int((x1-x0)*(v/vmax)*g)
    d.rounded_rectangle([x0, y-30, x0+max(bw, 8), y+30], radius=9, fill=(*col, int(235*a)))
    f = f or SMB(34)
    vt = counter(0, v, at, 0.8, t, txt) if "{" in txt else txt
    inside = bw > 300
    sh(d, (x0+14 if inside else x0+max(bw,8)+16, y), vt, f, (5,12,18) if inside else OFF, a, anch="lm", shad=0 if inside else 2)

def pov_tag(d, t, txt, t0, y=150):
    """POV ribbon: 'YOU ...' second-person header"""
    a = ease((t - t0)/0.35)
    if a <= 0: return
    f = BCB(40); tw = d.textlength(txt, font=f)
    d.rounded_rectangle([W/2-tw/2-30, y-34, W/2+tw/2+30, y+34], radius=12, fill=(*CYAN, int(235*a)))
    sh(d, (W/2, y), txt, f, (5,12,18), a, shad=0)

def ad_card(im, d, box, a, title, lines, price=None, badge=None, badge_col=CYAN):
    if a <= 0: return
    x0, y0, x1, y1 = box
    glass(d, box, a, fill=(246,249,250,228), line=(200,210,218), lw=2, r=16)
    sh(d, (x0+36, y0+46), title, BCB(40), (13,27,38), a, anch="lm", shad=0)
    y = y0+100
    for ln in lines:
        sh(d, (x0+36, y), ln, BCS(31), (60,78,92), a, anch="lm", shad=0); y += 42
    if price: sh(d, (x1-36, y0+46), price, SMB(38), (13,27,38), a, anch="rm", shad=0)
    if badge:
        f = BCB(30); tw = d.textlength(badge, font=f)
        d.rounded_rectangle([x1-36-tw-28, y1-70, x1-36, y1-22], radius=10, fill=(*badge_col, int(240*a)))
        sh(d, (x1-36-tw/2-14, y1-46), badge, f, (5,12,18) if badge_col != RED else OFF, a, shad=0)


# ---------- data (six_seat_tax_DATA_PACK.md, verified 2026-09-18) ----------
L4 = [("sr22c","CIRRUS SR22", 2006, "SR22"), ("skylane","CESSNA 182 SKYLANE", 1998, "Skylane"), ("mooney","MOONEY M20", 2000, "Mooney")]
L6 = [("bonanza","BEECH A36 BONANZA", 1978, "Bonanza"), ("c210","CESSNA 210 CENTURION", 1978, "Centurion"), ("c206b","CESSNA 206 STATIONAIR", 1977, "Stationair"), ("saratoga","PIPER SARATOGA", 1984, "Saratoga")]

def yearbar(d, y, x0, x1, yr, at, t, col, lab_f=None):
    a = ease((t-at)/0.4)
    if a <= 0: return
    g = easeo((t-at)/0.8)
    lo, hi = 1970, 2012
    bw = int((x1-x0)*((yr-lo)/(hi-lo))*g)
    d.rounded_rectangle([x0, y-26, x0+max(bw, 8), y+26], radius=8, fill=(*col, int(235*a)))
    v = int(lo + (yr-lo)*g)
    sh(d, (x0+max(bw,8)+16, y), str(v), lab_f or SMB(40), OFF, a, anch="lm")

def tile(d, box, lab, val, sub, at, t, col, big=150, vfmt=None, v0=0):
    a = ease((t-at)/0.4)
    if a <= 0: return
    x0, y0, x1, y1 = box
    glass(d, box, a, fill=(11,24,36,228), line=col)
    cx = (x0+x1)//2
    sh(d, (cx, y0+56), lab, SMB(28), MUTE, a)
    txt = counter(v0, val, at, 0.9, t, vfmt) if vfmt else val
    sh(d, (cx, (y0+y1)//2+10), txt, BCB(big), col, a)
    if sub: sh(d, (cx, y1-56), sub, SMB(24), OFF, a)

def s_hook(im, d, t):
    t0 = SC[0][1]
    pov_tag(d, t, "POV · YOU'RE BUYING A PISTON SINGLE", t0+0.1)
    ya = ease((t-(anchor("b1","three")-0.15))/0.4)
    if ya > 0:
        sh(d, (W/2, 290), "YOU HAVE", SMB(34), MUTE, ya)
        sh(d, (W/2, 390), counter(0, 300000, anchor("b1","three")-0.15, 0.9, t, "${:,.0f}"), BCB(150), OFF, ya)
    fa = anchor("b1","Four")-0.1; sa = anchor("b1","Six")-0.1
    tile(d, [70, 540, 530, 900], "4 SEATS · BUILD YEAR", 2004, "MEDIAN OF 268 ADS", fa, t, CYAN, big=140, vfmt="{:.0f}", v0=1960)
    tile(d, [550, 540, 1010, 900], "6 SEATS · BUILD YEAR", 1979, "MEDIAN OF 142 ADS", sa, t, AMBER, big=140, vfmt="{:.0f}", v0=2010)
    ta = anchor("b1","Two",2)-0.1
    a = ease((t-ta)/0.45)
    if a > 0:
        y0 = int(960 + (1-a)*50)
        glass(d, [70, y0, 1010, y0+330], a, fill=(11,24,36,232))
        sh(d, (W/2, y0+64), "TWO MORE SEATS COST YOU", SMB(30), MUTE, a)
        sh(d, (W/2, y0+180), counter(0, 25, ta, 0.9, t, "{:.0f} YEARS"), BCB(150), CYAN, a)
        sh(d, (W/2, y0+290), "SAME $250K–$350K BUDGET · US PISTON SINGLES", SMB(24), OFF, a)

def s_ladder(im, d, t):
    t0 = SC[1][1]
    topline(d, t, "SAME MONEY · MEDIAN BUILD YEAR BY FAMILY", t0+0.15)
    pa = ease((t-(t0+0.5))/0.4)
    if pa > 0: chip(d, W/2, 258, "$250K–$350K ASKS · DEDUPED BY TAIL · US ONLY", BCS(27), pa)
    y = 400
    ha = ease((t-(anchor("b2","Cirrus")-0.3))/0.35)
    if ha > 0: sh(d, (70, y-108), "4 SEATS", BCB(36), CYAN, ha, anch="lm")
    for slug, lab, yr, key in L4:
        at = anchor("b2", key) - 0.15
        a = ease((t-at)/0.4)
        if a > 0:
            paste_thumb(im, slug, (70, y-72, 270, y+72), a)
            d = ImageDraw.Draw(im, "RGBA")
            sh(d, (300, y-42), lab, BCB(34), OFF, a, anch="lm")
            yearbar(d, y+22, 300, 900, yr, at, t, CYAN)
        y += 170
    y += 50
    ha6 = ease((t-(anchor("b2","Now")-0.1))/0.35)
    if ha6 > 0: sh(d, (70, y-108), "6 SEATS", BCB(36), AMBER, ha6, anch="lm")
    for slug, lab, yr, key in L6:
        at = anchor("b2", key) - 0.15
        a = ease((t-at)/0.4)
        if a > 0:
            paste_thumb(im, slug, (70, y-72, 270, y+72), a)
            d = ImageDraw.Draw(im, "RGBA")
            sh(d, (300, y-42), lab, BCB(34), OFF, a, anch="lm")
            yearbar(d, y+22, 300, 900, yr, at, t, AMBER)
        y += 170

def s_engine(im, d, t):
    t0 = SC[2][1]
    topline(d, t, "HOURS ON THE AIRFRAME · HOURS ON THE ENGINE", t0+0.15)
    a4 = anchor("b3","twenty")-0.15; a6 = anchor("b3","forty")-0.15
    y = 330
    a = ease((t-a4)/0.4)
    if a > 0:
        sh(d, (70, y-50), "4 SEATS · MEDIAN AIRFRAME HOURS", SMB(26), MUTE, a, anch="lm")
        hbar(d, y+10, 70, 1010, 2204, 5000, a4, t, CYAN, "{:,.0f} H", f=SMB(40))
    a = ease((t-a6)/0.4)
    if a > 0:
        sh(d, (70, y+120), "6 SEATS · MEDIAN AIRFRAME HOURS", SMB(26), MUTE, a, anch="lm")
        hbar(d, y+180, 70, 1010, 4392, 5000, a6, t, AMBER, "{:,.0f} H", f=SMB(40))
    ea = ease((t-(anchor("b3","engines")-0.2))/0.4)
    if ea > 0: sh(d, (W/2, 640), "BUT THE ENGINES · MEDIAN HOURS SINCE OVERHAUL", SMB(28), OFF, ea)
    tile(d, [70, 700, 370, 1000], "BONANZA A36", 714, "6 SEATS", anchor("b3","Bonanza")-0.15, t, AMBER, big=110, vfmt="{:.0f}")
    tile(d, [390, 700, 690, 1000], "CENTURION", 468, "6 SEATS", anchor("b3","Centurion")-0.15, t, AMBER, big=110, vfmt="{:.0f}")
    tile(d, [710, 700, 1010, 1000], "CIRRUS SR22", 1207, "4 SEATS", anchor("b3","Cirrus")-0.15, t, CYAN, big=110, vfmt="{:,.0f}")
    ca = ease((t-(anchor("b3","engine")-0.15))/0.4)
    if ca > 0:
        chip(d, W/2, 1110, "THE MONEY WENT INTO THE ENGINE + PANEL", BCB(44), ca)
        na = ease((t-(anchor("b3","calendar")-0.2))/0.35)
        if na > 0: chip(d, W/2, 1215, "NOT THE CALENDAR", BCB(44), na, fg=AMBER)

def s_era(im, d, t):
    t0 = SC[3][1]
    topline(d, t, "SIX SEATS AT THE SAME BUILD YEAR", t0+0.15)
    ba = ease((t-(anchor("b4","build")-0.2))/0.4)
    if ba > 0: chip(d, W/2, 265, "BUILT 2004–2008 · MEDIAN ASK", BCS(30), ba)
    tile(d, [70, 330, 530, 690], "4 SEATS · n=245", 339900, "MEDIAN ASK", anchor("b4","build")-0.1, t, CYAN, big=96, vfmt="${:,.0f}")
    tile(d, [550, 330, 1010, 690], "6 SEATS · n=70", 558500, "MEDIAN ASK", anchor("b4","five")-0.15, t, AMBER, big=96, vfmt="${:,.0f}")
    ga = anchor("b4","Two")-0.1
    a = ease((t-ga)/0.45)
    if a > 0:
        y0 = int(760 + (1-a)*50)
        glass(d, [70, y0, 1010, y0+375], a, fill=(11,24,36,232))
        sh(d, (W/2, y0+64), "TWO MORE SEATS, SAME ERA", SMB(30), MUTE, a)
        sh(d, (W/2, y0+180), "+" + counter(0, 218600, ga, 1.0, t, "${:,.0f}"), BCB(150), AMBER, a)
        sh(d, (W/2, y0+292), "+64% · SR22 $339,900 vs BONANZA A36 $649,000", SMB(24), OFF, a)
        sh(d, (W/2, y0+330), "SKYLANE $359,950 vs STATIONAIR $441,500", SMB(24), OFF, a)

def s_twist(im, d, t):
    t0 = SC[4][1]
    topline(d, t, "THE TWIST · WHICH ONE LEAVES THE MARKET?", t0+0.15)
    tile(d, [70, 300, 530, 700], "6 SEATS · 1979 MEDIAN", 57.7, "LEFT THE MARKET", anchor("b5","Fifty")-0.15, t, AMBER, big=150, vfmt="{:.0f}%")
    tile(d, [550, 300, 1010, 700], "4 SEATS · 2004 MEDIAN", 45.9, "LEFT THE MARKET", anchor("b5","forty")-0.15, t, CYAN, big=150, vfmt="{:.0f}%")
    fa = ease((t-(anchor("b5","newer")-0.1))/0.4)
    if fa > 0:
        glass(d, [70, 780, 1010, 900], fa, fill=(11,24,36,225))
        sh(d, (W/2, 840), "142 SIX-SEAT ADS vs 268 FOUR-SEAT ADS · $250K–$350K", SMB(26), OFF, fa)
        sh(d, (W/2, 960), "GONE = DELISTED, NOT CONFIRMED SOLD · ASKING PRICES", SMR(24), MUTE, fa)

def s_cards(im, d, t):
    t0 = SC[5][1]
    topline(d, t, "TWO REAL AIRPLANES · SAME MONEY", t0+0.15)
    a1 = ease((t-(anchor("b6","A",1)-0.1))/0.4)
    if a1 > 0:
        y0 = 290
        ad_card(im, d, [70, y0, 1010, y0+330], a1, "N978SR · 2007 CIRRUS SR22-G3",
                ["1,854 H · ENGINE 1,854 SINCE NEW", "AVIDYNE ENTEGRA · DUAL GNS 430W", "4 SEATS · DEALER, OHIO"], price="$299,000", badge="4 SEATS")
        st = ease((t-(anchor("b6","nine",1)-0.1))/0.4)
        stamp(im, 760, y0+150, "STILL LISTED", (70,92,108), st, size=46)
    a2 = ease((t-(anchor("b6","A",2)-0.1))/0.4)
    if a2 > 0:
        y0 = 690
        d = ImageDraw.Draw(im, "RGBA")
        ad_card(im, d, [70, y0, 1010, y0+330], a2, "N23682 · 1978 BEECH A36 BONANZA",
                ["5,551 H · 714 SINCE OVERHAUL", "GARMIN GTN 750 · GFC 500 · G5s (2023)", "6 SEATS · DEALER, CALIFORNIA"], price="$299,950", badge="6 SEATS", badge_col=AMBER)
        st2 = ease((t-(anchor("b6","fifty",2)-0.1))/0.4)
        stamp(im, 760, y0+150, "STILL LISTED", (70,92,108), st2, size=46)
    fa = ease((t-(anchor("b6","Both")-0.1))/0.4)
    if fa > 0:
        d = ImageDraw.Draw(im, "RGBA")
        glass(d, [70, 1070, 1010, 1190], fa, fill=(11,24,36,228), line=CYAN)
        sh(d, (W/2, 1130), "$950 APART · 29 YEARS APART · 2 SEATS APART", BCB(40), OFF, fa)

def s_report(im, d, t):
    t0 = SC[6][1]
    topline(d, t, "THE CATCH · AND WHAT THE REPORT SHOWS", t0+0.15)
    chips = [("ASKING PRICES, NOT SALES · GONE IS NOT CONFIRMED SOLD", anchor("b7","Asking")-0.2, MUTE),
             ("SIX SEATS ON THE PLACARD IS NOT SIX ADULTS WITH BAGS", anchor("b7","placard")-0.3, AMBER)]
    y = 250
    for s, at, col in chips:
        a = ease((t-at)/0.4)
        if a > 0:
            glass(d, [80, y, 1000, y+86], a, r=20, fill=(13,27,38,180), line=col if col != MUTE else DIM)
            sh(d, (120, y+43), s, BCS(33), col if col != MUTE else (200,210,218), a, anch="lm")
        y += 104
    ra = ease((t-(anchor("b7","NextPlane")-0.3))/0.5)
    if ra > 0:
        y0 = int(480 + (1-ra)*60)
        glass(d, [80, y0, 1000, y0+840], ra, fill=(11, 24, 36, 235))
        lg = Image.open(f"{ROOT}/assets/logo.png").resize((64, 64), Image.LANCZOS)
        if ra > 0.5: im.paste(lg, (120, y0+30), lg)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (200, y0+62), "NEXTPLANE REPORT", BCB(44), OFF, ra, anch="lm")
        sh(d, (960, y0+62), "N23682", SMB(34), CYAN, ra, anch="rm")
        d.line([120, y0+112, 960, y0+112], fill=(*DIM, int(160*ra)), width=2)
        rows = [("AIRCRAFT", "1978 BEECH A36 BONANZA · 6 SEATS"),
                ("HOURS", "5,551 H AIRFRAME · 714 H SINCE OVERHAUL"),
                ("PEER SET", "59 A36s · $250K–$350K · MEDIAN 1978 · 4,780 H"),
                ("USEFUL LOAD", "CHECK THE WEIGHT & BALANCE, NOT THE SEAT COUNT"),
                ("SAME-MONEY 4-SEATER", "2004 MEDIAN · 2,205 H · 1,207 H SMOH"),
                ("THIS ASK", "$299,950  ·  AT THE A36 PEER MEDIAN")]
        yy = y0 + 160
        for k, v in rows:
            sh(d, (120, yy), k, SMR(22), MUTE, ra, anch="lm")
            sh(d, (120, yy+44), v, BCB(34), AMBER if k == "USEFUL LOAD" else (CYAN if k.startswith("THIS") else OFF), ra, anch="lm")
            yy += 100
        ha = ease((t-(anchor("b7","every")-0.2))/0.4)
        chip(d, W/2, y0+785, "PEERS · HOURS · ENGINE, ON EVERY LISTING", BCB(40), ha)

def s_end(im, d, t):
    t0 = SC[7][1]
    return draw_endcard(im, t - t0, FD, f"{ROOT}/assets/logo.png")

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

SCENE_FN = {"b1": s_hook, "b2": s_ladder, "b3": s_engine, "b4": s_era, "b5": s_twist, "b6": s_cards, "b7": s_report, "b8": s_end}
BG = {"b1": ("bonanza", 1.0, 1.12, 0.40, 0.58), "b2": ("c210b", 1.12, 1.0, 0.34, 0.66), "b3": ("cabin", 1.0, 1.1, 0.36, 0.64),
      "b4": ("c206b", 1.1, 1.0, 0.38, 0.62), "b5": ("saratoga", 1.12, 1.0, 0.34, 0.66), "b6": ("sr22c", 1.0, 1.1, 0.36, 0.64), "b7": ("bonanza2", 1.0, 1.1, 0.32, 0.70)}

def frame(i):
    t = i / FPS
    name, t0, t1 = next(s for s in SC if s[1] <= t < s[2] or s is SC[-1] and t >= s[1])
    p = (t - t0) / max(t1 - t0, 0.01)
    if name == "b8":
        im = end_bg()
    else:
        slug, z0, z1, dk, tn = BG[name]
        im = bg_photo(slug, p, zoom0=z0, zoom1=z1, dark=dk, tint=tn)
    if name not in ("b7", "b8"):
        im = vignette(im)
    d = ImageDraw.Draw(im, "RGBA")
    SCENE_FN[name](im, d, t)
    d = ImageDraw.Draw(im, "RGBA")
    if name != "b8":
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
        frame(i).save(fn, quality=91)
        n += 1
    print(f"rendered {n} frames [{a},{b}) step {step}")
