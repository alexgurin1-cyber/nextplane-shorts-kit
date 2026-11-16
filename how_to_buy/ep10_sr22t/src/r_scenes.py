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
# Masking (Alex): owner names (people and LLCs), seller names, data-source labels and fine print, inflated comp counts.
RELABEL = {HC: [(BX(HC, "NTSB DAMAGE"), "ACCIDENT RECORD"), (BX(HC, "USE TYPE"), "USE TYPE"),
                (BX(HC, "FINANCING ·"), "FINANCING"), (BX(HC, "SDR ·"), "SERVICE PROBLEMS")],
           "sdr": [(BX("sdr", "SERVICE DIFFICULTY REPORTS"), "SERVICE PROBLEMS")] + ([(BX("sdr", "No Service Difficulty"), "No service problem reports on this aircraft.")] if BXS("sdr", "No Service Difficulty") else []),
           "flight": [(BX("flight", "24-month history"), "24-month flight history")]}
EXTRA_BLUR = {HC: BXS(HC, "BERICHI", "FAA document index +", "Records searched", "Security agreement 2026") + [(90, VOFF + 414, 178, VOFF + 444)],
              "listhist": BXS("listhist", "Listed by", "An ad that disappears", "NextPlane began"),
              "reg": BXS("reg", "BERICHI", "The FAA registry", "A security conveyance is", "Repossession (REP)", "A dereg_removed",
                         "Derived from the FAA", "Engine and propeller securit", "Enter the engine", "2 agreements"),
              "sdr": BXS("sdr", "FAA Service Difficulty"),
              "valuation": BXS("valuation", "191 active", "Based on 191", "The estimated value"),
              "valafter": BXS("valafter", "191 active", "Based on 191", "The estimated value"),
              "opcost": BXS("opcost", "Region:"),
              "specs": BXS("specs", "Generation G6 per")}

def rep_label(im, txt):
    d = ImageDraw.Draw(im, "RGBA"); d.text((70, 925), txt, font=MR(18), fill=(200, 210, 218, 190), anchor="lm")
def big_line(d, y, txt, f=None, fill=OFF, p=1.0):
    f = f or BB(62); d.text((W / 2, y), txt, font=f, fill=(*fill, int(255 * min(max(p, 0), 1))), anchor="mm")
def chip_c(d, y, txt, f=None, fill=CYAN, fg=NAVY):
    f = f or MB(26); tw = d.textlength(txt, font=f); chip(d, W / 2 - tw / 2 - 18, y, txt, fill=fill, fg=fg, f=f)
RED = (230, 120, 110); AMBER = (240, 170, 80)
REP = "REPRESENTATIVE PHOTO · CIRRUS SR22T · NOT THE AIRCRAFT FOR SALE"
P1, P2, P3, P4 = "sr22t-1.jpg", "sr22t-7.jpg", "sr22t-5.jpg", "sr22t-0.jpg"
def dimbg(im, t, s0, s1, ph=P3, blur=14, dark=0.84):
    im.paste(kb(photo_bg(ph, blur=blur, dark=dark), (t - s0) / max(s1 - s0, 1)))

