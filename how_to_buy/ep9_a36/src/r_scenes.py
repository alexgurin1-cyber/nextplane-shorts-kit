# ---------- card text boxes (CSS px, from capture.py) ----------
SEC = json.load(open(f"{CAP}/sections.json"))
def BX(key, txt, n=1, pad=0, x1=None, exact=False):
    k = 0
    for b in SEC[key]["boxes"]:
        if (b["t"] == txt) if exact else b["t"].startswith(txt):
            k += 1
            if k == n:
                return (b["x"] - pad, b["y"] - pad, (x1 if x1 is not None else b["x"] + b["w"]) + pad, b["y"] + b["h"] + pad)
    raise KeyError((key, txt))
def UNION(*bs): return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))
HC = "_headercomb"
OWN = "CARHONIK"
# Alex 2026-10-19: never reveal where NextPlane's data comes from (ADS-B, FAA document index/registry, NTSB, SDR, source marketplace).
RELABEL = {HC: [(BX(HC, "NTSB DAMAGE"), "ACCIDENT RECORD"), (BX(HC, "USE TYPE"), "FLIGHT USE"),
                (BX(HC, "FINANCING ·"), "FINANCING"), (BX(HC, "SDR ·"), "SERVICE PROBLEMS")],
           "sdr": [(BX("sdr", "SERVICE DIFFICULTY REPORTS"), "SERVICE PROBLEMS"), (BX("sdr", "No Service Difficulty"), "No service problem reports on this aircraft.")]}
EXTRA_BLUR = {HC: [BX(HC, OWN, pad=2), BX(HC, "FAA document index +", pad=2), BX(HC, "Records searched", pad=2), (90, 576, 545, 602)],
              "listhist": [BX("listhist", "Listed on", 1, pad=3), BX("listhist", "Listed on", 2, pad=3), BX("listhist", "Ad removed", pad=3),
                           BX("listhist", "An ad that disappears", pad=2), (25, 200, 640, 222)],
              "reg": [BX("reg", OWN, 1, pad=2), BX("reg", OWN, 2, pad=2)] + [BX("reg", t, pad=2) for t in ("The FAA registry", "No security conveyance indexed in", "Repossession (REP)", "A dereg_removed", "Derived from the FAA Aircraft Document Index. This", "Engine and propeller securit", "Enter the engine and/or", "Derived from the FAA Aircraft Document Index. Lien")],
              "ads": [BX("ads", OWN, pad=2), BX("ads", "model_specs", pad=2), BX("ads", "Default 50", pad=2), BX("ads", "not in registry", pad=2)],
              "sdr": [BX("sdr", "FAA Service Difficulty", pad=2)],
              "valuation": [BX("valuation", "72 active", pad=2), BX("valuation", "Based on 72", pad=2)],
              "mktcomp": [BX("mktcomp", "How this aircraft's", pad=2), BX("mktcomp", "across 95", pad=2), BX("mktcomp", "across 94", pad=2)]}

def rep_label(im, txt):
    d = ImageDraw.Draw(im, "RGBA"); d.text((70, 925), txt, font=MR(18), fill=(200, 210, 218, 190), anchor="lm")
def big_line(d, y, txt, f=None, fill=OFF, p=1.0):
    f = f or BB(62); d.text((W / 2, y), txt, font=f, fill=(*fill, int(255 * min(max(p, 0), 1))), anchor="mm")
def chip_c(d, y, txt, f=None, fill=CYAN, fg=NAVY):
    f = f or MB(26); tw = d.textlength(txt, font=f); chip(d, W / 2 - tw / 2 - 18, y, txt, fill=fill, fg=fg, f=f)
def tiles(im, t, items, y=560, bw=520, h=300):
    d = ImageDraw.Draw(im, "RGBA"); n = len(items); gap = 34; x = (W - (n * bw + (n - 1) * gap)) / 2
    for lab, vtxt, sub, ts, hi in items:
        p = ease((t - ts) / 0.6)
        if p > 0:
            panel(d, [x, y, x + bw, y + h])
            d.text((x + bw / 2, y + 55), lab, font=MB(22), fill=CYAN if hi else GREY, anchor="mm")
            d.text((x + bw / 2, y + 140), vtxt, font=MB(56), fill=(*(CYAN if hi else WHITE), int(255 * p)), anchor="mm")
            d.text((x + bw / 2, y + 220), sub, font=MR(19), fill=GREY, anchor="mm")
        x += bw + gap
RED = (230, 120, 110)

# ---------- data (from DATA_PACK) ----------
LADDER = [("V35B · V-tail", "1972–1982", 232325, 30, "V35B,"), ("F33A · shorter", "1970–1994", 265000, 41, "F33A,"),
          ("A36 · to 1983", "1968–1983", 299000, 29, "through"), ("A36 · mid-80s–early 90s", "1984–1993", 369000, 9, "eighties"),
          ("B36TC · turbocharged", "1979–2002", 425000, 19, "turbocharged"), ("A36 · newer", "1994–2005", 466950, 18, "Newer"),
          ("G36 · current", "2006–", 680000, 35, "G36,")]
