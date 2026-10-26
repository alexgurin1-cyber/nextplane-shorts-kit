
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
# Alex 2026-10-19: never reveal where NextPlane's data comes from (ADS-B, FAA document index/registry, NTSB, SDR, source marketplace).
RELABEL = {HC: [(BX(HC, "NTSB DAMAGE"), "ACCIDENT RECORD"), (BX(HC, "USE TYPE"), "FLIGHT USE"),
                (BX(HC, "FINANCING ·"), "FINANCING"), (BX(HC, "SDR ·"), "SERVICE PROBLEMS")],
           "sdr": [(BX("sdr", "SERVICE DIFFICULTY REPORTS"), "SERVICE PROBLEMS"), (BX("sdr", "No Service Difficulty"), "No service problem reports on this aircraft.")]}
EXTRA_BLUR = {HC: [BX(HC, "APPLE X05 LLC", pad=2), BX(HC, "FAA document index +", pad=2), BX(HC, "1295 total", pad=2), (90, 632, 760, 660), BX(HC, "Records searched", pad=2)],
              "listhist": [BX("listhist", "Listed on", pad=3), BX("listhist", "An ad that disappears", pad=2)],
              "reg": [BX("reg", "APPLE X05 LLC", 1, pad=2), BX("reg", "APPLE X05 LLC (FL)", pad=2)] + [BX("reg", t, pad=2) for t in ("The FAA registry", "No security conveyance indexed in", "Repossession (REP)", "A dereg_removed", "Derived from the FAA Aircraft Document Index. This", "Engine and propeller security", "Enter the engine and/or", "Derived from the FAA Aircraft Document Index. Lien")],
              "ads": [BX("ads", "APPLE X05", pad=2), BX("ads", "FAA registry family", pad=2), BX("ads", "Default 260", pad=2), BX("ads", "not in registry", pad=2)],
              "sdr": [(23, 46, 345, 70), BX("sdr", "FAA Service Difficulty", pad=2)],
              "valuation": [BX("valuation", "37 active", pad=2), BX("valuation", "Based on 37", pad=2)],
              "mktcomp": [BX("mktcomp", "How this aircraft's", pad=2)]}

def rep_label(im, txt="REPRESENTATIVE PHOTO · PIPER ARCHER · NOT THE AIRCRAFT FOR SALE"):
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
LADDER = [("Cherokee 140 / 160", "1960s–70s", 75000, 70, "forty"), ("Cherokee 180", "1963–1975", 99000, 45, "eighty,"),
          ("Warrior · 160 hp", "1974–2001", 109900, 27, "Warrior,"), ("Arrow · retractable", "1967–2014", 128000, 69, "Arrow,"),
          ("Archer · 180 hp", "1974–1985", 138950, 21, "Archer,"), ("Dakota · 235 hp", "1979–1986", 210000, 11, "Dakota,"),
          ("Late-model Archer", "2011–2024", 435000, 4, "late-model")]
ASKS = [80000, 99000, 99900, 99900, 104900, 105000, 126000, 128500, 129495, 129950, 138950, 150000, 155000, 155000, 164900, 165000, 169500, 169900, 179000, 180000, 199900]
REP = "REPRESENTATIVE PHOTO · PIPER ARCHER II · NOT THE AIRCRAFT FOR SALE"