def sc_title(im, t, s0, s1):
    bid = BID["title"]
    tt = trig(bid, "This", 3)
    if t < tt - 0.2:
        dimbg(im, t, s0, s1, P1, blur=8, dark=0.8)
        report_slide(im, t, HC, (0, 0, 1152, 220), [(UNION(BX(HC, "ASKING PRICE"), BX(HC, "$819,000")), s0 + 0.6),
                                                     (UNION(BX(HC, "NTSB DAMAGE"), BX(HC, "None", exact=True)), trig(bid, "damage.", 2))], t0=s0, cy=300, maxh=420)
        d = ImageDraw.Draw(im, "RGBA")
        tq = trig(bid, "Is")
        if t > tq - 0.1: big_line(d, 640, "IS THAT THE RIGHT PRICE?", BB(110), CYAN, (t - tq + 0.1) / 0.4)
        tw = trig(bid, "worked.")
        if t > trig(bid, "shows") - 0.2: chip_c(d, 760, "959 FLIGHTS IN 2 YEARS · 1,678 HOURS ON A 2023", f=MB(30))
    else:
        im.paste(kb(photo_bg(P1, dark=0.35, focus=(0.55, 0.5)), (t - s0) / (s1 - s0), 1.0, 1.08))
        d = ImageDraw.Draw(im, "RGBA"); d.rectangle([0, 0, W, H], fill=(8, 16, 26, 120))
        p = ease((t - tt) / 0.8)
        d.text((W / 2, 380), "HOW TO BUY A", font=BB(90), fill=(*OFF, int(255 * p)), anchor="mm")
        d.text((W / 2, 505), "CIRRUS SR22T", font=BB(170), fill=(*CYAN, int(255 * p)), anchor="mm")
        d.text((W / 2, 645), "ONE REAL AIRPLANE FOR SALE · ONE REAL REPORT · WHAT TO OFFER", font=MB(30), fill=(*OFF, int(220 * p)), anchor="mm")
        rep_label(im, REP)

# ---------- product demo: the lookup ----------
LK = f"{ROOT}/lookup"
LBLUR = {"home": [(1200, 760, 1390, 792)],
         "report": [(1475, 532, 1795, 572), (1130, 735, 1380, 757), (440, 1010, 1600, 1034), (532, 958, 624, 986)]}
LRELAB = {"report": [((786, 338, 990, 358), "ACCIDENT RECORD"), ((440, 476, 600, 496), "USE TYPE"),
                     ((440, 677, 720, 697), "FINANCING"), ((1476, 677, 1660, 697), "SERVICE PROBLEMS")]}
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
    dimbg(im, t, s0, s1, P4, blur=14, dark=0.86)
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
    dimbg(im, t, s0, s1, P4)
    header_bar(im, "FIRST", "WHICH CIRRUS IS THIS?")
    d = ImageDraw.Draw(im, "RGBA")
    gens = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G7+"]
    tg = trig(bid, "generations")
    if t > tg - 0.2:
        x = 110
        for i, g in enumerate(gens):
            p = ease((t - tg - i * 0.25) / 0.4)
            if p <= 0: continue
            hero = g == "G6" and t > trig(bid, "confirms")
            fill = CYAN if hero else (15, 42, 63)
            d.rounded_rectangle([x, 170, x + 190, 270], radius=14, fill=(*fill, int(255 * p)), outline=(*CYAN, int(160 * p)), width=2)
            d.text((x + 95, 220), g, font=BB(64), fill=(*(NAVY if hero else OFF), int(255 * p)), anchor="mm")
            if g == "G4" and t > trig(bid, "G4."):
                d.line([x + 20, 250, x + 170, 190], fill=RED, width=7)
            x += 218
    if t > trig(bid, "turbocharged") - 0.2: d.text((W / 2, 320), "SR22T = THE TURBOCHARGED SR22", font=MB(30), fill=OFF, anchor="mm")
    tc = trig(bid, "confirms")
    if t > tc - 0.4:
        report_slide(im, t, "specs", (0, 0, 568, 318), [(BX("specs", "G6 Turbo"), tc + 0.3)], t0=tc - 0.4, cy=620, maxh=500, cx=700)
    te = trig(bid, "every")
    if t > te:
        panel(d, [1180, 470, 1810, 780]); d.text((1495, 560), "EVERY COMPARISON", font=MB(30), fill=GREY, anchor="mm")
        d.text((1495, 650), "G6 SR22T ONLY", font=BB(80), fill=CYAN, anchor="mm"); d.text((1495, 725), "BUILT 2017–2023", font=MB(26), fill=OFF, anchor="mm")

