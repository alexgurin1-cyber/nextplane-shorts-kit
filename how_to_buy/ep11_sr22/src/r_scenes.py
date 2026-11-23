# ---------- card text boxes (CSS px) ----------
SEC = json.load(open(f"{CAP}/sections.json"))
def BX(key, txt, n=1, pad=0, x1=None, exact=False):
    k = 0
    for b in SEC[key]["boxes"]:
        if (b["t"] == txt) if exact else b["t"].startswith(txt):
            k += 1
            if k == n:
                return (b["x"] - pad, b["y"] - pad, (x1 if x1 is not None else b["x"] + b["w"]) + pad, b["y"] + b["h"] + pad)
    raise KeyError((key, txt))
def BXS(key, *txts, pad=2):
    out = []
    for t in txts:
        n = 1
        while True:
            try: out.append(BX(key, t, n, pad=pad)); n += 1
            except KeyError: break
    return out
def UNION(*bs): return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))
HC = "_headercomb"
VOFF = SEC["header"]["h"]
# Masking (Alex): owner names (people and LLCs), seller and dealer names, data-source labels and fine print.
RELABEL = {HC: [(BX(HC, "NTSB DAMAGE"), "ACCIDENT RECORD"), (BX(HC, "USE TYPE"), "USE TYPE"),
                (BX(HC, "FINANCING ·"), "FINANCING"), (BX(HC, "SDR ·"), "SERVICE PROBLEMS")],
           "sdr": [(BX("sdr", "SERVICE DIFFICULTY REPORTS"), "SERVICE PROBLEMS"), (BX("sdr", "No Service Difficulty"), "No service problem reports on this aircraft.")],
           "flight": [(BX("flight", "24-month history"), "24-month flight history")],
           "fl_period": []}
EXTRA_BLUR = {HC: BXS(HC, "N814LT LLC", "FAA document index +", "Records searched") + [(90, 592, 207, 621)],
              "listhist": BXS("listhist", "Listed by", "An ad that disappears", "NextPlane began") + [(98, 247, 430, 288), (20, 548, 340, 572)],
              "reg": BXS("reg", "N814LT LLC", "The FAA registry", "No security conveyance indexed in", "Repossession (REP)", "A dereg_removed",
                         "Derived from the FAA", "Engine and propeller securit", "Enter the engine"),
              "sdr": BXS("sdr", "FAA Service Difficulty"),
              "ads": BXS("ads", "N814LT LLC", "model_specs", "Default 100 hr/yr"),
              "opcost": BXS("opcost", "Region:"),
              "specs": BXS("specs", "G3 · 2008"),
              "sellertop": [(220, 94, 420, 130), (220, 128, 605, 155)],
              "sellerusual": BXS("sellerusual", "They have"),
              "before": [(104, 148, 122, 172), (14, 202, 110, 226)]}

def rep_label(im, txt):
    d = ImageDraw.Draw(im, "RGBA"); d.text((70, 925), txt, font=MR(18), fill=(200, 210, 218, 190), anchor="lm")
def big_line(d, y, txt, f=None, fill=OFF, p=1.0):
    f = f or BB(62); d.text((W / 2, y), txt, font=f, fill=(*fill, int(255 * min(max(p, 0), 1))), anchor="mm")
def chip_c(d, y, txt, f=None, fill=CYAN, fg=NAVY):
    f = f or MB(26); tw = d.textlength(txt, font=f); chip(d, W / 2 - tw / 2 - 18, y, txt, fill=fill, fg=fg, f=f)
RED = (230, 120, 110); AMBER = (240, 170, 80)
REP = "REPRESENTATIVE PHOTO · CIRRUS SR22 · NOT THE AIRCRAFT FOR SALE"
P1, P2, P3, P4 = "sr22-0.jpg", "cirrussr-0.jpg", "sr22-1.jpg", "cirrussrgts-0.jpg"
def dimbg(im, t, s0, s1, ph=P3, blur=14, dark=0.84):
    im.paste(kb(photo_bg(ph, blur=blur, dark=dark), (t - s0) / max(s1 - s0, 1)))

