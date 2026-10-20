#!/usr/bin/env python3
"""NextPlane 15-second vertical (TikTok / Instagram Reels) renderer.
Usage: render15.py <video> [worker nworkers]   video in {sr20, a36, mirage, pa32, m20k, sr22t, a36cut, sr20g6, liq*}
       render15.py <video> info                 -> timeline JSON (used by gen_music.py / mux15.py)
Layout respects platform UI safe zones: text inside x 64..940, y 210..1440."""
import json, os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
sys.path.insert(0, os.environ["KIT"] + "/lib")
from endcard import draw_endcard

ROOT = os.environ["WORK"]
KIT = os.environ["KIT"]
FD = f"{KIT}/fonts"; LOGO = f"{KIT}/assets/logo_for_dark_800.png"
W, H, FPS = 1080, 1920, 30
NAVY = (15, 42, 63); CYAN = (37, 197, 203); OFF = (246, 249, 250); WHITE = (255, 255, 255)
GREY = (160, 172, 182)

_F = {}
def F(name, size):
    k = (name, size)
    if k not in _F:
        _F[k] = ImageFont.truetype(f"{FD}/{name}", size)
    return _F[k]
BCB = lambda s: F("BarlowCondensed-Bold.ttf", s)
BCS = lambda s: F("BarlowCondensed-SemiBold.ttf", s)
SMB = lambda s: F("SpaceMono-Bold.ttf", s)
SMR = lambda s: F("SpaceMono-Regular.ttf", s)

def ease(p):
    p = min(max(p, 0.0), 1.0); return p * p * (3 - 2 * p)
def eout(p):
    p = min(max(p, 0.0), 1.0); return 1 - (1 - p) ** 3
def lerp(a, b, p): return a + (b - a) * p
def money(v): return "${:,.0f}".format(v)

# ---------------- timeline from VO ----------------
V = sys.argv[1]
VO = f"{ROOT}/vo"
BEATS = [f"{V}_b{i}" for i in (1, 2, 3)]
WD = {b: json.load(open(f"{VO}/{b}.json")) for b in BEATS}
GAP = {1: 0.30, 2: 1.20} if V.startswith("liq") else {1: 0.30, 2: 0.85}   # liq: room for the silent verdict word
OFFS = {}; t = 0.15
for i, b in enumerate(BEATS):
    OFFS[b] = t
    t += WD[b]["dur"] + GAP.get(i + 1, 0)
def wt(bi, wi, end=False):
    b = BEATS[bi - 1]; w = WD[b]["words"][wi]
    return OFFS[b] + (w["e"] if end else w["s"])
T_B2 = OFFS[BEATS[1]] - 0.12
T_LOOK = OFFS[BEATS[2]] - 0.70
_w3 = [w["w"] for w in WD[BEATS[2]]["words"]]
CTA0 = _w3.index("Before")                    # beat 3 may open with extra words ("Check yours." in liq clips)
CHK = next(i for i in range(CTA0, len(_w3)) if _w3[i].lower() == "check")
T_END = wt(3, CHK) - 0.12                    # "check the data at NextPlane.us"
TOTAL = max(OFFS[BEATS[2]] + WD[BEATS[2]]["dur"] + 0.75, T_END + 2.95)
TOTAL = round(TOTAL * FPS) / FPS
NF = int(TOTAL * FPS)

# ---------------- captions ----------------
CAPS = {
 "sr20": [(1, "$354,900", 0, 2), (1, "for this Cirrus SR20", 3, 8),
          (2, "Twelve days ago,", 0, 2), (2, "same airplane, same hours:", 3, 6), (2, "$279,900", 7, 9)],
 "a36": [(1, "Two A36 Bonanzas.", 0, 2), (1, "Both $299,000.", 3, 5),
         (2, "One hasn't moved since April.", 0, 4), (2, "The other was $290,000 in August,", 5, 11),
         (2, "then went up.", 12, 14)],
 "mirage": [(1, "$550,000,", 0, 1), (1, "for the lowest-time Malibu Mirage on the market,", 2, 9),
            (1, "says the ad.", 10, 12), (2, "What it leaves out:", 0, 3), (2, "a 2020 NTSB report.", 4, 11),
            (2, "Substantial damage.", 12, 13)],
 "pa32": [(1, "$142,000", 0, 4), (1, "for this Piper Cherokee Six", 5, 9),
          (2, "In July, same seller, same hours:", 0, 5), (2, "$192,000", 6, 9),
          (2, "The new ad doesn't say.", 10, 14)],
 "m20k": [(1, "Two Mooney 231s.", 0, 3), (1, "Both $149,000.", 4, 9),
          (2, "One was cut twice.", 0, 3), (2, "The other has", 4, 6), (2, "a federal accident record", 7, 10),
          (2, "from 1984.", 11, 13)],
 "sr22t": [(1, "$798,900,", 0, 4), (1, "for a meticulously maintained", 5, 8),
           (1, "Cirrus SR22T, says the ad.", 9, 15), (2, "What it leaves out:", 0, 3),
           (2, "a 2024 federal accident record.", 4, 9), (2, "Substantial damage.", 10, 11)],
 "sr20g6": [(1, "Two Cirrus SR20s.", 0, 4), (1, "Both $489,900.", 5, 11),
            (2, "The newer one has", 0, 3), (2, "less than half the hours", 4, 8), (2, "and was cut twice.", 9, 12),
            (2, "The other hasn't moved", 13, 16), (2, "since April.", 17, 18)],
 "a36cut": [(1, "$229,000", 0, 4), (1, "for this Beechcraft Bonanza A36", 5, 9),
            (2, "In August, the same ad asked", 0, 5), (2, "$310,000.", 6, 9),
            (2, "It's been cut three times.", 10, 14)],
 "liq172m": [(1, "Is a Cessna 172M liquid?", 0, 6),
             (2, "A month on the market,", 0, 4), (2, "and most sellers", 5, 7), (2, "never touch the price.", 8, 11),
             (2, "Every flight school wants one.", 12, 16), (3, "Check yours.", 0, 1)],
 "liq182p": [(1, "Is a Cessna 182P Skylane", 0, 6), (1, "liquid?", 7, 7),
             (2, "About six and a half weeks", 0, 5), (2, "to sell.", 6, 7),
             (2, "Nine in ten sell", 8, 11), (2, "without a price cut.", 12, 15), (3, "Check yours.", 0, 1)],
}[V] + [(3, "Before you call the broker,", CTA0, CTA0 + 4)]

def draw_caption(im, tt):
    d = ImageDraw.Draw(im, "RGBA")
    for bi, txt, a, z in CAPS:
        s = wt(bi, a) - 0.05; e = wt(bi, z, True) + 0.18
        if s <= tt < e:
            f = BCS(62)
            words = txt.split(); lines = []; cur = ""
            for w_ in words:
                tst = (cur + " " + w_).strip()
                if d.textlength(tst, font=f) > 820 and cur: lines.append(cur); cur = w_
                else: cur = tst
            lines.append(cur)
            y = 1400 - (len(lines) - 1) * 36
            pa = ease((tt - s) / 0.12)
            for ln in lines:
                tw = d.textlength(ln, font=f)
                x0 = W / 2 - tw / 2 - 22; x1 = W / 2 + tw / 2 + 22
                d.rounded_rectangle([x0, y - 40, x1, y + 38], radius=14, fill=(8, 20, 31, int(205 * pa)))
                d.text((W / 2, y), ln, font=f, fill=(*WHITE, int(255 * pa)), anchor="mm")
                y += 74
            return