def sc_pick(im, t, s0, s1):
    bid = BID["pick"]
    im.paste(kb(photo_bg(P2, dark=0.45), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); rep_label(im, REP)
    to = trig(bid, "One")
    if t < to - 0.3:
        p = (t - s0 - 0.3) / 1.2
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 100))
        d.text((W / 2, 400), count(819000, p), font=MB(150), fill=WHITE, anchor="mm")
        d.text((W / 2, 520), "N657CB · 2023 CIRRUS SR22T G6 · PRIVATE OWNER · FORT LAUDERDALE, FL", font=MB(30), fill=CYAN, anchor="mm")
        if t > trig(bid, "Garmin"): chip_c(d, 620, "GARMIN PERSPECTIVE+ GLASS · AIR CONDITIONING · KNOWN-ICING APPROVAL", f=MB(28))
    else:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 160))
        p = ease((t - to + 0.3) / 0.6)
        panel(d, [460, 220, 1460, 640]); d.text((W / 2, 300), "AIRFRAME AND ENGINE", font=MB(30), fill=GREY, anchor="mm")
        d.text((W / 2, 430), "1,678", font=MB(170), fill=(*CYAN, int(255 * p)), anchor="mm"); d.text((W / 2, 560), "HOURS", font=MB(30), fill=GREY, anchor="mm")
        tth = trig(bid, "three-year-old")
        if t > tth: chip_c(d, 690, "ON AN AIRPLANE BUILT IN 2023", f=MB(32))

def sc_header(im, t, s0, s1):
    bid = BID["header"]
    dimbg(im, t, s0, s1)
    header_bar(im, "STEP 1", "READ THE SUMMARY")
    cos = [(UNION(BX(HC, "NTSB DAMAGE"), BX(HC, "None", exact=True)), trig(bid, "accident")),
           (UNION(BX(HC, "CURRENT OWNERSHIP"), BX(HC, "Certificate issued")), trig(bid, "company")),
           (UNION(BX(HC, "FINANCING"), BX(HC, "Security conveyance")), trig(bid, "loan")),
           (UNION(BX(HC, "MAJOR AD"), BX(HC, "CAPS rocket")), trig(bid, "parachute")),
           (UNION(BX(HC, "USE TYPE"), BX(HC, "40.2 flights")), trig(bid, "use"))]
    report_slide(im, t, HC, (0, 0, 1152, VOFF + 330), cos, t0=s0, cy=520, maxh=790)

def sc_value(im, t, s0, s1):
    bid = BID["value"]
    dimbg(im, t, s0, s1, P1)
    header_bar(im, "STEP 2", "IS THE PRICE RIGHT?")
    cos = [(UNION(BX("valuation", "ESTIMATED VALUE"), BX("valuation", "$849,900", 1)), trig(bid, "estimate")),
           (UNION(BX("valuation", "GENERATION"), BX("valuation", "same-generation")), trig(bid, "G6", 1)),
           (UNION(BX("valuation", "NET ADJUSTMENT"), BX("valuation", "+$0")), trig(bid, "adjustment"))]
    report_slide(im, t, "valuation", (25, 95, 1127, 385), cos, t0=s0, cy=440, maxh=600)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "below"): chip_c(d, 790, "ASKING $819,000 · ABOUT $31,000 UNDER THE ESTIMATE", f=MB(28))
    if t > trig(bid, "hours"): chip_c(d, 860, "THE ESTIMATE HAS NOT COUNTED THIS AIRPLANE'S HOURS YET", fill=AMBER, f=MB(28))