def sc_title(im, t, s0, s1):
    bid = BID["title"]
    tt = trig(bid, "This", 2)
    if t < tt - 0.2:
        dimbg(im, t, s0, s1, P1, blur=8, dark=0.8)
        report_slide(im, t, HC, (0, 0, 1152, 220), [(UNION(BX(HC, "ASKING PRICE"), BX(HC, "$399,900")), s0 + 0.6)], t0=s0, cy=300, maxh=420)
        d = ImageDraw.Draw(im, "RGBA")
        tq = trig(bid, "Is")
        if t > tq - 0.1: big_line(d, 640, "IS IT THE BARGAIN IT LOOKS LIKE?", BB(104), CYAN, (t - tq + 0.1) / 0.4)
        if t > trig(bid, "less") - 0.2: chip_c(d, 760, "ASKS ≈ $45,000 UNDER THE REPORT'S ESTIMATE", f=MB(32))
        if t > trig(bid, "why.") - 0.3: chip_c(d, 840, "3,102 AIRFRAME HOURS · NO TRACKED FLIGHTS IN 2025", fill=AMBER, f=MB(30))
    else:
        im.paste(kb(photo_bg(P1, dark=0.35, focus=(0.5, 0.5)), (t - s0) / (s1 - s0), 1.0, 1.08))
        d = ImageDraw.Draw(im, "RGBA"); d.rectangle([0, 0, W, H], fill=(8, 16, 26, 120))
        p = ease((t - tt) / 0.8)
        d.text((W / 2, 380), "HOW TO BUY A", font=BB(90), fill=(*OFF, int(255 * p)), anchor="mm")
        d.text((W / 2, 505), "CIRRUS SR22", font=BB(170), fill=(*CYAN, int(255 * p)), anchor="mm")
        d.text((W / 2, 645), "ONE REAL AIRPLANE FOR SALE · ONE REAL REPORT · WHAT TO OFFER", font=MB(30), fill=(*OFF, int(220 * p)), anchor="mm")
        rep_label(im, REP)

# ---------- product demo: the lookup ----------
LK = f"{ROOT}/lookup"
LBLUR = {"home": [(1200, 760, 1390, 792)],
         "report": [(1474, 532, 1655, 553), (1130, 735, 1375, 755), (532, 905, 660, 934), (440, 962, 1565, 982)]}
LRELAB = {"report": [((786, 338, 975, 356), "ACCIDENT RECORD"), ((440, 478, 605, 494), "USE TYPE"),
                     ((440, 678, 705, 695), "FINANCING"), ((1476, 678, 1640, 695), "SERVICE PROBLEMS")]}
_lk = {}
def lk_img(name, kind):
    if name in _lk: return _lk[name]
    im = Image.open(f"{LK}/{name}").convert("RGB")
    for bx in LBLUR.get(kind, []): im.paste(im.crop(bx).filter(ImageFilter.GaussianBlur(12)), bx[:2])
    dd = ImageDraw.Draw(im)
    for bx, txt in LRELAB.get(kind, []):
        col = im.getpixel((bx[0] - 2, bx[1] + 2)); dd.rectangle(bx, fill=col)
        dd.text((bx[0] + 4, (bx[1] + bx[3]) / 2), txt, font=MB(15), fill=(110, 122, 135), anchor="lm")
    im = im.resize((1600, 900), Image.LANCZOS); _lk[name] = im; return im
def sc_lookup(im, t, s0, s1):
    bid = BID["lookup"]
    dimbg(im, t, s0, s1, P2, blur=14, dark=0.86)
    header_bar(im, "THE LOOKUP", "NEXTPLANE.US · ENTER THE N-NUMBER")
    tty, top = trig(bid, "Type"), trig(bid, "Open")
    if t < tty: name, kind = "l0_home.png", "home"
    elif t < top:
        k = min(5, int((t - tty) / 0.35)); name, kind = (f"l1_type_{k}.png" if t - tty < 2.3 else "l2_typed.png"), "home"
    else: name, kind = "l4_report.png", "report"
    sim = lk_img(name, kind); x, y = 160, 130
    d = ImageDraw.Draw(im, "RGBA"); d.rounded_rectangle([x - 4, y - 4, x + 1604, y + 904], radius=8, outline=(*CYAN, 160), width=3)
    im.paste(sim, (x, y))
    d = ImageDraw.Draw(im, "RGBA")
    if kind == "home" and t > tty - 0.3:
        sc = 1600 / 1920; d.rounded_rectangle([x + 425 * sc, y + 615 * sc, x + 1092 * sc, y + 690 * sc], radius=8, outline=CYAN, width=5)
    tc = trig(bid, "costs")
    if t > tc: chip(d, 1360, 880, "$29 PER AIRPLANE", f=MB(30))