# ---------------- backgrounds ----------------
_BG = {}
def bg_layer(path, focus, dark=0.55, sat=0.75, size=(W, H), wfrac=1.0):
    k = (path, focus, dark, size, wfrac)
    if k in _BG: return _BG[k]
    src = Image.open(path).convert("RGB")
    bw, bh = int(size[0] * 1.14), int(size[1] * 1.14)
    sr = src.width / src.height; tr = bw / bh
    if wfrac < 1.0:
        nw = int(src.width * wfrac); nh = int(nw / tr)
        cx = int(focus * src.width); x0 = min(max(cx - nw // 2, 0), src.width - nw)
        y0 = min(max(int(src.height * 0.55) - nh // 2, 0), src.height - nh)
        crop = src.crop((x0, y0, x0 + nw, y0 + nh))
    elif sr > tr:
        nh = src.height; nw = int(nh * tr)
        cx = int(focus * src.width); x0 = min(max(cx - nw // 2, 0), src.width - nw)
        crop = src.crop((x0, 0, x0 + nw, nh))
    else:
        nw = src.width; nh = int(nw / tr); y0 = (src.height - nh) // 2
        crop = src.crop((0, y0, nw, y0 + nh))
    im = crop.resize((bw, bh), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Brightness(im).enhance(dark)
    # navy grade
    navy = Image.new("RGB", im.size, NAVY)
    im = Image.blend(im, navy, 0.22)
    _BG[k] = im
    return im

def paste_bg(im, layer, tt, t0, dur, box=(0, 0), zoom_in=True, size=(W, H)):
    p = min(max((tt - t0) / max(dur, 0.1), 0), 1)
    z = lerp(1.0, 1.10, p) if zoom_in else lerp(1.10, 1.0, p)
    cw, ch = int(size[0] * 1.14 / z), int(size[1] * 1.14 / z)
    lx, ly = layer.size
    x0 = (lx - cw) // 2; y0 = (ly - ch) // 2
    fr = layer.crop((x0, y0, x0 + cw, y0 + ch)).resize(size, Image.BILINEAR)
    im.paste(fr, box)

def gradient(im, top=0.55, bottom=0.85):
    g = Image.new("RGBA", (1, H))
    for y in range(H):
        a = 0
        if y < 520: a = top * (1 - y / 520)
        if y > 1100: a = max(a, bottom * (y - 1100) / (H - 1100))
        g.putpixel((0, y), (*NAVY, int(255 * a)))
    return g.resize((W, H))
GRAD = None

# ---------------- UI pieces ----------------
_LG = {}
def logo(sz):
    if sz not in _LG: _LG[sz] = Image.open(LOGO).convert("RGBA").resize((sz, sz), Image.LANCZOS)
    return _LG[sz]

def brand_bug(im, a=1.0):
    lg = logo(58)
    if a < 1:
        lg = lg.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
    im.paste(lg, (70, 222), lg)
    d = ImageDraw.Draw(im, "RGBA")
    d.text((140, 251), "NEXTPLANE", font=BCB(44), fill=(*OFF, int(235 * a)), anchor="lm")

def chip(d, x, y, txt, a=1.0, fill=None, outline=CYAN, col=CYAN, f=None, anchor="l"):
    f = f or SMB(30)
    tw = d.textlength(txt, font=f)
    if anchor == "c": x = x - (tw + 44) / 2
    d.rounded_rectangle([x, y - 30, x + tw + 44, y + 30], radius=30,
                        fill=(*(fill or (8, 20, 31)), int(200 * a)), outline=(*outline, int(255 * a)), width=3)
    d.text((x + 22, y), txt, font=f, fill=(*col, int(255 * a)), anchor="lm")
    return tw + 44

def shadow_text(d, xy, txt, f, fill, a=1.0, anchor="mm", sh=4):
    d.text((xy[0] + sh, xy[1] + sh), txt, font=f, fill=(0, 0, 0, int(160 * a)), anchor=anchor)
    d.text(xy, txt, font=f, fill=(*fill, int(255 * a)), anchor=anchor)

def panel(d, box, a=1.0, title="NEXTPLANE REPORT", sub=None):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=28, fill=(10, 30, 46, int(232 * a)), outline=(*CYAN, int(150 * a)), width=2)
    d.text((x0 + 36, y0 + 46), title, font=SMB(28), fill=(*CYAN, int(255 * a)), anchor="lm")
    if sub:
        d.text((x1 - 36, y0 + 46), sub, font=SMR(26), fill=(*GREY, int(255 * a)), anchor="rm")
    d.line([x0 + 36, y0 + 84, x1 - 36, y0 + 84], fill=(*CYAN, int(70 * a)), width=2)

def stamp(im, cx, cy, txt, a, ang=-8, col=CYAN, size=76):
    if a <= 0: return
    f = BCB(size)
    tmp = Image.new("RGBA", (900, 220), (0, 0, 0, 0)); dd = ImageDraw.Draw(tmp)
    tw = dd.textlength(txt, font=f)
    dd.rounded_rectangle([450 - tw / 2 - 30, 110 - 58, 450 + tw / 2 + 30, 110 + 58], radius=12,
                         outline=(*col, 255), width=7, fill=(8, 20, 31, 200))
    dd.text((450, 112), txt, font=f, fill=(*col, 255), anchor="mm")
    sc = lerp(1.5, 1.0, eout(a))
    tmp = tmp.rotate(ang, resample=Image.BICUBIC, expand=True)
    tmp = tmp.resize((int(tmp.width * sc), int(tmp.height * sc)), Image.BILINEAR)
    if a < 1: tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * min(a * 2, 1))))
    im.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)

def lookup(im, tt, t0, tails):
    """Report lookup card: plug in the N-number."""
    d = ImageDraw.Draw(im, "RGBA")
    a = ease((tt - t0) / 0.25)
    yoff = lerp(60, 0, eout((tt - t0) / 0.3))
    x0, x1 = 70, 940; y0 = 520 + yoff
    d.rounded_rectangle([x0, y0, x1, y0 + 560], radius=28, fill=(246, 249, 250, int(245 * a)))
    d.rounded_rectangle([x0, y0, x1, y0 + 74], radius=28, fill=(226, 232, 236, int(255 * a)))
    d.rectangle([x0, y0 + 46, x1, y0 + 74], fill=(226, 232, 236, int(255 * a)))
    for i, c in enumerate([(236, 106, 94), (245, 190, 79), (98, 197, 84)]):
        d.ellipse([x0 + 30 + i * 34, y0 + 26, x0 + 52 + i * 34, y0 + 48], fill=(*c, int(255 * a)))
    d.rounded_rectangle([x0 + 150, y0 + 16, x1 - 30, y0 + 58], radius=20, fill=(255, 255, 255, int(255 * a)))
    d.text((x0 + 172, y0 + 37), "nextplane.us/aircraft-report", font=SMR(26), fill=(70, 80, 90, int(255 * a)), anchor="lm")
    d.text((W / 2, y0 + 160), "PLUG IN THE N-NUMBER", font=BCB(72), fill=(*NAVY, int(255 * a)), anchor="mm")
    # input + typing
    full = "  ".join(tails)
    n = int(len(full) * min(max((tt - t0 - 0.25) / 0.55, 0), 1))
    txt = full[:n]
    d.rounded_rectangle([x0 + 60, y0 + 250, x1 - 60, y0 + 370], radius=18, fill=(255, 255, 255, int(255 * a)),
                        outline=(*CYAN, int(255 * a)), width=4)
    d.text((x0 + 96, y0 + 312), txt, font=SMB(64), fill=(*NAVY, int(255 * a)), anchor="lm")
    if int(tt * 3) % 2 == 0:
        cx = x0 + 96 + d.textlength(txt, font=SMB(64)) + 6
        d.rectangle([cx, y0 + 278, cx + 5, y0 + 346], fill=(*NAVY, int(255 * a)))
    pa = ease((tt - t0 - 0.85) / 0.2)
    pr = 1 - 0.06 * math.sin(min(max((tt - t0 - 1.05) / 0.25, 0), 1) * math.pi)
    bw_, bh_ = 420 * pr, 100 * pr
    d.rounded_rectangle([W / 2 - bw_ / 2, y0 + 450 - bh_ / 2, W / 2 + bw_ / 2, y0 + 450 + bh_ / 2], radius=50,
                        fill=(*CYAN, int(255 * a * max(pa, 0.35))))
    d.text((W / 2, y0 + 452), "GET THE REPORT", font=BCB(50), fill=(*NAVY, int(255 * a)), anchor="mm")

# ---------------- step chart ----------------
def step_chart(d, box, pts, t_from, t_to, tt, ymin, ymax, a=1.0, hi_last=True, labels=True, lw=7):
    """pts: list of (xfrac, price, label). Draws a step line revealed from t_from to t_to."""
    x0, y0, x1, y1 = box
    def X(f): return x0 + f * (x1 - x0)
    def Y(v): return y1 - (v - ymin) / (ymax - ymin) * (y1 - y0)
    p = min(max((tt - t_from) / max(t_to - t_from, 0.01), 0), 1)
    segs = []
    for i in range(len(pts) - 1):
        fa, va, _ = pts[i]; fb, vb, _ = pts[i + 1]
        segs.append(((X(fa), Y(va)), (X(fb), Y(va)), False))
        if vb != va: segs.append(((X(fb), Y(va)), (X(fb), Y(vb)), vb > va))
    fl, vl, _ = pts[-1]
    segs.append(((X(fl), Y(vl)), (X(1.0), Y(vl)), False))
    L = [math.dist(s[0], s[1]) for s in segs]; tot = sum(L); left = tot * p
    for (a_, b_, up), l in zip(segs, L):
        if left <= 0: break
        q = min(left / l, 1) if l else 1
        e = (lerp(a_[0], b_[0], q), lerp(a_[1], b_[1], q))
        col = WHITE if up else CYAN
        d.line([a_, e], fill=(*col, int(255 * a)), width=lw + (4 if up else 0))
        left -= l
    if labels:
        acc = 0
        for i, (f_, v_, lab) in enumerate(pts):
            # reveal label when the line reaches the point
            pos = sum(L[:2 * i]) if i else 0
            la = ease((tot * p - pos) / 40)
            if la > 0:
                d.ellipse([X(f_) - 9, Y(v_) - 9, X(f_) + 9, Y(v_) + 9], fill=(*OFF, int(255 * la * a)))
                nx = pts[i + 1][0] if i + 1 < len(pts) else 1.0
                mx = (X(f_) + X(nx)) / 2
                if lab is not False:
                    d.text((mx, Y(v_) - 22), money(v_), font=SMB(28), fill=(*OFF, int(255 * la * a)), anchor="ms")
                if lab:
                    d.text((X(f_), y1 + 44), lab, font=SMR(24), fill=(*GREY, int(255 * la * a)), anchor="ms")
    return X, Y

def punch(im, xy, txt, f, tt, t0, fade=1.0):
    """Full value visible from first frame; scale punch 1.18 -> 1.0."""
    sc = lerp(1.18, 1.0, eout((tt - t0) / 0.35))
    d0 = ImageDraw.Draw(im)
    tw = int(d0.textlength(txt, font=f)) + 40; th = f.size + 60
    tmp = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); dd = ImageDraw.Draw(tmp)
    dd.text((tw / 2 + 5, th / 2 + 5), txt, font=f, fill=(0, 0, 0, 160), anchor="mm")
    dd.text((tw / 2, th / 2), txt, font=f, fill=(255, 255, 255, 255), anchor="mm")
    if sc != 1: tmp = tmp.resize((int(tw * sc), int(th * sc)), Image.BILINEAR)
    if fade < 1: tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * fade)))
    im.paste(tmp, (int(xy[0] - tmp.width / 2), int(xy[1] - tmp.height / 2)), tmp)

