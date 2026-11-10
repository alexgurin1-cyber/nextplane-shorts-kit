# How to Buy a Beechcraft Bonanza A36 — Episode 9 — DATA PACK

- Slot: Wednesday 2026-11-11 16:00:00Z (single-engine piston only, per Alex's standing target segment of 2026-11-03).
- Model choice: the target order is SR22/SR22T → Bonanza A36 → … The Cirrus SR22 already has an episode (Ep 1, N2428E), so the next unused model is the **Beechcraft Bonanza A36**.
- Built: 2026-11-09 (scheduled cloud run). Supabase project `uiprgookspqnvyumkyse`. Latest scrape: both sources last seen 2026-11-09 07:19Z.
- **Status: report capture LOCKED (exit 3).** The capture grant insert into `public.purchased_reports` was refused by this run's permission check, so the live report could not be opened. No video was produced or uploaded. All report-section figures below come straight from Supabase; the report's own numbers (Estimated Market Value, operating cost card, grade) still have to be captured and cross-checked before anything goes on screen.
- Internal note: listing sources are kept here for verification only. Never name them on air.
- "Latest scrape" = `is_active and missed_scan_count = 0 and last_seen_at >= 2026-11-02`, N-registered (`registration ~ '^N[0-9]'`), deduplicated by N-number (latest row), ask ≥ $50,000 (drops "$0" and "$4,500" placeholder asks). Asks are quoted as asks, never as sold prices.
- **Every market figure in this pack is for Bonanzas only (the A36 or the Bonanza family), all single-engine pistons.** No twin, turboprop or jet data is used.

## Hero aircraft
| Field | Value | Source |
|---|---|---|
| Tail | **N1811Y** | `aircraft_listings.registration` |
| Listing | 256445563 (internal; a second, stale row tap_2456224 last seen 2026-07-04 at $395,000) | `listing_id` |
| Model / year | Beechcraft A36 Bonanza, **1981** | listing; registry year_mfr 1981, airworthiness 1981-06-02, mfr_mdl 1151604 |
| Serial | E-1877 | listing + registry |
| Ask | **$360,000** (published price) | `asking_price_usd` |
| First ask | $425,000 (2026-05-19) | `original_asking_price_usd` + price history |
| Airframe | **5,100 h** total time | listing |
| Engine | **19 h since factory remanufacture** (Continental IO-520 per the July ad; "just installed") | listing (`engine_time_label` SFRM). The stale July row said 10 h. |
| Prop | 27 h since overhaul (July row: 60 h) | listing |
| Avionics | Garmin G3X Touch (10") + second G3X display with engine monitoring, GTN 750Xi, GNS 650, **GFC 500** autopilot, GTX 345 (ADS-B in/out), PS Engineering 450 audio | `avionics_list`, `avionics_summary` |
| Annual | "September, 2026" (may now be due; not voiced — ask) | `annual_due` |
| Damage flag | false; accident record by tail or serial: **0**; service-difficulty reports on this tail: **0** | listing; `ntsb_accidents`; `sdr_reports` |
| Seller | **Dealer** (business), Blountville / Bristol TN | `seller_name`, `seller_type` |
| Registered owner | a **Tennessee company** (Piney Flats TN), type_registrant 7, certificate **2004-10-12** (22 years), expires 2028-07-31, status V | `aircraft_master` |
| Active | first seen 2026-05-19, last seen 2026-11-09, missed scans 0 → **174 days listed** | listing row |
| Share / partnership ad | No | description checked |
| Flight data | **No rows** in `aircraft_flight_intel` for this tail | — |

## Price history (`aircraft_price_history`, listing 256445563)
| Date | From | To | Change |
|---|---|---|---|
| 2026-06-16 | $425,000 | $395,000 | −$30,000 (−7.1%) |
| 2026-07-21 | $395,000 | $375,000 | −$20,000 (−5.1%) |
| 2026-09-29 | $375,000 | $360,000 | −$15,000 (−4.0%) |
- Three cuts, −$65,000 total, **−15.3%**. No jitter rows. Each cut smaller than the last.

## Bonanza family price ladder (latest scrape; median = "typical")
| Group | n priced | Typical ask | Half ask between | Typical airframe h |
|---|---|---|---|---|
| V35 (V-tail) | 11 | $145,000 | $132,000–$184,490 | 5,732 |
| V35B (V-tail) | 30 | **$232,325** | $179,000–$273,000 | 3,796 |
| F33A (straight tail, shorter) | 41 | **$265,000** | $235,000–$339,000 | 3,650 |
| **A36, 1968–1983** (incl. hero) | **29** | **$299,000** | **$269,000–$326,000** | **5,139** |
| A36, 1984–1993 | 9 | $369,000 | $349,000–$419,000 | 3,160 |
| B36TC (turbocharged piston) | 19 | $425,000 | $372,000–$517,200 | 2,498 |
| A36, 1994–2005 | 18 | **$466,950** | $377,175–$546,875 | 2,100 |
| G36 (current production) | 35 | **$680,000** | $597,000–$797,450 | 1,285 |
- Hero is the **4th-highest ask of 29** 1968–1983 A36s. Its 5,100 h airframe is right at the group's typical 5,139 h.

### The 29 priced A36s, 1968–1983 (one per tail)
| Tail | Year | Ask | Airframe h | Engine h (label) | G3X | GFC 500 | Damage flag |
|---|---|---|---|---|---|---|---|
| N9099S | 1976 | 169,000 | 5,821 | 2,101 SFRM | | | yes |
| N759VL | 1977 | 194,500 | 4,120 | 863 SMOH | | | |
| N342S | 1970 | 195,000 | 9,048 | 1,208 SMOH | | | yes |
| N17863 | 1977 | 209,900 | 3,085 | 1,788 SMOH | | ✓ | |
| N614MM | 1980 | 229,000 | 3,309 | 1,539 SMOH | | | |
| N3851L | 1981 | 244,900 | 8,170 | 2,055 SNEW | | | |
| N6284U | 1982 | 259,900 | 4,221 | 1,082 SMOH | | | |
| N904AD | 1974 | 269,000 | 5,967 | 1,388 SMOH | | | |
| N3160W | 1973 | 275,000 | 5,766 | 1,533 SMOH | | ✓ | |
| N25720 | 1973 | 284,450 | 7,367 | 361 SNEW | | | |
| N523AM | 1980 | 295,000 | 5,880 | 282 SMOH | | ✓ | |
| N40JH | 1976 | 298,000 | 4,090 | 95 SFRM | | | |
| N117EC | 1977 | 298,500 | 3,804 | 505 SMOH | | | |
| N72MD | 1977 | 299,000 | 4,780 | 1,413 SNEW | | ✓ | |
| N9022V | 1971 | 299,000 | 12,863 | 197 SMOH | ✓ | ✓ | |
| N23682 | 1978 | 299,950 | 5,551 | 714 SMOH | | ✓ | |
| N3333A | 1977 | 303,000 | 4,790 | 0 SNEW | | | |
| N630JL | 1976 | 304,500 | 6,657 | 100 SMOH | | | |
| N22WS | 1979 | 314,900 | 4,730 | 1,292 SNEW | | ✓ | |
| N743T | 1976 | 319,000 | 3,879 | 487 SNEW | | | |
| N4203S | 1977 | 320,000 | 5,500 | 430 SMOH | | | |
| N154M | 1981 | 326,000 | 5,000 | 1,100 SFOH | | | n/a |
| N36ET | 1981 | 339,900 | 3,720 | 1,040 SMOH | | | |
| N85BB | 1973 | 349,000 | 7,315 | 30 SMOH | | | |
| N6684D | 1979 | 349,000 | 5,139 | 5 SMOH | ✓ | ✓ | yes |
| **N1811Y** | **1981** | **360,000** | **5,100** | **19 SFRM** | ✓ | ✓ | |
| N212TD | 1982 | 365,000 | 5,985 | 1,343 SMOH | ✓ | ✓ | n/a |
| N1852S | 1981 | 375,000 | 2,960 | 290 SMOH | ✓ | ✓ | |
| N97GW | 1977 | 378,000 | 5,711 | 908 SMOH | ✓ | ✓ | |
- Median of all 29 = **$299,000**; interquartile range **$269,000–$326,000**.
- **Older-engine group (engine ≥ 600 h, excl. hero), n=16 → typical $272,000.** Hero vs this: **+$88,000**.
- **Fresh-engine group (engine < 600 h, excl. hero), n=12:** 284,450 · 295,000 · 298,000 · 298,500 · 299,000 · 303,000 · 304,500 · 319,000 · 320,000 · 349,000 · 349,000 · 375,000 → **typical $303,750**. Hero vs this: **+$56,250**.
- Fresh engine **and** G3X + GFC 500 (excl. hero): only **3** — N9022V $299,000 (12,863 h airframe), N6684D $349,000 (damage flag), N1852S $375,000.
- **Sister ship N1852S:** 1981 A36, 2,960 h airframe (≈2,140 fewer), 290 h engine, G3X + GFC 500 + GTN 750Xi, factory air, $375,000 (+$15,000). Listed by the **same dealer** since 2026-10-27; before that it was listed by another seller with no price (2026-07-29 → 2026-10-27).

## Engine value (on air, labelled as an estimate)
- NextPlane cost data (`model_cost_specs` BEE_36_BONANZA): overhaul **$68,000** every **1,700 h** → **$40 per engine hour**.
- Typical engine time of the other 28 A36s (1968–1983): **885.5 h**. Hero 19 h → difference ≈ 866 h × $40 = **$34,660 ≈ $35,000** of the $88,000 gap to older-engine A36s.
- Remainder ≈ **$53,000** = new Garmin panel and GFC 500 autopilot (no NextPlane installed-cost data → not valued; "decide what that is worth to you").
- Hours until the engine is due for an overhaul: 1,700 − 19 = **1,681 h** ("about seventeen hundred").

## Valuation
| Source | Value | Use |
|---|---|---|
| Report "Estimated Market Value" | **not captured** (report locked) | Must be captured and cross-checked before production. |
| `model_price_forecasts` fair value | $300,893 (Oct 7) → $386,294 (Oct 14) → $315,178 (Oct 21) → $382,785 (Oct 28) → $338,803 (Nov 4) | **Not used**: unstable, and it scores the stale $395,000 row (see REPORT_ISSUES #2). |
| Our groups | older-engine typical $272,000; fresh-engine typical $303,750 | Voiced. |

## Market behaviour — A36 Bonanzas first listed 2026-04-26 → 2026-08-10, one per tail
Excluded: tails whose first-seen date is 2026-07-04 (bulk ingest of the second source, not a listing date). Script: `src/cohort.py`.
| Metric | Value |
|---|---|
| Cohort | **42** A36s (includes the hero) |
| Gone from the panel within 30 days | **8** (N6736V, N25675, N836E, N6755Q, N709MA, N1836B, N711PR, N7936A) — not proof of sale |
| Still listed past 90 days | **23** |
| Net cut ≥ 1% | **24** (57%) |
| Typical cut among cutters | **6.8% → "about seven percent"** |
| Hero | −15.3% ≈ **twice** the typical cut |
Glitch rows ignored: N2024Q $275,000→$800,000→$275,000 (Jul 5–7), N903AT $150,000 first row. Never quote a mean days-on-market.

## Registration and ownership
- Registered owner: a Tennessee company (name kept off air), certificate **2004-10-12** → "twenty-two years", expires 2028-07-31. Seller: a dealer (business name kept off air until the report's seller section is verified).
- Liens / document index: no `aircraft_docindex` rows for this tail → **ask for a title search**; do not claim "no liens".

## Mandatory safety fixes (airworthiness directives)
- **2024-14-03** — Garmin GFC 500 autopilot software update (G3X Touch later than 9.01); applies because the GFC 500 + G3X are installed. Ask for the record.
- **2019-23-10** — right aileron control-cable end fittings inspection, certain 33/35/36-series Bonanzas including certain A36s. Ask whether serial E-1877 is affected and for the record.
- Not used: 2020-25-01 (a King Air wing-fitting AD wrongly mapped to A36/B36TC/G36 in `airworthiness_directives`, REPORT_ISSUES #3); 2018-06-11 (turbocharged Bonanzas only).
- Compliance is not derivable from NextPlane data → "ask for proof".

## Service difficulty / safety
- A36 model-wide service-difficulty reports: 347 total, **12 in the last 5 years** across 11 aircraft (top part: engine, 3). This tail: 0. Accident record by tail or serial: 0.

## Flight activity
- No NextPlane flight data rows for N1811Y. On air: "no recorded flights in NextPlane's flight data — that can mean little flying or a gap in our data; ask for the logbook hours" (honest, not a finding about use).

## Operating cost (NextPlane cost specs for the 36 Bonanza; report card not captured)
- 15.5 gal/h cruise, 170 kt, maintenance $45/flight hour, annual inspection $4,500, prop reserve $3/h, engine reserve $40/h. Not voiced until the report card is captured and matches.

## Offer logic (draft, on air)
Older-engine A36s typical $272,000 + ≈$35,000 engine value ≈ $307,000 before the panel; fresh-engine A36s typical $303,750; same-dealer sister ship with ≈2,140 fewer airframe hours at $375,000; listed 174 days with three cuts, A36 typical cut ≈ 7% → **open around $330,000 (−8.3%)**, subject to pre-buy, the engine-installation paperwork, both directives above and a title search.

## Capture grant (not created)
SQL for Alex (run once as admin; the capture account is a normal user):
```sql
insert into public.purchased_reports (user_id, n_number, make, model, year, amount_cents, report_data, expires_at, email_sent_at)
values ('95710b00-dab7-489d-85d0-262f53ddd349','N1811Y','BEECH','A36 BONANZA',1981,0,
        '{"internal":"How to Buy episode capture grant (no charge)"}'::jsonb, now()+interval '30 days', now());
```

---

## UPDATE 2026-11-10 — live report captured, cross-checked, episode produced
Alex set standing report access for the capture account (`profiles.subscription_status='active'`) and a one-off N1811Y grant (expires 2026-12-10). `report_capture.py N1811Y` exit 0 (52 sections); element capture 40 cards. The "LOCKED" status above is superseded.

### Report vs Supabase cross-check
| Report section | Report shows | Supabase / panel | Result |
|---|---|---|---|
| Header | $360,000 · NTSB none · "Last sold Oct 2004" · Piney Flats TN | ask $360,000; ntsb 0; cert 2004-10-12; owner city Piney Flats | ✓ |
| Estimated Market Value | **$299,925**, range $260,000–$361,000, High · 88%, net adjustment +$0 | our 1968–83 A36 typical $299,000 | ✓ estimate voiced; +$0 flagged (REPORT_ISSUES #1) |
| Listing history | 175 days; $425,000 → $360,000 (−$65,000, −15.3%); 3 cuts Jun 16 −$30,000, Jul 21 −$20,000, Sep 29 −$15,000 | `aircraft_price_history` identical | ✓ |
| Market comparison | airframe avg 5,237 (this 5,100, −137); engine avg 901 (this 19, −882) | our 1968–83 median 5,139 / 885.5 | ✓ (report figures voiced) |
| Operating cost | 120 h/yr: fuel $11,160 · insurance $5,880 · engine accrual $4,225 · total **$31,911** · **$266/h** | cost specs 15.5 gph, $68K/1,700 h | report card voiced as-is (REPORT_ISSUES #12) |
| Flight activity | 92 flights, 38.8 h (24 mo); last 12 mo 57 flights ~30.9 h; 24 mo ~37.9 h; 67% local; home TRI | `aircraft_flight_intel` fetched 2026-11-10 02:19Z: 92 / 38.8 / TRI / 67% | ✓; prior 12 mo = 37.9 − 30.9 ≈ 7 h |
| Registration | owner a TN LLC since 2004-10-12 (22.1 yrs); release indexed 2026-09-02; 0 agreements · 2 releases (window 2025-10-23 → 2026-11-05) | registry cert 2004-10-12 | ✓ owner name blurred |
| Airworthiness | 16 ADs · 4 OEM · 4 regulatory; critical item 2024-14-03 (GFC 500 software) | GFC 500 + G3X installed per listing | ✓ |
| Service difficulty | model 329 total, 12 in 5 yrs, this aircraft 0 | ours 347 / 12 / 0 (model-match differs) | ✓ "twelve in five years" voiced |
| Seller | dealer, +9.2% above market (n=12), 42% slower vs same models (9 sales), 18 in stock | location wrong (New Orleans) | stance voiced, name/location not (REPORT_ISSUES #8) |
| Market signal comparables | "Just listed" 1981 A36 $375,000, 2,960 h (N1852S) | N1852S listing: same dealer, 290 h engine, G3X/GTN 750Xi/GFC 500 | ✓ sister-ship beat |

### Engine value (final, report's own rate)
Report op-cost engine accrual $4,225 / 120 h = **$35.21/h**. Engine hours below the market average: 901 − 19 = **882 h** → 882 × $35.21 = **$31,055 ≈ $31,000**. Gap to the report estimate: $360,000 − $299,925 = **$60,075** → engine ≈ $31K, panel + autopilot ≈ $29K (not valued; "decide what that is worth to you"). The $40/h cost-spec figure above is superseded on air.

### Keep watching — A36 Bonanzas, 2026-10-27 → 2026-11-10
New tails: **4** (N72WP Oct 27, N1550U Oct 31, N17863 Nov 7, N3849X Nov 9). Price cuts: **9** (N904AD, N316P, N275EA, N480JK, N759VL, N22WS, N3851L, N336NA, N8088J). Increases: **0**. Excluded: N331SA $85,000 → $0 (placeholder).

### Offer (final, on air)
Report estimate $299,925 + engine ≈ $31,000 ≈ **$330,000** before the panel; sister ship $375,000 with ≈2,140 fewer airframe hours; three cuts; typical A36 cut ≈ 7% → **open around $330,000 (−8.3%)**, subject to pre-buy, engine paperwork, the GFC 500 directive record and a clean title (incl. the September loan-release paperwork).
