#!/usr/bin/env python3
"""NextPlane "Panel Flip" STORY-OF-ONE Short renderer (story #5: N38587, 1977 Piper Arrow III, $109K Apr -> $165K Sep).
Usage: render_ut.py <start> <end> [step]  -> /tmp/arrow/frames/f%05d.jpg (1080x1920@30). Resumable; step interleaves procs."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
sys.path.insert(0, "/tmp/arrow")
from endcard import draw_endcard

ROOT = "/tmp/arrow"
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
    return 1e9  # miss-safe

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

MERGE = [("one hundred nine thousand dollars", "$109,000"), ("one hundred sixty five thousand", "$165,000"),
         ("thirty two", "32"), ("november three eight five eight seven", "N38587"), ("nineteen seventy seven", "1977"),
         ("arrow three", "Arrow III"), ("arrow threes", "Arrow IIIs"), ("forty four hundred", "4,400"), ("garmin four thirty", "Garmin 430"),
         ("g fives", "G5s"), ("g n x three seventy five", "GNX 375"), ("g n c three fifty five", "GNC 355"),
         ("fifty six thousand dollars", "$56,000"), ("fifty one percent", "51%"), ("one sixty five", "$165K"), ("fourteen", "14"),
         ("one thirty seven", "$137K"), ("one twenty seven", "$127K"), ("twenty six percent", "26%"), ("nextplane dot u s", "NextPlane.us"),
         ("faa", "FAA")]
MERGE.sort(key=lambda r: -len(r[0].split()))
def merged_words(b):
    ws = VO[b]["words"]; out = []; i = 0
    norm = [w["w"].strip(".,?!:").lower() for w in ws]
    while i < len(ws):
        hit = None
        for pat, rep in MERGE:
            toks = pat.split(); n = len(toks)
            if norm[i:i+n] == toks:
                hit = (n, rep); break
        if hit:
            n, rep = hit; last = ws[i+n-1]["w"]
            tail = last[len(last.rstrip(".,?!:")):]
            out.append({"w": rep + tail, "s": ws[i]["s"], "e": last and ws[i+n-1]["e"]}); i += n
        else:
            out.append(ws[i]); i += 1
    return out
CHUNKS = []
for b in BEATS[:-1]:
    ws = merged_words(b); cur = []
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

def hbar(d, x0, y, wmax, frac, col, h=56, g=1.0, bgcol=(78,118,138,150)):
    d.rounded_rectangle([x0, y, x0+wmax, y+h], radius=10, fill=bgcol)
    w = int(wmax*frac*g)
    if w > 0: d.rounded_rectangle([x0, y, x0+max(w, 12), y+h], radius=10, fill=(*col, 240))

# ---------- scenes ----------
LIGHT = (150, 226, 230)
def s_hook(im, d, t):
    topline(d, t, "STORY OF ONE AIRPLANE · TWO ADS · ONE TAIL NUMBER", 0.3)
    a1 = ease((t-(anchor("b1","One")-0.15))/0.4)
    if a1 > 0:
        at = anchor("b1","One")
        glass(d, [60, 270, 1020, 600], a1, fill=(11,24,36,205), line=DIM, lw=3)
        sh(d, (95, 320), "APRIL 2026 · ASKING PRICE", SMR(24), MUTE, a1, anch="lm")
        sh(d, (95, 460), counter(0, 109000, at, 1.0, t, "${:,.0f}"), SMB(128), OFF, a1, anch="lm")
        sh(d, (985, 560), "AD #1", BCB(36), MUTE, a1, anch="rm")
    a2 = ease((t-(anchor("b1","One",2)-0.15))/0.4)
    if a2 > 0:
        at = anchor("b1","One",2)
        glass(d, [60, 640, 1020, 970], a2, fill=(11,24,36,215), line=CYAN, lw=3)
        sh(d, (95, 690), "SEPTEMBER 2026 · ASKING PRICE", SMR(24), CYAN, a2, anch="lm")
        sh(d, (95, 830), counter(109000, 165000, at, 1.2, t, "${:,.0f}"), SMB(128), CYAN, a2, anch="lm")
        sh(d, (985, 930), "AD #2", BCB(36), CYAN, a2, anch="rm")
    a3 = ease((t-(anchor("b1","Same")-0.1))/0.35)
    if a3 > 0:
        stamp(im, W/2, 1060, "SAME AIRPLANE", OFF, a3, size=70, angle=-4)
    a4 = ease((t-(anchor("b1","flew")-0.1))/0.4)
    if a4 > 0:
        d = ImageDraw.Draw(im, "RGBA")
        glass(d, [220, 1170, 860, 1360], a4, fill=(11,24,36,225), line=CYAN, lw=2)
        sh(d, (540, 1220), "FLOWN IN BETWEEN", SMR(22), MUTE, a4)
        sh(d, (540, 1300), "+" + counter(0, 32, anchor("b1","thirty")-0.05, 0.7, t) + " HOURS", BCB(84), OFF, a4)

def reg_card(im, d, box, a):
    x0, y0, x1, y1 = box
    glass(d, box, a, fill=(11,24,36,225), line=CYAN, lw=3)
    lg = Image.open(f"{ROOT}/assets/logo.png").resize((52, 52), Image.LANCZOS)
    if a > 0.5: im.paste(lg, (x0+28, y0+22), lg)
    d = ImageDraw.Draw(im, "RGBA")
    sh(d, (x0+95, y0+48), "FAA REGISTRY", BCB(34), OFF, a, anch="lm")
    sh(d, (x1-30, y0+48), "N38587", SMB(40), CYAN, a, anch="rm")
    d.line([x0+28, y0+88, x1-28, y0+88], fill=(*DIM, int(160*a)), width=2)
    sh(d, (x0+30, y0+122), "1977 PIPER PA-28R-201 ARROW III", BCB(38), OFF, a, anch="lm")
    sh(d, (x0+30, y0+165), "S/N 28R-7737100 · AIRWORTHY SINCE 1977-06-29", SMR(19), MUTE, a, anch="lm")
    return d

def s_registry(im, d, t):
    topline(d, t, "THE AIRPLANE · FAA REGISTRY + AD #1", T0["b2"]+0.15)
    a1 = ease((t-(anchor("b2","November")-0.1))/0.4)
    if a1 > 0:
        d = reg_card(im, d, [60, 230, 1020, 440], a1)
    a2 = ease((t-(anchor("b2","April")-0.1))/0.4)
    if a2 > 0:
        glass(d, [60, 470, 1020, 1000], a2, fill=(11,24,36,225), line=DIM, lw=3)
        paste_thumb(im, "oldpanel", (80, 490, 420, 720), a2)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (450, 515), "AD #1 · APRIL 2026 · BROKER, SC", SMR(19), MUTE, a2, anch="lm")
        sh(d, (450, 570), "1977 ARROW III", BCB(44), OFF, a2, anch="lm")
        sh(d, (450, 625), "$109,000", SMB(52), OFF, a2, anch="lm")
        sh(d, (450, 690), "PANEL PHOTO: TYPICAL PA-28, NOT N38587", SMR(15), DIM, a2, anch="lm")
        rows = [("TOTAL TIME", "4,438 H", OFF, anchor("b2","forty")-0.1),
                ("NAV/GPS", "GARMIN GNS 430W · ROUND GAUGES", OFF, anchor("b2","Garmin")-0.1),
                ("RADIO #2", "NARCO COM-120 · (INOP)", AMBER, anchor("b2","second")-0.1)]
        for j, (lab, val, col, at) in enumerate(rows):
            ra = ease((t-at)/0.35)
            if ra <= 0: continue
            y = 745 + j*80
            d.rounded_rectangle([90, y, 990, y+66], radius=12, fill=(18,36,52,int(220*ra)), outline=(*(AMBER if col == AMBER else DIM), int(180*ra)), width=2)
            sh(d, (115, y+33), lab, SMR(19), MUTE, ra, anch="lm")
            sh(d, (380, y+33), val, BCB(34), col, ra, anch="lm")
    timeline(im, d, t, [anchor("b2","April")-0.1, anchor("b2","July")-0.1, 1e9], y=1130)

def timeline(im, d, t, ats, y=1130):
    a0 = ease((t-ats[0])/0.4)
    if a0 <= 0: return
    glass(d, [60, y-90, 1020, y+150], a0, fill=(11,24,36,215), line=DIM, lw=2)
    xs = [190, 540, 890]
    labs = [("APR 2026", "AD #1 · $109,000", MUTE), ("JUL 8, 2026", "FAA · NEW OWNER", OFF), ("SEP 1, 2026", "AD #2 · $165,000", CYAN)]
    subs = ["BROKER · SC", "MISSOURI LLC", "NEW OWNER · MO"]
    for j in range(3):
        aj = ease((t-ats[j])/0.4)
        if j > 0:
            g = easeo((t-ats[j]+0.2)/0.6)
            d.line([xs[j-1]+22, y, xs[j-1]+22+int((xs[j]-xs[j-1]-44)*g), y], fill=(*CYAN, int(220*a0)), width=5)
        col = labs[j][2]
        if aj > 0:
            d.ellipse([xs[j]-18, y-18, xs[j]+18, y+18], fill=(*col, int(255*aj)))
            sh(d, (xs[j], y-50), labs[j][0], SMB(22), col, aj)
            sh(d, (xs[j], y+50), labs[j][1], BCB(28), OFF, aj)
            sh(d, (xs[j], y+92), subs[j], SMR(16), MUTE, aj)
        else:
            d.ellipse([xs[j]-14, y-14, xs[j]+14, y+14], outline=(*DIM, int(200*a0)), width=3)

def s_diff(im, d, t):
    topline(d, t, "AD #2 · WHAT CHANGED BETWEEN THE ADS", T0["b3"]+0.15)
    a0 = ease((t-(anchor("b3","September")-0.1))/0.4)
    if a0 > 0:
        glass(d, [60, 230, 1020, 1060], a0, fill=(11,24,36,225), line=CYAN, lw=3)
        sh(d, (95, 280), "FROM THE TWO ADS", SMR(20), MUTE, a0, anch="lm")
        sh(d, (560, 280), "APRIL", BCB(34), MUTE, a0, anch="mm")
        sh(d, (850, 280), "SEPTEMBER", BCB(34), CYAN, a0, anch="mm")
        d.line([90, 312, 990, 312], fill=(*DIM, int(160*a0)), width=2)
    rows = [("SELLER", "BROKER · SC", "NEW OWNER · MO", "lists", OFF),
            ("TOTAL TIME", "4,438 H", "4,470 H", "lists", OFF),
            ("ENGINE", "832 SMOH", "830 SMOH", "Same", OFF),
            ("NAVIGATOR", "GNS 430W", "GNX 375 + GNC 355", "N", CYAN),
            ("FLIGHT INSTR.", "ROUND GAUGES", "DUAL GARMIN G5", "fives", CYAN),
            ("INTERIOR", "NOT MENTIONED", "BRAND NEW", "interior", CYAN)]
    for j, (lab, a_, b_, word, col) in enumerate(rows):
        at = anchor("b3", word) - 0.15 + (0.25 if j == 1 else 0)
        ra = ease((t-at)/0.35)
        if ra <= 0: continue
        y = 335 + j*92
        d.rounded_rectangle([90, y, 990, y+80], radius=12, fill=(18,36,52,int(220*ra)), outline=(*(col if col == CYAN else DIM), int(170*ra)), width=2)
        sh(d, (110, y+40), lab, SMR(18), MUTE, ra, anch="lm")
        sh(d, (560, y+40), a_, BCB(30), MUTE, ra, anch="mm")
        sh(d, (850, y+40), b_, BCB(30), col if col == CYAN else OFF, ra, anch="mm")
    qa = ease((t-(anchor("b3","brand")-0.1))/0.4)
    if qa > 0:
        sh(d, (95, 905), "AD #2, VERBATIM:", SMR(19), MUTE, qa, anch="lm")
        sh(d, (95, 950), "“All new Garmin Panel, Brand New Airtex Interior”", BCS(38), OFF, qa, anch="lm")
        sh(d, (95, 1010), "PANEL LIST IS THE AD'S TEXT · NOT INSPECTED BY US", SMR(17), DIM, qa, anch="lm")
    pa = ease((t-(anchor("b3","price")-0.15))/0.4)
    if pa > 0:
        at = anchor("b3","fifty")-0.1
        glass(d, [60, 1100, 1020, 1360], pa, fill=(11,24,36,230), line=CYAN, lw=3)
        sh(d, (95, 1150), "AD #1 $109,000  ·  AD #2 $165,000", SMR(22), MUTE, pa, anch="lm")
        sh(d, (95, 1260), "+" + counter(0, 56000, at, 0.9, t, "${:,.0f}"), SMB(100), CYAN, pa, anch="lm")
        stamp(im, 850, 1250, "+51%", OFF, ease((t-(anchor("b3","Fifty",2)-0.1))/0.35), size=80, angle=-7)

COH = [("N2811M",70000,0),("N2672Q",88000,0),("N5202T",89500,0),("N40010",110000,0),("N2496M",127500,0),("N2590Q",134900,0),
       ("N2611M",135000,0),("N21870",139900,0),("N531GS",145000,0),("N31994",164500,1),("N38587",165000,2),("N84AR",169000,1),
       ("N47442",169900,1),("N158CC",229000,1)]
def px(v, x0=110, x1=970, lo=60000, hi=240000): return x0 + (x1-x0)*(v-lo)/(hi-lo)
def s_peers(im, d, t):
    topline(d, t, "IS $165,000 CRAZY? · EVERY ARROW III WE TRACKED", T0["b4"]+0.15)
    a0 = ease((t-(anchor("b4","tracked")-0.15))/0.4)
    if a0 <= 0: return
    glass(d, [60, 230, 1020, 1000], a0, fill=(11,24,36,215), line=DIM, lw=2)
    sh(d, (95, 280), "NON-TURBO ARROW III · 1977-79 · US ADS SINCE APRIL · ONE PER TAIL", SMR(18), MUTE, a0, anch="lm")
    sh(d, (95, 340), counter(0, 14, anchor("b4","fourteen")-0.05, 0.6, t) + " AIRPLANES", BCB(52), OFF, a0, anch="lm")
    base = 700
    d.line([110, base, 970, base], fill=(*DIM, int(220*a0)), width=3)
    for v in (60000, 100000, 140000, 180000, 220000):
        x = px(v); d.line([x, base-10, x, base+10], fill=(*DIM, int(220*a0)), width=2)
        sh(d, (x, base+40), f"${v//1000}K", SMR(18), MUTE, a0)
    ma = ease((t-(anchor("b4","middle")-0.1))/0.4)
    if ma > 0:
        x = px(137450)
        d.line([x, 430, x, base], fill=(*OFF, int(200*ma)), width=3)
        sh(d, (x, 410), "MEDIAN $137,450", BCB(32), OFF, ma)
    at0 = anchor("b4","fourteen")
    hi_a = ease((t-(anchor("b4","Only")-0.1))/0.4)
    stack = {}
    for k, (reg, v, cls) in enumerate(COH):
        ak = ease((t-(at0+0.08*k))/0.3)
        if ak <= 0: continue
        x = px(v); key = round(x/28); lvl = stack.get(key, 0); stack[key] = lvl+1
        y = base - 40 - lvl*46
        if cls == 2:
            r = 24; col = CYAN
        elif cls == 1 and hi_a > 0:
            r = 17; col = tuple(int(MUTE[i]*(1-hi_a) + LIGHT[i]*hi_a) for i in range(3))
        else:
            r = 17; col = MUTE
        d.ellipse([x-r, y-r, x+r, y+r], fill=(*col, int(245*ak)))
        if cls == 2:
            sh(d, (x, y-50), "N38587", SMB(22), CYAN, ak)
    # ghost April marker
    ga = ease((t-(anchor("b4","April")-0.1))/0.4)
    if ga > 0:
        x = px(109000); y = base - 190
        d.ellipse([x-20, y-20, x+20, y+20], outline=(*OFF, int(220*ga)), width=4)
        for yy in range(y+24, base-62, 14): d.line([x, yy, x, yy+7], fill=(*OFF, int(160*ga)), width=2)
        sh(d, (x, y-44), "SAME PLANE · APRIL AD $109K", SMR(18), OFF, ga)
    if hi_a > 0:
        glass(d, [60, 1040, 1020, 1360], hi_a, fill=(11,24,36,225), line=CYAN, lw=3)
        sh(d, (95, 1090), "ASKING MORE THAN $165,000: ONLY 3", BCB(40), OFF, hi_a, anch="lm")
        items = [("N84AR", "$169,000", "AVIDYNE IFD 440 · DUAL G5"), ("N47442", "$169,900", "GARMIN GNC 375"), ("N158CC", "$229,000", "GARMIN GTN 750Xi · GFC 500")]
        for j, (reg, pr, eq) in enumerate(items):
            aj = ease((t-(anchor("b4","every")-0.2+0.25*j))/0.35)
            if aj <= 0: continue
            y = 1150 + j*62
            d.ellipse([100, y-12, 124, y+12], fill=(*LIGHT, int(240*aj)))
            sh(d, (145, y), reg, SMB(26), OFF, aj, anch="lm")
            sh(d, (330, y), pr, SMB(26), CYAN, aj, anch="lm")
            sh(d, (520, y), eq, BCS(30), OFF, aj, anch="lm")

def s_fair(im, d, t):
    topline(d, t, "NEXTPLANE REPORT · N38587", T0["b5"]+0.15)
    a0 = ease((t-(anchor("b5","fair")-0.3))/0.45)
    if a0 <= 0: return
    glass(d, [60, 230, 1020, 1000], a0, fill=(11, 24, 36, 238), line=CYAN, lw=3)
    lg = Image.open(f"{ROOT}/assets/logo.png").resize((56, 56), Image.LANCZOS)
    if a0 > 0.5: im.paste(lg, (90, 258), lg)
    d = ImageDraw.Draw(im, "RGBA")
    sh(d, (160, 286), "NEXTPLANE REPORT · PRICE CHECK", BCB(36), OFF, a0, anch="lm")
    sh(d, (990, 286), "N38587", SMB(30), CYAN, a0, anch="rm")
    d.line([90, 325, 990, 325], fill=(*DIM, int(160*a0)), width=2)
    at = anchor("b5","twenty")-0.3
    sh(d, (90, 370), "FAIR VALUE · MODEL ESTIMATE (SEP 16)", SMR(19), MUTE, a0, anch="lm")
    hbar(d, 90, 395, 900, 127062/165000, MUTE, h=50, g=easeo((t-at)/0.8))
    sh(d, (90+int(900*127062/165000)-14, 420), counter(0, 127062, at, 0.8, t, "${:,.0f}"), SMB(28), NAVY, a0, anch="rm", shad=0)
    pa = ease((t-(anchor("b5","ask")-0.15))/0.4)
    if pa > 0:
        at2 = anchor("b5","ask")-0.1
        sh(d, (90, 490), "ASK · AD #2", SMR(19), MUTE, pa, anch="lm")
        hbar(d, 90, 515, 900, 1.0, CYAN, h=50, g=easeo((t-at2)/0.8))
        sh(d, (975, 540), "$165,000", SMB(28), NAVY, pa, anch="rm", shad=0)
        ca = ease((t-(anchor("b5","percent")-0.2))/0.4)
        if ca > 0:
            chip(d, 540, 625, counter(0, 26, anchor("b5","twenty",2)-0.1, 0.6, t, "+{:.0f}% ABOVE FAIR VALUE"), BCB(36), ca, fg=AMBER, w_pad=20, h_pad=10)
    ga = ease((t-(anchor("b5","gap")-0.15))/0.4)
    if ga > 0:
        # stacked decomposition
        y = 720
        sh(d, (90, 668), "HOW THE $165,000 STACKS UP", SMR(19), MUTE, ga, anch="lm")
        segs = [(109000, MUTE, "AD #1 $109K"), (127062-109000, (120, 170, 185), "FAIR VALUE $127K"), (165000-127062, CYAN, "PANEL CLAIM $38K")]
        x = 90; g = easeo((t-(anchor("b5","gap")-0.1))/1.0)
        for j, (v, col, lab) in enumerate(segs):
            w = int(900*v/165000*g)
            if w > 4:
                d.rectangle([x, y+20, x+w, y+90], fill=(*col, 235))
                if g > 0.9:
                    if j == 0: sh(d, (x+w/2, y+125), lab, BCB(30), OFF, ga)
                    elif j == 1: sh(d, (x+w/2, y-8), lab, BCB(28), (150, 200, 212), ga)
                    else: sh(d, (x+w, y+125), lab, BCB(30), CYAN, ga, anch="rm")
            x += w
        sh(d, (90, 930), "ASK MINUS FAIR VALUE = $37,938 · WHAT THE SELLER SAYS THE PANEL IS WORTH", SMR(17), MUTE, ga, anch="lm")
    sa = ease((t-(anchor("b5","skips")-0.15))/0.4)
    if sa > 0:
        glass(d, [60, 1040, 1020, 1300], sa, fill=(11,24,36,225), line=CYAN, lw=2)
        sh(d, (540, 1110), "WHAT THE NEXT BUYER GETS FOR IT", SMR(20), MUTE, sa)
        sh(d, (540, 1180), "THE PANEL IS ALREADY IN", BCB(56), OFF, sa)
        sh(d, (540, 1250), "NO SHOP DOWNTIME · NO PICKING THE BOXES", BCS(32), CYAN, sa)

def s_verdict(im, d, t):
    topline(d, t, "IS IT A DEAL? · WHAT THE DATA CAN AND CAN'T SAY", T0["b6"]+0.15)
    a1 = ease((t-(anchor("b6","Nobody")-0.1))/0.4)
    if a1 > 0:
        glass(d, [60, 240, 1020, 520], a1, fill=(11,24,36,225), line=DIM, lw=2)
        sh(d, (90, 285), "THE HONEST PART", SMB(22), MUTE, a1, anch="lm")
        sh(d, (90, 345), "THE AD SAYS “NEW PANEL” OUT LOUD", BCB(42), OFF, a1, anch="lm")
        ra = ease((t-(anchor("b6","asking")-0.1))/0.4)
        sh(d, (90, 410), "ASKING PRICES, NOT SALES", BCS(32), OFF, ra, anch="lm")
        sh(d, (90, 460), "THE JULY PURCHASE PRICE IS NOT PUBLIC · FAIR VALUE IS A MODEL, NOT AN APPRAISAL", SMR(16), MUTE, ra, anch="lm")
    a2 = ease((t-(anchor("b6","question")-0.1))/0.4)
    if a2 > 0:
        glass(d, [60, 560, 1020, 900], a2, fill=(11,24,36,230), line=CYAN, lw=3)
        sh(d, (540, 615), "THE QUESTION IS YOURS", SMR(22), MUTE, a2)
        sh(d, (540, 700), "A PANEL YOU DIDN'T PICK", BCB(64), OFF, a2)
        qa = ease((t-(anchor("b6","worth")-0.1))/0.4)
        sh(d, (540, 800), "WORTH " + counter(0, 56000, anchor("b6","fifty")-0.1, 0.8, t, "${:,.0f}") + "?", SMB(64), CYAN, qa)
    a3 = ease((t-(anchor("b6","shows")-0.15))/0.4)
    if a3 > 0:
        glass(d, [60, 940, 1020, 1340], a3, fill=(11,24,36,238), line=CYAN, lw=3)
        lg = Image.open(f"{ROOT}/assets/logo.png").resize((50, 50), Image.LANCZOS)
        if a3 > 0.5: im.paste(lg, (90, 962), lg)
        d = ImageDraw.Draw(im, "RGBA")
        sh(d, (155, 987), "NEXTPLANE · PRICE HISTORY BY TAIL NUMBER", BCB(32), OFF, a3, anch="lm")
        d.line([90, 1025, 990, 1025], fill=(*DIM, int(160*a3)), width=2)
        rows = [("APR 2026", "AD #1 · BROKER", "$109,000", MUTE, anchor("b6","shows")-0.1),
                ("JUL 8, 2026", "FAA · OWNER CHANGE", "NEW OWNER", OFF, anchor("b6","September")-0.2),
                ("SEP 1, 2026", "AD #2 · OWNER", "$165,000", CYAN, anchor("b6","tail")-0.1)]
        for j, (dt, what, val, col, at) in enumerate(rows):
            ra = ease((t-at)/0.35)
            if ra <= 0: continue
            y = 1050 + j*78
            d.rounded_rectangle([90, y, 990, y+66], radius=12, fill=(18,36,52,int(220*ra)), outline=(*(AMBER if j == 0 else DIM), int(170*ra)), width=2)
            sh(d, (110, y+33), dt, SMB(22), col, ra, anch="lm")
            sh(d, (360, y+33), what, BCS(30), OFF, ra, anch="lm")
            sh(d, (975, y+33), val, SMB(26), col, ra, anch="rm")
        ea = ease((t-(anchor("b6","remembers")-0.1))/0.4)
        sh(d, (540, 1300), "THE AD SHOWS SEPTEMBER. THE TAIL NUMBER REMEMBERS APRIL.", BCS(28), CYAN, ea)

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

SCENE_FN = {"b1": s_hook, "b2": s_registry, "b3": s_diff, "b4": s_peers, "b5": s_fair, "b6": s_verdict, "b7": s_end}
BG = {"b1": ("hbpig", 1.0, 1.12, 0.46, 0.50), "b2": ("exxd", 1.12, 1.0, 0.42, 0.58), "b3": ("navypanel", 1.0, 1.10, 0.36, 0.64),
      "b4": ("erro", 1.10, 1.0, 0.40, 0.60), "b5": ("oldpanel", 1.0, 1.08, 0.30, 0.72), "b6": ("exxd2", 1.08, 1.0, 0.38, 0.62)}

def frame(i):
    t = i / FPS
    name, t0, t1 = next(s for s in SC if s[1] <= t < s[2] or s is SC[-1] and t >= s[1])
    p = (t - t0) / max(t1 - t0, 0.01)
    if name in BG:
        slug, z0, z1, dk, tn = BG[name]
        im = bg_photo(slug, p, zoom0=z0, zoom1=z1, dark=dk, tint=tn)
        if name != "b5": im = vignette(im)
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
