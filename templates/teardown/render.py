#!/usr/bin/env python3
"""NextPlane "New Paint" AD TEARDOWN Short renderer. Usage: render_np.py <start> <end> [step]
Writes /tmp/np/frames/f%05d.jpg (1080x1920@30). Resumable; step lets N procs interleave."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, "/tmp/np")
from endcard import draw_endcard

ROOT = "/tmp/np"
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
    return 1e9  # miss-safe: trimmed words simply never trigger their overlay

SC = []
edges = [0.0]
for b in BEATS[1:]: edges.append(OFFS[b] - GAP/2)
edges.append(TOTAL)
for i, b in enumerate(BEATS): SC.append((b, edges[i], edges[i+1]))
T0 = {b: e0 for b, e0, e1 in SC}

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
    hh = max(size*0.95, 40); box = [500-tw/2-28, 100-hh, 500+tw/2+28, 100+hh]
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

# ---------- data (new_paint_DATA_PACK.md) ----------
def ad_card(im, d, box, a, lines, hl=("NEW", "PAINT"), size=38, lh=56, hlcol=CYAN):
    """listing-text card with highlighted words"""
    if a <= 0: return
    x0, y0, x1, y1 = box
    glass(d, box, a, fill=(246,249,250,225), line=(200,210,218), lw=2, r=16)
    f = BCS(size); y = y0+50
    for ln in lines:
        x = x0+40
        for w in ln.split(" "):
            ww = d.textlength(w+" ", font=f)
            if w.strip(".,!\":;").upper() in hl:
                d.rounded_rectangle([x-6, y-size*0.62, x+ww-4, y+size*0.62], radius=6, fill=(*hlcol, int(230*a)))
                d.text((x, y), w, font=f, fill=(5,12,18,int(255*a)), anchor="lm")
            else:
                d.text((x, y), w, font=f, fill=(30,45,58,int(255*a)), anchor="lm")
            x += ww
        y += lh

# ---------- scenes ----------
def s_hook(im, d, t):
    topline(d, t, "NEXTPLANE · AD TEARDOWN", 0.3)
    a0 = ease((t-(anchor("b1","The")-0.1))/0.4)
    ad_card(im, d, [70, 250, 1010, 560], a0, ["1979 CESSNA 182Q SKYLANE II · $229,900", "\"boasts a NEW PAINT job, wonderfully", "upgraded avionics panel, generous useful", "load, and numerous other upgrades\""])
    d = ImageDraw.Draw(im, "RGBA")
    a1 = ease((t-(anchor("b1","seller")-0.1))/0.4)
    if a1 > 0:
        glass(d, [70, 600, 1010, 880], a1, fill=(11,24,36,215), line=DIM)
        paste_thumb(im, "booth", (95, 625, 375, 855), a1)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (410, 660), "THE SELLER PAID", BCB(40), OFF, a1, anch="lm")
        sh(d, (410, 705), "STRIP & REPAINT, PISTON SINGLE, 2026", SMR(18), MUTE, a1, anch="lm")
        ca = ease((t-(anchor("b1","twenty")-0.1))/0.4)
        sh(d, (410, 790), counter(0, 20000, anchor("b1","twenty")-0.05, 0.7, t, "${:,.0f}") + counter(0, 30000, anchor("b1","thirty")-0.05, 0.6, t, " – ${:,.0f}"), SMB(60), WHITE, ca, anch="lm")
        sh(d, (410, 850), "SHOP QUOTES · NOT OUR DATA", BCB(24), MUTE, ca, anch="lm")
    a2 = ease((t-(anchor("b1","asking")-0.1))/0.4)
    if a2 > 0:
        glass(d, [70, 920, 1010, 1200], a2, fill=(11,24,36,215), line=CYAN, lw=3)
        paste_thumb(im, "q182", (95, 945, 375, 1175), a2)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (410, 980), "THE ASKING PRICE CARRIES", BCB(40), OFF, a2, anch="lm")
        sh(d, (410, 1025), "VS SAME MODEL, SAME VINTAGE, NOTHING NEW", SMR(18), MUTE, a2, anch="lm")
        na = ease((t-(anchor("b1","nine")-0.1))/0.4)
        sh(d, (410, 1110), counter(0, 9000, anchor("b1","nine")-0.05, 0.8, t, "+${:,.0f}"), SMB(84), CYAN, na, anch="lm")
        sh(d, (410, 1170), "MEDIAN · 39 ADS · +5.2%", BCB(24), CYAN, na, anch="lm")
    oa = ease((t-(anchor("b1","nine")+0.7))/0.35)
    stamp(im, W/2, 1320, "ABOUT A THIRD OF THE BILL", CYAN, oa, size=52, angle=-5)
    d = ImageDraw.Draw(im, "RGBA")
    sh(d, (W/2, 1420), "US LISTINGS · 3,442 COMPARABLE PISTON ADS · 143 MENTION PAINT", SMR(18), DIM, oa)

def s_words(im, d, t):
    t0 = T0['b2']
    topline(d, t, "WHAT THE WORDS ADD TO THE ASK", t0+0.15)
    line_tag(d, t, 1, "THE WORDS", anchor("b2","Line")-0.1)
    ga = ease((t-(anchor("b2","thirty")-0.1))/0.4)
    if ga > 0:
        glass(d, [60, 320, 1020, 660], ga, fill=(11,24,36,205), line=DIM)
        sh(d, (110, 370), "COMPARABLE US PISTON ADS · SAME MODEL, ±3 YEARS, ≥5 PEERS", SMR(18), MUTE, ga, anch="lm")
        sh(d, (110, 450), counter(0, 3442, anchor("b2","thirty")-0.05, 0.9, t, "{:,.0f}"), SMB(72), WHITE, ga, anch="lm")
        # grid of dots: 100 dots, 4.2% cyan
        ha = ease((t-(anchor("b2","hundred",2)-0.1))/0.4)
        pa = easeo((t-(anchor("b2","hundred",2)-0.05))/0.8)
        for i in range(50):
            cx = 120 + (i % 25)*36; cy = 575 + (i // 25)*42
            col = CYAN if i < 2 and pa > i/2 else DIM
            d.ellipse([cx-11, cy-11, cx+11, cy+11], fill=(*col, int(230*ga)))
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (970, 450), counter(0, 143, anchor("b2","hundred",2)-0.05, 0.8, t, "{:,.0f}"), SMB(72), CYAN, ha, anch="rm")
        sh(d, (970, 510), "MENTION PAINT · 1 IN 24", BCB(26), CYAN, ha, anch="rm")
        sh(d, (970, 543), "DEDUPED BY N-NUMBER · SHARES EXCLUDED", SMR(16), DIM, ha, anch="rm")
    fa = ease((t-(anchor("b2","Fresh")-0.1))/0.4)
    if fa > 0:
        glass(d, [60, 700, 1020, 1180], fa, fill=(11,24,36,215), line=CYAN, lw=3)
        sh(d, (110, 755), "FRESH PAINT · NOTHING ELSE NEW", BCB(38), OFF, fa, anch="lm")
        sh(d, (110, 800), "39 ADS · NO NEW PANEL, NO FRESH ENGINE, NO NEW INTERIOR", SMR(17), MUTE, fa, anch="lm")
        va = ease((t-(anchor("b2","same")-0.1))/0.4)
        sh(d, (110, 870), "SAME MODEL · SAME VINTAGE · NOTHING NEW", BCB(30), MUTE, va, anch="lm")
        hbar(d, 925, 110, 970, 100, 118, anchor("b2","same")-0.05, t, (95,135,155), "PEER MEDIAN ASK", SMB(26))
        pa2 = ease((t-(anchor("b2","plus")-0.1))/0.4)
        sh(d, (110, 1000), "FRESH-PAINT AD", BCB(30), OFF, pa2, anch="lm")
        hbar(d, 1055, 110, 970, 105.2, 118, anchor("b2","plus")-0.05, t, CYAN, "+5.2%", SMB(26))
        sh(d, (970, 1135), counter(0, 9000, anchor("b2","plus")-0.05, 0.9, t, "+${:,.0f}"), SMB(64), WHITE, pa2, anch="rm")
        sh(d, (110, 1135), "MEDIAN GAP", SMR(20), MUTE, pa2, anch="lm")
    ca = ease((t-(anchor("b2","About")-0.1))/0.4)
    chip(d, W/2, 1265, "+$9,000 FOR TWO WORDS", BCB(50), ca)
    sh(d, (W/2, 1350), "HONESTY CONTROL: PAINT ADS HAVE +277 H AIRFRAME, +44 H SMOH VS PEERS — NOT HIDDEN HOURS", SMR(15), DIM, ca)

def s_bill(im, d, t):
    t0 = T0['b3']
    topline(d, t, "WHO PAID FOR THE PAINT?", t0+0.15)
    line_tag(d, t, 2, "THE BILL", anchor("b3","Line")-0.1)
    ga = ease((t-(anchor("b3","strip")-0.1))/0.4)
    if ga > 0:
        glass(d, [60, 320, 1020, 700], ga, fill=(11,24,36,215), line=DIM)
        paste_thumb(im, "booth", (85, 345, 385, 675), ga)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (420, 380), "STRIP & REPAINT", BCB(40), OFF, ga, anch="lm")
        sh(d, (420, 425), "PISTON SINGLE · 2026 SHOP QUOTES", SMR(18), MUTE, ga, anch="lm")
        va = ease((t-(anchor("b3","twenty")-0.1))/0.4)
        sh(d, (420, 510), counter(0, 20, anchor("b3","twenty")-0.05, 0.6, t, "${:,.0f}K") + counter(0, 30, anchor("b3","thirty")-0.05, 0.5, t, " – ${:,.0f}K"), SMB(64), WHITE, va, anch="lm")
        sh(d, (420, 580), "~25 WORKING DAYS IN THE SHOP", BCB(26), MUTE, va, anch="lm")
        qa = ease((t-(anchor("b3","Shop")-0.1))/0.3)
        sh(d, (420, 640), "SHOP QUOTES · NOT OUR DATA", BCB(26), CYAN, qa, anch="lm")
    ra = ease((t-(anchor("b3","recovers")-0.2))/0.4)
    if ra > 0:
        glass(d, [60, 740, 1020, 1120], ra, fill=(11,24,36,215), line=CYAN, lw=3)
        sh(d, (110, 795), "A $25,000 PAINT JOB, AT ASKING", BCB(36), OFF, ra, anch="lm")
        g = easeo((t-(anchor("b3","recovers")-0.1))/1.0)
        x0, x1, y = 110, 970, 880
        d.rounded_rectangle([x0, y-34, x1, y+34], radius=10, fill=(*DIM, int(120*ra)))
        w9 = int((x1-x0)*(9000/25000)*g)
        d.rounded_rectangle([x0, y-34, x0+max(w9,8), y+34], radius=10, fill=(*CYAN, int(240*ra)))
        sh(d, (x0+16, y), "SELLER RECOVERS  " + counter(0, 9000, anchor("b3","recovers")-0.1, 1.0, t, "${:,.0f}"), SMB(24), (5,12,18), ra, anch="lm", shad=0)
        ea = ease((t-(anchor("b3","third")-0.1))/0.4)
        sh(d, (x1-16, y), "SELLER EATS ≈ $16,000", SMB(22), OFF, ea, anch="rm", shad=1)
        ya = ease((t-(anchor("b3","You")-0.1))/0.4)
        sh(d, (110, 980), "YOU GET THE PAINT FOR", BCB(36), OFF, ya, anch="lm")
        sh(d, (970, 980), "≈ 1/3 OF THE SHOP PRICE", BCB(36), CYAN, ya, anch="rm")
        sh(d, (110, 1050), "A DEALER'S PAINT JOB IS THE CHEAPEST PAINT JOB YOU'LL EVER BUY", SMR(18), MUTE, ease((t-(anchor("b3","price")-0.1))/0.4), anch="lm")
    ca = ease((t-(anchor("b3","third",2)-0.1))/0.4)
    chip(d, W/2, 1230, "≈ ONE THIRD", BCB(56), ca)
    sh(d, (W/2, 1330), "ASKING PRICES · MEDIAN GAP OF 39 FRESH-PAINT-ONLY ADS VS NO-UPGRADE PEERS", SMR(15), DIM, ca)

def s_sell(im, d, t):
    t0 = T0['b4']
    topline(d, t, "SELL-THROUGH · LISTINGS GONE (SOLD) · 2026", t0+0.15)
    line_tag(d, t, 3, "DOES IT SELL?", anchor("b4","Line")-0.1)
    ya = ease((t-(anchor("b4","Fifty")-0.2))/0.4)
    stamp(im, W/2, 400, "YES", GREEN, ya, size=96, angle=-6)
    d = ImageDraw.Draw(im, "RGBA")
    fa = ease((t-(anchor("b4","Fifty")-0.1))/0.4)
    if fa > 0:
        glass(d, [60, 500, 1020, 1000], fa, fill=(11,24,36,215), line=DIM)
        paste_thumb(im, "p182b", (85, 525, 505, 705), fa)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (300, 760), "FRESH-PAINT ADS", SMR(20), MUTE, fa)
        sh(d, (300, 850), counter(0, 59.0, anchor("b4","Fifty")-0.05, 0.7, t, "{:.0f}%"), SMB(88), GREEN, fa)
        sh(d, (300, 930), "GONE · 23 OF 39", BCB(24), GREEN, fa)
        oa = ease((t-(anchor("b4","Fifty",2)-0.1))/0.4)
        paste_thumb(im, "ettm", (575, 525, 995, 705), oa)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (785, 760), "NOTHING NEW MENTIONED", SMR(20), MUTE, oa)
        sh(d, (785, 850), counter(0, 52.0, anchor("b4","Fifty",2)-0.05, 0.7, t, "{:.0f}%"), SMB(88), OFF, oa)
        sh(d, (785, 930), "GONE · 1,804 ADS", BCB(24), MUTE, oa)
        sh(d, (W/2, 980), "GONE = LISTING EXITED AS SOLD · ASKS, NOT SALE PRICES", SMR(15), DIM, oa)
    pa = ease((t-(anchor("b4","Paint")-0.1))/0.4)
    chip(d, W/2, 1100, "PAINT MOVES AIRPLANES", BCB(54), pa, fg=GREEN)
    sh(d, (W/2, 1200), "PHOTOS: SAME TYPE, NOT THE SUBJECT AIRCRAFT", SMR(15), DIM, pa)

TW = [("PAINT ONLY", 9000, 59, "paint", CYAN, "39 ADS"), ("NEW PANEL / FRESH ENGINE, NO PAINT", 29000, 54, "panel", (95,135,155), "1,249 ADS"), ("PAINT + NEW PANEL / FRESH ENGINE", 39800, 44, "jumps", RED, "48 ADS")]
def s_twist(im, d, t):
    t0 = T0['b5']
    topline(d, t, "WHAT ELSE IS \"NEW\" IN THE AD", t0+0.15)
    line_tag(d, t, 4, "THE TWIST", anchor("b5","Line")-0.1)
    ga = ease((t-(anchor("b5","New")-0.1))/0.4)
    glass(d, [60, 320, 1020, 1000], ga, fill=(11,24,36,205), line=DIM)
    sh(d, (110, 365), "ASK VS SAME-MODEL, SAME-VINTAGE PEERS WITH NOTHING NEW (MEDIAN)", SMR(18), MUTE, ga, anch="lm")
    sh(d, (970, 365), "GONE", SMR(18), MUTE, ga, anch="rm")
    y = 450
    for lab, v, gone, key, col, n in TW:
        at = anchor("b5", key)-0.1
        a = ease((t-at)/0.4)
        if a > 0:
            sh(d, (110, y-30), lab, BCB(30), OFF if col != (95,135,155) else MUTE, a, anch="lm")
            sh(d, (110, y+2), n, SMR(16), DIM, a, anch="lm")
            hbar(d, y+50, 110, 830, v, 42000, at, t, col, "+${:,.0f}", SMB(30))
            ga2 = ease((t-(at+0.9))/0.4)
            sh(d, (970, y+50), counter(0, gone, at+0.9, 0.6, t, "{:.0f}%"), SMB(44), col if col != (95,135,155) else OFF, ga2, anch="rm")
        y += 185
    pa = ease((t-(anchor("b5","Thirty")-0.1))/0.4)
    sh(d, (W/2, 950), "+30% ON THE BUNDLE  ·  ONLY 44% GONE VS 52% BASELINE", BCB(30), RED, pa)
    na = ease((t-(anchor("b5","problem")-0.2))/0.4)
    chip(d, W/2, 1090, "THE PAINT ISN'T THE PROBLEM", BCB(46), na)
    ba = ease((t-(anchor("b5","bundle")-0.15))/0.35)
    stamp(im, W/2, 1230, "THE BUNDLE IS", RED, ba, size=60, angle=-4)
    d = ImageDraw.Draw(im, "RGBA")
    sh(d, (W/2, 1340), "UPGRADES ON THEIR OWN ASK +$29,000 — THE BUNDLE ISN'T CRAZY, JUST AGGRESSIVE", SMR(15), DIM, ba)

def paint_card(im, d, box, slug, at, t, title, quote, ask, peers, gapfmt, gapcol, tag, tagcol, sub):
    a = ease((t-at)/0.4)
    if a <= 0: return
    x0, y0, x1, y1 = box
    glass(d, box, a, fill=(11,24,36,220), line=DIM)
    paste_thumb(im, slug, (x0+20, y0+20, x0+270, y0+200), a)
    d = ImageDraw.Draw(im, "RGBA")
    sh(d, (x0+300, y0+50), title, BCB(38), OFF, a, anch="lm")
    f = BCS(27); x = x0+300; yq = y0+98
    for w in quote.split(" "):
        ww = d.textlength(w+" ", font=f)
        if w.strip(",.\"").upper() in ("NEW", "PAINT", "UPGRADED", "PANEL"):
            d.rounded_rectangle([x-4, yq-18, x+ww-4, yq+18], radius=5, fill=(*CYAN, int(220*a)))
            d.text((x, yq), w, font=f, fill=(5,12,18,int(255*a)), anchor="lm")
        else:
            d.text((x, yq), w, font=f, fill=(*MUTE, int(255*a)), anchor="lm")
        x += ww
    ha = ease((t-(at+0.6))/0.4)
    sh(d, (x0+300, y0+150), "THIS AD", SMR(18), MUTE, ha, anch="lm")
    hbar(d, y0+185, x0+300, x1-40, ask, 240000, at+0.6, t, CYAN, "${:,.0f}", SMB(28))
    ta = ease((t-(at+1.4))/0.4)
    sh(d, (x0+300, y0+232), "PEERS · SAME MODEL ±3 YRS, NOTHING NEW (MEDIAN)", SMR(18), MUTE, ta, anch="lm")
    hbar(d, y0+267, x0+300, x1-40, peers, 240000, at+1.4, t, (95,135,155), "${:,.0f}", SMB(28))
    ga = ease((t-(at+2.2))/0.4)
    sh(d, (x0+150, y0+222), gapfmt, SMB(38), gapcol, ga)
    sa = ease((t-(at+3.0))/0.3)
    stamp(im, x0+150, y0+322, tag, tagcol, sa, size=24, angle=-3)
    d = ImageDraw.Draw(im, "RGBA")
    sh(d, (x0+340, y1-24), sub, SMR(15), DIM, sa, anch="lm")

def s_cards(im, d, t):
    t0 = T0['b6']
    topline(d, t, "TWO SKYLANE ADS · BOTH SAY NEW PAINT", t0+0.15)
    paint_card(im, d, [60, 250, 1020, 610], "q182", anchor("b6","Seventy")-0.15, t,
               "1979 CESSNA 182Q · N97875", "\"new paint job, upgraded avionics panel\"", 229900, 189900, "+$40,000", RED,
               "64 DAYS · STILL LISTED", RED, "DEALER · MN · 4,035 TT · 567 SMOH · 61 PEERS 1976–82 · 0 PRICE CUTS")
    paint_card(im, d, [60, 660, 1020, 1020], "p182", anchor("b6","Seventy",2)-0.15, t,
               "1973 CESSNA 182P · N845PC", "\"Garmin 650, New Paint, Fresh Annual\"", 165000, 165000, "+$0", GREEN,
               "GONE · 48 DAYS", GREEN, "DEALER · TX · 5,133 TT · 1,301 SMOH · 43 PEERS 1970–76 · AT THE MEDIAN")
    d = ImageDraw.Draw(im, "RGBA")
    ma = ease((t-(anchor("b6","median")-0.1))/0.4)
    chip(d, W/2, 1130, "SAME BRAG · SAME MODEL · OPPOSITE OUTCOME", BCB(40), ma)
    sh(d, (W/2, 1220), "PHOTOS: SAME TYPE, NOT THE SUBJECT AIRCRAFT · LISTINGS AS OF SEP 17 2026", SMR(16), DIM, ma)

def s_report(im, d, t):
    t0 = T0['b7']
    topline(d, t, "THE CATCH · AND WHAT THE REPORT SHOWS", t0+0.15)
    chips = [("ASKING PRICES, NOT SALES · SMALL SAMPLES (39 / 48 ADS)", anchor("b7","asks")-0.2, MUTE),
             ("\"NEW\" IS THE SELLER'S WORD — MOST ADS DON'T DATE THE PAINT", anchor("b7","seller's")-0.2, OFF)]
    y = 250
    for s, at, col in chips:
        a = ease((t-at)/0.4)
        if a > 0:
            glass(d, [80, y, 1000, y+86], a, r=20, fill=(13,27,38,180), line=col if col != MUTE else DIM)
            sh(d, (120, y+43), s, BCS(32), col if col != MUTE else (200,210,218), a, anch="lm")
        y += 104
    ra = ease((t-(anchor("b7","Check")-0.3))/0.5)
    if ra > 0:
        y0 = int(480 + (1-ra)*60)
        glass(d, [80, y0, 1000, y0+840], ra, fill=(11, 24, 36, 235))
        lg = Image.open(f"{ROOT}/assets/logo.png").resize((64, 64), Image.LANCZOS)
        if ra > 0.5: im.paste(lg, (120, y0+30), lg)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (200, y0+62), "NEXTPLANE REPORT", BCB(44), OFF, ra, anch="lm")
        sh(d, (960, y0+62), "N97875", SMB(34), CYAN, ra, anch="rm")
        d.line([120, y0+112, 960, y0+112], fill=(*DIM, int(160*ra)), width=2)
        rows = [("AIRCRAFT", "1979 CESSNA 182Q SKYLANE II", None, OFF),
                ("AD SAYS", "\"NEW PAINT\" · \"UPGRADED AVIONICS PANEL\"", None, OFF),
                ("1 · WHEN THE PAINT WENT ON", "NOT STATED IN THE AD", "when", AMBER),
                ("2 · WHAT ELSE IS NEW", "PANEL · +$29,000 ON ITS OWN, MARKET-WIDE", "else", AMBER),
                ("3 · ASK VS SAME-YEAR COMPS", "$229,900 · +$40,000 · +21%", "comps", CYAN),
                ("DAYS LISTED · CUTS", "64 · 0", None, OFF),
                ("FAA REGISTRY", "CJD AVIATION LLC · MN · OWNER SINCE 2004", None, OFF)]
        yy = y0 + 160
        for k, v, key, col in rows:
            a = ra if key is None else ease((t-(anchor("b7", key)-0.15))/0.35)
            sh(d, (120, yy), k, SMR(21), MUTE, a, anch="lm")
            sh(d, (120, yy+42), v, BCB(34), col, a, anch="lm")
            yy += 92
        ha = ease((t-(anchor("b7","three")-0.2))/0.4)
        chip(d, W/2, y0+790, "THREE THINGS · ONE REPORT", BCB(40), ha)

def s_end(im, d, t):
    t0 = T0['b8']
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

SCENE_FN = {"b1": s_hook, "b2": s_words, "b3": s_bill, "b4": s_sell, "b5": s_twist, "b6": s_cards, "b7": s_report, "b8": s_end}
BG = {"b1": ("q182", 1.0, 1.12, 0.40, 0.58), "b2": ("takeoff182", 1.12, 1.0, 0.36, 0.64), "b3": ("booth", 1.0, 1.1, 0.34, 0.66),
      "b4": ("p182b", 1.1, 1.0, 0.38, 0.62), "b5": ("ettm", 1.12, 1.0, 0.34, 0.66), "b6": ("p182", 1.0, 1.1, 0.36, 0.64),
      "b7": ("q182", 1.1, 1.0, 0.32, 0.70)}

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