def sc_gen(im, t, s0, s1):
    bid = BID["gen"]
    dimbg(im, t, s0, s1, P2)
    header_bar(im, "FIRST", "WHICH CIRRUS IS THIS?")
    d = ImageDraw.Draw(im, "RGBA")
    gens = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G7+"]
    tg = trig(bid, "generations")
    if t > tg - 0.2:
        x = 110
        for i, g in enumerate(gens):
            p = ease((t - tg - i * 0.25) / 0.4)
            if p <= 0: continue
            hero = g == "G3" and t > trig(bid, "confirms")
            fill = CYAN if hero else (15, 42, 63)
            d.rounded_rectangle([x, 170, x + 190, 270], radius=14, fill=(*fill, int(255 * p)), outline=(*CYAN, int(160 * p)), width=2)
            d.text((x + 95, 220), g, font=BB(64), fill=(*(NAVY if hero else OFF), int(255 * p)), anchor="mm")
            if g == "G4" and t > trig(bid, "G4."):
                d.line([x + 20, 250, x + 170, 190], fill=RED, width=7)
            x += 218
    tc = trig(bid, "confirms")
    if t > tc - 0.4:
        report_slide(im, t, "specs", (0, 70, 568, 100), [(BX("specs", "Generation G3 per"), tc + 0.3)], t0=tc - 0.4, cy=420, maxh=200, maxw=1300)
    tb = trig(bid, "built")
    if t > tb - 0.3:
        report_slide(im, t, "valuation", (580, 100, 850, 185), [(UNION(BX("valuation", "GENERATION"), BX("valuation", "same-generation")), tb)], t0=tb - 0.3, cy=640, maxh=200, maxw=640, cx=560)
    if t > trig(bid, "normally") - 0.2: d.text((1300, 600), "NORMALLY ASPIRATED", font=BB(56), fill=OFF, anchor="mm"); d.text((1300, 660), "NOT THE SR22T (TURBO)", font=MB(28), fill=GREY, anchor="mm")
    te = trig(bid, "every")
    if t > te:
        panel(d, [480, 740, 1440, 900]); d.text((960, 790), "EVERY COMPARISON IN THIS EPISODE", font=MB(26), fill=GREY, anchor="mm")
        d.text((960, 852), "G3 SR22 ONLY · BUILT ABOUT 2007–2012", font=BB(56), fill=CYAN, anchor="mm")

def sc_pick(im, t, s0, s1):
    bid = BID["pick"]
    im.paste(kb(photo_bg(P2, dark=0.45), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); rep_label(im, REP)
    to = trig(bid, "One")
    if t < to - 0.3:
        p = (t - s0 - 0.3) / 1.2
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 110))
        d.text((W / 2, 380), count(399900, p), font=MB(150), fill=WHITE, anchor="mm")
        d.text((W / 2, 500), "N814LT · 2010 CIRRUS SR22 G3 · OFFERED BY A LARGE DEALER · OHIO", font=MB(30), fill=CYAN, anchor="mm")
        if t > trig(bid, "Garmin"): chip_c(d, 590, "GARMIN PERSPECTIVE GLASS · AIR CONDITIONING · KNOWN-ICING APPROVAL", f=MB(28))
        if t > trig(bid, "engine") - 0.2: chip_c(d, 670, "ENGINE: 1,100 HOURS SINCE OVERHAUL (PER THE AD)", fill=(15, 42, 63), fg=OFF, f=MB(28))
    else:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 165))
        p = ease((t - to + 0.3) / 0.6)
        panel(d, [460, 200, 1460, 620]); d.text((W / 2, 280), "AIRFRAME", font=MB(30), fill=GREY, anchor="mm")
        d.text((W / 2, 410), "3,102", font=MB(170), fill=(*CYAN, int(255 * p)), anchor="mm"); d.text((W / 2, 540), "HOURS", font=MB(30), fill=GREY, anchor="mm")
        tth = trig(bid, "average")
        if t > tth - 0.2: report_slide(im, t, "mktcomp", (40, 110, 380, 245), [(BX("mktcomp", "This aircraft: 3,102"), tth + 0.4)], t0=tth - 0.2, cy=770, maxh=240, maxw=900)

def sc_header(im, t, s0, s1):
    bid = BID["header"]
    dimbg(im, t, s0, s1)
    header_bar(im, "STEP 1", "READ THE SUMMARY")
    cos = [(UNION(BX(HC, "NTSB DAMAGE"), BX(HC, "None", exact=True)), trig(bid, "accident")),
           (UNION(BX(HC, "CURRENT OWNERSHIP"), BX(HC, "Certificate issued")), trig(bid, "company")),
           (UNION(BX(HC, "FINANCING"), BX(HC, "Window 2025")), trig(bid, "loan")),
           (UNION(BX(HC, "MAJOR AD"), BX(HC, "$17,000")), trig(bid, "parachute")),
           (UNION(BX(HC, "USE TYPE"), BX(HC, "0.5 flights")), trig(bid, "use"))]
    report_slide(im, t, HC, (0, 0, 1152, VOFF + 400), cos, t0=s0, cy=520, maxh=800)