def counter(v_to, tt, t0, dur=0.45, v_from=0):
    return lerp(v_from, v_to, eout((tt - t0) / dur))

# ---------------- per-video scenes ----------------
PH = f"{ROOT}/photos"

def scene_sr20(im, tt):
    d = ImageDraw.Draw(im, "RGBA")
    if tt < T_B2 + 0.3:
        L = bg_layer(f"{PH}/sr20-4.jpg", 0.47, dark=0.62)
        paste_bg(im, L, tt, 0, T_B2 + 0.3)
    else:
        L = bg_layer(f"{PH}/sr20-3.jpg", 0.5, dark=0.42)
        paste_bg(im, L, tt, T_B2, T_LOOK - T_B2, zoom_in=False)
    im.alpha_composite(GRAD)
    d = ImageDraw.Draw(im, "RGBA")
    brand_bug(im)
    if tt < T_B2 + 0.25:
        fade = 1 - ease((tt - T_B2) / 0.25)
        chip(d, W / 2, 360, "FOR SALE NOW", fade, anchor="c")
        shadow_text(d, (W / 2, 470), "2012 CIRRUS SR20", BCB(84), OFF, fade)
        punch(im, (W / 2, 660), "$354,900", BCB(236), tt, 0.0, fade); d = ImageDraw.Draw(im, "RGBA")
        la = ease((tt - wt(1, 5)) / 0.2) * fade
        if la > 0:
            d.rounded_rectangle([200, 820, 880, 900], radius=16, fill=(8, 20, 31, int(190 * la)))
            d.text((W / 2, 860), "DEALER AD · LISTED SEP 27", font=SMB(32), fill=(*GREY, int(255 * la)), anchor="mm")
    else:
        a = ease((tt - T_B2 - 0.1) / 0.3) * (1 - ease((tt - T_LOOK) / 0.2))
        if a <= 0: return
        yo = lerp(40, 0, eout((tt - T_B2 - 0.1) / 0.35))
        panel(d, (64, 330 + yo, 948, 1230 + yo), a, sub="PRICE HISTORY")
        pts = [(0.0, 294900, "APR"), (0.20, 284900, "MAY"), (0.55, 279900, "AUG"), (0.80, 354900, "SEP 27")]
        X, Y = step_chart(d, (110, 560 + yo, 900, 1010 + yo), pts, T_B2 + 0.2, wt(2, 9, True), tt,
                          262000, 372000, a)
        # +75,000 bracket
        ba = ease((tt - wt(2, 7)) / 0.3) * a
        if ba > 0:
            xb = X(0.80) - 44; ya, yb = Y(279900) - 40, Y(354900)
            d.line([xb + 18, ya, xb + 18, yb], fill=(*CYAN, int(255 * ba)), width=4)
            d.line([xb + 18, yb, xb + 34, yb], fill=(*CYAN, int(255 * ba)), width=4)
            v = counter(75000, tt, wt(2, 7), 0.5)
            d.rounded_rectangle([xb - 250, (ya + yb) / 2 - 36, xb - 6, (ya + yb) / 2 + 36], radius=12,
                                fill=(8, 20, 31, int(230 * ba)))
            d.text((xb - 128, (ya + yb) / 2), "+" + money(round(v / 100) * 100), font=BCB(58),
                   fill=(*CYAN, int(255 * ba)), anchor="mm")
        c1 = ease((tt - wt(2, 3)) / 0.2) * a; c2 = ease((tt - wt(2, 5)) / 0.2) * a
        if c1 > 0: chip(d, 110, 1150 + yo, "SAME AIRPLANE", c1, f=SMB(28))
        if c2 > 0: chip(d, 450, 1150 + yo, "SAME 4,120 HOURS", c2, f=SMB(28))

