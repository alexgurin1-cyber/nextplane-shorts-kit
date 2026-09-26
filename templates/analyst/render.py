#!/usr/bin/env python3
"""NextPlane "The Buzzwords" CLASSIC ANALYST Short renderer.
Usage: render_bw.py <start> <end> [step]  -> /tmp/bw/frames/f%05d.jpg (1080x1920@30). Resumable; step interleaves procs."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, "/tmp/bw")
from endcard import draw_endcard

ROOT = "/tmp/bw"
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

BEATS = ["b1","b2","b3","b4","b5","b6","b7"]
VO = {b: json.load(open(f"{ROOT}/vo/{b}.json")) for b in BEATS}
OFFS = {}
t = 0.4; GAP = 0.3
for b in BEATS:
    OFFS[b] = t; t += VO[b]["dur"] + GAP + (0.3 if b == "b1" else 0)
TOTAL = OFFS["b7"] + VO["b7"]["dur"] + 1.6
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
    tmp = Image.new("RGBA", (900, 200), (0,0,0,0))
    td = ImageDraw.Draw(tmp)
    tw = td.textlength(txt, font=f)
    box = [450-tw/2-28, 20, 450+tw/2+28, 180]
    td.rounded_rectangle(box, radius=14, outline=(*color, 255), width=6)
    td.text((450, 100), txt, font=f, fill=(*color, 255), anchor="mm")
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
    cur = []
    for w in VO[b]["words"]:
        ww, s0, e0 = w["w"], OFFS[b]+w["s"], OFFS[b]+w["e"]
        cur.append((ww, s0, e0))
        if len(cur) >= 4 or ww.rstrip().endswith((".", "?", "!", ",", ":")):
            CHUNKS.append(cur); cur = []
    if cur: CHUNKS.append(cur)

def draw_captions(d, t):
    for ch in CHUNKS:
        if ch[0][1] - 0.05 <= t <= ch[-1][2] + 0.12:
            f = BCS(56)
            words = [w for w, s, e in ch]
            widths = [d.textlength(w+" ", font=f) for w in words]
            tot = sum(widths)
            scale = min(1.0, 980/tot)
            f2 = BCS(int(56*scale)) if scale < 1 else f
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
    sh(d, (W/2, 150), txt, SMB(30), MUTE, a)
    if a > 0:
        lw = int(300*a)
        d.rectangle([W/2-lw/2, 190, W/2+lw/2, 193], fill=(*CYAN, int(160*a)))

def hbar(d, x0, y, wmax, frac, col, h=56, g=1.0, bgcol=(78,118,138,150)):
    d.rounded_rectangle([x0, y, x0+wmax, y+h], radius=10, fill=bgcol)
    w = int(wmax*abs(frac)*g)
    if w > 0:
        if frac >= 0:
            d.rounded_rectangle([x0, y, x0+max(w, 12), y+h], radius=10, fill=(*col, 240))
        else:
            d.rounded_rectangle([x0+wmax-max(w,12), y, x0+wmax, y+h], radius=10, fill=(*col, 240))

# ---------- scenes ----------

def s_hook(im, d, t):
    topline(d, t, "THE BUZZWORDS · NEXTPLANE MARKET DATA", 0.3)
    a0 = ease((t-(anchor("b1","complete")-0.1))/0.4)
    if a0 > 0:
        glass(d, [60, 250, 1020, 560], a0, fill=(11,24,36,215), line=CYAN, lw=3)
        sh(d, (90, 300), "WHAT THE AD SAYS", SMR(22), MUTE, a0, anch="lm")
        sh(d, (90, 400), "“COMPLETE LOGS”", BCB(76), OFF, a0, anch="lm")
        sh(d, (90, 480), "A TYPICAL LISTING PHRASE", SMR(20), MUTE, a0, anch="lm")
    a1 = ease((t-(anchor("b1","four")-0.15))/0.4)
    if a1 > 0:
        at = anchor("b1","four")-0.1
        glass(d, [60, 600, 1020, 850], a1, fill=(11,24,36,215), line=DIM)
        sh(d, (90, 645), "US LISTINGS THAT USE IT", SMR(21), MUTE, a1, anch="lm")
        sh(d, (90, 760), counter(0, 449, at, 1.0, t) + " ADS", BCB(96), OFF, a1, anch="lm")
    a2 = ease((t-(anchor("b1","zero")-0.2))/0.4)
    if a2 > 0:
        at2 = anchor("b1","zero")-0.15
        glass(d, [60, 900, 1020, 1330], a2, fill=(11,24,36,225), line=CYAN, lw=3)
        sh(d, (90, 950), "WHAT THOSE WORDS ADD TO THE ASKING PRICE", SMR(20), MUTE, a2, anch="lm")
        sh(d, (90, 1090), counter(300, 0, at2, 0.8, t, "${:,.0f}"), BCB(160), CYAN, a2, anch="lm")
        stamp(im, 830, 1230, "WORTH NOTHING", AMBER, ease((t-at2-0.6)/0.4), size=40, angle=-8)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (990, 1290), "ASKING PRICES · MATCHED VS PEERS", SMR(17), DIM, a2, anch="rm")

def s_method(im, d, t):
    topline(d, t, "THE METHOD", T0["b2"]+0.15)
    a0 = ease((t-(anchor("b2","matched")-0.1))/0.4)
    if a0 > 0:
        glass(d, [60, 240, 1020, 770], a0, fill=(11,24,36,215), line=DIM)
        sh(d, (90, 285), "EVERY LISTING WITH A BRAG PHRASE, MATCHED TO", SMR(20), MUTE, a0, anch="lm")
        rows = [("SAME MAKE + MODEL", anchor("b2","same",1)-0.1),
                ("MODEL YEAR ± 3", anchor("b2","years")-0.1),
                ("PEERS THAT DON'T SAY IT", anchor("b2","say")-0.1)]
        for j,(lab,at) in enumerate(rows):
            ra = ease((t-at)/0.35)
            if ra <= 0: continue
            y = 340 + j*130
            d.rounded_rectangle([90, y, 990, y+100], radius=12, fill=(18,36,52,int(220*ra)), outline=(*CYAN,int(190*ra)), width=2)
            sh(d, (120, y+50), lab, BCB(38), OFF, ra, anch="lm")
    a1 = ease((t-(anchor("b2","Six")-0.15))/0.4)
    if a1 > 0:
        at = anchor("b2","Six")-0.1
        glass(d, [60, 810, 1020, 1150], a1, fill=(11,24,36,215), line=CYAN, lw=3)
        sh(d, (90, 855), "SIX PHRASES SHOW UP AGAIN AND AGAIN", SMR(20), MUTE, a1, anch="lm")
        names = ["COMPLETE LOGS","ALWAYS HANGARED","NO DAMAGE","ONE OWNER","METICULOUS","NO ACCIDENT"]
        for k, nm in enumerate(names):
            ca = ease((t-at-0.1*k)/0.35)
            if ca <= 0: continue
            x = 90 + (k%3)*310; y = 920 + (k//3)*110
            d.rounded_rectangle([x, y, x+290, y+80], radius=12, fill=(18,36,52,int(220*ca)), outline=(*OFF,int(160*ca)), width=2)
            sh(d, (x+145, y+40), nm, SMR(19), OFF, ca)
    a2 = ease((t-(anchor("b2","which")-0.15))/0.4)
    if a2 > 0:
        chip(d, W/2, 1240, "WHICH ONES ARE WORTH REAL MONEY?", BCB(34), a2, fg=CYAN, w_pad=24, h_pad=14)

LADDER = [
    ("METICULOUSLY MAINTAINED", "n = 199", 10000, CYAN, ("Meticulously",1)),
    ("ALWAYS HANGARED", "n = 242", 5300, OFF, ("Always",1)),
    ("ONE OWNER", "n = 56", 3000, OFF, ("One",1)),
    ("NO DAMAGE HISTORY", "n = 482 · basically nothing", 1000, MUTE, ("No",1)),
    ("COMPLETE LOGS", "n = 449", 0, DIM, ("complete",1)),
]
def s_ladder(im, d, t):
    topline(d, t, "MEDIAN ASKING-PRICE GAP VS PLAIN PEERS", T0["b3"]+0.15)
    MAXV = 10000
    for j, (lab, sub, v, col, (word, occ)) in enumerate(LADDER):
        at = anchor("b3", word, occ) - 0.1
        ra = ease((t-at)/0.4)
        if ra <= 0: continue
        y = 290 + j*205
        sh(d, (90, y), lab, BCB(34), OFF, ra, anch="lm")
        sh(d, (990, y), sub, SMR(16), DIM, ra, anch="rm")
        hbar(d, 90, y+22, 900, v/MAXV, col, h=58, g=easeo((t-at)/0.9))
        vt = "$0" if v == 0 else counter(0, v, at, 0.9, t, "+${:,.0f}")
        frac = v/MAXV
        if v == 0:
            sh(d, (990, y+51), vt, SMB(30), DIM, ra, anch="rm")
        elif frac > 0.78:
            sh(d, (90+int(900*frac)-16, y+51), vt, SMB(30), NAVY, ra, anch="rm", shad=0)
        else:
            sh(d, (90+int(900*frac)+16, y+51), vt, SMB(30), OFF, ra, anch="lm")

def s_twist(im, d, t):
    topline(d, t, "THE ONE THAT SHOULD REASSURE YOU MOST", T0["b4"]+0.15)
    a0 = ease((t-(anchor("b4","phrase")-0.1))/0.4)
    if a0 > 0:
        glass(d, [60, 240, 1020, 470], a0, fill=(11,24,36,215), line=DIM)
        sh(d, (90, 290), "BUILT TO REASSURE THE BUYER", SMR(21), MUTE, a0, anch="lm")
        sh(d, (90, 380), "COSTS THE SELLER MONEY", BCB(52), OFF, a0, anch="lm")
    a1 = ease((t-(anchor("b4","No")-0.15))/0.4)
    if a1 > 0:
        glass(d, [60, 510, 1020, 720], a1, fill=(11,24,36,225), line=AMBER, lw=3)
        sh(d, (90, 560), "WHAT THE AD SAYS", SMR(20), MUTE, a1, anch="lm")
        sh(d, (90, 645), "“NO ACCIDENT, NO CORROSION”", BCB(52), OFF, a1, anch="lm")
    a2 = ease((t-(anchor("b4","minus")-0.15))/0.4)
    if a2 > 0:
        at = anchor("b4","minus")-0.1
        glass(d, [60, 760, 1020, 1080], a2, fill=(11,24,36,225), line=RED, lw=3)
        sh(d, (90, 810), "MEDIAN ASKING-PRICE GAP · n = 75", SMR(20), MUTE, a2, anch="lm")
        sh(d, (90, 940), counter(0, -9900, at, 0.9, t, "-${:,.0f}").replace("-$-","-$"), BCB(140), RED, a2, anch="lm")
        stamp(im, 850, 950, "LOWER, NOT HIGHER", AMBER, ease((t-at-0.7)/0.4), size=32, angle=-8)
        d = ImageDraw.Draw(im, "RGBA")
    a3 = ease((t-(anchor("b4","older")-0.15))/0.4)
    if a3 > 0:
        glass(d, [60, 1120, 1020, 1330], a3, fill=(11,24,36,215), line=DIM)
        sh(d, (90, 1165), "SHOWS UP MORE ON OLDER AIRPLANES", SMR(20), MUTE, a3, anch="lm")
        sh(d, (90, 1250), "AVG MODEL YEAR 1981 vs 1991 BASELINE", BCS(30), OFF, a3, anch="lm")

def s_hero(im, d, t):
    topline(d, t, "SAME WORDS · TWO REAL LISTINGS", T0["b5"]+0.15)
    a0 = ease((t-(anchor("b5","nineteen")-0.15))/0.4)
    if a0 > 0:
        glass(d, [60, 240, 1020, 700], a0, fill=(11,24,36,225), line=DIM)
        paste_thumb(im, "chero", (90, 265, 400, 670), a0)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (430, 310), "1968 PIPER CHEROKEE 140", BCB(40), OFF, a0, anch="lm")
        pa = ease((t-(anchor("b5","forty")-0.1))/0.4)
        sh(d, (430, 400), counter(0, 43000, anchor("b5","forty")-0.05, 0.7, t, "${:,.0f}"), BCB(78), CYAN, pa, anch="lm")
        qa = ease((t-(anchor("b5","complete")-0.1))/0.4)
        if qa > 0:
            d.rounded_rectangle([430, 500, 970, 640], radius=12, fill=(18,36,52,int(220*qa)), outline=(*OFF,int(170*qa)), width=2)
            sh(d, (450, 545), "“COMPLETE LOGBOOKS,", SMB(21), OFF, qa, anch="lm")
            sh(d, (450, 590), "NO DAMAGE HISTORY”", SMB(21), OFF, qa, anch="lm")
    a1 = ease((t-(anchor("b5","A",2)-0.15))/0.4)
    if a1 > 0:
        glass(d, [60, 750, 1020, 1210], a1, fill=(11,24,36,225), line=CYAN, lw=3)
        paste_thumb(im, "sr22t2", (90, 775, 400, 1180), a1)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (430, 820), "2023 CIRRUS SR22 TURBO", BCB(40), OFF, a1, anch="lm")
        pb = ease((t-(anchor("b5","nine")-0.1))/0.4)
        sh(d, (430, 910), counter(0, 950000, anchor("b5","nine")-0.05, 0.7, t, "${:,.0f}"), BCB(78), CYAN, pb, anch="lm")
        qb = ease((t-(anchor("b5","meticulously")-0.1))/0.4)
        if qb > 0:
            d.rounded_rectangle([430, 1010, 970, 1120], radius=12, fill=(18,36,52,int(220*qb)), outline=(*OFF,int(170*qb)), width=2)
            sh(d, (450, 1065), "“METICULOUSLY MAINTAINED”", SMB(19), OFF, qb, anch="lm")
    a2 = ease((t-(anchor("b5","Same")-0.15))/0.4)
    if a2 > 0:
        chip(d, W/2, 1290, "SAME SCRIPT · DIFFERENT STAKES", BCB(36), a2, fg=CYAN, w_pad=26, h_pad=14)

def s_honest(im, d, t):
    topline(d, t, "THE HONEST PART", T0["b6"]+0.15)
    a0 = ease((t-(anchor("b6","This")-0.1))/0.4)
    if a0 > 0:
        glass(d, [60, 240, 1020, 1080], a0, fill=(11,24,36,215), line=AMBER, lw=3)
        rows = [
            ("CORRELATION, NOT CAUSATION", "matched by make, model and year — not proof a phrase changes what a plane sells for", anchor("b6","proof")-0.1),
            ("ASKING, NOT SOLD", "every number here is what sellers asked, not what buyers paid", anchor("b6","sold")-0.1),
            ("THE ADJECTIVE TRAVELS WITH THE AIRPLANE", "meticulous ads skew newer and better-equipped — that's part of the story too", anchor("b6","adjective")-0.1),
        ]
        for j, (lab, sub, at) in enumerate(rows):
            ra = ease((t-at)/0.35)
            if ra <= 0: continue
            y = 290 + j*260
            d.rounded_rectangle([90, y, 990, y+225], radius=14, fill=(18,36,52,int(220*ra)), outline=(*AMBER, int(170*ra)), width=2)
            sh(d, (120, y+55), lab, BCB(32), OFF, ra, anch="lm")
            words = sub.split(" ")
            line1 = " ".join(words[:8]); line2 = " ".join(words[8:])
            sh(d, (120, y+120), line1, SMR(18), MUTE, ra, anch="lm")
            sh(d, (120, y+155), line2, SMR(18), MUTE, ra, anch="lm")
    a1 = ease((t-(T0["b6"]+9.0))/0.5)
    if a1 > 0:
        glass(d, [60, 1130, 1020, 1330], a1, fill=(11,24,36,225), line=CYAN, lw=3)
        sh(d, (90, 1180), "A NEXTPLANE REPORT READS THE RECORD,", SMR(19), MUTE, a1, anch="lm")
        sh(d, (90, 1220), "NOT THE AD COPY", BCB(44), OFF, a1, anch="lm")
        sh(d, (990, 1290), "RUN ANY TAIL NUMBER · NEXTPLANE.US", SMR(18), CYAN, a1, anch="rm")

def s_end(im, d, t):
    return draw_endcard(im, t - T0["b7"], FD, f"{ROOT}/assets/logo.png")

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

SCENE_FN = {"b1": s_hook, "b2": s_method, "b3": s_ladder, "b4": s_twist, "b5": s_hero, "b6": s_honest, "b7": s_end}
BG = {"b1": ("chero", 1.0, 1.12, 0.40, 0.58), "b2": ("sr22t2", 1.12, 1.0, 0.38, 0.62), "b3": ("sr22t", 1.0, 1.10, 0.34, 0.66),
      "b4": ("chero2", 1.12, 1.0, 0.34, 0.66), "b5": ("sr22t", 1.0, 1.08, 0.36, 0.66), "b6": ("chero2", 1.0, 1.10, 0.36, 0.64)}

def frame(i):
    t = i / FPS
    name, t0, t1 = next(s for s in SC if s[1] <= t < s[2] or s is SC[-1] and t >= s[1])
    p = (t - t0) / max(t1 - t0, 0.01)
    if name in BG:
        slug, z0, z1, dk, tn = BG[name]
        im = bg_photo(slug, p, zoom0=z0, zoom1=z1, dark=dk, tint=tn)
        im = vignette(im)
    else:
        im = end_bg()
    d = ImageDraw.Draw(im, "RGBA")
    SCENE_FN[name](im, d, t)
    d = ImageDraw.Draw(im, "RGBA")
    if name != "b7":
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