def sc_adjust(im, t, s0, s1):
    bid = BID["adjust"]
    dimbg(im, t, s0, s1, P1)
    header_bar(im, "STEP 2", "REFINE WITH THIS AIRPLANE'S HOURS")
    tp = trig(bid, "Press"); tn = trig(bid, "Now", 1)
    if t < tn - 0.15:
        cos = [(UNION(BX("valuation", "TOTAL TIME"), BX("valuation", "ENGINE SMOH")) [:2] + (900, 520), trig(bid, "hours")),
               (BX("valuation", "Update valuation", pad=2) if BXS("valuation", "Update valuation") else (919, 484, 1060, 520), tp)]
        report_slide(im, t, "valuation", (25, 200, 1127, 620), cos, t0=s0, cy=500, maxh=700)
    else:
        cos = [(UNION(BX("valafter", "Airframe time"), BX("valafter", "−$7,931")), trig(bid, "eight")),
               (UNION(BX("valafter", "Engine approaching"), BX("valafter", "−$42,495")), trig(bid, "forty-two")),
               (UNION(BX("valafter", "ADJUSTED VALUE"), BX("valafter", "$799,474")), trig(bid, "adjusted"))]
        report_slide(im, t, "valafter", (25, 200, 1127, 680), cos, t0=tn - 0.15, cy=480, maxh=740)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "Now", 2): chip_c(d, 880, "ASKING $819,000 · ABOUT $19,500 ABOVE THE ADJUSTED VALUE", f=MB(28))

def sc_engine(im, t, s0, s1):
    bid = BID["engine"]
    dimbg(im, t, s0, s1, P4)
    header_bar(im, "STEP 2", "WHY THE ENGINE MATTERS")
    cos = [(BX("cpm", "Cirrus SR22T · Continental"), trig(bid, "two")),
           (UNION(BX("cpm", "THIS AIRCRAFT"), BX("cpm", "1,678 hr SMOH")), trig(bid, "three")),
           (UNION(BX("cpm", "MARKET AVERAGE"), BX("cpm", "727 hr")), trig(bid, "typical")),
           (BX("cpm", "$1.16/nm"), trig(bid, "mile"))]
    report_slide(im, t, "cpm", (0, 0, 1152, 400), cos, t0=s0, cy=470, maxh=640)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "three"): chip_c(d, 840, "≈ 322 HOURS LEFT BEFORE THE ENGINE IS DUE FOR OVERHAUL", fill=AMBER, f=MB(28))

def sc_flight(im, t, s0, s1):
    bid = BID["flight"]
    dimbg(im, t, s0, s1, P2)
    header_bar(im, "STEP 2", "HOW WAS IT USED?")
    cos = [(BX("flight", "959", 1, pad=4), trig(bid, "nine")), ((222, 128, 340, 172), trig(bid, "eight")),
           (BX("flight", "40.2", 1, pad=4), trig(bid, "forty")), ((598, 128, 650, 172), trig(bid, "hour", 1))]
    report_slide(im, t, "flight", (0, 0, 1152, 210), cos, t0=s0, cy=290, maxh=360)
    tr = trig(bid, "common")
    if t > tr - 0.3:
        cr = [(UNION(BX("fl_routes", "FXE → BCT"), BX("fl_routes", "11 nm", 1)), tr + 0.3), (UNION(BX("fl_routes", "FXE → TMB"), BX("fl_routes", "36 nm", 1)), trig(bid, "thirty-six"))]
        report_slide(im, t, "fl_routes", (0, 0, 543, 276), cr, t0=tr - 0.3, cy=690, maxh=380, maxw=760, cx=600)
    tp = trig(bid, "pattern")
    if t > tp - 0.3:
        report_slide(im, t, HC, (0, VOFF, 290, VOFF + 95), [(UNION(BX(HC, "USE TYPE"), BX(HC, "Likely trainer")), tp)], t0=tp - 0.3, cy=690, maxh=300, maxw=700, cx=1390)

def sc_period(im, t, s0, s1):
    bid = BID["period"]
    dimbg(im, t, s0, s1, P2)
    header_bar(im, "STEP 2", "IS IT STILL FLYING THAT MUCH?")
    cos = [(UNION(BX("fl_period", "Last 12 months"), BX("fl_period", "~420.3")), trig(bid, "twelve")),
           (UNION(BX("fl_period", "Last 3 months"), BX("fl_period", "~40.6")), trig(bid, "three"))]
    report_slide(im, t, "fl_period", (0, 0, 1102, 238), cos, t0=s0, cy=300, maxh=380)
    tj = trig(bid, "slowed")
    if t > tj - 0.4: report_slide(im, t, "fl_monthly", (0, 0, 543, 319), [], t0=tj - 0.4, cy=700, maxh=400, maxw=900)