def sc_value(im, t, s0, s1):
    bid = BID["value"]
    dimbg(im, t, s0, s1, P1)
    header_bar(im, "STEP 2", "IS THE PRICE RIGHT?")
    cos = [(UNION(BX("valuation", "COMP COUNT"), BX("valuation", "19 active")), trig(bid, "nineteen")),
           (UNION(BX("valuation", "ESTIMATED VALUE"), BX("valuation", "$444,900", 1)), trig(bid, "estimate")),
           (UNION(BX("valuation", "ESTIMATED RANGE"), BX("valuation", "$429,900")), trig(bid, "range")),
           (UNION(BX("valuation", "NET ADJUSTMENT"), BX("valuation", "+$0")), trig(bid, "adjustment"))]
    report_slide(im, t, "valuation", (25, 95, 1127, 385), cos, t0=s0, cy=440, maxh=600)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "below") - 0.2: chip_c(d, 790, "ASKING $399,900 · $45,000 UNDER THE ESTIMATE · BELOW THE RANGE", f=MB(28))
    if t > trig(bid, "hours"): chip_c(d, 860, "THE ESTIMATE HAS NOT COUNTED THIS AIRPLANE'S HOURS YET", fill=AMBER, f=MB(28))

def sc_adjust(im, t, s0, s1):
    bid = BID["adjust"]
    dimbg(im, t, s0, s1, P1)
    header_bar(im, "STEP 2", "REFINE WITH THIS AIRPLANE'S HOURS")
    tp = trig(bid, "Press"); tn = trig(bid, "takes")
    if t < tn - 0.15:
        cos = [((38, 455, 905, 525), trig(bid, "hours")), (BX("valuation", "Update valuation", pad=2), tp)]
        report_slide(im, t, "valuation", (25, 200, 1127, 620), cos, t0=s0, cy=500, maxh=700)
    else:
        cos = [(UNION(BX("valafter", "Airframe time"), BX("valafter", "−$8,913", 2)), tn + 0.2),
               (UNION(BX("valafter", "ADJUSTED VALUE"), BX("valafter", "$435,987")), trig(bid, "adjusted"))]
        report_slide(im, t, "valafter", (25, 200, 1127, 640), cos, t0=tn - 0.15, cy=480, maxh=720)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "paper"): chip_c(d, 880, "ASKING $399,900 · ABOUT $36,000 UNDER THE ADJUSTED VALUE", f=MB(28))

def sc_hours(im, t, s0, s1):
    bid = BID["hours"]
    dimbg(im, t, s0, s1, P3)
    header_bar(im, "STEP 2", "WHAT DO HIGH-HOUR G3s ASK?")
    tc = trig(bid, "checked")
    if t < tc - 0.3:
        cos = [((604, 164, 1106, 236), trig(bid, "twenty", 1)), ((45, 430, 547, 500), trig(bid, "seven")), ((604, 256, 1106, 328), trig(bid, "seven") + 2.5)]
        report_slide(im, t, "signals", (25, 100, 1127, 600), cos, t0=s0, cy=520, maxh=780)
    else:
        d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 880])
        d.text((W / 2, 200), "G3 SR22s WITH ABOUT 2,800–3,100 AIRFRAME HOURS · TRACKED SINCE APRIL 2026", font=MB(26), fill=GREY, anchor="mm")
        rows = [("2009", "3,100 h", 385000), ("2008", "2,800 h", 395000), ("2010", "3,102 h", 399900), ("2008", "3,110 h", 419900), ("2009", "3,120 h", 429900), ("2007", "3,111 h", 430000)]
        X = lambda v: 520 + (v - 370000) / (450000 - 370000) * 1180
        ts = trig(bid, "Six")
        for i, (y, h, v) in enumerate(rows):
            p = ease((t - ts - i * 0.2) / 0.4)
            if p <= 0: continue
            yy = 270 + i * 82; hero = v == 399900; col = CYAN if hero else OFF
            d.text((150, yy), y, font=MB(26), fill=(*col, int(255 * p)), anchor="lm"); d.text((470, yy), h, font=MR(24), fill=(*GREY, int(255 * p)), anchor="rm")
            d.rounded_rectangle([520, yy - 16, X(v), yy + 16], radius=6, fill=(*((37, 197, 203) if hero else (70, 92, 110)), int(255 * p)))
            d.text((X(v) + 14, yy), money(v) + ("  ← THIS AIRPLANE" if hero else ""), font=MB(26), fill=(*col, int(255 * p)), anchor="lm")
        tf = trig(bid, "fair,")
        if t > tf - 0.2: chip_c(d, 790, "IN LINE WITH HIGH-HOUR G3s · FAIR, NOT A BARGAIN", f=MB(30))
        chip_c(d, 920, "NEXTPLANE LISTING DATA · CIRRUS SR22 G3 ONLY · ONE PER TAIL · ASKING PRICES, NOT SALE PRICES", fill=(15, 42, 63), fg=OFF, f=MB(20))