def scene_a36(im, tt):
    HH = 960
    dark = 0.6 if tt < T_B2 else 0.38
    LA = bg_layer(f"{PH}/a36c-0.jpg", 0.27, dark=dark, size=(W, HH), wfrac=0.58)
    LB = bg_layer(f"{PH}/a36d-0.jpg", 0.40, dark=dark, size=(W, HH), wfrac=0.62)
    paste_bg(im, LA, tt, 0, T_LOOK, size=(W, HH), box=(0, 0))
    paste_bg(im, LB, tt, 0, T_LOOK, size=(W, HH), box=(0, HH), zoom_in=False)
    im.alpha_composite(GRAD)
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, HH - 3, W, HH + 3], fill=(*CYAN, 255))
    brand_bug(im)
    fade = 1 - ease((tt - T_LOOK) / 0.2)
    if fade <= 0: return
    # labels
    for yy, lab in ((360, "A · 1976 A36 BONANZA"), (1040, "B · 1977 A36 BONANZA")):
        d.rounded_rectangle([70, yy - 34, 70 + d.textlength(lab, font=SMB(30)) + 40, yy + 34], radius=12,
                            fill=(8, 20, 31, int(200 * fade)))
        d.text((90, yy), lab, font=SMB(30), fill=(*OFF, int(255 * fade)), anchor="lm")
    if tt < T_B2 + 0.25:
        pf = (1 - ease((tt - T_B2) / 0.25)) * fade
        t0 = wt(1, 3)
        for yy in (560, 1240):
            v = counter(299000, tt, t0 - 0.1, 0.45)
            if tt > t0 - 0.15:
                shadow_text(d, (W / 2, yy), money(round(v / 100) * 100), BCB(190), WHITE, pf)
        stamp(im, W / 2, HH, "SAME PRICE", ease((tt - wt(1, 5, True) + 0.1) / 0.25) * pf)
    else:
        a = ease((tt - T_B2) / 0.3) * fade
        # A: flat line
        aa = ease((tt - wt(2, 0)) / 0.3) * a
        if aa > 0:
            panel(d, (64, 430, 948, 860), aa, sub="PRICE HISTORY · A")
            step_chart(d, (120, 600, 880, 740), [(0.0, 299000, "APR")],
                       wt(2, 0), wt(2, 4, True), tt, 280000, 330000, aa, labels=True)
            d.text((W / 2, 812), "UNCHANGED SINCE APRIL", font=BCB(46), fill=(*CYAN, int(255 * aa)), anchor="mm")
        ab = ease((tt - wt(2, 5)) / 0.3) * a
        if ab > 0:
            panel(d, (64, 1000, 948, 1330), ab, sub="PRICE HISTORY · B")
            X, Y = step_chart(d, (120, 1140, 880, 1240),
                              [(0.0, 325000, "JUN 2"), (0.18, 290000, None), (0.70, 299000, "AUG 23")],
                              wt(2, 5), wt(2, 14, True), tt, 280000, 335000, ab)
            ua = ease((tt - wt(2, 12)) / 0.3) * ab
            if ua > 0:
                d.text((900, 1112), "+$9,000 IN AUGUST", font=BCB(46), fill=(*CYAN, int(255 * ua)), anchor="rm")

def scene_mirage(im, tt):
    if tt < T_B2 + 0.3:
        L = bg_layer(f"{PH}/mirage-3.jpg", 0.17, dark=0.62)
        paste_bg(im, L, tt, 0, T_B2 + 0.3)
    else:
        L = bg_layer(f"{PH}/mirage-2.jpg", 0.78, dark=0.40)
        paste_bg(im, L, tt, T_B2, T_LOOK - T_B2, zoom_in=False)
    im.alpha_composite(GRAD)
    d = ImageDraw.Draw(im, "RGBA")
    brand_bug(im)
    if tt < T_B2 + 0.25:
        fade = 1 - ease((tt - T_B2) / 0.25)
        shadow_text(d, (W / 2, 400), "2002 PIPER MALIBU MIRAGE", BCB(74), OFF, fade)
        punch(im, (W / 2, 580), "$550,000", BCB(236), tt, 0.0, fade); d = ImageDraw.Draw(im, "RGBA")
        qa = ease((tt - wt(1, 2)) / 0.25) * fade
        if qa > 0:
            yo = lerp(30, 0, eout((tt - wt(1, 2)) / 0.3))
            d.rounded_rectangle([90, 740 + yo, 930, 1010 + yo], radius=22, fill=(226, 232, 236, int(235 * qa)))
            d.text((130, 790 + yo), "FROM THE AD", font=SMB(26), fill=(90, 100, 110, int(255 * qa)), anchor="lm")
            d.text((130, 870 + yo), "“Lowest Time Malibu Mirage", font=BCS(60), fill=(*NAVY, int(255 * qa)), anchor="lm")
            d.text((130, 940 + yo), "on the market!”", font=BCS(60), fill=(*NAVY, int(255 * qa)), anchor="lm")
        ha = ease((tt - wt(1, 7)) / 0.25) * fade
        if ha > 0:
            chip(d, W / 2, 1090, "1,185 HOURS SINCE NEW", ha, anchor="c", f=SMB(32))
    else:
        a = ease((tt - T_B2 - 0.1) / 0.3) * (1 - ease((tt - T_LOOK) / 0.2))
        if a <= 0: return
        yo = lerp(40, 0, eout((tt - T_B2 - 0.1) / 0.35))
        panel(d, (64, 360 + yo, 948, 1130 + yo), a, sub="SAFETY RECORD")
        r1 = ease((tt - wt(2, 4)) / 0.3) * a
        if r1 > 0:
            d.text((110, 520 + yo), "NTSB  CEN20CA232", font=SMB(34), fill=(*GREY, int(255 * r1)), anchor="lm")
            d.text((110, 610 + yo), "JUN 16, 2020", font=BCB(96), fill=(*WHITE, int(255 * r1)), anchor="lm")
            d.text((110, 700 + yo), "ELY, MINNESOTA · SERIAL MATCH", font=SMB(30), fill=(*OFF, int(255 * r1)), anchor="lm")
        r2 = ease((tt - wt(2, 12)) / 0.25) * a
        if r2 > 0:
            d.text((110, 800 + yo), "DAMAGE", font=SMB(30), fill=(*GREY, int(255 * r2)), anchor="lm")
            d.text((110, 880 + yo), "SUBSTANTIAL", font=BCB(110), fill=(*CYAN, int(255 * r2)), anchor="lm")
        stamp(im, 620, 1040 + yo, "NOT IN THE AD", ease((tt - wt(2, 12) - 0.35) / 0.25) * a, ang=-6, col=WHITE, size=68)

_BB = {}
def blur_backdrop(path, dark=0.45, radius=18):
    """Full-bleed blurred, darkened backdrop for landscape photos too small to fill 1080x1920 sharply."""
    k = (path, dark, radius)
    if k not in _BB:
        src = Image.open(path).convert("RGB")
        tr = W / H; nh = src.height; nw = int(nh * tr)
        x0 = (src.width - nw) // 2
        im = src.crop((x0, 0, x0 + nw, nh)).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius))
        im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.7)).enhance(dark)
        _BB[k] = Image.blend(im, Image.new("RGB", (W, H), NAVY), 0.25).convert("RGBA")
    return _BB[k]