def sc_pricehist(im, t, s0, s1):
    bid = BID["pricehist"]
    dimbg(im, t, s0, s1, P1)
    header_bar(im, "STEP 2", "HAS THE SELLER MOVED?")
    cos = [(UNION(BX("listhist", "PRICE SINCE FIRST SEEN"), BX("listhist", "First seen at")), trig(bid, "May")),
           (UNION(BX("listhist", "PRICE CUTS"), BX("listhist", "Largest")), trig(bid, "Six")),
           (UNION(BX("listhist", "Oct 9, 2026"), BX("listhist", "$819,000", 2)), trig(bid, "October"))]
    report_slide(im, t, "listhist", (0, 0, 1152, 640), cos, t0=s0, cy=525, maxh=800)

COH = dict(n=87, cut=43, cutpct=3.7, cutd=30000, past90=46, gone30=10, rank=5)
def sc_cohort(im, t, s0, s1):
    bid = BID["cohort"]
    dimbg(im, t, s0, s1, P3, dark=0.86)
    header_bar(im, "STEP 2", "IS THAT NORMAL FOR A G6 SR22T?")
    d = ImageDraw.Draw(im, "RGBA")
    ts = trig(bid, "eighty-seven")
    if t > ts - 0.2:
        panel(d, [110, 150, 1810, 330]); d.text((W / 2, 205), "WE FOLLOWED", font=MB(26), fill=GREY, anchor="mm")
        d.text((W / 2, 275), "87 G6 SR22Ts FIRST LISTED APR 20 – AUG 15, 2026", font=BB(64), fill=OFF, anchor="mm")
    items = [("CUT THEIR PRICE", "43 of 87", "typical cut 3.7% · ≈ $30,000", trig(bid, "half", 1)),
             ("LISTED OVER 90 DAYS", "46 of 87", "more than half", trig(bid, "ninety")),
             ("LEFT WITHIN 30 DAYS", "10 of 87", "about one in ten", trig(bid, "ten"))]
    x = 110
    for lab, v, sub, tt in items:
        p = ease((t - tt) / 0.6)
        if p > 0:
            panel(d, [x, 370, x + 540, 640]); d.text((x + 270, 420), lab, font=MB(24), fill=GREY, anchor="mm")
            d.text((x + 270, 515), v, font=MB(72), fill=(*WHITE, int(255 * p)), anchor="mm"); d.text((x + 270, 595), sub, font=MR(22), fill=CYAN, anchor="mm")
        x += 580
    if t > trig(bid, "This"): chip_c(d, 700, "THIS SELLER: −9.0% · THE 5th-LARGEST CUT OF THE 43", f=MB(32))
    chip_c(d, 800, "NEXTPLANE LISTING PANEL · CIRRUS SR22T G6 (2017–2023) ONLY · ONE PER TAIL · ASKS, NOT SALE PRICES", fill=(15, 42, 63), fg=OFF, f=MB(20))

def sc_owner(im, t, s0, s1):
    bid = BID["owner"]
    dimbg(im, t, s0, s1, P4)
    header_bar(im, "STEP 2", "WHO OWNS IT? IS THERE A LOAN?")
    cos = [(UNION(BX("reg", "CERTIFICATE DATE"), BX("reg", "May 17, 2023", 1)), trig(bid, "since")),
           (UNION(BX("reg", "Sep 3, 2026"), BX("reg", "Security agreement indexed")), trig(bid, "September")),
           (UNION(BX("reg", "FINANCING & LIENS"), BX("reg", "Latest release")), trig(bid, "release"))]
    report_slide(im, t, "reg", (0, 0, 1152, 600), cos, t0=s0, cy=520, maxh=800)

