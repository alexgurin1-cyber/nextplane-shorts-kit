
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

def rep_label(im, txt="REPRESENTATIVE PHOTO · DAHER TBM 900-SERIES · NOT THE AIRCRAFT FOR SALE"):
    d = ImageDraw.Draw(im, "RGBA"); d.text((70, 925), txt, font=MR(18), fill=(200, 210, 218, 190), anchor="lm")
def big_line(d, y, txt, f=None, fill=OFF, p=1.0):
    f = f or BB(62); d.text((W / 2, y), txt, font=f, fill=(*fill, int(255 * min(max(p, 0), 1))), anchor="mm")
def chip_c(d, y, txt, f=None, fill=CYAN, fg=NAVY):
    f = f or MB(26); tw = d.textlength(txt, font=f); chip(d, W / 2 - tw / 2 - 18, y, txt, fill=fill, fg=fg, f=f)
def money_m(v): return "${:,.0f}".format(v)

# ---------- data (from DATA_PACK) ----------
LADDER = [("1994–2005", "TBM 700", 1700000, "$1,700,000", 9, "seven"),
          ("2006–2013", "TBM 850", 2449900, "$2,449,900", 7, "fifties"),
          ("2014–2019", "TBM 900 · 910 · 930", 3324500, "$3,324,500", 6, "series,"),
          ("2020–2021", "TBM 940", 4200000, "$3,695,000 · $4,200,000", 2, "forties"),
          ("2022–2023", "TBM 960", 5225000, "$4,925,000 · $5,225,000", 2, "sixties,")]
ASKS930 = [(3295000, "N24MY", "2,218 HRS"), (3349000, "2016", "1,870 HRS"), (3400000, "2016", "1,800 HRS")]
REP = "REPRESENTATIVE PHOTO · DAHER TBM 930 · NOT THE AIRCRAFT FOR SALE"