def photo_card(im, path, box, tt, t0, dur, sat=0.9):
    """Sharp landscape photo card (slow push-in) inside box=(x0,y0,x1,y1)."""
    x0, y0, x1, y1 = [int(v) for v in box]; bw, bh = x1 - x0, y1 - y0
    k = ("card", path, bw, bh)
    if k not in _BB:
        src = Image.open(path).convert("RGB"); sr = src.width / src.height; tr = bw / bh
        if sr > tr:
            nw = int(src.height * tr); c = src.crop(((src.width - nw) // 2, 0, (src.width - nw) // 2 + nw, src.height))
        else:
            nh = int(src.width / tr); c = src.crop((0, (src.height - nh) // 2, src.width, (src.height - nh) // 2 + nh))
        c = ImageEnhance.Color(c.resize((int(bw * 1.08), int(bh * 1.08)), Image.LANCZOS)).enhance(sat)
        _BB[k] = c
    L = _BB[k]
    z = lerp(1.0, 1.08, min(max((tt - t0) / max(dur, 0.1), 0), 1))
    cw, ch = int(L.width / z), int(L.height / z)
    fr = L.crop(((L.width - cw) // 2, (L.height - ch) // 2, (L.width - cw) // 2 + cw, (L.height - ch) // 2 + ch)).resize((bw, bh), Image.BILINEAR)
    m = Image.new("L", (bw, bh), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=26, fill=255)
    im.paste(fr, (x0, y0), m)
    ImageDraw.Draw(im, "RGBA").rounded_rectangle([x0, y0, x1, y1], radius=26, outline=(*CYAN, 160), width=3)

def scene_pa32(im, tt):
    """PRICE JUMP (down): N123BE, same dealer, same hours, $192,000 (Jul 9-Aug 7) -> $142,000 (Oct 9)."""
    hook = tt < T_B2 + 0.3
    im.alpha_composite(blur_backdrop(f"{PH}/pa32-0.jpg" if hook else f"{PH}/pa32-1.jpg", 0.5 if hook else 0.36))
    im.alpha_composite(GRAD)
    d = ImageDraw.Draw(im, "RGBA")
    brand_bug(im)
    if tt < T_B2 + 0.25:
        fade = 1 - ease((tt - T_B2) / 0.25)
        chip(d, W / 2, 360, "FOR SALE NOW", fade, anchor="c")
        shadow_text(d, (W / 2, 460), "1967 PIPER CHEROKEE SIX", BCB(80), OFF, fade)
        punch(im, (W / 2, 640), "$142,000", BCB(236), tt, 0.0, fade)
        if fade > 0.02:
            card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            photo_card(card, f"{PH}/pa32-0.jpg", (70, 800, 1010, 1197), tt, 0, T_B2)
            if fade < 1: card.putalpha(card.getchannel("A").point(lambda v: int(v * fade)))
            im.alpha_composite(card)
        d = ImageDraw.Draw(im, "RGBA")
        la = ease((tt - wt(1, 5)) / 0.2) * fade
        if la > 0:
            chip(d, W / 2, 1250, "DEALER AD · LISTED OCT 9", la, anchor="c", f=SMB(30), col=OFF, outline=GREY)
        return
    a = ease((tt - T_B2 - 0.1) / 0.3) * (1 - ease((tt - T_LOOK) / 0.2))
    if a <= 0: return
    yo = lerp(40, 0, eout((tt - T_B2 - 0.1) / 0.35))
    panel(d, (64, 330 + yo, 948, 1230 + yo), a, sub="PRICE HISTORY")
    x0, x1, y0, y1 = 120, 890, 560 + yo, 1000 + yo
    X = lambda f: x0 + f * (x1 - x0)
    Y = lambda v: y1 - (v - 120000) / (210000 - 120000) * (y1 - y0)
    # ad 1: Jul 9 -> Aug 7 at $192,000 (white); off market Aug 7 -> Oct 9 (dashed); ad 2: Oct 9 -> now at $142,000 (cyan)
    p1 = min(max((tt - wt(2, 0)) / 0.5, 0), 1)
    if p1 > 0:
        d.line([(X(0), Y(192000)), (X(lerp(0, 0.36, p1)), Y(192000))], fill=(*WHITE, int(255 * a)), width=8)
        d.ellipse([X(0) - 9, Y(192000) - 9, X(0) + 9, Y(192000) + 9], fill=(*OFF, int(255 * a)))
        d.text((X(0), y1 + 46), "JUL 9", font=SMR(26), fill=(*GREY, int(255 * a)), anchor="ls")
    la = ease((tt - wt(2, 6)) / 0.25) * a
    if la > 0:
        d.text((X(0.18), Y(192000) - 26), "$192,000", font=SMB(34), fill=(*OFF, int(255 * la)), anchor="ms")
        d.text((X(0.36), y1 + 46), "AUG 7", font=SMR(26), fill=(*GREY, int(255 * la)), anchor="ms")
    p2 = min(max((tt - wt(2, 6)) / 0.6, 0), 1)
    if p2 > 0:
        xe = lerp(0.36, 0.72, p2); xx = 0.36
        while xx < xe:
            d.line([(X(xx), Y(192000)), (X(min(xx + 0.018, xe)), Y(192000))], fill=(*GREY, int(200 * a)), width=4); xx += 0.036
        if p2 > 0.4:
            d.text((X(0.54), Y(192000) + 44), "OFF THE MARKET", font=SMR(24), fill=(*GREY, int(255 * a * ease((p2 - 0.4) / 0.3))), anchor="mm")
    p3 = min(max((tt - wt(2, 9, True)) / 0.45, 0), 1)
    if p3 > 0:
        yd = lerp(Y(192000), Y(142000), eout(min(p3 * 2, 1)))
        d.line([(X(0.72), Y(192000)), (X(0.72), yd)], fill=(*CYAN, int(255 * a)), width=8)
        if p3 > 0.5:
            d.line([(X(0.72), Y(142000)), (X(lerp(0.72, 1.0, (p3 - 0.5) * 2)), Y(142000))], fill=(*CYAN, int(255 * a)), width=8)
            d.ellipse([X(0.72) - 9, Y(142000) - 9, X(0.72) + 9, Y(142000) + 9], fill=(*OFF, int(255 * a)))
            d.text((X(0.86), Y(142000) - 26), "$142,000", font=SMB(34), fill=(*CYAN, int(255 * a)), anchor="ms")
            d.text((X(0.72), y1 + 46), "OCT 9", font=SMR(26), fill=(*GREY, int(255 * a)), anchor="ms")
        ba = ease((p3 - 0.3) / 0.4) * a
        if ba > 0:
            v = counter(50000, tt, wt(2, 9, True) + 0.15, 0.5)
            ym = (Y(192000) + Y(142000)) / 2
            d.rounded_rectangle([X(0.72) - 290, ym - 40, X(0.72) - 24, ym + 40], radius=12, fill=(8, 20, 31, int(230 * ba)))
            d.text((X(0.72) - 157, ym), "-" + money(round(v / 100) * 100), font=BCB(62), fill=(*CYAN, int(255 * ba)), anchor="mm")
    c1 = ease((tt - wt(2, 2)) / 0.2) * a; c2 = ease((tt - wt(2, 4)) / 0.2) * a
    if c1 > 0: chip(d, 110, 1150 + yo, "SAME SELLER", c1, f=SMB(28))
    if c2 > 0: chip(d, 400, 1150 + yo, "SAME 5,262.7 HOURS", c2, f=SMB(28))
    stamp(im, W / 2, 1290, "NOT IN THE NEW AD", ease((tt - wt(2, 12)) / 0.25) * a, ang=-4, col=WHITE, size=58)

def scene_m20k(im, tt):
    """SAME PRICE TWINS: Mooney M20K 231s at $149,000. A = N231HB (1979, cut twice from $167,500);
    B = N3594H (1980, unchanged since Apr 14; 1984 federal accident record FTW84LA341, serial 25-0428, not in the ad).
    Photos are the model (registrations blurred), not the subject tails."""
    HH = 960
    dark = 0.6 if tt < T_B2 else 0.36
    LA = bg_layer(f"{PH}/b.jpg", 0.55, dark=dark, size=(W, HH))
    LB = bg_layer(f"{PH}/a.jpg", 0.55, dark=dark, size=(W, HH))
    paste_bg(im, LA, tt, 0, T_LOOK, size=(W, HH), box=(0, 0))
    paste_bg(im, LB, tt, 0, T_LOOK, size=(W, HH), box=(0, HH), zoom_in=False)
    im.alpha_composite(GRAD)
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, HH - 3, W, HH + 3], fill=(*CYAN, 255))
    brand_bug(im)
    fade = 1 - ease((tt - T_LOOK) / 0.2)
    if fade <= 0: return
    if tt < T_B2 + 0.25:
        pf = (1 - ease((tt - T_B2) / 0.25)) * fade
        for yy, lab in ((360, "A · 1979 MOONEY 231"), (1040, "B · 1980 MOONEY 231")):
            d.rounded_rectangle([70, yy - 34, 70 + d.textlength(lab, font=SMB(30)) + 40, yy + 34], radius=12,
                                fill=(8, 20, 31, int(200 * pf)))
            d.text((90, yy), lab, font=SMB(30), fill=(*OFF, int(255 * pf)), anchor="lm")
        for yy, t0 in ((580, 0.0), (1225, 0.12)):   # price on screen from the first frame (spec)
            punch(im, (W / 2, yy), "$149,000", BCB(190), tt, t0, pf)
        stamp(im, W / 2, HH, "SAME PRICE", ease((tt - wt(1, 4)) / 0.25) * pf)
        return
    a = ease((tt - T_B2) / 0.3) * fade
    # A: cut twice, $167,500 -> $159,000 (May 14) -> $149,000 (Jun 27)
    aa = ease((tt - wt(2, 0)) / 0.3) * a
    if aa > 0:
        panel(d, (64, 400, 948, 880), aa, title="A · N231HB", sub="PRICE HISTORY")
        step_chart(d, (120, 590, 880, 770),
                   [(0.0, 167500, "APR"), (0.20, 159000, "MAY 14"), (0.50, 149000, "JUN 27")],
                   wt(2, 0), wt(2, 3, True) + 0.3, tt, 140000, 175000, aa)
        ca = ease((tt - wt(2, 2)) / 0.3) * aa
        if ca > 0:
            d.text((900, 548), "CUT TWICE · -$18,500", font=BCB(46), fill=(*CYAN, int(255 * ca)), anchor="rm")
    # B: same price since April, but a 1984 federal accident record
    ab = ease((tt - wt(2, 4)) / 0.3) * a
    if ab > 0:
        panel(d, (64, 990, 948, 1335), ab, title="B · N3594H", sub="SAFETY RECORD")
        r1 = ease((tt - wt(2, 8)) / 0.3) * ab
        if r1 > 0:
            d.text((110, 1112), "NTSB FTW84LA341", font=SMB(30), fill=(*GREY, int(255 * r1)), anchor="lm")
        r2 = ease((tt - wt(2, 12)) / 0.25) * ab
        if r2 > 0:
            d.text((110, 1185), "AUG 6, 1984", font=BCB(84), fill=(*WHITE, int(255 * r2)), anchor="lm")
            d.text((110, 1258), "SUBSTANTIAL DAMAGE · NO INJURIES", font=BCB(50), fill=(*CYAN, int(255 * r2)), anchor="lm")
            d.text((110, 1308), "SERIAL 25-0428 MATCHES THE AD", font=SMR(24), fill=(*OFF, int(255 * r2)), anchor="lm")
        stamp(im, 735, 1170, "NOT IN THE AD", ease((tt - wt(2, 12) - 0.1) / 0.25) * ab, ang=-6, col=WHITE, size=54)

def scene_sr22t(im, tt):
    """WHAT THE AD LEFT OUT: N236CB, 2021 Cirrus SR22T, dealer ad 259479463 at $798,900, "meticulously maintained
    by its original owner, always hangared"; NTSB CEN24LA309, Aug 6 2024, Salem IN, substantial damage, 3 aboard,
    no injuries, serial 2336 matched. Photos are the model (registrations blurred), not the subject tail.
    Landscape photos -> blur_backdrop + photo_card (pa32 pattern) with the mirage quote card."""
    hook = tt < T_B2 + 0.3
    im.alpha_composite(blur_backdrop(f"{PH}/hook.jpg" if hook else f"{PH}/find.jpg", 0.5 if hook else 0.36))
    im.alpha_composite(GRAD)
    d = ImageDraw.Draw(im, "RGBA")
    brand_bug(im)
    if tt < T_B2 + 0.25:
        fade = 1 - ease((tt - T_B2) / 0.25)
        chip(d, W / 2, 360, "FOR SALE NOW", fade, anchor="c")
        shadow_text(d, (W / 2, 460), "2021 CIRRUS SR22T", BCB(84), OFF, fade)
        punch(im, (W / 2, 640), "$798,900", BCB(236), tt, 0.0, fade)
        if fade > 0.02:
            card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            photo_card(card, f"{PH}/hook.jpg", (70, 790, 1010, 1180), tt, 0, T_B2)
            if fade < 1: card.putalpha(card.getchannel("A").point(lambda v: int(v * fade)))
            im.alpha_composite(card)
        d = ImageDraw.Draw(im, "RGBA")
        qa = ease((tt - wt(1, 7)) / 0.25) * fade
        if qa > 0:
            yo = lerp(30, 0, eout((tt - wt(1, 7)) / 0.3))
            d.rounded_rectangle([90, 1010 + yo, 940, 1270 + yo], radius=22, fill=(226, 232, 236, int(240 * qa)))
            d.text((130, 1056 + yo), "FROM THE AD", font=SMB(26), fill=(90, 100, 110, int(255 * qa)), anchor="lm")
            d.text((130, 1130 + yo), "\u201cMeticulously maintained", font=BCS(58), fill=(*NAVY, int(255 * qa)), anchor="lm")
            d.text((130, 1200 + yo), "by its original owner\u2026\u201d", font=BCS(58), fill=(*NAVY, int(255 * qa)), anchor="lm")
        return
    a = ease((tt - T_B2 - 0.1) / 0.3) * (1 - ease((tt - T_LOOK) / 0.2))
    if a <= 0: return
    yo = lerp(40, 0, eout((tt - T_B2 - 0.1) / 0.35))
    panel(d, (64, 360 + yo, 948, 1180 + yo), a, sub="SAFETY RECORD")
    r1 = ease((tt - wt(2, 4)) / 0.3) * a
    if r1 > 0:
        d.text((110, 520 + yo), "FEDERAL ACCIDENT RECORD", font=SMB(32), fill=(*GREY, int(255 * r1)), anchor="lm")
        d.text((110, 610 + yo), "AUG 6, 2024", font=BCB(104), fill=(*WHITE, int(255 * r1)), anchor="lm")
        d.text((110, 700 + yo), "SALEM, INDIANA \u00b7 NTSB CEN24LA309", font=SMB(28), fill=(*OFF, int(255 * r1)), anchor="lm")
        d.text((110, 748 + yo), "SERIAL 2336 MATCHES THE AD", font=SMR(26), fill=(*OFF, int(255 * r1)), anchor="lm")
    r2 = ease((tt - wt(2, 10)) / 0.25) * a
    if r2 > 0:
        d.text((110, 840 + yo), "DAMAGE", font=SMB(30), fill=(*GREY, int(255 * r2)), anchor="lm")
        d.text((110, 925 + yo), "SUBSTANTIAL", font=BCB(110), fill=(*CYAN, int(255 * r2)), anchor="lm")
        d.text((110, 1000 + yo), "3 ABOARD \u00b7 NO INJURIES", font=SMB(28), fill=(*OFF, int(255 * r2)), anchor="lm")
    stamp(im, 700, 1112 + yo, "NOT IN THE AD", ease((tt - wt(2, 10) - 0.3) / 0.25) * a, ang=-6, col=WHITE, size=64)

def scene_a36cut(im, tt):
    """PRICE JUMP (down, same ad): N614MM 1980 A36, dealer ad 259025415. $310,000 Aug 5 -> $285,000 Aug 15
    -> $269,000 Sep 11 -> $229,000 Oct 15 (three cuts, -$81,000). Photos are the model (registrations blurred)."""
    hook = tt < T_B2 + 0.3
    im.alpha_composite(blur_backdrop(f"{PH}/a36j-b.jpg" if hook else f"{PH}/a36m-b.jpg", 0.5 if hook else 0.34))
    im.alpha_composite(GRAD)
    d = ImageDraw.Draw(im, "RGBA")
    brand_bug(im)
    if tt < T_B2 + 0.25:
        fade = 1 - ease((tt - T_B2) / 0.25)
        chip(d, W / 2, 360, "FOR SALE NOW", fade, anchor="c")
        shadow_text(d, (W / 2, 460), "1980 BEECHCRAFT A36 BONANZA", BCB(76), OFF, fade)
        punch(im, (W / 2, 640), "$229,000", BCB(236), tt, 0.0, fade)
        if fade > 0.02:
            card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            photo_card(card, f"{PH}/a36j-b.jpg", (70, 800, 1010, 1197), tt, 0, T_B2)
            if fade < 1: card.putalpha(card.getchannel("A").point(lambda v: int(v * fade)))
            im.alpha_composite(card)
        d = ImageDraw.Draw(im, "RGBA")
        la = ease((tt - wt(1, 5)) / 0.2) * fade
        if la > 0:
            chip(d, W / 2, 1250, "DEALER AD \u00b7 LISTED AUG 5", la, anchor="c", f=SMB(30), col=OFF, outline=GREY)
        return
    a = ease((tt - T_B2 - 0.1) / 0.3) * (1 - ease((tt - T_LOOK) / 0.2))
    if a <= 0: return
    yo = lerp(40, 0, eout((tt - T_B2 - 0.1) / 0.35))
    panel(d, (64, 330 + yo, 948, 1230 + yo), a, sub="PRICE HISTORY \u00b7 ONE AD")
    pts = [(0.0, 310000, "AUG 5"), (0.22, 285000, "AUG 15"), (0.50, 269000, "SEP 11"), (0.78, 229000, "OCT 15")]
    box = (120, 560 + yo, 880, 1000 + yo)
    ymin, ymax = 205000, 330000
    # dashed guide at the original ask
    ga = ease((tt - wt(2, 10)) / 0.3) * a
    X0 = lambda f: box[0] + f * (box[2] - box[0])
    Y0 = lambda v: box[3] - (v - ymin) / (ymax - ymin) * (box[3] - box[1])
    if ga > 0:
        xx = 0.22
        while xx < 1.0:
            d.line([(X0(xx), Y0(310000)), (X0(min(xx + 0.02, 1.0)), Y0(310000))], fill=(*GREY, int(170 * ga)), width=3); xx += 0.04
    X, Y = step_chart(d, box, pts, wt(2, 5), wt(2, 12), tt, ymin, ymax, a)
    # -$81,000 bracket at the right edge + badge in the empty lower-left
    ba = ease((tt - wt(2, 12)) / 0.3) * a
    if ba > 0:
        xb = 915; ya, yb = Y(310000), Y(229000)
        d.line([xb, ya, xb, yb], fill=(*CYAN, int(255 * ba)), width=5)
        d.line([xb - 16, ya, xb, ya], fill=(*CYAN, int(255 * ba)), width=5)
        d.line([xb - 16, yb, xb, yb], fill=(*CYAN, int(255 * ba)), width=5)
        v = counter(81000, tt, wt(2, 12), 0.5)
        yc = Y(232000)
        d.rounded_rectangle([130, yc - 42, 420, yc + 42], radius=12, fill=(8, 20, 31, int(230 * ba)), outline=(*CYAN, int(200 * ba)), width=3)
        d.text((275, yc), "-" + money(round(v / 100) * 100), font=BCB(64), fill=(*CYAN, int(255 * ba)), anchor="mm")
    c1 = ease((tt - wt(2, 3)) / 0.2) * a; c2 = ease((tt - wt(2, 4)) / 0.2) * a
    if c1 > 0: chip(d, 110, 1150 + yo, "SAME AD", c1, f=SMB(28))
    if c2 > 0: chip(d, 300, 1150 + yo, "SAME DEALER", c2, f=SMB(28))
    stamp(im, 700, 1150 + yo, "3 PRICE CUTS", ease((tt - wt(2, 12) - 0.15) / 0.25) * a, ang=-4, col=WHITE, size=54)

def scene_sr20g6(im, tt):
    """SAME PRICE TWINS: Cirrus SR20 G6s at $489,900. A = N665M (2022, 740 h, cut twice: $534,900 Apr 16 ->
    $514,900 Jun 2 -> $489,900 Sep 29); B = N34AS (2021, 1,785 h, unchanged since Apr 13). No accident record on either.
    Photos are the model (registrations blurred), not the subject tails."""
    HH = 960
    dark = 0.62 if tt < T_B2 else 0.36
    LA = bg_layer(f"{PH}/a2.jpg", 0.35, dark=dark, size=(W, HH))
    LB = bg_layer(f"{PH}/b.jpg", 0.55, dark=dark, size=(W, HH))
    paste_bg(im, LA, tt, 0, T_LOOK, size=(W, HH), box=(0, 0))
    paste_bg(im, LB, tt, 0, T_LOOK, size=(W, HH), box=(0, HH), zoom_in=False)
    im.alpha_composite(GRAD)
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, HH - 3, W, HH + 3], fill=(*CYAN, 255))
    brand_bug(im)
    fade = 1 - ease((tt - T_LOOK) / 0.2)
    if fade <= 0: return
    if tt < T_B2 + 0.25:
        pf = (1 - ease((tt - T_B2) / 0.25)) * fade
        for yy, lab in ((360, "A · 2022 CIRRUS SR20 G6"), (1040, "B · 2021 CIRRUS SR20 G6")):
            d.rounded_rectangle([70, yy - 34, 70 + d.textlength(lab, font=SMB(30)) + 40, yy + 34], radius=12,
                                fill=(8, 20, 31, int(200 * pf)))
            d.text((90, yy), lab, font=SMB(30), fill=(*OFF, int(255 * pf)), anchor="lm")
        for yy, t0 in ((580, 0.0), (1225, 0.12)):   # price on screen from the first frame (spec)
            punch(im, (W / 2, yy), "$489,900", BCB(190), tt, t0, pf)
        stamp(im, W / 2, HH, "SAME PRICE", ease((tt - wt(1, 5)) / 0.25) * pf)
        return
    a = ease((tt - T_B2) / 0.3) * fade
    # A: newer, 740 h, cut twice
    aa = ease((tt - wt(2, 0)) / 0.3) * a
    if aa > 0:
        panel(d, (64, 400, 948, 880), aa, title="A · N665M", sub="PRICE HISTORY")
        step_chart(d, (120, 600, 880, 770),
                   [(0.0, 534900, "APR"), (0.30, 514900, "JUN 2"), (0.72, 489900, "SEP 29")],
                   wt(2, 1), wt(2, 12, True) + 0.25, tt, 480000, 545000, aa)
        ha = ease((tt - wt(2, 4)) / 0.25) * aa
        if ha > 0:
            chip(d, 110, 540, "2022 · 740 HOURS", ha, f=SMB(28))
        ca = ease((tt - wt(2, 11)) / 0.3) * aa
        if ca > 0:
            d.text((900, 540), "CUT TWICE · -$45,000", font=BCB(46), fill=(*CYAN, int(255 * ca)), anchor="rm")
    # B: older, 1,785 h, unchanged since April
    ab = ease((tt - wt(2, 13)) / 0.3) * a
    if ab > 0:
        panel(d, (64, 990, 948, 1335), ab, title="B · N34AS", sub="PRICE HISTORY")
        step_chart(d, (120, 1170, 880, 1230), [(0.0, 489900, "APR 13")],
                   wt(2, 13), wt(2, 18, True), tt, 480000, 545000, ab)
        chip(d, 110, 1112, "2021 · 1,785 HOURS", ab, f=SMB(28))
        ua = ease((tt - wt(2, 16)) / 0.3) * ab
        if ua > 0:
            d.text((900, 1112), "UNCHANGED SINCE APRIL", font=BCB(46), fill=(*CYAN, int(255 * ua)), anchor="rm")

# ---------------- liquidity check (campaign Format A, model-level, no tail) ----------------
# One entry per clip; the slug must start with "liq". nums: (value, label, beat-2 word index where it drops in,
# optional plain-words note shown under the number, e.g. "ABOUT A MONTH").
# Third number (value lost per year) only when the campaign table gives one (omit for "—").
# verdict: LIQUID / AVERAGE / PATIENT MONEY (never "bad"); it lands on word `verdict_at` of beat 2.
LIQ = {
 "liq172m": dict(model="CESSNA 172M SKYHAWK", q1="IS A CESSNA 172M", hook="hook.jpg", find="find.jpg", sold=66,
                 nums=[("29 DAYS", "TYPICAL TIME TO SELL", 1, "ABOUT A MONTH"),
                       ("14%", "SELLERS WHO CUT THE PRICE", 7, "86 IN 100 SELL WITHOUT A CUT")],
                 verdict="LIQUID", verdict_at=12),
 # 2026-10-20: 73 sold, 6 model years (< 8) -> value-lost-per-year omitted
 "liq182p": dict(model="CESSNA 182P SKYLANE", q1="IS A CESSNA 182P", hook="hook.jpg", find="find.jpg", sold=73,
                 nums=[("46 DAYS", "TYPICAL TIME TO SELL", 1, "ABOUT SIX AND A HALF WEEKS"),
                       ("11%", "SELLERS WHO CUT THE PRICE", 9, "89 IN 100 SELL WITHOUT A CUT")],
                 verdict="LIQUID", verdict_at=13),
}
VERDICT_COL = {"LIQUID": CYAN, "AVERAGE": OFF, "PATIENT MONEY": (245, 190, 79)}

def drop_in(im, xy, txt, f, col, tt, t0, dur=0.38):
    """Number drops from above with a small overshoot and fades in."""
    p = (tt - t0) / dur
    if p <= 0: return
    q = min(p, 1.0)
    y = xy[1] - 90 * (1 - eout(q)) + (8 * math.sin(min((p - 1) / 0.25, 1) * math.pi) if 1 < p < 1.25 else 0)
    d = ImageDraw.Draw(im, "RGBA")
    shadow_text(d, (xy[0], y), txt, f, col, ease(q * 1.6), anchor="lm")

def scene_liq(im, tt):
    c = LIQ[V]
    hook = tt < T_B2 + 0.3
    im.alpha_composite(blur_backdrop(f"{PH}/{c['hook']}" if hook else f"{PH}/{c['find']}", 0.5 if hook else 0.34))
    im.alpha_composite(GRAD)
    d = ImageDraw.Draw(im, "RGBA")
    brand_bug(im)
    if tt < T_B2 + 0.25:
        fade = 1 - ease((tt - T_B2) / 0.25)
        chip(d, W / 2, 360, "LIQUIDITY CHECK", fade, anchor="c")
        shadow_text(d, (W / 2, 470), c["q1"], BCB(92), OFF, fade)
        punch(im, (W / 2, 640), "LIQUID?", BCB(220), tt, 0.0, fade)
        if fade > 0.02:
            card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            photo_card(card, f"{PH}/{c['hook']}", (70, 800, 1010, 1197), tt, 0, T_B2)
            if fade < 1: card.putalpha(card.getchannel("A").point(lambda v: int(v * fade)))
            im.alpha_composite(card)
        return
    a = ease((tt - T_B2 - 0.1) / 0.3) * (1 - ease((tt - T_LOOK) / 0.2))
    if a <= 0: return
    yo = lerp(40, 0, eout((tt - T_B2 - 0.1) / 0.35))
    panel(d, (64, 330 + yo, 948, 1300 + yo), a, title="NEXTPLANE SOLD DATA", sub=f"{c['model'].split()[0]} · {c['sold']} SOLD")
    d.text((110, 452 + yo), c["model"], font=BCB(54), fill=(*OFF, int(255 * a)), anchor="lm")
    n = len(c["nums"]); step = 230 if n == 3 else 260
    for k, (val, lab, wi, *note) in enumerate(c["nums"]):
        y0 = 560 + yo + k * step; t0 = wt(2, wi) - 0.1
        la = ease((tt - t0) / 0.25) * a
        if la <= 0: continue
        d.text((110, y0), lab, font=SMB(30), fill=(*GREY, int(255 * la)), anchor="lm")
        drop_in(im, (104, y0 + 100), val, BCB(150 if n < 3 else 130), WHITE if k else CYAN, tt, t0)
        d = ImageDraw.Draw(im, "RGBA")
        na = ease((tt - t0 - 0.45) / 0.25) * a
        if note and note[0] and na > 0 and n < 3:
            d.text((110, y0 + 192), note[0], font=SMB(28), fill=(*OFF, int(255 * na)), anchor="lm")
    va = ease((tt - wt(2, c["verdict_at"]) + 0.1) / 0.25) * a
    if va > 0:
        vy = 560 + yo + n * step + 90          # clear of the last number's note line
        d.text((W / 2, vy - 70), "VERDICT", font=SMB(28), fill=(*GREY, int(255 * va)), anchor="mm")
        stamp(im, W / 2, vy + 30, c["verdict"], va, ang=-4, col=VERDICT_COL[c["verdict"]], size=104)

_EB = []
def endbg():
    if not _EB:
        g = Image.new("RGB", (1, H))
        for y in range(H):
            k = y / H
            g.putpixel((0, y), (int(lerp(18, 8, k)), int(lerp(48, 22, k)), int(lerp(72, 34, k))))
        _EB.append(g.resize((W, H)).convert("RGBA"))
    return _EB[0]

SCENE = scene_liq if V.startswith("liq") else {"sr20": scene_sr20, "a36": scene_a36, "mirage": scene_mirage, "pa32": scene_pa32, "m20k": scene_m20k, "sr22t": scene_sr22t, "a36cut": scene_a36cut, "sr20g6": scene_sr20g6}[V]
TAILS = ["YOUR N-NUMBER"] if V.startswith("liq") else {"sr20": ["N881PF"], "a36": ["N29DL", "N72MD"], "mirage": ["N27RZ"], "pa32": ["N123BE"], "m20k": ["N231HB", "N3594H"], "sr22t": ["N236CB"], "a36cut": ["N614MM"], "sr20g6": ["N665M", "N34AS"]}[V]

def frame(i):
    global GRAD
    if GRAD is None: GRAD = gradient(None)
    tt = i / FPS
    im = Image.new("RGBA", (W, H), (*NAVY, 255))
    if tt < T_END:
        SCENE(im, tt)
        if tt >= T_LOOK:
            # darken + lookup
            ov = Image.new("RGBA", (W, H), (*NAVY, int(170 * ease((tt - T_LOOK) / 0.25))))
            im.alpha_composite(ov)
            brand_bug(im)
            lookup(im, tt, T_LOOK, TAILS)
        draw_caption(im, tt)
        # crossfade into end card
    else:
        te = tt - T_END
        im = draw_endcard(endbg().copy(), te, FD, LOGO)
    return im.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[2] == "info":
        print(json.dumps({"total": TOTAL, "nf": NF, "offs": OFFS, "t_b2": T_B2, "t_look": T_LOOK, "t_end": T_END}))
        sys.exit()
    wk = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    nw = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    out = f"{ROOT}/frames_{V}"; os.makedirs(out, exist_ok=True)
    only = os.environ.get("ONLY")
    rng = [int(x) for x in only.split(",")] if only else range(wk, NF, nw)
    for i in rng:
        frame(i).save(f"{out}/f{i:05d}.jpg", quality=92)