def sc_seller(im, t, s0, s1):
    bid = BID["seller"]
    dimbg(im, t, s0, s1, P2)
    header_bar(im, "STEP 2", "WHO ARE YOU DEALING WITH?")
    report_slide(im, t, "sellercard", (20, 105, 1065, 248), [((40, 118, 230, 168), trig(bid, "private")), ((550, 184, 1050, 240), trig(bid, "waited"))],
                 t0=s0, cy=300, maxh=400, maxw=1500)
    tb = trig(bid, "Before")
    if t > tb - 0.3:
        bc = [(BX("before", "Verify"), trig(bid, "Check")), (BX("before", "Use a title"), trig(bid, "escrow")), (BX("before", "Budget"), trig(bid, "pay"))]
        report_slide(im, t, "before", (0, 0, 1152, 216), bc, t0=tb - 0.3, cy=690, maxh=420, maxw=1600)

def sc_safety(im, t, s0, s1):
    bid = BID["safety"]
    dimbg(im, t, s0, s1, P4)
    header_bar(im, "STEP 2", "WHAT SHOULD THE LOGBOOKS SHOW?")
    cos = [(BX(HC, "$17,000"), trig(bid, "mandatory")), (UNION(BX(HC, "MAJOR AD"), BX(HC, "CAPS rocket")), trig(bid, "parachute"))]
    report_slide(im, t, HC, (290, VOFF, 580, VOFF + 160), cos, t0=s0, cy=330, maxh=420, maxw=820, cx=560)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "years"):
        panel(d, [1060, 200, 1800, 470]); d.text((1430, 260), "PARACHUTE REPACK", font=MB(26), fill=GREY, anchor="mm")
        d.text((1430, 345), "EVERY 10 YEARS", font=BB(76), fill=CYAN, anchor="mm"); d.text((1430, 420), "BUILT 2023 → NOT DUE SOON", font=MB(26), fill=OFF, anchor="mm")
    tn = trig(bid, "service")
    if t > tn - 0.3:
        k = BXS("sdr", "No Service Difficulty", pad=0)
        if k:
            y0 = k[0][1] - 40
            report_slide(im, t, "sdr", (0, y0, 1152, y0 + 90), [(k[0], tn + 0.2)], t0=tn - 0.3, cy=720, maxh=260, maxw=1500)
        else:
            report_slide(im, t, HC, (870, VOFF + 175, 1152, VOFF + 260), [], t0=tn - 0.3, cy=720, maxh=260, maxw=900)

def sc_opcost(im, t, s0, s1):
    bid = BID["opcost"]
    dimbg(im, t, s0, s1, P3)
    header_bar(im, "STEP 2", "WHAT WILL IT COST TO KEEP?")
    cos = [(UNION(BX("opcost", "Total Annual Cost"), BX("opcost", "$40,364")), trig(bid, "forty")),
           (UNION(BX("opcost", "Cost per Flight Hour"), BX("opcost", "$336/hr")), trig(bid, "thirty-six")),
           (UNION(BX("opcost", "Engine Overhaul Accrual"), BX("opcost", "$3,969")), trig(bid, "engine", 1))]
    report_slide(im, t, "opcost", (0, 0, 1152, 545), cos, t0=s0, cy=510, maxh=780)

