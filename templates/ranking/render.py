#!/usr/bin/env python3
"""NextPlane RANKING Short renderer (liquidity campaign, 2026-10). Spec-driven: $WORK/spec.json.
Usage: render.py <start> <end> [step]  -> $WORK/frames/f%05d.jpg (1080x1920@30). Resumable.
Beats: b1 hook, r5..r1 countdown rows, b7 the catch (live count), b8 the report tail, b9 end card."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT = os.environ["WORK"]
sys.path.insert(0, ROOT)
from endcard import draw_endcard
SPEC = json.load(open(f"{ROOT}/spec.json"))
W, H, FPS = 1080, 1920, 30
NAVY = (10, 22, 34); NAVY2 = (16, 34, 52); INK = (13, 27, 38)
CYAN = (37, 197, 203); OFF = (246, 249, 250); WHITE = (255, 255, 255)
MUTE = (128, 148, 162); DIM = (70, 92, 108); AMBER = (245, 166, 35); RED = (232, 88, 88)
FD = f"{ROOT}/fonts"
_f = {}
def F(name, size):
    k = (name, size)
    if k not in _f: _f[k] = ImageFont.truetype(f"{FD}/{name}", size)
    return _f[k]
BCB = lambda s: F("BarlowCondensed-Bold.ttf", s); BCS = lambda s: F("BarlowCondensed-SemiBold.ttf", s)
SMB = lambda s: F("SpaceMono-Bold.ttf", s); SMR = lambda s: F("SpaceMono-Regular.ttf", s)
def ease(p): p = min(max(p, 0.0), 1.0); return p*p*(3-2*p)
def easeo(p): p = min(max(p, 0.0), 1.0); return 1-(1-p)**3

BEATS = ["b1", "r5", "r4", "r3", "r2", "r1", "b7", "b8", "b9"]
VO = {b: json.load(open(f"{ROOT}/vo/{b}.json")) for b in BEATS}
OFFS = {}; t = 0.4; GAP = 0.3
for b in BEATS:
    OFFS[b] = t; t += VO[b]["dur"] + GAP + (0.3 if b == "b1" else 0)
TOTAL = OFFS["b9"] + VO["b9"]["dur"] + 1.6
NF = int(TOTAL * FPS)
edges = [0.0] + [OFFS[b] - GAP/2 for b in BEATS[1:]] + [TOTAL]
SC = [(b, edges[i], edges[i+1]) for i, b in enumerate(BEATS)]
T0 = {b: SC[i][1] for i, b in enumerate(BEATS)}
def wt(b, idx): w = VO[b]["words"][idx]; return OFFS[b] + w["s"]
def anchor(b, text, occ=1):
    n = 0
    for i, w in enumerate(VO[b]["words"]):
        if w["w"].strip(".,?!'’:;").lower() == text.lower():
            n += 1
            if n == occ: return wt(b, i)
    return T0[b] + 0.5

_ph = {}
def photo(slug, dark=0.42, tint=0.55):
    k = (slug, dark, tint)
    if k in _ph: return _ph[k]
    cache = f"{ROOT}/assets/bg_{slug}_{int(dark*100)}_{int(tint*100)}.jpg"
    if os.path.exists(cache):
        try: _ph[k] = Image.open(cache).convert("RGB"); return _ph[k]
        except Exception: pass
    im = Image.open(f"{ROOT}/photos/{slug}-0.jpg").convert("RGB")
    tw, th = int(W*1.12), int(H*1.12); r = max(tw/im.width, th/im.height)
    im = im.resize((int(im.width*r)+1, int(im.height*r)+1), Image.LANCZOS)
    x = (im.width-tw)//2; y = (im.height-th)//2; im = im.crop((x, y, x+tw, y+th))
    im = ImageEnhance.Color(im).enhance(0.55); im = ImageEnhance.Brightness(im).enhance(dark)
    im = Image.blend(im, Image.new("RGB", im.size, NAVY), tint)
    tmp = cache + f".{os.getpid()}.tmp"; im.save(tmp, quality=90, format="JPEG"); os.replace(tmp, cache)
    _ph[k] = im; return im
def bg_photo(slug, p, zoom0=1.10, zoom1=1.0, dark=0.42, tint=0.55):
    src = photo(slug, dark, tint); z = zoom0 + (zoom1-zoom0)*p
    cw, ch = min(int(W*z), src.width), min(int(H*z), src.height)
    x = (src.width-cw)//2; y = (src.height-ch)//2
    return src.crop((x, y, x+cw, y+ch)).resize((W, H), Image.BILINEAR)
def bg_grad(top=NAVY, bot=NAVY2):
    k = ("grad", top, bot)
    if k not in _ph:
        im = Image.new("RGB", (1, H)); px = im.load()
        for y in range(H):
            a = y/H; px[0, y] = tuple(int(top[i]*(1-a)+bot[i]*a) for i in range(3))
        _ph[k] = im.resize((W, H))
    return _ph[k].copy()
def vignette(im):
    if "vig" not in _ph:
        m = Image.new("L", (W//4, H//4), 0); d = ImageDraw.Draw(m)
        d.ellipse([-W//16, -H//16, W//4+W//16, H//4+H//16], fill=255)
        _ph["vig"] = m.filter(ImageFilter.GaussianBlur(40)).resize((W, H)).point(lambda v: 185+(v*70)//255)
    return Image.composite(im, Image.new("RGB", (W, H), (4, 10, 16)), _ph["vig"])
def glass(d, box, a=1.0, fill=(13,27,38,200), line=CYAN, lw=2, r=22):
    if a <= 0: return
    d.rounded_rectangle(box, radius=r, fill=(fill[0], fill[1], fill[2], int(fill[3]*a)), outline=(*line, int(210*a)), width=lw)
def sh(d, xy, s, f, fill, a=1.0, anch="mm", shad=3):
    if a <= 0: return
    col = tuple(int(v*min(a, 1)) for v in fill)
    if shad: d.text((xy[0]+shad, xy[1]+shad), s, font=f, fill=(0, 0, 0), anchor=anch)
    d.text(xy, s, font=f, fill=col, anchor=anch)
def chip(d, cx, cy, txt, f, a, fg=CYAN, w_pad=34, h_pad=20, fill=(13,27,38,190)):
    if a <= 0: return
    tw = d.textlength(txt, font=f); hh = f.size//2
    d.rounded_rectangle([cx-tw/2-w_pad, cy-hh-h_pad, cx+tw/2+w_pad, cy+hh+h_pad], radius=18,
                        fill=(fill[0], fill[1], fill[2], int(fill[3]*a)), outline=(*fg, int(200*a)), width=2)
    sh(d, (cx, cy), txt, f, OFF if fg == CYAN else fg, a)
def counter(v0, v1, t0, dur, t, fmt="{:,.0f}"):
    return fmt.format(v0 + (v1-v0)*easeo((t-t0)/dur))
def wrap(d, txt, f, maxw):
    lines, cur = [], ""
    for w in txt.split():
        tst = (cur+" "+w).strip()
        if d.textlength(tst, font=f) > maxw and cur: lines.append(cur); cur = w
        else: cur = tst
    lines.append(cur); return lines
_th = {}
def thumb(slug, w, h):
    k = (slug, w, h)
    if k not in _th:
        p = f"{ROOT}/photos/{slug}-0.jpg"
        if not os.path.exists(p): _th[k] = None; return None
        im = Image.open(p).convert("RGB"); r = max(w/im.width, h/im.height)
        im = im.resize((int(im.width*r)+1, int(im.height*r)+1), Image.LANCZOS)
        x = (im.width-w)//2; y = (im.height-h)//2; im = im.crop((x, y, x+w, y+h))
        im = ImageEnhance.Color(im).enhance(0.8)
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], radius=14, fill=255)
        _th[k] = (im, m)
    return _th[k]
def paste_thumb(im, slug, box, a):
    if a <= 0: return False
    x0, y0, x1, y1 = box; th = thumb(slug, x1-x0, y1-y0)
    if th is None: return False
    img, m = th
    if a < 1: m = m.point(lambda v: int(v*a))
    im.paste(img, (x0, y0), m); return True
def paste_img(im, path, box, a, radius=18):
    if a <= 0 or not os.path.exists(path): return
    x0, y0, x1, y1 = box; w, h = x1-x0, y1-y0
    k = ("img", path, w, h)
    if k not in _th:
        src = Image.open(path).convert("RGB"); r = w/src.width
        src = src.resize((w, int(src.height*r)), Image.LANCZOS)
        h = min(h, src.height); src = src.crop((0, 0, w, h))
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w-1, h-1], radius=radius, fill=255)
        _th[k] = (src, m)
    src, m = _th[k]
    if a < 1: m = m.point(lambda v: int(v*a))
    im.paste(src, (x0, y0), m)

CHUNKS = []
for b in BEATS[:-1]:
    cur = []
    for w in VO[b]["words"]:
        cur.append((w["w"], OFFS[b]+w["s"], OFFS[b]+w["e"]))
        if len(cur) >= 4 or w["w"].rstrip().endswith((".", "?", "!", ",", ":")):
            CHUNKS.append(cur); cur = []
    if cur: CHUNKS.append(cur)
def draw_captions(d, t):
    for ch in CHUNKS:
        if ch[0][1]-0.05 <= t <= ch[-1][2]+0.12:
            f = BCS(56); words = [w for w, s, e in ch]
            widths = [d.textlength(w+" ", font=f) for w in words]; tot = sum(widths)
            scale = min(1.0, 980/tot); f2 = BCS(int(56*scale)) if scale < 1 else f
            widths = [d.textlength(w+" ", font=f2) for w in words]; tot = sum(widths)
            x = W/2-tot/2; y = 1575
            d.rounded_rectangle([W/2-tot/2-30, y-52, W/2+tot/2+30, y+52], radius=16, fill=(5, 12, 18, 165))
            for (w, s, e), wd in zip(ch, widths):
                col = CYAN if s <= t <= e else OFF
                d.text((x+3, y+3), w, font=f2, fill=(0, 0, 0), anchor="lm"); d.text((x, y), w, font=f2, fill=col, anchor="lm"); x += wd
            return
def topline(d, t, txt, t0):
    a = ease((t-t0)/0.4); sh(d, (W/2, 150), txt, SMB(28), MUTE, a)
    if a > 0:
        lw = int(300*a); d.rectangle([W/2-lw/2, 190, W/2+lw/2, 193], fill=(*CYAN, int(160*a)))

# ---------------- scenes ----------------
ROWS = SPEC["rows"]            # index 0 = rank 5 ... index 4 = rank 1
RB = ["r5", "r4", "r3", "r2", "r1"]
MAXV = max(r["bar"] for r in ROWS) or 1.0

def s_hook(im, d, t):
    topline(d, t, "IS YOUR AIRPLANE LIQUID? · NEXTPLANE SOLD-LISTING DATA", 0.3)
    a0 = ease((t-0.5)/0.5)
    if a0 > 0:
        glass(d, [60, 250, 1020, 760], a0, fill=(11,24,36,220), line=CYAN, lw=3)
        sh(d, (90, 300), SPEC["category"].upper(), SMR(22), MUTE, a0, anch="lm")
        y = 370
        for ln in wrap(d, SPEC["title"], BCB(72), 880):
            sh(d, (90, y), ln, BCB(72), OFF, a0, anch="lm"); y += 82
        sh(d, (90, y+20), SPEC["subline"].upper(), SMR(19), CYAN, a0, anch="lm")
    a1 = ease((t-(T0["b1"]+SPEC.get("hook_stat_at", 4.0)))/0.5)
    if a1 > 0 and SPEC.get("hook_stat"):
        glass(d, [60, 820, 1020, 1200], a1, fill=(11,24,36,215), line=DIM)
        sh(d, (90, 870), SPEC["hook_stat"]["label"].upper(), SMR(20), MUTE, a1, anch="lm")
        sh(d, (90, 1000), SPEC["hook_stat"]["big"], BCB(150), CYAN, a1, anch="lm")
        sh(d, (90, 1130), SPEC["hook_stat"]["sub"], BCS(34), OFF, a1, anch="lm")

def s_rank(im, d, t, upto):
    topline(d, t, SPEC["subline"].upper(), T0["r5"]+0.1)
    for j in range(upto+1):
        r = ROWS[j]; rank = 5-j; at = T0[RB[j]]+0.1
        ra = ease((t-at)/0.4)
        if ra <= 0: continue
        y = 240 + j*262
        glass(d, [60, y, 1020, y+238], ra, fill=(11,24,36,215), line=(CYAN if rank == 1 else DIM), lw=(3 if rank == 1 else 2))
        has = paste_thumb(im, r["photo"], (84, y+24, 294, y+214), ra)
        d = ImageDraw.Draw(im, "RGBA")
        x0 = 320 if has else 90
        sh(d, (x0, y+50), f"#{rank}", SMB(26), CYAN, ra, anch="lm")
        sh(d, (x0+70, y+50), r["model"].upper(), BCB(40), OFF, ra, anch="lm")
        vt = counter(0, r["num"], at, 0.8, t, r["fmt"]) if r.get("num") is not None else r["value"]
        sh(d, (990, y+118), vt, BCB(72), CYAN if rank == 1 else OFF, ra, anch="rm")
        sh(d, (x0, y+118), SPEC["unit"].upper(), SMR(18), MUTE, ra, anch="lm")
        d.rounded_rectangle([x0, y+150, 990, y+168], radius=8, fill=(78,118,138,120))
        bw = int((990-x0)*(r["bar"]/MAXV)*easeo((t-at)/0.9))
        if bw > 0: d.rounded_rectangle([x0, y+150, x0+max(bw, 10), y+168], radius=8, fill=(*(CYAN if rank == 1 else OFF), 230))
        sh(d, (x0, y+205), r["reason"], BCS(26), MUTE, ra, anch="lm")

def s_catch(im, d, t):
    topline(d, t, "THE CATCH", T0["b7"]+0.1)
    c = SPEC["catch"]; at = T0["b7"]+0.4; a0 = ease((t-at)/0.5)
    if a0 > 0:
        glass(d, [60, 250, 1020, 700], a0, fill=(11,24,36,220), line=CYAN, lw=3)
        sh(d, (90, 300), f"{c['model'].upper()} · FOR SALE RIGHT NOW", SMR(21), MUTE, a0, anch="lm")
        sh(d, (90, 450), counter(0, c["count"], at, 1.0, t), BCB(190), CYAN, a0, anch="lm")
        sh(d, (90, 620), "LISTINGS · UNITED STATES · THIS WEEK", SMR(20), MUTE, a0, anch="lm")
    a1 = ease((t-(at+1.6))/0.5)
    if a1 > 0:
        glass(d, [60, 740, 1020, 1330], a1, fill=(11,24,36,215), line=DIM)
        sh(d, (90, 790), "ON THE LISTING SITE THEY LOOK IDENTICAL", SMR(20), MUTE, a1, anch="lm")
        n = min(c["count"], 40); cols = 8; cw = 100; ch = 84
        for i in range(n):
            ia = ease((t-(at+1.7)-i*0.035)/0.3)
            if ia <= 0: continue
            x = 90 + (i % cols)*cw + 8; yy = 840 + (i//cols)*ch + 8
            d.rounded_rectangle([x, yy, x+cw-16, yy+ch-16], radius=10, fill=(18,36,52,int(230*ia)), outline=(*DIM, int(200*ia)), width=2)
            sh(d, (x+(cw-16)/2, yy+(ch-16)/2), "N", SMB(22), DIM, ia)
        a2 = ease((t-(at+3.4))/0.4)
        chip(d, W/2, 1290, "WHICH ONE IS THE ONE ON THE LIST?", BCB(34), a2, fg=CYAN, w_pad=24, h_pad=14)

def s_report(im, d, t):
    topline(d, t, "THE REPORT · ONE REAL AIRPLANE", T0["b8"]+0.1)
    r = SPEC["tail"]; at = T0["b8"]+0.3; a0 = ease((t-at)/0.5)
    if a0 > 0:
        glass(d, [60, 240, 1020, 560], a0, fill=(11,24,36,220), line=CYAN, lw=3)
        sh(d, (90, 290), r["n"], SMB(44), CYAN, a0, anch="lm")
        sh(d, (90, 370), r["desc"].upper(), BCB(44), OFF, a0, anch="lm")
        if r.get("price"): sh(d, (90, 460), r["price"], BCB(64), OFF, a0, anch="lm")
        sh(d, (990, 520), "SOURCE: NEXTPLANE AIRCRAFT REPORT", SMR(16), DIM, a0, anch="rm")
    paste_img(im, f"{ROOT}/assets/report.png", (60, 590, 1020, 1130), ease((t-(at+0.6))/0.5))
    d = ImageDraw.Draw(im, "RGBA")
    for j, f in enumerate(r["facts"]):
        fa = ease((t-(at+1.2+j*1.2))/0.4)
        if fa <= 0: continue
        y = 1160 + j*95
        d.rounded_rectangle([60, y, 1020, y+80], radius=14, fill=(18,36,52,int(225*fa)), outline=(*(AMBER if f.get("warn") else CYAN), int(190*fa)), width=2)
        sh(d, (90, y+40), f["k"].upper(), SMR(18), MUTE, fa, anch="lm")
        sh(d, (990, y+40), f["v"], BCB(36), OFF, fa, anch="rm")
    a3 = ease((t-(at+1.2+len(r["facts"])*1.2+0.3))/0.4)
    chip(d, W/2, 1480, r["verdict"].upper(), BCB(32), a3, fg=AMBER, w_pad=22, h_pad=12)

def s_end(im, d, t): return draw_endcard(im, t-T0["b9"], FD, f"{ROOT}/assets/logo.png")
def end_bg():
    if "endbg" not in _ph:
        im = bg_grad((15, 32, 48), (11, 24, 38)); gl = Image.new("L", (W//4, H//4), 0)
        ImageDraw.Draw(gl).ellipse([W//8-160, 100, W//8+160, 420], fill=70)
        gl = gl.filter(ImageFilter.GaussianBlur(60)).resize((W, H))
        _ph["endbg"] = Image.composite(Image.new("RGB", (W, H), (24, 60, 70)), im, gl)
    return _ph["endbg"].copy()

BGS = SPEC["bg"]   # list of photo slugs to cycle per beat
def frame(i):
    t = i/FPS
    name, t0, t1 = next(s for s in SC if s[1] <= t < s[2] or s is SC[-1] and t >= s[1])
    p = (t-t0)/max(t1-t0, 0.01)
    if name == "b9": im = end_bg()
    else:
        bi = BEATS.index(name); slug = BGS[bi % len(BGS)]
        im = vignette(bg_photo(slug, p, zoom0=1.10 if bi % 2 == 0 else 1.0, zoom1=1.0 if bi % 2 == 0 else 1.10, dark=0.36, tint=0.64))
    d = ImageDraw.Draw(im, "RGBA")
    if name == "b1": s_hook(im, d, t)
    elif name in RB: s_rank(im, d, t, RB.index(name))
    elif name == "b7": s_catch(im, d, t)
    elif name == "b8": s_report(im, d, t)
    else: im = s_end(im, d, t)
    d = ImageDraw.Draw(im, "RGBA")
    if name != "b9": draw_captions(d, t)
    return im

if __name__ == "__main__":
    a, b = int(sys.argv[1]), min(int(sys.argv[2]), NF); step = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    os.makedirs(f"{ROOT}/frames", exist_ok=True)
    if a == 0 and step == 1: print(f"TOTAL {TOTAL:.2f}s NF={NF}"); print(json.dumps({k: round(v, 2) for k, v in OFFS.items()}))
    n = 0
    for i in range(a, b, step):
        fn = f"{ROOT}/frames/f{i:05d}.jpg"
        if os.path.exists(fn): continue
        tmp = fn+f".{os.getpid()}.tmp"; frame(i).save(tmp, quality=91, format="JPEG"); os.replace(tmp, fn); n += 1
    print(f"rendered {n} frames [{a},{b}) step {step}")