def sc_title(im, t, s0, s1):
    bid = BID["title"]
    im.paste(kb(photo_bg("archer-1.jpg", dark=0.35, focus=(0.5, 0.5)), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); d.rectangle([0, 0, W, H], fill=(8, 16, 26, 120))
    tt = trig(bid, "This", 2)
    if t < tt - 0.2:
        p = ease((t - s0 - 0.3) / 0.6)
        panel(d, [380, 230, 1540, 740], a=220)
        d.text((W / 2, 300), "AIRFRAME HOURS vs ENGINE HOURS", font=MB(26), fill=GREY, anchor="mm")
        d.text((700, 420), "12,364", font=MB(104), fill=(*WHITE, int(255 * p)), anchor="mm"); d.text((700, 510), "AIRFRAME", font=MB(26), fill=OFF, anchor="mm")
        te = trig(bid, "engine"); p2 = ease((t - te) / 0.6)
        if t > te: d.text((1220, 420), "174", font=MB(104), fill=(*CYAN, int(255 * p2)), anchor="mm"); d.text((1220, 510), "ENGINE · SINCE REBUILT", font=MB(26), fill=CYAN, anchor="mm")
        ta = trig(bid, "asks")
        if t > ta: d.text((W / 2, 640), "ASKS ≈ $80,000 MORE THAN OTHER HIGH-HOUR ARCHERS", font=MB(30), fill=(*WHITE, int(255 * ease((t - ta) / 0.5))), anchor="mm")
    else:
        p = ease((t - tt) / 0.8)
        d.text((W / 2, 390), "HOW TO BUY A", font=BB(90), fill=(*OFF, int(255 * p)), anchor="mm")
        d.text((W / 2, 510), "PIPER PA-28", font=BB(170), fill=(*CYAN, int(255 * p)), anchor="mm")
        d.text((W / 2, 645), "ONE REAL AIRCRAFT · ONE REAL REPORT", font=MB(30), fill=(*OFF, int(220 * p)), anchor="mm")
    rep_label(im, REP)

def sc_problem(im, t, s0, s1):
    bid = BID["problem"]
    im.paste(kb(photo_bg("archer-6.jpg", dark=0.5), (t - s0) / (s1 - s0), 1.02, 1.1, dx=-1))
    header_bar(im, "STEP 1", "CHOOSE WHICH ONE"); rep_label(im, REP)
    d = ImageDraw.Draw(im, "RGBA")
    tb = trig(bid, "tracking")
    if t < tb - 0.2:
        tf = trig(bid, "four-seat,")
        if t > tf - 0.2:
            panel(d, [330, 330, 1590, 620], a=200)
            big_line(d, 410, "PIPER PA-28 FAMILY", BB(100), OFF, (t - tf) / 0.4)
            big_line(d, 510, "4 SEATS · LOW WING · BUILT SINCE THE EARLY 1960s", MB(34), CYAN, (t - tf - 0.6) / 0.4)
        if t > trig(bid, "learned"): big_line(d, 575, "A CLASSIC FIRST AIRPLANE FOR MANY PILOTS", MB(30), OFF, (t - trig(bid, "learned")) / 0.4)
    else:
        p = (t - tb) / 1.0
        panel(d, [300, 300, 920, 700]); d.text((610, 450), "~" + str(int(330 * ease(p))), font=MB(160), fill=WHITE, anchor="mm")
        d.text((610, 590), "PA-28s FOR SALE · US", font=MB(26), fill=CYAN, anchor="mm")
        t2 = trig(bid, "About", 2)
        if t > t2:
            p2 = (t - t2) / 0.8
            panel(d, [1000, 300, 1620, 700]); d.text((1310, 450), "~" + str(int(270 * ease(p2))), font=MB(160), fill=CYAN, anchor="mm")
            d.text((1310, 590), "SHOW A PUBLISHED PRICE", font=MB(26), fill=OFF, anchor="mm")
        chip_c(d, 760, "NEXTPLANE LISTING PANEL · OCT 26, 2026 · PA-28 FAMILY · US-REGISTERED · ONE PER TAIL", fill=(15, 42, 63), fg=OFF, f=MB(22))

def sc_ladder(im, t, s0, s1):
    bid = BID["ladder"]
    im.paste(kb(photo_bg("pa28-2.jpg", blur=10, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "THE PRICE LADDER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [90, 130, 1830, 950])
    d.text((140, 172), "TYPICAL (MEDIAN) ASKING PRICE · ACTIVE US LISTINGS WITH A PRICE · OCT 26, 2026", font=MB(22), fill=GREY, anchor="lm")
    x0, xmax = 700, 1480; vmax = 480000
    for i, (lab, yrs, v, n, key) in enumerate(LADDER):
        ts = trig(bid, key, default=s0 + 3 + i * 5); p = ease((t - ts) / 0.8)
        y = 215 + i * 102; hero = i == 4
        d.text((140, y + 22), lab, font=BB(46), fill=CYAN if hero else OFF, anchor="lm")
        d.text((480, y + 24), yrs, font=MR(22), fill=CYAN if hero else GREY, anchor="lm")
        if p > 0:
            bw = (xmax - x0) * v / vmax * p
            d.rounded_rectangle([x0, y, x0 + max(bw, 8), y + 44], radius=8, fill=(*(CYAN if hero else (120, 150, 170)), 255))
            txt = money(v) + "  (n={})".format(n) if i < 6 else "$362,900 – $435,000  (4 priced)"
            d.text((x0 + bw + 18, y + 22), txt, font=MB(24), fill=WHITE, anchor="lm")

def sc_shortlist(im, t, s0, s1):
    bid = BID["shortlist"]
    im.paste(kb(photo_bg("archer-4.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "YOUR SHORTLIST")
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "Archer:") - 0.3: chip_c(d, 150, "ARCHER · PA-28-181 · 180 HP · BUILT 1974–1985 IN TODAY'S LISTINGS", f=MB(26))
    tr = trig(bid, "Twenty-one")
    if t > tr - 0.2:
        panel(d, [110, 240, 1810, 880])
        d.text((150, 285), "THE 21 ASKING PRICES · ARCHER / ARCHER II · ACTIVE US LISTINGS · OCT 26, 2026", font=MB(22), fill=GREY, anchor="lm")
        X = lambda v: 200 + (v - 70000) / 140000 * 1520
        d.line([200, 560, 1720, 560], fill=(90, 110, 128), width=3)
        for v in range(80000, 210001, 20000):
            d.line([X(v), 545, X(v), 575], fill=(90, 110, 128), width=3); d.text((X(v), 610), "${}K".format(v // 1000), font=MR(22), fill=GREY, anchor="mm")
        th = trig(bid, "Half")
        if t > th:
            p = ease((t - th) / 0.6)
            d.rounded_rectangle([X(104975), 520, X(104975) + (X(164925) - X(104975)) * p, 600], radius=10, fill=(37, 197, 203, 50), outline=(37, 197, 203, 160), width=2)
            if p >= 1: d.text(((X(104975) + X(164925)) / 2, 680), "HALF ASK BETWEEN $105,000 AND $165,000", font=MB(26), fill=CYAN, anchor="mm")
        hi = t > trig(bid, "highest", 1)
        stack = {}
        for i, v in enumerate(ASKS):
            p = ease((t - tr - i * 0.08) / 0.4)
            if p <= 0: continue
            k = round(v / 4000); stack[k] = stack.get(k, 0) + 1; yy = 560 - (stack[k] - 1) * 30
            hero = v == 180000 and hi; r = 17 if hero else 11
            d.ellipse([X(v) - r, yy - r - (1 - p) * 40, X(v) + r, yy + r - (1 - p) * 40], fill=(*(CYAN if hero else OFF), int(255 * p)))
            if hero:
                d.text((X(v), 440), "$180,000", font=MB(30), fill=CYAN, anchor="mm"); d.text((X(v), 480), "12,364 HRS", font=MR(22), fill=CYAN, anchor="mm")
        if t > trig(bid, "ran"): chip_c(d, 780, "ONE OF THE HIGHEST ASKS · ONE OF THE HIGHEST-HOUR AIRFRAMES · WE RAN IT", f=MB(26))

def sc_pick(im, t, s0, s1):
    bid = BID["pick"]
    im.paste(kb(photo_bg("archer-7.jpg", dark=0.4), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); rep_label(im, REP)
    ta = trig(bid, "airframe")
    if t < ta - 0.3:
        p = (t - s0 - 0.3) / 1.2
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 90))
        d.text((W / 2, 420), count(180000, p), font=MB(150), fill=WHITE, anchor="mm")
        d.text((W / 2, 545), "N8395H · 1981 PIPER ARCHER II · PRIVATE SELLER, FLORIDA", font=MB(30), fill=CYAN, anchor="mm")
    else:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 150))
        p = ease((t - ta + 0.3) / 0.6)
        panel(d, [260, 200, 900, 600]); d.text((580, 280), "AIRFRAME", font=MB(26), fill=GREY, anchor="mm")
        d.text((580, 400), "12,364", font=MB(130), fill=(*WHITE, int(255 * p)), anchor="mm"); d.text((580, 520), "HOURS", font=MB(24), fill=GREY, anchor="mm")
        if t > trig(bid, "twice"): chip(d, 270, 625, "MARKET AVERAGE: 5,580", f=MB(24))
        if t > trig(bid, "training"): d.text((580, 720), "OFTEN: YEARS OF TRAINING OR RENTAL FLYING", font=MR(22), fill=OFF, anchor="mm")
        te = trig(bid, "engine", 1)
        if t > te:
            p = ease((t - te) / 0.6)
            panel(d, [1020, 200, 1660, 600]); d.text((1340, 280), "ENGINE · FACTORY REBUILT", font=MB(26), fill=CYAN, anchor="mm")
            d.text((1340, 400), "174", font=MB(130), fill=(*CYAN, int(255 * p)), anchor="mm"); d.text((1340, 520), "HOURS", font=MB(24), fill=GREY, anchor="mm")
        if t > trig(bid, "panel"): chip_c(d, 800, "GARMIN G3X TOUCH · GTN 750Xi · GFC 500 AUTOPILOT", f=MB(30))

def sc_header(im, t, s0, s1):
    bid = BID["header"]
    im.paste(kb(photo_bg("archer-0.jpg", blur=14, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT DOES THE REPORT SAY FIRST?")
    cos = [(UNION(BX(HC, "NTSB DAMAGE"), BX(HC, "None", 1)), trig(bid, "accident")),
           (UNION(BX(HC, "FINANCING"), BX(HC, "Window 2025")), trig(bid, "loan")),
           (UNION(BX(HC, "CURRENT OWNERSHIP"), BX(HC, "Certificate issued")), trig(bid, "company")),
           (UNION(BX(HC, "MAJOR AD"), BX(HC, "$2,500")), trig(bid, "warning:"))]
    report_slide(im, t, HC, (0, 0, 1152, 640), cos, t0=s0, cy=525, maxh=800)

def sc_value(im, t, s0, s1):
    bid = BID["value"]
    im.paste(kb(photo_bg("archer-2.jpg", blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "IS THE PRICE FAIR?")
    tc = trig(bid, "Seven")
    if t < tc - 0.2:
        cos = [(UNION(BX("valuation", "ESTIMATED VALUE"), BX("valuation", "$124,900", 1)), trig(bid, "twenty-five")),
               (UNION(BX("valuation", "NET ADJUSTMENT"), BX("valuation", "+$0")), trig(bid, "adjustment")),
               (UNION(BX("valuation", "ESTIMATED RANGE"), BX("valuation", "$105,000")), trig(bid, "twenty-five") + 1.2)]
        report_slide(im, t, "valuation", (25, 95, 1127, 385), cos, t0=s0, cy=430, maxh=560)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "fifty-five"): chip_c(d, 760, "THIS ONE ASKS $180,000 · +$55,100 OVER THE ESTIMATE", f=MB(28))
        if t > trig(bid, "adjustment"): chip_c(d, 840, "HOURS ENTERED, BUT NO ADJUSTMENT FOR AIRFRAME OR ENGINE TIME", f=MB(24), fill=(15, 42, 63), fg=OFF)
    else:
        tiles(im, t, [("REPORT ESTIMATE", "$124,900", "no adjustment for hours", tc - 0.2, False),
                      ("7 HIGH-HOUR ARCHERS", "$99,900", "9,000+ airframe hrs · typical ask", tc, False),
                      ("6 FRESH-ENGINE ARCHERS", "$167,450", "engine < 600 hrs · typical ask", trig(bid, "Six"), False),
                      ("THIS ONE", "$180,000", "12,364 airframe · 174 engine", trig(bid, "both"), True)], y=330, bw=410, h=300)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "both"): chip_c(d, 720, "IT ASKS MORE THAN BOTH GROUPS", f=MB(32))
        d.text((W / 2, 820), "ARCHER / ARCHER II, 1974–1985 · ACTIVE US LISTINGS WITH A PRICE · OCT 26, 2026 · NEXTPLANE PANEL", font=MR(19), fill=GREY, anchor="mm")

def sc_hours(im, t, s0, s1):
    bid = BID["hours"]
    im.paste(kb(photo_bg("archer-5.jpg", blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT IS THE EXTRA MONEY BUYING?")
    tc = trig(bid, "cost")
    if t < tc - 0.2:
        cos = [(BX("mktcomp", "This aircraft: 12,364"), trig(bid, "sixty-eight")), (BX("mktcomp", "This aircraft: 174"), trig(bid, "thousand", 1))]
        report_slide(im, t, "mktcomp", (25, 105, 760, 290), cos, t0=s0, cy=430, maxh=420, maxw=1600)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "matters,"): chip_c(d, 800, "AN ENGINE OVERHAUL IS A BIG BILL · FEWER ENGINE HOURS = MORE TIME BEFORE IT", f=MB(24))
    else:
        cos = [((42, 110, 553, 190), trig(bid, "twenty-two")), ((599, 110, 1110, 190), trig(bid, "forty-four"))]
        report_slide(im, t, "cpm", (25, 20, 1127, 380), cos, t0=tc - 0.2, cy=500, maxh=640)

def sc_engine(im, t, s0, s1):
    bid = BID["engine"]
    im.paste(kb(photo_bg("pa28-0.jpg", blur=12, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HOW MUCH IS A FRESH ENGINE WORTH?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 150, 1810, 930])
    rows = [("REPORT'S ENGINE OVERHAUL SET-ASIDE", "$2,268 / 120 HRS ≈ $18.90 / HR", trig(bid, "nineteen")),
            ("EXTRA ENGINE LIFE vs HIGH-HOUR ARCHERS", "1,639 − 174 ≈ 1,465 HRS", trig(bid, "fifteen")),
            ("WORTH, AT THAT RATE", "≈ $27,700", trig(bid, "twenty-eight"))]
    for i, (lab, v, ts) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 220 + i * 80
        d.text((160, y), lab, font=MB(26), fill=(*GREY, int(255 * p)), anchor="lm"); d.text((1760, y), v, font=MB(36), fill=(*(CYAN if i == 2 else OFF), int(255 * p)), anchor="rm")
    if t > trig(bid, "third") - 0.4:
        d.text((160, 510), "THE GAP: $180,000 ASK − $99,900 TYPICAL HIGH-HOUR ARCHER = $80,100", font=MB(26), fill=WHITE, anchor="lm")
        p = ease((t - trig(bid, "third") + 0.4) / 0.8); x0, x1 = 160, 1760; xe = x0 + (x1 - x0) * 27700 / 80100
        d.rounded_rectangle([x0, 560, x0 + (xe - x0) * p, 650], radius=10, fill=CYAN)
        if p >= 1: d.text(((x0 + xe) / 2, 605), "ENGINE ≈ $28K", font=MB(30), fill=NAVY, anchor="mm")
        tr = trig(bid, "rest")
        if t > tr:
            p2 = ease((t - tr) / 0.8)
            d.rounded_rectangle([xe + 8, 560, xe + 8 + (x1 - xe - 8) * p2, 650], radius=10, fill=(120, 150, 170))
            if p2 >= 1: d.text(((xe + x1) / 2, 605), "PANEL · AUTOPILOT · PAINT · INTERIOR ≈ $52K", font=MB(30), fill=NAVY, anchor="mm")
    if t > trig(bid, "Decide"): chip_c(d, 740, "DECIDE WHAT THE PANEL IS WORTH TO YOU, BEFORE YOU CALL", f=MB(30))
    d.text((W / 2, 880), "SET-ASIDE FROM THE REPORT'S COST OF OWNERSHIP · ENGINE HOURS FROM LISTINGS · AN ESTIMATE, NOT A QUOTE", font=MR(19), fill=GREY, anchor="mm")

def sc_flight(im, t, s0, s1):
    bid = BID["flight"]
    im.paste(kb(photo_bg("archer-3.jpg", blur=6, dark=0.78), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "STEP 2", "IS IT FLYING?")
    cos = [(UNION(BX("fl_period", "Last 24 months"), BX("fl_period", "~18.6")), trig(bid, "twenty-six")),
           (UNION(BX("fl_period", "Last 12 months"), BX("fl_period", "~9.7")), trig(bid, "twelve"))]
    report_slide(im, t, "fl_period", (0, 0, 1102, 238), cos, t0=s0, cy=340, maxw=1500, maxh=330)
    d = ImageDraw.Draw(im, "RGBA")
    tf = trig(bid, "fits")
    if t > tf:
        panel(d, [210, 560, 1710, 880])
        d.text((W / 2, 610), "ENGINE: FACTORY REBUILT · LISTING DATES IT TO 2021", font=MB(24), fill=GREY, anchor="mm")
        d.text((W / 2, 690), "174 HRS IN ~5 YEARS ≈ 35 HRS A YEAR", font=MB(44), fill=WHITE, anchor="mm")
        if t > trig(bid, "corrode"): d.text((W / 2, 770), "ENGINES THAT SIT TEND TO CORRODE INSIDE", font=MB(30), fill=RED, anchor="mm")
        if t > trig(bid, "oil"): d.text((W / 2, 830), "PRE-BUY: OIL ANALYSIS + CAMERA (BORESCOPE) LOOK INSIDE THE CYLINDERS", font=MB(24), fill=CYAN, anchor="mm")

def sc_pricehist(im, t, s0, s1):
    bid = BID["pricehist"]
    im.paste(kb(photo_bg("archer-6.jpg", blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS THE SELLER MOVED?")
    tc = trig(bid, "Of", 1)
    if t < tc - 0.2:
        cos = [(UNION(BX("listhist", "PRICE SINCE"), BX("listhist", "First seen")), trig(bid, "October")),
               (BX("listhist", "Price cut", pad=3), trig(bid, "cut", 1))]
        report_slide(im, t, "listhist", (25, 95, 1127, 500), cos, t0=s0, cy=500, maxh=720)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "forty"): chip(d, 1200, 860, "ONE CUT · −$40,000 · −18.2% · 6 DAYS IN", f=MB(28))
    else:
        d = ImageDraw.Draw(im, "RGBA"); panel(d, [140, 160, 1780, 900])
        d.text((W / 2, 215), "ARCHERS (PRE-2007) FIRST LISTED APR 26 – JUL 20, 2026 · US · ONE PER TAIL", font=MB(24), fill=GREY, anchor="mm")
        items = [("25", "ARCHERS LISTED", tc), ("8", "CUT THEIR PRICE (1%+)", trig(bid, "eight")), ("≈6%", "TYPICAL CUT", trig(bid, "six")), ("9", "STILL LISTED AFTER 90 DAYS", trig(bid, "Nine"))]
        for i, (v, lab, ts) in enumerate(items):
            p = ease((t - ts) / 0.6)
            if p <= 0: continue
            x = 345 + i * 410
            d.text((x, 410), v, font=MB(120), fill=(*(CYAN if i in (1, 2) else WHITE), int(255 * p)), anchor="mm")
            d.text((x, 510), lab, font=MB(20), fill=OFF, anchor="mm")
        if t > trig(bid, "faster"): chip_c(d, 620, "THIS SELLER: −18.2% IN THE FIRST 6 DAYS · ABOUT 3x THE TYPICAL CUT", f=MB(28))
        if t > trig(bid, "often"): d.text((W / 2, 740), "A BIG EARLY CUT OFTEN MEANS THE SELLER WANTS A SALE (A MARKET READ, NOT MEASURED)", font=MR(22), fill=GREY, anchor="mm")

def sc_owner(im, t, s0, s1):
    bid = BID["owner"]
    im.paste(kb(photo_bg("archer-4.jpg", blur=14, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO OWNS IT?")
    cos = [(BX("reg", "Jun 1, 2020", pad=2), trig(bid, "June")), (BX("reg", "No security conveyance indexed", 1, pad=4), trig(bid, "airframe.")),
           (UNION(BX("reg", "ENGINE SERIAL"), BX("reg", "Check")), trig(bid, "serial"))]
    report_slide(im, t, "reg", (0, 80, 1152, 730), cos, t0=s0, cy=440, maxh=610)
    d = ImageDraw.Draw(im, "RGBA")
    tm = trig(bid, "matches")
    if trig(bid, "different") < t < tm: chip_c(d, 790, "OWNER: A FLORIDA COMPANY · SELLER: A PRIVATE PERSON IN ANOTHER FLORIDA CITY", f=MB(24))
    if t > tm: chip_c(d, 790, "MAKE SURE THE REGISTERED OWNER MATCHES THE SELLER", f=MB(30))
    items = [("Engine serial: check for an engine loan", trig(bid, "serial")), ("Title search", trig(bid, "title")), ("Escrow · a neutral party holds the money", trig(bid, "escrow,"))]
    x = 60
    for s, tt in items:
        if t > tt:
            f = BS(32); tw = d.textlength(s, font=f)
            d.rounded_rectangle([x, 880, x + tw + 80, 950], radius=12, fill=(10, 22, 34, 230), outline=(37, 197, 203, 120), width=2)
            bullet(d, x + 20, 915, s, f); x += tw + 100

def sc_ads(im, t, s0, s1):
    bid = BID["ads"]
    im.paste(kb(photo_bg("pa28-1.jpg", blur=14, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT SHOULD THE LOGBOOKS SHOW?")
    tb = trig(bid, "First,")
    if t < tb - 0.3:
        cos = [(UNION(BX("ads", "ITEMS"), BX("ads", "11 ADs")), trig(bid, "eleven")), (UNION(BX("ads", "AIRCRAFT"), BX("ads", "s/n 28")), trig(bid, "mandatory"))]
        report_slide(im, t, "ads", (25, 115, 660, 345), cos, t0=s0, cy=430, maxh=520, maxw=1300)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "Six"): chip_c(d, 780, "11 MATCHED · 6 APPLY ONLY IF CERTAIN PARTS ARE INSTALLED", f=MB(28))
    else:
        cos2 = [(UNION(BX("ads", "2024-10-04", 1), BX("ads", "Inspect rear wing")), tb), (UNION(BX("ads", "2024-14-03"), BX("ads", "Update Garmin GFC")), trig(bid, "Second,"))]
        report_slide(im, t, "ads", (0, 1795, 345, 2045), cos2, t0=tb - 0.3, cy=360, maxh=480, maxw=900, cx=560)
        d = ImageDraw.Draw(im, "RGBA")
        panel(d, [1060, 150, 1820, 600], a=220)
        d.text((1100, 200), "WING SPAR = THE MAIN BEAM", font=MB(26), fill=CYAN, anchor="lm")
        d.text((1100, 240), "THAT HOLDS THE WING ON", font=MB(26), fill=CYAN, anchor="lm")
        if t > trig(bid, "flags"):
            d.text((1100, 320), "REPORT: FLAGGED PAST 5,000 HRS", font=MB(26), fill=OFF, anchor="lm"); d.text((1100, 360), "ESTIMATE ≈ $2,500", font=MB(26), fill=OFF, anchor="lm")
        if t > trig(bid, "twelve"): d.text((1100, 430), "THIS AIRFRAME: 12,364 HRS", font=MB(34), fill=RED, anchor="lm")
        if t > trig(bid, "software"): d.text((1100, 520), "GFC 500 AUTOPILOT: SOFTWARE UPDATE AD", font=MB(24), fill=OFF, anchor="lm")
        tr = trig(bid, "rival")
        if t > tr:
            panel(d, [160, 680, 1760, 900], a=220)
            d.text((200, 730), "RIVAL 1983 ARCHER II · $199,900 · LISTING: SPAR INSPECTION / AD COMPLIANCE COMPLETED", font=MR(22), fill=OFF, anchor="lm")
            if t > trig(bid, "mention"): d.text((200, 790), "THIS LISTING: NO MENTION OF THE SPAR INSPECTION", font=MB(30), fill=RED, anchor="lm")
            if t > trig(bid, "proof"): d.text((200, 850), "ASK FOR PROOF OF BOTH IN THE LOGBOOKS", font=MB(30), fill=CYAN, anchor="lm")

def sc_sdr(im, t, s0, s1):
    bid = BID["sdr"]
    im.paste(kb(photo_bg("archer-0.jpg", blur=14, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS IT EVER BEEN HURT?")
    cos = [(UNION(BX("sdr", "LAST 5 YRS"), BX("sdr", "496")), trig(bid, "five", 1)),
           (UNION(BX("sdr", "BRACKET"), BX("sdr", "SKIN"), BX("sdr", "101"), BX("sdr", "61")), trig(bid, "brackets")),
           (BX("sdr", "No Service", pad=4), trig(bid, "None"))]
    report_slide(im, t, "sdr", (0, 100, 1152, 590), cos, t0=s0, cy=450, maxh=640)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "accident"): chip(d, 70, 880, "ACCIDENT RECORDS FOR THIS AIRCRAFT: NONE", f=MB(26))
    if t > trig(bid, "None"): chip(d, 1180, 880, "THIS AIRCRAFT: 0 REPORTS", fill=CYAN, f=MB(26))

def sc_opcost(im, t, s0, s1):
    bid = BID["opcost"]
    im.paste(kb(photo_bg("archer-3.jpg", blur=12, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT WILL IT COST TO KEEP?")
    cos = [(UNION(BX("opcost", "Total Annual"), BX("opcost", "$23,522")), trig(bid, "twenty-three")),
           (UNION(BX("opcost", "Cost per Flight"), BX("opcost", "$196/hr")), trig(bid, "ninety-six")),
           (UNION(BX("opcost", "Fuel (120"), BX("opcost", "$7,068")), trig(bid, "Fuel")),
           (UNION(BX("opcost", "Region:"), BX("opcost", "Insurance"), BX("opcost", "$3,540")), trig(bid, "Insurance"))]
    report_slide(im, t, "opcost", (0, 0, 1152, 590), cos, t0=s0, cy=480, maxh=720)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "quote."): chip(d, 70, 880, "INSURANCE FIGURED ON THE $180,000 ASK · GET A REAL QUOTE", f=MB(26))

def sc_seller(im, t, s0, s1):
    bid = BID["seller"]
    im.paste(kb(photo_bg("archer-2.jpg", blur=12, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO AM I DEALING WITH?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [330, 200, 1590, 840])
    d.text((W / 2, 300), "PRIVATE SELLER", font=BB(100), fill=CYAN, anchor="mm")
    d.text((W / 2, 385), "FLORIDA · LISTED OCT 3, 2026 · OWNER: A FLORIDA COMPANY", font=MB(28), fill=OFF, anchor="mm")
    items = [("No dealer to stand behind the sale", trig(bid, "dealer")), ("Your own pre-buy, at a Piper shop you choose", trig(bid, "pre-buy")),
             ("Confirm the seller can sign for the company", trig(bid, "confirm"))]
    for i, (s, ts) in enumerate(items):
        if t > ts: bullet(d, 400, 500 + i * 95, s, BS(46), mark="ok" if i else "arrow")

def sc_offer(im, t, s0, s1):
    bid = BID["offer"]
    im.paste(kb(photo_bg("archer-7.jpg", blur=12, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 3", "THE OFFER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 140, 1810, 940])
    rows = [("TYPICAL ASK · 7 HIGH-HOUR ARCHERS (9,000+ HRS)", "$99,900", trig(bid, "High-hour")),
            ("TYPICAL ASK · 6 FRESH-ENGINE ARCHERS (FAR FEWER AIRFRAME HRS)", "$167,450", trig(bid, "nearly")),
            ("THIS ONE · 12,364 AIRFRAME · 174 ENGINE", "$180,000", trig(bid, "asks", 3)),
            ("THIS SELLER'S CUT · FIRST WEEK", "−$40,000", trig(bid, "already")),
            ("MODEL ODDS OF ANOTHER CUT, 90 DAYS", "≈ EVEN (46%)", trig(bid, "even"))]
    for i, (lab, v, ts) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 210 + i * 70
        d.text((170, y), lab, font=MB(26), fill=(*GREY, int(255 * p)), anchor="lm"); d.text((1740, y), v, font=MB(36), fill=(*OFF, int(255 * p)), anchor="rm")
    to = trig(bid, "reasonable")
    if t > to:
        p = ease((t - to) / 0.5)
        d.rounded_rectangle([180, 565, 1740, 665], radius=18, fill=(*CYAN, int(255 * p)))
        d.text((W / 2, 615), "OPEN AROUND $160,000 · ABOUT 11% UNDER THE ASK", font=BB(58), fill=NAVY, anchor="mm")
    ts = trig(bid, "subject")
    for i, s in enumerate(["Subject to a pre-buy inspection", "The wing spar inspection record", "The engine rebuild paperwork"]):
        if t > ts + i * 0.9: bullet(d, 200, 740 + i * 62, s, BS(40))

def sc_watch(im, t, s0, s1):
    bid = BID["watch"]
    im.paste(kb(photo_bg("pa28-2.jpg", blur=8, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 4", "KEEP WATCHING")
    d = ImageDraw.Draw(im, "RGBA")
    items = [(3, "NEW ARCHER LISTINGS", "Oct 12 – Oct 26", trig(bid, "three")), (4, "PRICE CUTS", "Oct 12 – Oct 26", trig(bid, "four")),
             (0, "PRICE INCREASES", "Oct 12 – Oct 26", trig(bid, "increases."))]
    bw, gap = 520, 40; x = (W - (3 * bw + 2 * gap)) / 2; y = 280
    for v, lab, sub, ts in items:
        p = (t - ts) / 0.8
        if p > 0:
            panel(d, [x, y, x + bw, y + 330])
            d.text((x + bw / 2, y + 130), str(int(round(v * ease(p)))), font=MB(120), fill=WHITE, anchor="mm")
            d.text((x + bw / 2, y + 235), lab, font=MB(26), fill=CYAN, anchor="mm"); d.text((x + bw / 2, y + 280), sub, font=MR(22), fill=GREY, anchor="mm")
        x += bw + gap
    if t > trig(bid, "Right"): chip_c(d, 700, "RIGHT NOW, ARCHER SELLERS ARE MOVING", f=MB(30))

def sc_verdict(im, t, s0, s1):
    bid = BID["verdict"]
    im.paste(kb(photo_bg("archer-1.jpg", dark=0.55), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "VERDICT", "WHO IS THIS AIRPLANE RIGHT FOR?"); rep_label(im, REP)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "buyer"):
        panel(d, [110, 190, 940, 680], a=215); d.text((150, 245), "RIGHT FOR", font=MB(28), fill=CYAN, anchor="lm")
        for i, (s, k) in enumerate([("A modern Garmin panel", "modern"), ("An autopilot", "autopilot,"), ("A fresh engine", "fresh"), ("Plans to fly a lot", "plans")]):
            if t > trig(bid, k): bullet(d, 150, 325 + i * 80, s, BS(42))
    if t > trig(bid, "not"):
        panel(d, [980, 190, 1810, 680], a=215); d.text((1020, 245), "NOT RIGHT IF", font=MB(28), fill=RED, anchor="lm")
        bullet(d, 1020, 325, "You want low airframe hours", BS(42), mark="no")
        if t > trig(bid, "resell"): bullet(d, 1020, 405, "You plan to resell soon", BS(42), mark="no")
    if t > trig(bid, "Priced"): big_line(d, 750, "PRICED WELL ABOVE SIMILAR AIRPLANES · CLEAN HISTORY", BB(54), OFF, (t - trig(bid, "Priced")) / 0.4)
    tq = trig(bid, "Check")
    if t > tq: big_line(d, 835, "THE SPAR INSPECTION  ·  THE ENGINE PAPERWORK  ·  WHAT THE PANEL IS WORTH TO YOU", BB(44), CYAN, (t - tq) / 0.4)

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