def sc_offer(im, t, s0, s1):
    bid = BID["offer"]
    dimbg(im, t, s0, s1, P1, dark=0.88)
    header_bar(im, "STEP 3", "WHAT TO OFFER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [90, 140, 1830, 900])
    d.text((140, 185), "FROM THE NEXTPLANE REPORT ON N657CB · NOT ADVICE", font=MB(22), fill=GREY, anchor="lm")
    X = lambda v: 200 + (v - 770000) / (870000 - 770000) * 1520
    d.line([200, 520, 1720, 520], fill=(90, 110, 128), width=4)
    for v in range(770000, 870001, 20000):
        d.line([X(v), 505, X(v), 535], fill=(90, 110, 128), width=3); d.text((X(v), 565), "${}K".format(v // 1000), font=MR(22), fill=GREY, anchor="mm")
    marks = [(849900, "ESTIMATE · TYPICAL G6", "$849,900", trig(bid, "typical"), OFF, 300),
             (799474, "ADJUSTED FOR HOURS", "$799,474", trig(bid, "Adjusted"), CYAN, 300),
             (819000, "ASKING", "$819,000", trig(bid, "sale"), WHITE, 400),
             (794200, "RANGE STARTS", "$794,200", trig(bid, "range"), GREY, 400)]
    for v, lab, val, ts, col, yy in marks:
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        d.line([X(v), yy + 60, X(v), 520], fill=(*col, int(200 * p)), width=3)
        d.ellipse([X(v) - 12, 508, X(v) + 12, 532], fill=(*col, int(255 * p)))
        d.text((X(v), yy), lab, font=MB(20), fill=(*col, int(255 * p)), anchor="mm"); d.text((X(v), yy + 32), val, font=MB(28), fill=(*col, int(255 * p)), anchor="mm")
    tc = trig(bid, "cut", 1)
    if t > tc: d.text((W / 2, 640), "FOR SALE 6 MONTHS · 6 CUTS · ABOUT ONE A MONTH", font=MB(28), fill=OFF, anchor="mm")
    to = trig(bid, "opening")
    if t > to - 0.2:
        p = ease((t - to + 0.2) / 0.5)
        d.polygon([(X(795000) - 16, 470), (X(795000) + 16, 470), (X(795000), 500)], fill=(*CYAN, int(255 * p)))
        d.rounded_rectangle([380, 680, 1540, 780], radius=16, fill=(*CYAN, int(255 * p)))
        d.text((W / 2, 730), "OPENING NEAR $795,000 · ≈ 3% UNDER THE ASK", font=MB(32), fill=(*NAVY, int(255 * p)), anchor="mm")
    tm = trig(bid, "subject")
    if t > tm: d.text((W / 2, 840), "SUBJECT TO: PRE-BUY INSPECTION · ENGINE LOGBOOKS · CLEAN TITLE", font=MB(26), fill=CYAN, anchor="mm")

def sc_verdict(im, t, s0, s1):
    bid = BID["verdict"]
    im.paste(kb(photo_bg(P1, dark=0.62, focus=(0.6, 0.5)), (t - s0) / (s1 - s0), 1.0, 1.06))
    rep_label(im, REP); header_bar(im, "VERDICT", "WHO IS IT RIGHT FOR?")
    d = ImageDraw.Draw(im, "RGBA")
    tb = trig(bid, "buyer")
    if t > tb - 0.2:
        panel(d, [110, 190, 940, 560], a=215); d.text((150, 245), "RIGHT FOR", font=MB(28), fill=CYAN, anchor="lm")
        bullet(d, 150, 325, "You want a late G6", BS(42))
        if t > trig(bid, "budget"): bullet(d, 150, 405, "You'll budget for an overhaul soon", BS(42))
    if t > trig(bid, "not", 1):
        panel(d, [980, 190, 1810, 560], a=215); d.text((1020, 245), "NOT RIGHT IF", font=MB(28), fill=RED, anchor="lm")
        bullet(d, 1020, 325, "You want low hours", BS(42), mark="no")
    tp = trig(bid, "paying")
    if t > tp: big_line(d, 650, "YOU ARE PAYING FOR THE YEAR, NOT THE HOURS", BB(60), OFF, (t - tp) / 0.4)
    tq = trig(bid, "Check")
    if t > tq: big_line(d, 745, "HOW IT WAS FLOWN  ·  THE LOAN PAYOFF  ·  THE ENGINE LOGBOOKS", BB(46), CYAN, (t - tq) / 0.4)

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