def sc_engine(im, t, s0, s1):
    bid = BID["engine"]
    dimbg(im, t, s0, s1, P2)
    header_bar(im, "STEP 2", "WHAT ABOUT THE ENGINE?")
    cos = [(UNION(BX("cpm", "THIS AIRCRAFT"), BX("cpm", "1,100 hr SMOH")), trig(bid, "nine")),
           (UNION(BX("cpm", "MARKET AVERAGE"), BX("cpm", "1,051 hr")), trig(bid, "typical")),
           (BX("cpm", "$0.03/nm"), trig(bid, "ordinary"))]
    report_slide(im, t, "cpm", (0, 0, 1152, 400), cos, t0=s0, cy=470, maxh=640)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "nine"): chip_c(d, 840, "≈ 900 HOURS UNTIL THE ENGINE IS DUE FOR AN OVERHAUL", f=MB(28))
    if t > trig(bid, "discount"): chip_c(d, 910, "THE DISCOUNT IS ABOUT THE AIRFRAME HOURS, NOT THE ENGINE", fill=AMBER, f=MB(28))

def sc_flight(im, t, s0, s1):
    bid = BID["flight"]
    dimbg(im, t, s0, s1, P4, dark=0.82)
    header_bar(im, "STEP 2", "HOW HAS IT BEEN USED?")
    cos = [(BX("flight", "12", 1, pad=4), trig(bid, "twelve", 1)), ((222, 128, 340, 172), trig(bid, "twelve", 2))]
    report_slide(im, t, "flight", (0, 0, 1152, 210), cos, t0=s0, cy=270, maxh=330)
    tm = trig(bid, "monthly")
    if t > tm - 0.3:
        report_slide(im, t, "fl_monthly", (0, 0, 543, 318), [((140, 60, 400, 300), trig(bid, "twenty", 2))], t0=tm - 0.3, cy=700, maxh=440, maxw=780, cx=520)
    tl = trig(bid, "last")
    tc = trig(bid, "calls")
    if tl - 0.3 < t < tc - 0.2:
        report_slide(im, t, "fl_period", (0, 0, 1102, 238), [(UNION(BX("fl_period", "Last 3 months"), BX("fl_period", "~0.0")), tl + 0.2)], t0=tl - 0.3, cy=700, maxh=320, maxw=900, cx=1400)
    if t > tc - 0.2:
        report_slide(im, t, HC, (0, VOFF, 290, VOFF + 95), [(UNION(BX(HC, "USE TYPE"), BX(HC, "Very Light")), tc)], t0=tc - 0.2, cy=640, maxh=280, maxw=780, cx=1400)
    d = ImageDraw.Draw(im, "RGBA")
    ta = trig(bid, "Ask")
    if t > ta: chip(d, 1020, 830, "ASK: WHEN DID IT LAST FLY?", f=MB(28))

def sc_pricehist(im, t, s0, s1):
    bid = BID["pricehist"]
    dimbg(im, t, s0, s1, P1)
    header_bar(im, "STEP 2", "HAS THE SELLER MOVED?")
    cos = [(UNION(BX("listhist", "PRICE SINCE FIRST SEEN"), BX("listhist", "First seen at")), trig(bid, "April")),
           (UNION(BX("listhist", "PRICE CUTS"), BX("listhist", "Largest")), trig(bid, "Four")),
           (UNION(BX("listhist", "Oct 23, 2026"), BX("listhist", "$399,900", 3)), trig(bid, "October")),
           ((32, 222, 640, 290), trig(bid, "warning"))]
    report_slide(im, t, "listhist", (0, 0, 1152, 790), cos, t0=s0, cy=525, maxh=810)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "lower"): chip_c(d, 960, "NEGOTIATE FROM $399,900, NOT $459,900", fill=AMBER, f=MB(30))