HERO_I = 2
ASKS = [169000, 194500, 195000, 209900, 229000, 244900, 259900, 269000, 275000, 284450, 295000, 298000, 298500, 299000, 299000, 299950,
        303000, 304500, 314900, 319000, 320000, 326000, 339900, 349000, 349000, 360000, 365000, 375000, 378000]
REP = "REPRESENTATIVE PHOTO · BEECHCRAFT A36 BONANZA · NOT THE AIRCRAFT FOR SALE"
REPV = "REPRESENTATIVE PHOTO · BEECHCRAFT BONANZA FAMILY · NOT THE AIRCRAFT FOR SALE"
P1, P2, P3, PV = "a36-0.jpg", "a36x-0.jpg", "m36-0.jpg", "bb-0.jpg"
STAMP = "NEXTPLANE LISTING PANEL · NOV 9, 2026 · US-REGISTERED · ONE PER TAIL · BONANZAS ONLY"

def sc_title(im, t, s0, s1):
    bid = BID["title"]
    im.paste(kb(photo_bg(P1, dark=0.35, focus=(0.6, 0.5)), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); d.rectangle([0, 0, W, H], fill=(8, 16, 26, 120))
    tt = trig(bid, "This", 2)
    if t < tt - 0.2:
        p = ease((t - s0 - 0.3) / 0.6)
        panel(d, [380, 230, 1540, 740], a=220)
        d.text((W / 2, 300), "ASKING PRICE · 175 DAYS ON THE MARKET", font=MB(26), fill=GREY, anchor="mm")
        d.text((700, 420), "$425,000", font=MB(90), fill=(*GREY, int(255 * p)), anchor="mm"); d.text((700, 510), "MAY 2026", font=MB(26), fill=OFF, anchor="mm")
        tc = trig(bid, "cut", 1)
        if t > tc:
            p2 = ease((t - tc) / 0.6)
            d.line([560, 425, 840, 415], fill=(*RED, int(255 * p2)), width=6)
            d.text((1220, 420), "$360,000", font=MB(90), fill=(*CYAN, int(255 * p2)), anchor="mm"); d.text((1220, 510), "TODAY · 3 CUTS · −$65,000", font=MB(26), fill=CYAN, anchor="mm")
        ta = trig(bid, "still")
        if t > ta: d.text((W / 2, 640), "STILL ≈ $60,000 ABOVE NEXTPLANE'S ESTIMATE", font=MB(32), fill=(*WHITE, int(255 * ease((t - ta) / 0.5))), anchor="mm")
    else:
        p = ease((t - tt) / 0.8)
        d.text((W / 2, 380), "HOW TO BUY A", font=BB(90), fill=(*OFF, int(255 * p)), anchor="mm")
        d.text((W / 2, 505), "BEECHCRAFT BONANZA A36", font=BB(150), fill=(*CYAN, int(255 * p)), anchor="mm")
        d.text((W / 2, 640), "ONE REAL AIRCRAFT · ONE REAL REPORT", font=MB(30), fill=(*OFF, int(220 * p)), anchor="mm")
    rep_label(im, REP)

def sc_problem(im, t, s0, s1):
    bid = BID["problem"]
    im.paste(kb(photo_bg(P2, dark=0.5), (t - s0) / (s1 - s0), 1.02, 1.1, dx=-1))
    header_bar(im, "STEP 1", "CHOOSE WHICH ONE"); rep_label(im, REP)
    d = ImageDraw.Draw(im, "RGBA")
    tb = trig(bid, "tracking")
    if t < tb - 0.2:
        tf = trig(bid, "six-seat")
        if t > trig(bid, "single-engine") - 0.2:
            panel(d, [330, 330, 1590, 640], a=200)
            big_line(d, 410, "BEECHCRAFT BONANZA FAMILY", BB(96), OFF, (t - trig(bid, "single-engine")) / 0.4)
            big_line(d, 505, "SINGLE ENGINE · BUILT SINCE THE LATE 1940s", MB(34), CYAN, (t - trig(bid, "single-engine") - 0.6) / 0.4)
        if t > tf: big_line(d, 580, "A36: 6 SEATS · STRAIGHT TAIL · DOUBLE REAR DOORS", MB(30), OFF, (t - tf) / 0.4)
    else:
        p = (t - tb) / 1.0
        panel(d, [300, 300, 920, 700]); d.text((610, 450), "~" + str(int(60 * ease(p))), font=MB(160), fill=WHITE, anchor="mm")
        d.text((610, 590), "A36s FOR SALE · US-REGISTERED", font=MB(26), fill=CYAN, anchor="mm")
        t2 = trig(bid, "fifty-five")
        if t > t2:
            p2 = (t - t2) / 0.8
            panel(d, [1000, 300, 1620, 700]); d.text((1310, 450), "~" + str(int(55 * ease(p2))), font=MB(160), fill=CYAN, anchor="mm")
            d.text((1310, 590), "SHOW A PUBLISHED PRICE", font=MB(26), fill=OFF, anchor="mm")
        chip_c(d, 760, "NEXTPLANE LISTING PANEL · NOV 9, 2026 · A36 BONANZA · ONE PER TAIL", fill=(15, 42, 63), fg=OFF, f=MB(22))

def sc_ladder(im, t, s0, s1):
    bid = BID["ladder"]
    im.paste(kb(photo_bg(PV, blur=10, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "THE PRICE LADDER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [90, 130, 1830, 950])
    d.text((140, 172), "TYPICAL (MEDIAN) ASKING PRICE · BONANZAS ONLY · ACTIVE LISTINGS WITH A PRICE · NOV 9, 2026", font=MB(22), fill=GREY, anchor="lm")
    x0, xmax = 760, 1480; vmax = 780000
    for i, (lab, yrs, v, n, key) in enumerate(LADDER):
        ts = trig(bid, key, default=s0 + 8 + i * 5); p = ease((t - ts) / 0.8)
        y = 215 + i * 102; hero = i == HERO_I
        d.text((140, y + 22), lab, font=BB(44), fill=CYAN if hero else OFF, anchor="lm")
        d.text((560, y + 24), yrs, font=MR(22), fill=CYAN if hero else GREY, anchor="lm")
        if p > 0:
            bw = (xmax - x0) * v / vmax * p
            d.rounded_rectangle([x0, y, x0 + max(bw, 8), y + 44], radius=8, fill=(*(CYAN if hero else (120, 150, 170)), 255))
            d.text((x0 + bw + 18, y + 22), money(v) + "  (n={})".format(n), font=MB(24), fill=WHITE, anchor="lm")
    if t > trig(bid, "1983", default=s0 + 20): d.text((140, 925), "OUR AIRPLANE: A 1981 A36 (HIGHLIGHTED)", font=MB(22), fill=CYAN, anchor="lm")

def sc_shortlist(im, t, s0, s1):
    bid = BID["shortlist"]
    im.paste(kb(photo_bg(P3, blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "YOUR SHORTLIST")
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "older") - 0.3: chip_c(d, 150, "A36 BONANZA · BUILT 1968–1983 · IN TODAY'S LISTINGS", f=MB(26))
    tr = trig(bid, "Twenty-nine")
    if t > tr - 0.2:
        panel(d, [110, 240, 1810, 880])
        d.text((150, 285), "THE 29 ASKING PRICES · A36, 1968–1983 · ACTIVE LISTINGS · NOV 9, 2026", font=MB(22), fill=GREY, anchor="lm")
        X = lambda v: 200 + (v - 150000) / 250000 * 1520
        d.line([200, 560, 1720, 560], fill=(90, 110, 128), width=3)
        for v in range(150000, 400001, 50000):
            d.line([X(v), 545, X(v), 575], fill=(90, 110, 128), width=3); d.text((X(v), 610), "${}K".format(v // 1000), font=MR(22), fill=GREY, anchor="mm")
        th = trig(bid, "Half")
        if t > th:
            p = ease((t - th) / 0.6)
            d.rounded_rectangle([X(269000), 520, X(269000) + (X(326000) - X(269000)) * p, 600], radius=10, fill=(37, 197, 203, 50), outline=(37, 197, 203, 160), width=2)
            if p >= 1: d.text(((X(269000) + X(326000)) / 2, 680), "HALF ASK BETWEEN $269,000 AND $326,000", font=MB(26), fill=CYAN, anchor="mm")
        hi = t > trig(bid, "fourth")
        stack = {}
        for i, v in enumerate(ASKS):
            p = ease((t - tr - i * 0.08) / 0.4)
            if p <= 0: continue
            k = round(v / 7000); stack[k] = stack.get(k, 0) + 1; yy = 560 - (stack[k] - 1) * 30
            hero = v == 360000 and hi; r = 17 if hero else 11
            d.ellipse([X(v) - r, yy - r - (1 - p) * 40, X(v) + r, yy + r - (1 - p) * 40], fill=(*(CYAN if hero else OFF), int(255 * p)))
            if hero:
                d.text((X(v), 430), "$360,000", font=MB(30), fill=CYAN, anchor="mm"); d.text((X(v), 470), "4th HIGHEST OF 29", font=MR(22), fill=CYAN, anchor="mm")
        if t > trig(bid, "ran"): chip_c(d, 780, "ONE OF THE HIGHEST ASKS · WE RAN THE REPORT", f=MB(26))

def sc_pick(im, t, s0, s1):
    bid = BID["pick"]
    im.paste(kb(photo_bg(P2, dark=0.4), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); rep_label(im, REP)
    ta = trig(bid, "airframe")
    if t < ta - 0.3:
        p = (t - s0 - 0.3) / 1.2
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 90))
        d.text((W / 2, 420), count(360000, p), font=MB(150), fill=WHITE, anchor="mm")
        d.text((W / 2, 545), "N1811Y · 1981 BEECHCRAFT A36 BONANZA · DEALER, TENNESSEE", font=MB(30), fill=CYAN, anchor="mm")
    else:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 150))
        p = ease((t - ta + 0.3) / 0.6)
        panel(d, [260, 200, 900, 600]); d.text((580, 280), "AIRFRAME", font=MB(26), fill=GREY, anchor="mm")
        d.text((580, 400), "5,100", font=MB(130), fill=(*WHITE, int(255 * p)), anchor="mm"); d.text((580, 520), "HOURS", font=MB(24), fill=GREY, anchor="mm")
        if t > trig(bid, "average."): chip(d, 270, 625, "MARKET AVERAGE: 5,237", f=MB(24))
        te = trig(bid, "engine", 1)
        if t > te:
            p = ease((t - te) / 0.6)
            panel(d, [1020, 200, 1660, 600]); d.text((1340, 280), "ENGINE · FACTORY REMANUFACTURED", font=MB(24), fill=CYAN, anchor="mm")
            d.text((1340, 400), "19", font=MB(130), fill=(*CYAN, int(255 * p)), anchor="mm"); d.text((1340, 520), "HOURS", font=MB(24), fill=GREY, anchor="mm")
        if t > trig(bid, "seventeen"): chip(d, 1030, 625, "≈ 1,700 HRS UNTIL OVERHAUL IS DUE", f=MB(24))
        if t > trig(bid, "panel"): chip_c(d, 800, "GARMIN G3X TOUCH · GTN 750Xi · GNS 650 · GFC 500 AUTOPILOT", f=MB(30))

def sc_header(im, t, s0, s1):
    bid = BID["header"]
    im.paste(kb(photo_bg(P3, blur=14, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT DOES THE REPORT SAY FIRST?")
    cos = [(UNION(BX(HC, "NTSB DAMAGE"), BX(HC, "None", 1)), trig(bid, "accident")),
           (UNION(BX(HC, "CURRENT OWNERSHIP"), BX(HC, "Certificate issued")), trig(bid, "company")),
           (UNION(BX(HC, "FINANCING"), BX(HC, "Window 2025")), trig(bid, "loan")),
           (UNION(BX(HC, "MAJOR AD"), BX(HC, "16 applicable")), trig(bid, "critical:"))]
    report_slide(im, t, HC, (0, 0, 1152, 615), cos, t0=s0, cy=530, maxh=800)

def sc_value(im, t, s0, s1):
    bid = BID["value"]
    im.paste(kb(photo_bg(P1, blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "IS THE PRICE FAIR?")
    tc = trig(bid, "A36s", 1)
    if t < tc - 0.2:
        cos = [(UNION(BX("valuation", "ESTIMATED VALUE"), BX("valuation", "$299,925", 1)), trig(bid, "three", 1)),
               (UNION(BX("valuation", "ESTIMATED RANGE"), BX("valuation", "$260,000")), trig(bid, "three", 1) + 1.4),
               (UNION(BX("valuation", "NET ADJUSTMENT"), BX("valuation", "+$0")), trig(bid, "adjustment"))]
        report_slide(im, t, "valuation", (25, 95, 1127, 385), cos, t0=s0, cy=430, maxh=560)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "sixty"): chip_c(d, 760, "THIS ONE ASKS $360,000 · +$60,075 OVER THE ESTIMATE", f=MB(28))
        if t > trig(bid, "adjustment"): chip_c(d, 840, "ENGINE HOURS ENTERED, BUT NO ADJUSTMENT FOR THE NEW ENGINE", f=MB(24), fill=(15, 42, 63), fg=OFF)
    else:
        tiles(im, t, [("REPORT ESTIMATE", "$299,925", "no adjustment for engine hours", tc - 0.2, False),
                      ("16 OLDER-ENGINE A36s", "$272,000", "engine 600+ hrs · typical ask", tc, False),
                      ("12 FRESH-ENGINE A36s", "$303,750", "engine < 600 hrs · typical ask", trig(bid, "A36s", 2), False),
                      ("THIS ONE", "$360,000", "5,100 airframe · 19 engine", trig(bid, "both"), True)], y=330, bw=410, h=300)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "both"): chip_c(d, 720, "IT ASKS MORE THAN BOTH GROUPS", f=MB(32))
        d.text((W / 2, 820), "A36 BONANZA, 1968–1983 · ACTIVE LISTINGS WITH A PRICE · NOV 9, 2026 · NEXTPLANE PANEL", font=MR(19), fill=GREY, anchor="mm")

def sc_engine(im, t, s0, s1):
    bid = BID["engine"]
    im.paste(kb(photo_bg(P2, blur=12, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT IS THE EXTRA MONEY BUYING?")
    tc = trig(bid, "sets")
    if t < tc - 0.2:
        cos = [(BX("mktcomp", "This aircraft: 5,100"), trig(bid, "airframe")), (BX("mktcomp", "This aircraft: 19"), trig(bid, "eighty", 1))]
        report_slide(im, t, "mktcomp", (25, 105, 760, 290), cos, t0=s0, cy=430, maxh=420, maxw=1600)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "matters,"): chip_c(d, 800, "AN ENGINE OVERHAUL IS A BIG BILL · FEWER ENGINE HOURS = MORE TIME BEFORE IT", f=MB(24))
    else:
        d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 930])
        rows = [("REPORT'S ENGINE OVERHAUL SET-ASIDE", "$4,225 / 120 HRS ≈ $35 / HR", tc),
                ("FEWER ENGINE HOURS THAN THE TYPICAL A36 FOR SALE", "901 − 19 = 882 HRS", tc + 1.5),
                ("WORTH, AT THAT RATE", "≈ $31,000", trig(bid, "thirty-one"))]
        for i, (lab, v, ts) in enumerate(rows):
            p = ease((t - ts) / 0.5)
            if p <= 0: continue
            y = 220 + i * 80
            d.text((160, y), lab, font=MB(26), fill=(*GREY, int(255 * p)), anchor="lm"); d.text((1760, y), v, font=MB(36), fill=(*(CYAN if i == 2 else OFF), int(255 * p)), anchor="rm")
        th = trig(bid, "half")
        if t > th - 0.4:
            d.text((160, 510), "THE GAP: $360,000 ASK − $299,925 REPORT ESTIMATE = $60,075", font=MB(26), fill=WHITE, anchor="lm")
            p = ease((t - th + 0.4) / 0.8); x0, x1 = 160, 1760; xe = x0 + (x1 - x0) * 31000 / 60075
            d.rounded_rectangle([x0, 560, x0 + (xe - x0) * p, 650], radius=10, fill=CYAN)
            if p >= 1: d.text(((x0 + xe) / 2, 605), "NEWER ENGINE ≈ $31K", font=MB(30), fill=NAVY, anchor="mm")
            tr = trig(bid, "rest")
            if t > tr:
                p2 = ease((t - tr) / 0.8)
                d.rounded_rectangle([xe + 8, 560, xe + 8 + (x1 - xe - 8) * p2, 650], radius=10, fill=(120, 150, 170))
                if p2 >= 1: d.text(((xe + x1) / 2, 605), "PANEL · AUTOPILOT ≈ $29K", font=MB(30), fill=NAVY, anchor="mm")
        if t > trig(bid, "Decide"): chip_c(d, 740, "DECIDE WHAT THE PANEL IS WORTH TO YOU, BEFORE YOU CALL", f=MB(30))
        d.text((W / 2, 880), "SET-ASIDE FROM THE REPORT'S COST OF OWNERSHIP · HOURS FROM THE REPORT'S MARKET COMPARISON · AN ESTIMATE, NOT A QUOTE", font=MR(18), fill=GREY, anchor="mm")

def sc_sister(im, t, s0, s1):
    bid = BID["sister"]
    im.paste(kb(photo_bg(P3, blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT ELSE IS THE BUYER SEEING?")
    cos = [((46, 380, 590, 500), trig(bid, "listed"))]
    report_slide(im, t, "signals", (36, 370, 600, 510), cos, t0=s0, cy=300, maxh=300, maxw=1100)
    d = ImageDraw.Draw(im, "RGBA")
    tw = trig(bid, "twenty-one")
    if t > tw - 0.3:
        panel(d, [160, 480, 1760, 900], a=225)
        d.text((260, 530), "", font=MB(24), fill=GREY, anchor="lm")
        hdr = [("", 200), ("THIS ONE · N1811Y", 830), ("SISTER SHIP · SAME DEALER", 1360)]
        for s, x in hdr[1:]: d.text((x, 535), s, font=MB(24), fill=CYAN, anchor="mm")
        rows = [("YEAR", "1981", "1981", tw - 0.3), ("AIRFRAME HOURS", "5,100", "2,960", tw), ("ENGINE HOURS", "19", "290", trig(bid, "ninety")),
                ("PANEL", "G3X · GTN 750Xi · GFC 500", "G3X · GTN 750Xi · GFC 500", trig(bid, "similar")), ("ASKING PRICE", "$360,000", "$375,000", trig(bid, "seventy-five"))]
        for i, (lab, a, b, ts) in enumerate(rows):
            if t < ts: continue
            y = 600 + i * 58
            d.text((200, y), lab, font=MB(24), fill=GREY, anchor="lm")
            d.text((830, y), a, font=MB(28), fill=WHITE, anchor="mm"); d.text((1360, y), b, font=MB(28), fill=OFF, anchor="mm")
        if t > trig(bid, "both."): chip_c(d, 940, "+$15,000 FOR ≈ 2,140 FEWER AIRFRAME HOURS · ASK ABOUT BOTH", f=MB(26))

def sc_flight(im, t, s0, s1):
    bid = BID["flight"]
    im.paste(kb(photo_bg(P2, blur=6, dark=0.78), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "STEP 2", "IS IT FLYING?")
    cos = [(UNION(BX("fl_period", "Last 24 months"), BX("fl_period", "~37.9")), trig(bid, "ninety-two")),
           (UNION(BX("fl_period", "Last 12 months"), BX("fl_period", "~30.9")), trig(bid, "twelve", 1))]
    report_slide(im, t, "fl_period", (0, 0, 1102, 238), cos, t0=s0, cy=340, maxw=1500, maxh=330)
    d = ImageDraw.Draw(im, "RGBA")
    tf = trig(bid, "before")
    if t > tf:
        panel(d, [210, 560, 1710, 900])
        d.text((W / 2, 610), "HOURS FLOWN · FROM THE REPORT'S FLIGHT HOURS BY PERIOD", font=MB(24), fill=GREY, anchor="mm")
        d.text((W / 2, 690), "PREVIOUS 12 MONTHS ≈ 7 HRS  →  LAST 12 MONTHS ≈ 31 HRS", font=MB(40), fill=WHITE, anchor="mm")
        if t > trig(bid, "spring"): d.text((W / 2, 770), "MOSTLY APRIL–SEPTEMBER 2026 · SHORT LOCAL HOPS (AVG 27 MIN)", font=MB(28), fill=CYAN, anchor="mm")
        if t > trig(bid, "guess."): d.text((W / 2, 840), "ASK WHEN THE ENGINE WENT IN · SEE IT IN THE LOGBOOK", font=MB(28), fill=OFF, anchor="mm")

def sc_pricehist(im, t, s0, s1):
    bid = BID["pricehist"]
    im.paste(kb(photo_bg(P1, blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS THE SELLER MOVED?")
    tc = trig(bid, "followed")
    if t < tc - 0.2:
        cos = [(UNION(BX("listhist", "PRICE SINCE"), BX("listhist", "First seen")), trig(bid, "May")),
               (UNION(BX("listhist", "PRICE CUTS"), BX("listhist", "Largest")), trig(bid, "Cut", 1))]
        report_slide(im, t, "listhist", (25, 95, 1127, 400), cos, t0=s0, cy=470, maxh=640)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "total."): chip(d, 1100, 860, "3 CUTS · −$65,000 · −15.3%", f=MB(28))
    else:
        d = ImageDraw.Draw(im, "RGBA"); panel(d, [140, 160, 1780, 900])
        d.text((W / 2, 215), "A36 BONANZAS FIRST LISTED APR 26 – AUG 10, 2026 · ONE PER TAIL · A36s ONLY", font=MB(24), fill=GREY, anchor="mm")
        items = [("42", "A36s LISTED", tc), ("24", "CUT THEIR PRICE (1%+)", trig(bid, "Twenty-four")), ("≈7%", "TYPICAL CUT", trig(bid, "seven")), ("23", "STILL LISTED AFTER 90 DAYS", trig(bid, "Twenty-three"))]
        for i, (v, lab, ts) in enumerate(items):
            p = ease((t - ts) / 0.6)
            if p <= 0: continue
            x = 345 + i * 410
            d.text((x, 410), v, font=MB(120), fill=(*(CYAN if i in (1, 2) else WHITE), int(255 * p)), anchor="mm")
            d.text((x, 510), lab, font=MB(20), fill=OFF, anchor="mm")
        if t > trig(bid, "fifteen"): chip_c(d, 620, "THIS SELLER: −15.3% · ABOUT TWICE THE TYPICAL CUT", f=MB(28))
        if t > trig(bid, "often"): d.text((W / 2, 740), "A36 SELLERS OFTEN WAIT MONTHS · A PATIENT BUYER HAS LEVERAGE", font=MB(26), fill=OFF, anchor="mm")

def sc_owner(im, t, s0, s1):
    bid = BID["owner"]
    im.paste(kb(photo_bg(P3, blur=14, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO OWNS IT?")
    cos = [(UNION(BX("reg", "CERTIFICATE DATE"), BX("reg", "Oct 12, 2004", pad=2)), trig(bid, "October")),
           (UNION(BX("reg", "Sep 2, 2026"), BX("reg", "Release indexed")), trig(bid, "release", 1)),
           (UNION(BX("reg", "Latest release"), BX("reg", "0 agreements")), trig(bid, "paid"))]
    report_slide(im, t, "reg", (0, 80, 1152, 520), cos, t0=s0, cy=430, maxh=600)
    d = ImageDraw.Draw(im, "RGBA")
    if trig(bid, "Long") < t < trig(bid, "release", 1): chip_c(d, 790, "SAME OWNER FOR 22 YEARS · ONE MAINTENANCE STORY TO FOLLOW", f=MB(26))
    if trig(bid, "release", 1) < t < trig(bid, "dealer,"): chip_c(d, 790, "LOAN RELEASE FILED SEP 2, 2026 · USUALLY AN OLD LOAN PAID OFF", f=MB(26))
    if t > trig(bid, "dealer,"): chip_c(d, 790, "THE SELLER IS A DEALER, NOT THE OWNER", f=MB(30))
    items = [("Owner has agreed to the sale", trig(bid, "dealer,")), ("Release paperwork", trig(bid, "paperwork,")), ("Title search", trig(bid, "title"))]
    x = 60
    for s, tt in items:
        if t > tt:
            f = BS(32); tw = d.textlength(s, font=f)
            d.rounded_rectangle([x, 880, x + tw + 80, 950], radius=12, fill=(10, 22, 34, 230), outline=(37, 197, 203, 120), width=2)
            bullet(d, x + 20, 915, s, f); x += tw + 100

def sc_ads(im, t, s0, s1):
    bid = BID["ads"]
    im.paste(kb(photo_bg(P2, blur=14, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT SHOULD THE LOGBOOKS SHOW?")
    tb = trig(bid, "flags")
    if t < tb - 0.3:
        cos = [(UNION(BX("ads", "ITEMS"), BX("ads", "16 ADs")), trig(bid, "sixteen")), (UNION(BX("ads", "AIRCRAFT"), BX("ads", "s/n E-1877")), trig(bid, "serial"))]
        report_slide(im, t, "ads", (25, 115, 660, 345), cos, t0=s0, cy=430, maxh=520, maxw=1300)
    else:
        cos2 = [(UNION(BX("ads", "2024-14-03"), BX("ads", "Update Garmin GFC")), tb)]
        report_slide(im, t, "ads", (0, 1756, 380, 1818), cos2, t0=tb - 0.3, cy=330, maxh=300, maxw=1000, cx=640)
        d = ImageDraw.Draw(im, "RGBA")
        panel(d, [1200, 200, 1820, 560], a=220)
        d.text((1240, 250), "AIRWORTHINESS DIRECTIVE =", font=MB(24), fill=CYAN, anchor="lm")
        d.text((1240, 290), "A MANDATORY SAFETY FIX", font=MB(24), fill=CYAN, anchor="lm")
        if t > trig(bid, "autopilot,"): d.text((1240, 380), "THIS AIRPLANE HAS A GFC 500", font=MB(26), fill=OFF, anchor="lm")
        if t > trig(bid, "record."): d.text((1240, 450), "ASK FOR THE UPDATE RECORD", font=MB(30), fill=RED, anchor="lm")
        tr = trig(bid, "checklist")
        if t > tr:
            panel(d, [160, 640, 1760, 880], a=220)
            d.text((200, 700), "THE REPORT'S CHECKLIST: \"SHOULD BE DONE BY NOW\" + \"COMING UP\" (NEXT 5 YEARS)", font=MB(26), fill=OFF, anchor="lm")
            if t > trig(bid, "pre-buy"): d.text((200, 790), "BRING IT TO YOUR PRE-BUY INSPECTION", font=MB(36), fill=CYAN, anchor="lm")

def sc_sdr(im, t, s0, s1):
    bid = BID["sdr"]
    im.paste(kb(photo_bg(P1, blur=14, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS IT EVER BEEN HURT?")
    cos = [(UNION(BX("sdr", "LAST 5 YRS"), BX("sdr", "12")), trig(bid, "twelve")),
           (BX("sdr", "No Service", pad=4), trig(bid, "None"))]
    report_slide(im, t, "sdr", (0, 100, 1152, 590), cos, t0=s0, cy=450, maxh=640)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "accident"): chip(d, 70, 880, "ACCIDENT RECORDS FOR THIS AIRCRAFT: NONE", f=MB(26))
    if t > trig(bid, "None"): chip(d, 1180, 880, "THIS AIRCRAFT: 0 REPORTS", fill=CYAN, f=MB(26))

def sc_opcost(im, t, s0, s1):
    bid = BID["opcost"]
    im.paste(kb(photo_bg(P3, blur=12, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT WILL IT COST TO KEEP?")
    cos = [(UNION(BX("opcost", "Total Annual"), BX("opcost", "$31,911")), trig(bid, "thirty-two")),
           (UNION(BX("opcost", "Cost per Flight"), BX("opcost", "$266/hr")), trig(bid, "sixty-six")),
           (UNION(BX("opcost", "Fuel (120"), BX("opcost", "$11,160")), trig(bid, "Fuel")),
           (UNION(BX("opcost", "Insurance"), BX("opcost", "$5,880")), trig(bid, "Insurance"))]
    report_slide(im, t, "opcost", (0, 0, 1152, 590), cos, t0=s0, cy=480, maxh=720)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "quote."): chip(d, 70, 880, "INSURANCE FIGURED ON THE $360,000 ASK · GET A REAL QUOTE", f=MB(26))

def sc_seller(im, t, s0, s1):
    bid = BID["seller"]
    im.paste(kb(photo_bg(P1, blur=12, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO AM I DEALING WITH?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [330, 180, 1590, 860])
    d.text((W / 2, 270), "DEALER", font=BB(100), fill=CYAN, anchor="mm")
    d.text((W / 2, 350), "FROM THE REPORT'S SELLER SECTION · NEXTPLANE DEALER DATA", font=MB(24), fill=GREY, anchor="mm")
    items = [("PRICE VS MARKET", "+9.2%", "asking prices above market · 12 compared", trig(bid, "nine")),
             ("SALE SPEED", "42% SLOWER", "than the same models · 9 sales", trig(bid, "longer"))]
    for i, (lab, v, sub, ts) in enumerate(items):
        if t < ts: continue
        x = 640 + i * 640
        d.text((x, 450), lab, font=MB(24), fill=GREY, anchor="mm"); d.text((x, 540), v, font=MB(70), fill=WHITE, anchor="mm"); d.text((x, 615), sub, font=MR(20), fill=GREY, anchor="mm")
    if t > trig(bid, "waiting."): chip_c(d, 720, "A DEALER USED TO WAITING · USE THE TIME FOR YOUR HOMEWORK", f=MB(26))

def sc_offer(im, t, s0, s1):
    bid = BID["offer"]
    im.paste(kb(photo_bg(P2, blur=12, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 3", "THE OFFER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 140, 1810, 940])
    rows = [("NEXTPLANE ESTIMATE", "$299,925", trig(bid, "estimate")),
            ("+ NEWER ENGINE (REPORT'S OWN SET-ASIDE)", "≈ +$31,000", trig(bid, "Add")),
            ("SISTER SHIP · 2,960 AIRFRAME HRS · SAME DEALER", "$375,000", trig(bid, "sister")),
            ("THIS SELLER'S CUTS SO FAR", "3 · −$65,000", trig(bid, "already")),
            ("THIS ONE · ASKING", "$360,000", trig(bid, "already") + 0.8)]
    for i, (lab, v, ts) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 210 + i * 70
        d.text((170, y), lab, font=MB(26), fill=(*GREY, int(255 * p)), anchor="lm"); d.text((1740, y), v, font=MB(36), fill=(*OFF, int(255 * p)), anchor="rm")
    to = trig(bid, "reasonable")
    if t > to:
        p = ease((t - to) / 0.5)
        d.rounded_rectangle([180, 565, 1740, 665], radius=18, fill=(*CYAN, int(255 * p)))
        d.text((W / 2, 615), "OPEN AROUND $330,000 · ABOUT 8% UNDER THE ASK", font=BB(58), fill=NAVY, anchor="mm")
    ts = trig(bid, "subject")
    for i, s in enumerate(["Subject to a pre-buy inspection", "The engine paperwork", "The autopilot directive record", "A clean title"]):
        if t > ts + i * 0.9: bullet(d, 200 + (i % 2) * 800, 740 + (i // 2) * 70, s, BS(40))

def sc_watch(im, t, s0, s1):
    bid = BID["watch"]
    im.paste(kb(photo_bg(PV, blur=8, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 4", "KEEP WATCHING")
    d = ImageDraw.Draw(im, "RGBA")
    items = [(4, "NEW A36 LISTINGS", "Oct 27 – Nov 10", trig(bid, "four")), (9, "PRICE CUTS", "Oct 27 – Nov 10", trig(bid, "nine")),
             (0, "PRICE INCREASES", "Oct 27 – Nov 10", trig(bid, "increases."))]
    bw, gap = 520, 40; x = (W - (3 * bw + 2 * gap)) / 2; y = 280
    for v, lab, sub, ts in items:
        p = (t - ts) / 0.8
        if p > 0:
            panel(d, [x, y, x + bw, y + 330])
            d.text((x + bw / 2, y + 130), str(int(round(v * ease(p)))), font=MB(120), fill=WHITE, anchor="mm")
            d.text((x + bw / 2, y + 235), lab, font=MB(26), fill=CYAN, anchor="mm"); d.text((x + bw / 2, y + 280), sub, font=MR(22), fill=GREY, anchor="mm")
        x += bw + gap
    if t > trig(bid, "Right"): chip_c(d, 700, "RIGHT NOW, A36 PRICES ARE MOVING DOWN", f=MB(30))
    rep_label(im, REPV)

def sc_verdict(im, t, s0, s1):
    bid = BID["verdict"]
    im.paste(kb(photo_bg(P1, dark=0.55, focus=(0.6, 0.5)), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "VERDICT", "WHO IS THIS AIRPLANE RIGHT FOR?"); rep_label(im, REP)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "buyer"):
        panel(d, [110, 190, 940, 680], a=215); d.text((150, 245), "RIGHT FOR", font=MB(28), fill=CYAN, anchor="lm")
        for i, (s, k) in enumerate([("A six-seat Bonanza", "six-seat"), ("No engine bill for years", "engine"), ("A modern Garmin panel", "modern")]):
            if t > trig(bid, k): bullet(d, 150, 325 + i * 80, s, BS(42))
    if t > trig(bid, "not"):
        panel(d, [980, 190, 1810, 680], a=215); d.text((1020, 245), "NOT RIGHT IF", font=MB(28), fill=RED, anchor="lm")
        bullet(d, 1020, 325, "You want the lowest price", BS(42), mark="no")
        if t > trig(bid, "install"): bullet(d, 1020, 405, "You'll install your own panel", BS(42), mark="no")
    if t > trig(bid, "Priced"): big_line(d, 750, "PRICED ABOVE SIMILAR AIRPLANES · CLEAN HISTORY", BB(54), OFF, (t - trig(bid, "Priced")) / 0.4)
    tq = trig(bid, "Check")
    if t > tq: big_line(d, 835, "THE ENGINE PAPERWORK  ·  THE LOAN RELEASE  ·  WHAT THE PANEL IS WORTH TO YOU", BB(44), CYAN, (t - tq) / 0.4)

def sc_end(im, t, s0, s1):
    p = Image.new("RGB", (1080, 1920), NAVY)
    EC.draw_endcard(p, t - s0, FD, f"{ROOT}/assets/logo.png")
    p = p.crop((0, 380, 1080, 1480)).resize((1060, 1080), Image.LANCZOS)
    im.paste(NAVY, (0, 0, W, H)); im.paste(p, ((W - 1060) // 2, 0))

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