def sc_title(im, t, s0, s1):
    bid = BID["title"]
    im.paste(kb(photo_bg("tbm930-0.jpg", dark=0.4, focus=(0.5, 0.5)), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); d.rectangle([0, 0, W, H], fill=(8, 16, 26, 120))
    tt = trig(bid, "This", 2)
    if t < tt - 0.2:
        p = ease((t - s0 - 0.3) / 0.6)
        panel(d, [420, 260, 1500, 700], a=220)
        d.text((W / 2, 330), "AIRFRAME HOURS vs ENGINE HOURS", font=MB(26), fill=GREY, anchor="mm")
        d.text((700, 450), "2,218", font=MB(110), fill=(*WHITE, int(255 * p)), anchor="mm"); d.text((700, 540), "AIRFRAME", font=MB(26), fill=OFF, anchor="mm")
        p2 = ease((t - s0 - 1.2) / 0.6)
        d.text((1220, 450), "1,650", font=MB(110), fill=(*CYAN, int(255 * p2)), anchor="mm"); d.text((1220, 540), "ENGINE · SINCE NEW", font=MB(26), fill=CYAN, anchor="mm")
        if t > trig(bid, "younger"): d.text((W / 2, 630), "THE ENGINE IS 568 HOURS YOUNGER THAN THE AIRPLANE", font=MB(28), fill=WHITE, anchor="mm")
    else:
        p = ease((t - tt) / 0.8)
        d.text((W / 2, 390), "HOW TO BUY A", font=BB(90), fill=(*OFF, int(255 * p)), anchor="mm")
        d.text((W / 2, 510), "DAHER TBM 930", font=BB(170), fill=(*CYAN, int(255 * p)), anchor="mm")
        d.text((W / 2, 645), "ONE REAL AIRCRAFT · ONE REAL REPORT", font=MB(30), fill=(*OFF, int(220 * p)), anchor="mm")
    rep_label(im, REP)

def sc_problem(im, t, s0, s1):
    bid = BID["problem"]
    im.paste(kb(photo_bg("tbm900-1.jpg", dark=0.5), (t - s0) / (s1 - s0), 1.02, 1.1, dx=-1))
    header_bar(im, "STEP 1", "CHOOSE WHICH ONE"); rep_label(im, "REPRESENTATIVE PHOTO · DAHER TBM 900 · NOT THE AIRCRAFT FOR SALE")
    d = ImageDraw.Draw(im, "RGBA")
    tb = trig(bid, "tracking")
    if t < tb - 0.2:
        if t > trig(bid, "single-engine") - 0.2: panel(d, [330, 330, 1590, 620], a=200)
        if t > trig(bid, "single-engine"): big_line(d, 400, "SINGLE-ENGINE TURBOPROP", BB(96), OFF, (t - trig(bid, "single-engine")) / 0.4)
        if t > trig(bid, "turbine"): big_line(d, 500, "ONE TURBINE ENGINE · JET FUEL · TURNS A PROPELLER", MB(34), CYAN, (t - trig(bid, "turbine")) / 0.4)
        if t > trig(bid, "pressurized,"): big_line(d, 570, "PRESSURIZED · 6 SEATS · ~330 KNOTS CRUISE", MB(34), OFF, (t - trig(bid, "pressurized,")) / 0.4)
    else:
        p = (t - tb) / 1.0
        panel(d, [300, 300, 920, 700]); d.text((610, 450), str(int(44 * ease(p))), font=MB(170), fill=WHITE, anchor="mm")
        d.text((610, 590), "TBMs FOR SALE · US", font=MB(26), fill=CYAN, anchor="mm")
        t2 = trig(bid, "Twenty-six")
        if t > t2:
            p2 = (t - t2) / 0.8
            panel(d, [1000, 300, 1620, 700]); d.text((1310, 450), str(int(26 * ease(p2))), font=MB(170), fill=CYAN, anchor="mm")
            d.text((1310, 590), "SHOW A PUBLISHED PRICE", font=MB(26), fill=OFF, anchor="mm")
        chip_c(d, 760, "NEXTPLANE LISTING PANEL · OCT 19, 2026 · TBM 700 TO 960 · US-REGISTERED", fill=(15, 42, 63), fg=OFF, f=MB(22))

def sc_ladder(im, t, s0, s1):
    bid = BID["ladder"]
    im.paste(kb(photo_bg("tbm850-1.jpg", blur=10, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "THE PRICE LADDER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 140, 1810, 940])
    d.text((160, 185), "TYPICAL (MEDIAN) ASKING PRICE · ACTIVE US LISTINGS WITH A PRICE · OCT 19, 2026", font=MB(24), fill=GREY, anchor="lm")
    x0, xmax = 760, 1450; vmax = 6200000
    for i, (yrs, lab, v, vt, n, key) in enumerate(LADDER):
        ts = trig(bid, key, default=s0 + 3 + i * 6); p = ease((t - ts) / 0.8)
        y = 250 + i * 125; hero = i == 2
        d.text((160, y + 22), yrs, font=BB(50), fill=CYAN if hero else OFF, anchor="lm")
        d.text((420, y + 24), lab, font=MR(24), fill=CYAN if hero else GREY, anchor="lm")
        if p > 0:
            bw = (xmax - x0) * v / vmax * p
            d.rounded_rectangle([x0, y, x0 + max(bw, 8), y + 44], radius=8, fill=(*(CYAN if hero else (120, 150, 170)), 255))
            txt = (vt if n > 2 else vt) + "  (n={})".format(n)
            d.text((x0 + bw + 18, y + 22), txt if n > 2 else vt, font=MB(26), fill=WHITE, anchor="lm")
            if n <= 2: d.text((x0 + bw + 18, y + 58), "ONLY 2 PRICED · SHOWN AS THE TWO ASKS", font=MR(18), fill=GREY, anchor="lm")
    if t > trig(bid, "examples."): chip_c(d, 880, "SMALL GROUPS: EXAMPLES, NOT A PATTERN", f=MB(24), fill=(15, 42, 63), fg=OFF)

def sc_shortlist(im, t, s0, s1):
    bid = BID["shortlist"]
    im.paste(kb(photo_bg("tbm930-4.jpg", blur=12, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 1", "YOUR SHORTLIST")
    d = ImageDraw.Draw(im, "RGBA")
    rows = [("44", "TBMs for sale", s0 + 0.2), ("26", "with a published price", s0 + 0.9),
            ("4", "2016 TBM 930s", trig(bid, "Four")), ("3", "2016 930s with a price", trig(bid, "show"))]
    panel(d, [90, 150, 640, 900]); d.text((130, 195), "THE FUNNEL", font=MB(24), fill=GREY, anchor="lm")
    for i, (n, lab, ts) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 270 + i * 150; w = [460, 360, 200, 170][i]; last = i == 3
        d.rounded_rectangle([130, y, 130 + w * p, y + 70], radius=10, fill=(*(CYAN if last else (60, 90, 112)), 255))
        d.text((150, y + 35), n, font=MB(40), fill=NAVY if last else WHITE, anchor="lm")
        d.text((130, y + 97), lab, font=MR(22), fill=OFF, anchor="lm")
    if t > trig(bid, "G") - 0.3 and t < trig(bid, "Four"):
        chip(d, 700, 840, "G3000 = GARMIN'S TOUCHSCREEN COCKPIT", f=MB(26))
    tr = trig(bid, "Three", 3)
    if t > tr - 0.2:
        panel(d, [680, 150, 1830, 900])
        d.text((720, 195), "THE 3 ASKING PRICES · 2016 TBM 930 · ACTIVE US LISTINGS", font=MB(24), fill=GREY, anchor="lm")
        X = lambda v: 780 + (v - 3250000) / 200000 * 960
        d.line([780, 520, 1740, 520], fill=(90, 110, 128), width=3)
        for v in (3250000, 3300000, 3350000, 3400000, 3450000):
            d.line([X(v), 505, X(v), 535], fill=(90, 110, 128), width=3); d.text((X(v), 570), "${:.2f}M".format(v / 1e6), font=MR(22), fill=GREY, anchor="mm")
        hi = t > trig(bid, "cheapest", 1)
        for i, (v, lab, hrs) in enumerate(ASKS930):
            p = ease((t - tr - i * 1.3) / 0.4)
            if p <= 0: continue
            hero = i == 0 and hi; r = 18 if hero else 13
            d.ellipse([X(v) - r, 520 - r - (1 - p) * 40, X(v) + r, 520 + r - (1 - p) * 40], fill=(*(CYAN if hero else OFF), int(255 * p)))
            d.text((X(v), 440 - (i % 2) * 70), money_m(v), font=MB(26), fill=(*(CYAN if hero else WHITE), int(255 * p)), anchor="mm")
            d.text((X(v), 620), hrs, font=MR(20), fill=GREY, anchor="mm")
        if hi: chip_c(d, 700, "WE RAN THE CHEAPEST · TO SEE WHY", f=MB(28))

def sc_pick(im, t, s0, s1):
    bid = BID["pick"]
    im.paste(kb(photo_bg("tbm930-3.jpg", dark=0.4), (t - s0) / (s1 - s0), 1.0, 1.08))
    d = ImageDraw.Draw(im, "RGBA"); rep_label(im, REP)
    t_here = trig(bid, "airframe")
    if t < t_here - 0.3:
        p = (t - s0 - 0.3) / 1.2
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 90))
        d.text((W / 2, 420), count(3295000, p), font=MB(150), fill=WHITE, anchor="mm")
        d.text((W / 2, 545), "N24MY · 2016 DAHER TBM 930 · DEALER LISTING, CALIFORNIA", font=MB(30), fill=CYAN, anchor="mm")
    else:
        d.rectangle([0, 0, W, H], fill=(8, 16, 26, 150))
        ta = trig(bid, "airframe")
        if t > ta - 0.3:
            p = ease((t - ta + 0.3) / 0.6)
            panel(d, [260, 270, 900, 670]); d.text((580, 350), "AIRFRAME", font=MB(26), fill=GREY, anchor="mm")
            d.text((580, 470), "2,218", font=MB(150), fill=(*WHITE, int(255 * p)), anchor="mm"); d.text((580, 590), "HOURS", font=MB(24), fill=GREY, anchor="mm")
        te = trig(bid, "engine", 1)
        if t > te:
            p = ease((t - te) / 0.6)
            panel(d, [1020, 270, 1660, 670]); d.text((1340, 350), "ENGINE · SINCE NEW", font=MB(26), fill=CYAN, anchor="mm")
            d.text((1340, 470), "1,650", font=MB(150), fill=(*CYAN, int(255 * p)), anchor="mm"); d.text((1340, 590), "HOURS", font=MB(24), fill=GREY, anchor="mm")
        if t > trig(bid, "likely,"): chip_c(d, 730, "568 HOURS APART · MOST LIKELY NOT THE ORIGINAL ENGINE · ASK WHY", f=MB(28))
        if t > trig(bid, "inspection"): chip_c(d, 810, "AND A BIG ENGINE INSPECTION IS CLOSE", f=MB(28), fill=(15, 42, 63), fg=OFF)

def sc_header(im, t, s0, s1):
    bid = BID["header"]
    im.paste(kb(photo_bg("tbm930-1.jpg", blur=14, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT DOES THE REPORT SAY FIRST?")
    K = "_headercomb"
    cos = [(BX(K, "NTSB DAMAGE", pad=4, x1=560) [:2] + (560, 234), trig(bid, "accident")),
           (UNION(BX(K, "FINANCING"), BX(K, "Window 2025")), trig(bid, "loan")),
           (UNION(BX(K, "CURRENT OWNERSHIP"), BX(K, "Certificate issued")), trig(bid, "company")),
           (UNION(BX(K, "NEXTPLANE INVESTMENT"), BX(K, "Strong"), BX(K, "A", 1, exact=True)), trig(bid, "summary,"))]
    blurs = [BX(K, "1024AVIATION", pad=2), BX(K, "Odessa, TX", pad=2)]
    report_slide(im, t, K, (0, 0, 1152, 600), cos, blurs=blurs, t0=s0, cy=535, maxh=800)

def tiles(im, t, items, y=560, bw=520, h=300):
    d = ImageDraw.Draw(im, "RGBA"); n = len(items); gap = 40; x = (W - (n * bw + (n - 1) * gap)) / 2
    for lab, vtxt, sub, ts, hi in items:
        p = ease((t - ts) / 0.6)
        if p > 0:
            panel(d, [x, y, x + bw, y + h])
            d.text((x + bw / 2, y + 60), lab, font=MB(24), fill=CYAN if hi else GREY, anchor="mm")
            d.text((x + bw / 2, y + 150), vtxt, font=MB(64), fill=(*(CYAN if hi else WHITE), int(255 * p)), anchor="mm")
            d.text((x + bw / 2, y + 235), sub, font=MR(20), fill=GREY, anchor="mm")
        x += bw + gap

def sc_value(im, t, s0, s1):
    bid = BID["value"]
    im.paste(kb(photo_bg("tbm930-1.jpg", blur=12, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "IS THE PRICE FAIR?")
    tc = trig(bid, "checked")
    if t < tc - 0.2:
        cos = [(UNION(BX("valuation", "ESTIMATED VALUE"), BX("valuation", "$3,444,000")), trig(bid, "four", 1)),
               (UNION(BX("valuation", "ESTIMATED RANGE"), BX("valuation", "$3,361,750")), trig(bid, "four", 1) + 1.2)]
        report_slide(im, t, "valuation", (25, 100, 1127, 385), cos, t0=s0, cy=430, maxh=520)
    else:
        cos = [(UNION(BX("similar", "2018", 1), BX("similar", "$3,550,000"), BX("similar", "1,060 hrs")), trig(bid, "Three", 2))]
        report_slide(im, t, "similar", (0, 20, 1152, 390), cos, t0=tc - 0.2, cy=330, maxh=400)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "Three", 2):
            d.text((W / 2, 545), "NO LONGER IN THE LATEST SCAN: 2018 GERMANY-BASED · 2017 GA · 2017 CA (NOT IN VIEW)", font=MR(20), fill=(230, 120, 110), anchor="mm")
        tu = trig(bid, "Using")
        if t > tu:
            tiles(im, t, [("NEXTPLANE ESTIMATE", "$3,444,000", "report · 6 listings, 3 gone", tu, False),
                          ("TYPICAL ASK TODAY", "$3,349,000", "5 similar 910/930s for sale now", trig(bid, "typical"), True),
                          ("THIS ONE", "−$54,000", "$3,295,000 · −1.6%", trig(bid, "fifty-four"), True)], y=590, h=280)
        if t > trig(bid, "end"): chip_c(d, 900, "NOT A BIG DISCOUNT · THE LOW END OF THE MARKET", f=MB(28))

def sc_hours(im, t, s0, s1):
    bid = BID["hours"]
    im.paste(kb(photo_bg("tbm930-5.jpg", blur=12, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHY IS IT CHEAPEST? THE HOURS")
    cos = [(BX("mktcomp", "This aircraft: 2,218"), trig(bid, "twenty-two"))]
    report_slide(im, t, "mktcomp", (25, 105, 760, 260), cos, t0=s0, cy=330, maxh=330, maxw=1500)
    d = ImageDraw.Draw(im, "RGBA")
    to = trig(bid, "other")
    if t > to:
        rows = [("N24MY · THIS ONE", 2218, "$3,295,000", True), ("2016 TBM 930", 1870, "$3,349,000", False), ("2016 TBM 930", 1800, "$3,400,000", False)]
        panel(d, [210, 560, 1710, 880])
        for i, (lab, hrs, ask, hero) in enumerate(rows):
            p = ease((t - to - i * 0.9) / 0.5)
            if p <= 0: continue
            y = 610 + i * 85; bw = 700 * hrs / 2400 * p
            d.text((250, y + 22), lab, font=MB(24), fill=CYAN if hero else OFF, anchor="lm")
            d.rounded_rectangle([620, y, 620 + bw, y + 44], radius=8, fill=CYAN if hero else (120, 150, 170))
            d.text((620 + bw + 16, y + 22), "{:,} HRS · ASK {}".format(hrs, ask), font=MB(24), fill=WHITE, anchor="lm")
    if t > trig(bid, "buyers"): chip_c(d, 910, "BUYERS PAY FOR TIME LEFT, NOT TIME USED", f=MB(28))

def sc_engine(im, t, s0, s1):
    bid = BID["engine"]
    im.paste(kb(photo_bg("tbm900-0.jpg", blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "THE ENGINE: AN INSPECTION IS CLOSE")
    hsi = UNION(BX("ads", "HSI"), BX("ads", "↻ EVERY 1,800"), BX("ads", "Dec 2027"))
    cos = [(hsi, trig(bid, "schedules"))]
    report_slide(im, t, "ads", (0, 3650, 1152, 3805), cos, t0=s0, cy=300, maxh=300, maxw=1700)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "mid-life"): chip(d, 70, 520, "HOT SECTION INSPECTION = A MID-LIFE CHECK OF THE HOTTEST PARTS OF A TURBINE", f=MB(26))
    ts = trig(bid, "shows")
    if t > ts:
        panel(d, [110, 600, 930, 860])
        d.text((150, 640), "ENGINE HOURS · SINCE NEW (LISTING)", font=MB(22), fill=GREY, anchor="lm")
        p = ease((t - ts) / 0.8); x0, x1 = 150, 890
        d.rounded_rectangle([x0, 690, x1, 740], radius=8, fill=(40, 60, 76))
        d.rounded_rectangle([x0, 690, x0 + (x1 - x0) * 1650 / 1800 * p, 740], radius=8, fill=CYAN)
        d.line([x1, 675, x1, 755], fill=(230, 120, 110), width=4)
        d.text((x0, 790), "1,650 HRS", font=MB(30), fill=CYAN, anchor="lm"); d.text((x1, 790), "1,800 · INSPECTION", font=MB(26), fill=(230, 120, 110), anchor="rm")
        if t > trig(bid, "remain."): d.text((520, 835), "≈ 150 HOURS REMAIN", font=MB(28), fill=WHITE, anchor="mm")
    tr = trig(bid, "rival's")
    if t > tr:
        panel(d, [990, 600, 1810, 860])
        d.text((1030, 640), "NEAREST RIVAL · 2016 TBM 930", font=MB(22), fill=GREY, anchor="lm")
        d.text((1030, 700), "LISTING: \"RECENT HOT SECTION\"", font=MB(28), fill=OFF, anchor="lm")
        if t > trig(bid, "fifty-four"): d.text((1030, 770), "$3,349,000 · +$54,000", font=MB(44), fill=WHITE, anchor="lm")
    if t > trig(bid, "quote"): chip_c(d, 900, "NO RELIABLE COST IN OUR DATA · GET A QUOTE FROM A TBM SHOP FIRST", f=MB(26))

def sc_pricehist(im, t, s0, s1):
    bid = BID["pricehist"]
    im.paste(kb(photo_bg("tbm930-2.jpg", blur=12, dark=0.82), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS THE SELLER MOVED?")
    tc = trig(bid, "Of", 1)
    blurs = [(104, 474, 420, 496)]
    if t < tc - 0.2:
        cos = [(UNION(BX("listhist", "PRICE SINCE"), BX("listhist", "First seen")), trig(bid, "August")),
               (BX("listhist", "Price cut", pad=3), trig(bid, "Cut"))]
        report_slide(im, t, "listhist", (25, 95, 1127, 500), cos, blurs=blurs, t0=s0, cy=500, maxh=720)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "since."): chip(d, 1240, 860, "ONE CUT · −$100,000 · −2.9%", f=MB(28))
    else:
        d = ImageDraw.Draw(im, "RGBA"); panel(d, [160, 170, 1760, 900])
        d.text((W / 2, 225), "TBMs FIRST LISTED APR 26 – JUL 20, 2026 · US · ONE PER TAIL", font=MB(24), fill=GREY, anchor="mm")
        items = [("26", "TBMs LISTED", tc), ("4", "CUT THEIR PRICE (1%+)", trig(bid, "four")), ("≈2%", "TYPICAL CUT", trig(bid, "two")), ("14", "STILL LISTED AFTER 90 DAYS", trig(bid, "ninety"))]
        for i, (v, lab, ts) in enumerate(items):
            p = ease((t - ts) / 0.6)
            if p <= 0: continue
            x = 360 + i * 400
            d.text((x, 420), v, font=MB(120), fill=(*(CYAN if i in (1, 2) else WHITE), int(255 * p)), anchor="mm")
            d.text((x, 520), lab, font=MB(20), fill=OFF, anchor="mm")
        if t > trig(bid, "forced"): d.text((W / 2, 650), "OWNERS OFTEN AREN'T FORCED TO SELL, SO THEY WAIT (A MARKET READ, NOT MEASURED)", font=MR(24), fill=GREY, anchor="mm")
        if t > trig(bid, "most."): chip_c(d, 740, "THIS SELLER: ONE CUT OF 2.9% · ALREADY MORE THAN MOST", f=MB(30))

def sc_owner(im, t, s0, s1):
    bid = BID["owner"]
    im.paste(kb(photo_bg("tbm930-4.jpg", blur=14, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO OWNS IT?")
    blurs = [BX("reg", "1024AVIATION LLC", 1, pad=2), (60, 206, 330, 230)]
    cos = [(BX("reg", "Mar 10, 2023", pad=2), trig(bid, "March")), (BX("reg", "No security", pad=4), trig(bid, "airframe.")),
           (UNION(BX("reg", "ENGINE SERIAL"), BX("reg", "Check")), trig(bid, "serial"))]
    report_slide(im, t, "reg", (0, 80, 1152, 720), cos, blurs=blurs, t0=s0, cy=445, maxh=620)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "Texas"): chip_c(d, 805, "OWNER: A TEXAS COMPANY · LISTED BY A CALIFORNIA DEALER", f=MB(24))
    items = [("Engine serial → engine lien check", trig(bid, "logbook.")), ("Title search", trig(bid, "title")), ("Escrow · a neutral party holds the money", trig(bid, "escrow,"))]
    x = 60
    for s, tt in items:
        if t > tt:
            f = BS(32); tw = d.textlength(s, font=f)
            d.rounded_rectangle([x, 880, x + tw + 80, 950], radius=12, fill=(10, 22, 34, 230), outline=(37, 197, 203, 120), width=2)
            bullet(d, x + 20, 915, s, f); x += tw + 100

def sc_flight(im, t, s0, s1):
    bid = BID["flight"]
    im.paste(kb(photo_bg("tbm930-5.jpg", blur=6, dark=0.75), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "STEP 2", "IS IT FLYING?")
    cos = [(UNION(BX("fl_period", "Last 24 months"), BX("fl_period", "~432.4")), trig(bid, "thirty-five")),
           (UNION(BX("fl_period", "Last 12 months"), BX("fl_period", "~255.9")), trig(bid, "fifty-six")),
           (UNION(BX("fl_period", "Last 3 months"), BX("fl_period", "64.6")), trig(bid, "sixty-five"))]
    report_slide(im, t, "fl_period", (0, 0, 1102, 238), cos, t0=s0, cy=330, maxw=1500, maxh=330, cx=960)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "sixty-five"): d.text((W / 2, 530), "LISTED FOR SALE AUG 13 · STILL FLYING ABOUT 20 HOURS A MONTH", font=MB(26), fill=CYAN, anchor="mm")
    tb = trig(bid, "Bakersfield")
    if t > tb - 0.3:
        report_slide(im, t, "fl_airports", (0, 0, 543, 276), [(UNION(BX("fl_airports", "HOME"), BX("fl_airports", "126")), tb)], t0=tb - 0.3, cy=760, maxw=620, maxh=340, cx=460)
        d.text((460, 950), "BFL = BAKERSFIELD, CA · ODT = ODESSA, TX", font=MR(20), fill=GREY, anchor="mm")
    if t > trig(bid, "date."):
        panel(d, [900, 610, 1810, 900])
        d.text((940, 650), "HOURS IN THE LISTING ARE ALREADY OUT OF DATE", font=MB(22), fill=(230, 120, 110), anchor="lm")
        if t > trig(bid, "pace,"): d.text((940, 730), "~150 HRS ÷ ~21 HRS/MONTH", font=MB(36), fill=WHITE, anchor="lm"); d.text((940, 790), "≈ 7 MONTHS TO THE INSPECTION", font=MB(36), fill=CYAN, anchor="lm")
        if t > trig(bid, "writing."): d.text((940, 860), "REPORT ASSUMES 130 HRS/YR · TRACKED: ~256", font=MR(20), fill=GREY, anchor="lm")

def sc_ads(im, t, s0, s1):
    bid = BID["ads"]
    im.paste(kb(photo_bg("tbm900-3.jpg", blur=14, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT SHOULD THE LOGBOOKS SHOW?")
    cos = [(UNION(BX("ads", "AIRCRAFT"), BX("ads", "SOCATA TBM 700")), trig(bid, "version")),
           (UNION(BX("ads", "ITEMS"), BX("ads", "17 ADs")), trig(bid, "seventeen"))]
    blurs = [BX("ads", "1024AVIATION", pad=2)]
    tb = trig(bid, "emergency")
    if t < tb - 0.3:
        report_slide(im, t, "ads", (25, 115, 660, 345), cos, blurs=blurs, t0=s0, cy=430, maxh=520, maxw=1300)
        d = ImageDraw.Draw(im, "RGBA")
        if t > trig(bid, "Six"): chip_c(d, 780, "17 MATCHED · 6 APPLY ONLY IF CERTAIN PARTS ARE INSTALLED", f=MB(28))
        if t > trig(bid, "repeat"): chip_c(d, 850, "SEVERAL REPEAT EVERY 100 HOURS · CONFIRM EACH IS SIGNED OFF", f=MB(26), fill=(15, 42, 63), fg=OFF)
    else:
        cos2 = [(UNION(BX("ads", "2024-04-51"), BX("ads", "Comply with Transport")), tb)]
        report_slide(im, t, "ads", (0, 3650, 1152, 3745), cos2, t0=tb - 0.3, cy=330, maxh=260, maxw=1700)
        d = ImageDraw.Draw(im, "RGBA")
        chip_c(d, 560, "AD 2024-04-51 · TURBINE BLADES · PT6A-66D ENGINE MODEL", f=MB(28))
        if t > trig(bid, "serial"): big_line(d, 680, "APPLIES DEPENDING ON THE ENGINE SERIAL NUMBER", BB(60), OFF, (t - trig(bid, "serial")) / 0.4)
        if t > trig(bid, "original,"): big_line(d, 770, "NOT THE ORIGINAL ENGINE? CHECK THIS ONE FIRST", BB(60), CYAN, (t - trig(bid, "original,")) / 0.4)

def sc_sdr(im, t, s0, s1):
    bid = BID["sdr"]
    im.paste(kb(photo_bg("tbm930-0.jpg", blur=14, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "HAS IT EVER BEEN HURT?")
    cos = [(UNION(BX("sdr", "LAST 5 YRS"), BX("sdr", "2", 1)), trig(bid, "two")), (BX("sdr", "No Service", pad=4), trig(bid, "None"))]
    report_slide(im, t, "sdr", (0, 100, 1152, 590), cos, t0=s0, cy=450, maxh=640)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "accident"): chip(d, 70, 880, "NTSB ACCIDENT RECORDS FOR THIS AIRCRAFT: NONE", f=MB(26))
    if t > trig(bid, "clean"): chip(d, 1240, 880, "A CLEAN RECORD", fill=CYAN, f=MB(26))

def sc_opcost(im, t, s0, s1):
    bid = BID["opcost"]
    im.paste(kb(photo_bg("tbm930-3.jpg", blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT WILL IT COST TO KEEP?")
    cos = [(UNION(BX("opcost", "Total Annual"), BX("opcost", "$172,202")), trig(bid, "seventy-two")),
           (UNION(BX("opcost", "Cost per Flight"), BX("opcost", "$861/hr")), trig(bid, "sixty-one", 1)),
           (UNION(BX("opcost", "Fuel (200"), BX("opcost", "$61,200")), trig(bid, "Fuel")),
           (BX("opcost", "Estimated — fuel", pad=3, x1=420), trig(bid, "estimate"))]
    report_slide(im, t, "opcost", (0, 60, 1152, 590), cos, t0=s0, cy=480, maxh=720)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "records."): chip(d, 70, 880, "FUEL BURN IS AN ESTIMATE · ASK FOR REAL FUEL RECORDS", f=MB(26))

def sc_msrp(im, t, s0, s1):
    bid = BID["msrp"]
    im.paste(kb(photo_bg("tbm900-4.jpg", blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHAT DID IT COST NEW?")
    cos = [(UNION(BX("msrp", "EQUIPPED MSRP"), BX("msrp", "$4,200,000")), trig(bid, "equipped,")), (UNION(BX("msrp", "OFF EQUIPPED"), BX("msrp", "21.6%")), trig(bid, "twenty-two"))]
    report_slide(im, t, "msrp", (0, 0, 1152, 200), cos, t0=s0, cy=300, maxh=330, maxw=1700)
    d = ImageDraw.Draw(im, "RGBA")
    tn = trig(bid, "sixty")
    if t > tn:
        tiles(im, t, [("NEW 2016 TBM 930", "$4,200,000", "typically equipped", tn, False), ("THIS ONE, ASKING", "$3,295,000", "about 78% of new, 10 yrs on", tn + 0.4, True),
                      ("NEW 2025 TBM 960", "$5,525,144", "typically equipped (BCA)", tn + 0.8, False)], y=520, h=280)
    if t > trig(bid, "tend"): chip_c(d, 860, "RISING NEW PRICES TEND TO HOLD UP USED ONES", f=MB(28))

def sc_seller(im, t, s0, s1):
    bid = BID["seller"]
    im.paste(kb(photo_bg("tbm930-1.jpg", blur=12, dark=0.84), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 2", "WHO AM I DEALING WITH?")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [360, 200, 1560, 840])
    d.text((W / 2, 300), "DEALER LISTING", font=BB(100), fill=CYAN, anchor="mm")
    d.text((W / 2, 385), "CALIFORNIA · LISTED AUG 13, 2026 · OWNER: A TEXAS COMPANY", font=MB(28), fill=OFF, anchor="mm")
    items = [("Does the dealer own it, or sell it for the owner?", trig(bid, "own")), ("Independent pre-buy at a TBM shop you choose", trig(bid, "pre-buy"))]
    for i, (s, ts) in enumerate(items):
        if t > ts: bullet(d, 430, 520 + i * 95, s, BS(46))

def sc_offer(im, t, s0, s1):
    bid = BID["offer"]
    im.paste(kb(photo_bg("tbm930-0.jpg", blur=12, dark=0.86), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 3", "THE OFFER")
    d = ImageDraw.Draw(im, "RGBA"); panel(d, [110, 140, 1810, 940])
    rows = [("TYPICAL ASK · 5 SIMILAR FOR SALE TODAY", "$3,349,000", trig(bid, "Similar")),
            ("THIS ONE · MOST HOURS · INSPECTION CLOSE", "$3,295,000", trig(bid, "less,")),
            ("RIVAL WITH FRESH INSPECTION · CUT OCT 6", "−$50,000", trig(bid, "rival")),
            ("THIS SELLER'S ONE CUT · SEP 9", "−$100,000", trig(bid, "once,")),
            ("MODEL ODDS OF ANOTHER CUT, 90 DAYS", "≈ 1 IN 4 (26%)", trig(bid, "four", 1))]
    for i, (lab, v, ts) in enumerate(rows):
        p = ease((t - ts) / 0.5)
        if p <= 0: continue
        y = 210 + i * 70
        d.text((170, y), lab, font=MB(26), fill=(*GREY, int(255 * p)), anchor="lm"); d.text((1740, y), v, font=MB(36), fill=(*OFF, int(255 * p)), anchor="rm")
    to = trig(bid, "reasonable")
    if t > to:
        p = ease((t - to) / 0.5)
        d.rounded_rectangle([180, 565, 1740, 665], radius=18, fill=(*CYAN, int(255 * p)))
        d.text((W / 2, 615), "OPEN AROUND $3,200,000 · ABOUT 3% UNDER THE ASK", font=BB(58), fill=NAVY, anchor="mm")
    ts = trig(bid, "subject")
    for i, s in enumerate(["Subject to a pre-buy inspection", "Current hours, in writing", "The engine logbook"]):
        if t > ts + i * 0.9: bullet(d, 200, 730 + i * 62, s, BS(40))
    tw = trig(bid, "seller", 2)
    if t > tw:
        panel(d, [960, 700, 1770, 910], a=200)
        d.text((1365, 745), "THE HOT SECTION INSPECTION", font=MB(24), fill=CYAN, anchor="mm")
        d.text((1365, 805), "SELLER DOES IT BEFORE CLOSING", font=BB(46), fill=WHITE, anchor="mm")
        if t > trig(bid, "quoted"): d.text((1365, 865), "OR TAKE ITS QUOTED COST OFF", font=BB(42), fill=CYAN, anchor="mm")

def sc_watch(im, t, s0, s1):
    bid = BID["watch"]
    im.paste(kb(photo_bg("tbm900-2.jpg", blur=8, dark=0.8), (t - s0) / (s1 - s0)))
    header_bar(im, "STEP 4", "KEEP WATCHING")
    d = ImageDraw.Draw(im, "RGBA")
    items = [(5, "NEW TBM LISTINGS", "Oct 5 – Oct 19", trig(bid, "five")), (3, "PRICE CUTS", "Oct 5 – Oct 19", trig(bid, "three")),
             (0, "PRICE INCREASES", "Oct 5 – Oct 19", trig(bid, "increases."))]
    bw, gap = 520, 40; x = (W - (3 * bw + 2 * gap)) / 2; y = 280
    for v, lab, sub, ts in items:
        p = (t - ts) / 0.8
        if p > 0:
            panel(d, [x, y, x + bw, y + 330])
            d.text((x + bw / 2, y + 130), str(int(round(v * ease(p)))), font=MB(120), fill=WHITE, anchor="mm")
            d.text((x + bw / 2, y + 235), lab, font=MB(26), fill=CYAN, anchor="mm"); d.text((x + bw / 2, y + 280), sub, font=MR(22), fill=GREY, anchor="mm")
        x += bw + gap
    if t > trig(bid, "rival."): chip_c(d, 680, "ONE CUT: THIS AIRPLANE'S CLOSEST RIVAL · $3,399,000 → $3,349,000", f=MB(26), fill=(15, 42, 63), fg=OFF)
    if t > trig(bid, "Right"): chip_c(d, 760, "RIGHT NOW, SELLERS ARE MOVING, SLOWLY", f=MB(30))

def sc_verdict(im, t, s0, s1):
    bid = BID["verdict"]
    im.paste(kb(photo_bg("tbm930-3.jpg", dark=0.5), (t - s0) / (s1 - s0), 1.0, 1.08))
    header_bar(im, "VERDICT", "WHO IS THIS AIRPLANE RIGHT FOR?"); rep_label(im, REP)
    d = ImageDraw.Draw(im, "RGBA")
    if t > trig(bid, "buyer"):
        panel(d, [110, 190, 940, 680], a=215); d.text((150, 245), "RIGHT FOR", font=MB(28), fill=CYAN, anchor="lm")
        for i, (s, k) in enumerate([("Flies a lot", "flies"), ("Wants the 930 at the lowest ask", "lowest"), ("Ready to pay for the hot", "ready"), ("section inspection soon", "ready")]):
            if t > trig(bid, k): bullet(d, 150, 325 + i * 80, s, BS(42), mark="ok" if i < 3 else "arrow", fill=WHITE if i < 3 else GREY)
    if t > trig(bid, "not"):
        panel(d, [980, 190, 1810, 680], a=215); d.text((1020, 245), "NOT RIGHT IF", font=MB(28), fill=(230, 120, 110), anchor="lm")
        bullet(d, 1020, 325, "You want low hours", BS(42), mark="no")
        if t > trig(bid, "engine"): bullet(d, 1020, 405, "You want no engine work", BS(42), mark="no"); bullet(d, 1020, 485, "in your first year", BS(42), fill=GREY, mark="arrow")
    if t > trig(bid, "Fairly"): big_line(d, 750, "FAIRLY PRICED AT THE LOW END · CLEAN HISTORY", BB(54), OFF, (t - trig(bid, "Fairly")) / 0.4)
    tq = trig(bid, "Check")
    if t > tq: big_line(d, 835, "WHY THE ENGINE IS YOUNGER  ·  WHEN THE INSPECTION IS DUE  ·  CURRENT HOURS", BB(46), CYAN, (t - tq) / 0.4)

def sc_end(im, t, s0, s1):
    p = Image.new("RGB", (1080, 1920), NAVY)
    EC.draw_endcard(p, t - s0, FD, f"{ROOT}/assets/logo.png")
    p = p.crop((0, 380, 1080, 1480)).resize((1060, 1080), Image.LANCZOS)
    im.paste(NAVY, (0, 0, W, H)); im.paste(p, ((W - 1060) // 2, 0))

SCENE_FN = {"title": sc_title, "problem": sc_problem, "ladder": sc_ladder, "shortlist": sc_shortlist, "pick": sc_pick, "header": sc_header,
            "value": sc_value, "hours": sc_hours, "engine": sc_engine, "pricehist": sc_pricehist, "owner": sc_owner,
            "flight": sc_flight, "ads": sc_ads, "sdr": sc_sdr, "opcost": sc_opcost, "msrp": sc_msrp, "seller": sc_seller, "offer": sc_offer, "watch": sc_watch,
            "verdict": sc_verdict, "end": sc_end}