def sc_cohort(im, t, s0, s1):
    bid = BID["cohort"]
    dimbg(im, t, s0, s1, P3, dark=0.86)
    header_bar(im, "STEP 2", "IS THAT NORMAL FOR A G3?")
    d = ImageDraw.Draw(im, "RGBA")
    ts = trig(bid, "twenty-nine")
    if t > ts - 0.2:
        panel(d, [110, 150, 1810, 330]); d.text((W / 2, 205), "WE FOLLOWED", font=MB(26), fill=GREY, anchor="mm")
        d.text((W / 2, 275), "29 G3 SR22s TRACKED SINCE APRIL 2026", font=BB(64), fill=OFF, anchor="mm")
    items = [("CUT THEIR PRICE", "11 of 29", "typical cut 4.2% · ≈ $25,000", trig(bid, "four", 1)),
             ("THIS SELLER'S CUT", "−14.9%", "the largest of the 11", trig(bid, "largest")),
             ("THIS AIRPLANE FOR SALE", "221 days", "3rd-longest of the 29", trig(bid, "third"))]
    x = 110
    for lab, v, sub, tt in items:
        p = ease((t - tt) / 0.6)
        if p > 0:
            panel(d, [x, 370, x + 540, 640]); d.text((x + 270, 420), lab, font=MB(24), fill=GREY, anchor="mm")
            d.text((x + 270, 515), v, font=MB(72), fill=(*(CYAN if "THIS" in lab else WHITE), int(255 * p)), anchor="mm"); d.text((x + 270, 595), sub, font=MR(22), fill=CYAN, anchor="mm")
        x += 580
    chip_c(d, 720, "NEXTPLANE LISTING DATA · CIRRUS SR22 G3 (2007–2012) ONLY · ONE PER TAIL · ASKS, NOT SALE PRICES", fill=(15, 42, 63), fg=OFF, f=MB(20))

def sc_owner(im, t, s0, s1):
    bid = BID["owner"]
    dimbg(im, t, s0, s1, P2)
    header_bar(im, "STEP 2", "WHO OWNS IT? IS THERE A LOAN?")
    cos = [(UNION(BX("reg", "STATE"), BX("reg", "NY", exact=True)), trig(bid, "York")),
           (UNION(BX("reg", "CERTIFICATE DATE"), BX("reg", "Sep 6, 2017", 1)), trig(bid, "September")),
           (UNION(BX("reg", "FINANCING & LIENS"), BX("reg", "0 agreements")), trig(bid, "loan", 2))]
    report_slide(im, t, "reg", (0, 0, 1152, 520), cos, t0=s0, cy=470, maxh=700)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "dealer") - 0.2: chip_c(d, 880, "OWNER: A NEW YORK COMPANY · SELLER: A DEALER IN OHIO", fill=AMBER, f=MB(28))
    if t > trig(bid, "title"): chip_c(d, 950, "TITLE SEARCH + ESCROW", f=MB(28))

def sc_seller(im, t, s0, s1):
    bid = BID["seller"]
    dimbg(im, t, s0, s1, P3)
    header_bar(im, "STEP 2", "WHO ARE YOU DEALING WITH?")
    tb = trig(bid, "Before")
    if t < tb - 0.3:
        report_slide(im, t, "sellertop", (215, 88, 1385, 272), [((995, 202, 1182, 266), trig(bid, "eight"))], t0=s0, cy=330, maxh=330, maxw=1700)
        ta = trig(bid, "airplane", 1)
        if t > ta - 0.3:
            cos = [((226, 50, 602, 105), ta + 0.3), ((997, 50, 1376, 105), trig(bid, "forty-four"))]
            report_slide(im, t, "sellerusual", (215, 10, 1385, 112), cos, t0=ta - 0.3, cy=700, maxh=260, maxw=1700)
            d = ImageDraw.Draw(im, "RGBA")
            if t > ta + 0.3: chip_c(d, 820, "DEALER USUALLY +8.3% VS MARKET · THIS AIRPLANE −10.1%", f=MB(28))
            if t > trig(bid, "forty-four"): chip_c(d, 890, "FOR SALE 221 DAYS · THEIR TYPICAL SALE 44 DAYS", fill=AMBER, f=MB(28))
    else:
        cos = [(BX("before", "This unit has sat", x1=600), trig(bid, "sat")), (BX("before", "They have", x1=636), trig(bid, "stock"))]
        report_slide(im, t, "before", (22, 94, 645, 172), cos, t0=tb - 0.3, cy=500, maxh=420, maxw=1700)

def sc_safety(im, t, s0, s1):
    bid = BID["safety"]
    dimbg(im, t, s0, s1, P2)
    header_bar(im, "STEP 2", "WHAT SHOULD THE LOGBOOKS SHOW?")
    tp = trig(bid, "parachute")
    tn = trig(bid, "service")
    if t < tp - 0.3:
        cos = [((22, 782, 1128, 975), trig(bid, "mandatory")), ((28, 616, 168, 690), trig(bid, "repeat"))]
        report_slide(im, t, "ads", (0, 450, 1152, 980), cos, t0=s0, cy=520, maxh=760)
    elif t < tn - 0.3:
        cos = [((20, 1972, 1128, 2028), tp + 0.4), ((295, 1988, 345, 2012), trig(bid, "twenty", 3))]
        report_slide(im, t, "ads", (0, 1905, 1152, 2032), cos, t0=tp - 0.3, cy=360, maxh=340, maxw=1700)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "seventeen") - 0.2:
            panel(d, [360, 590, 1560, 860]); d.text((W / 2, 650), "PARACHUTE REPACK · ≈ $17,000 · EVERY 10 YEARS", font=MB(28), fill=GREY, anchor="mm")
            d.text((W / 2, 740), "DUE FEB 2020 · NEXT FEB 2030", font=BB(76), fill=CYAN, anchor="mm")
            if t > trig(bid, "records"): d.text((W / 2, 815), "ASK TO SEE THE 2020 REPACK IN THE RECORDS", font=MB(26), fill=OFF, anchor="mm")
    else:
        k = BXS("sdr", "No Service Difficulty", pad=0)[0]
        report_slide(im, t, "sdr", (0, k[1] - 40, 1152, k[1] + 50), [(k, tn + 0.2)], t0=tn - 0.3, cy=540, maxh=260, maxw=1500)

def sc_opcost(im, t, s0, s1):
    bid = BID["opcost"]
    dimbg(im, t, s0, s1, P3)
    header_bar(im, "STEP 2", "WHAT WILL IT COST TO KEEP?")
    cos = [(UNION(BX("opcost", "Total Annual Cost"), BX("opcost", "$35,125")), trig(bid, "thirty-five")),
           (UNION(BX("opcost", "Cost per Flight Hour"), BX("opcost", "$293/hr")), trig(bid, "ninety-three")),
           (UNION(BX("opcost", "Engine Overhaul Accrual"), BX("opcost", "$3,906")), trig(bid, "engine", 1))]
    report_slide(im, t, "opcost", (0, 0, 1152, 545), cos, t0=s0, cy=510, maxh=780)

def sc_offer(im, t, s0, s1):
    bid = BID["offer"]
    dimbg(im, t, s0, s1, P1, dark=0.88)
    header_bar(im, "STEP 3", "WHAT TO OFFER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [90, 140, 1830, 920])
    d.text((140, 185), "FROM THE NEXTPLANE REPORT ON N814LT · NOT ADVICE", font=MB(22), fill=GREY, anchor="lm")
    X = lambda v: 200 + (v - 360000) / (460000 - 360000) * 1520
    d.line([200, 520, 1720, 520], fill=(90, 110, 128), width=4)
    for v in range(360000, 460001, 20000):
        d.line([X(v), 505, X(v), 535], fill=(90, 110, 128), width=3); d.text((X(v), 565), "${}K".format(v // 1000), font=MR(22), fill=GREY, anchor="mm")
    tb = trig(bid, "between")
    if t > tb - 0.2:
        p = ease((t - tb + 0.2) / 0.5)
        d.rounded_rectangle([X(385000), 588, X(430000), 618], radius=8, fill=(70, 92, 110, int(230 * p)))
        d.text(((X(385000) + X(430000)) / 2, 603), "G3s WITH ≈3,100 H ASK $385K–$430K", font=MB(18), fill=(*OFF, int(255 * p)), anchor="mm")
    marks = [(444900, "ESTIMATE · TYPICAL G3", "$444,900", trig(bid, "typical"), OFF, 300),
             (435987, "ADJUSTED FOR HOURS", "$435,987", trig(bid, "Adjusted"), CYAN, 400),
             (399900, "ASKING", "$399,900", trig(bid, "steps"), WHITE, 400)]
    for v, lab, val, ts, col, yy in marks:
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        d.line([X(v), yy + 60, X(v), 520], fill=(*col, int(200 * p)), width=3)
        d.ellipse([X(v) - 12, 508, X(v) + 12, 532], fill=(*col, int(255 * p)))
        d.text((X(v), yy), lab, font=MB(20), fill=(*col, int(255 * p)), anchor="mm"); d.text((X(v), yy + 32), val, font=MB(28), fill=(*col, int(255 * p)), anchor="mm")
    tc = trig(bid, "steps")
    if t > tc: d.text((W / 2, 670), "CUTS OF $20,000 · FOR SALE 221 DAYS · DEALER'S TYPICAL SALE 44 DAYS", font=MB(28), fill=OFF, anchor="mm")
    to = trig(bid, "opening")
    if t > to - 0.2:
        p = ease((t - to + 0.2) / 0.5)
        d.polygon([(X(380000) - 16, 470), (X(380000) + 16, 470), (X(380000), 500)], fill=(*CYAN, int(255 * p)))
        d.rounded_rectangle([340, 715, 1580, 815], radius=16, fill=(*CYAN, int(255 * p)))
        d.text((W / 2, 765), "OPENING NEAR $380,000 · ONE $20,000 STEP UNDER THE ASK", font=MB(32), fill=(*NAVY, int(255 * p)), anchor="mm")
    tm = trig(bid, "subject")
    if t > tm: d.text((W / 2, 870), "SUBJECT TO: PRE-BUY FOR AN AIRPLANE THAT SAT · PARACHUTE RECORDS · CLEAN TITLE", font=MB(24), fill=CYAN, anchor="mm")

def sc_verdict(im, t, s0, s1):
    bid = BID["verdict"]
    im.paste(kb(photo_bg(P1, dark=0.62, focus=(0.5, 0.5)), (t - s0) / (s1 - s0), 1.0, 1.06))
    rep_label(im, REP); header_bar(im, "VERDICT", "WHO IS IT RIGHT FOR?")
    d = ImageDraw.Draw(im, "RGBA")
    tb = trig(bid, "buyer")
    if t > tb - 0.2:
        panel(d, [110, 190, 940, 560], a=215); d.text((150, 245), "RIGHT FOR", font=MB(28), fill=CYAN, anchor="lm")
        bullet(d, 150, 325, "You want a G3 with Perspective + A/C", BS(40))
        if t > trig(bid, "fine"): bullet(d, 150, 405, "You're fine with high airframe hours", BS(40))
    if t > trig(bid, "not", 1):
        panel(d, [980, 190, 1810, 560], a=215); d.text((1020, 245), "NOT RIGHT IF", font=MB(28), fill=RED, anchor="lm")
        bullet(d, 1020, 325, "You want low hours", BS(42), mark="no")
    tp = trig(bid, "paying")
    if t > tp: big_line(d, 650, "A FAIR PRICE FOR THOSE HOURS, NOT A BARGAIN", BB(60), OFF, (t - tp) / 0.4)
    tq = trig(bid, "Check")
    if t > tq: big_line(d, 745, "WHEN IT LAST FLEW  ·  PARACHUTE RECORDS  ·  WHICH PRICE", BB(46), CYAN, (t - tq) / 0.4)

def sc_end(im, t, s0, s1):
    p = Image.new("RGB", (1080, 1920), NAVY)
    EC.draw_endcard(p, t - s0, FD, f"{ROOT}/assets/logo.png")
    p = p.crop((0, 380, 1080, 1480)).resize((1000, 1019), Image.LANCZOS)
    im.paste(NAVY, (0, 0, W, H)); im.paste(p, ((W - 1000) // 2, 0))
    d = ImageDraw.Draw(im, "RGBA"); a = ease((t - s0 - 2.6) / 0.5)
    if a > 0:
        d.text((W / 2, 1035), "KNOW WHAT TO OFFER BEFORE YOU CALL THE SELLER  ·  $29 PER AIRPLANE", font=MB(28), fill=(*CYAN, int(255 * a)), anchor="mm")

SCENE_FN = {k[3:]: v for k, v in list(globals().items()) if k.startswith("sc_")}
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
        os.makedirs(f"{ROOT}/stills", exist_ok=True)
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f"{ROOT}/stills/still_{float(ts):07.2f}.png")
    elif sys.argv[1] == "words":
        for s, e, w, b in WORDS:
            if b == sys.argv[2]: print(round(s, 2), w)
    elif sys.argv[1] == "seg":
        i, n = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(f"{ROOT}/segs", exist_ok=True)
        NF = int(math.ceil(TOTAL * FPS)); a, b = NF * i // n, NF * (i + 1) // n
        out = f"{ROOT}/segs/seg_{i:02d}.mp4"
        pr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                               "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out + ".part.mp4"], stdin=subprocess.PIPE)
        for f in range(a, b):
            pr.stdin.write(frame(f / FPS).tobytes())
        pr.stdin.close(); pr.wait(); os.replace(out + ".part.mp4", out); print("seg", i, "frames", a, b, "done")
