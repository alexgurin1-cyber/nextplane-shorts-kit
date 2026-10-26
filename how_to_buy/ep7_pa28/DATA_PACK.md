# How to Buy a Piper PA-28 — Episode 7 — DATA PACK

- Slot: Wednesday 2026-10-28 16:00:00Z (class: piston single; rotation next = Piper PA-28; Ep6 was high-performance).
- Built: 2026-10-26 (scheduled cloud run). Supabase project `uiprgookspqnvyumkyse`.
- Live report captured 2026-10-26 with `lib/report_capture.py` (exit 0, 44 sections) and the element-level `src/capture.py` (40 cards); report text re-captured once more and compared — the Flight Activity section was identical, the only diff was one competing listing's days-listed counter (15 → 16).
- Internal note: listing sources are kept here for verification only. Never name them on air.
- "Latest scrape" = `is_active and missed_scan_count = 0 and last_seen_at >= 2026-10-20` (both sources last ran 2026-10-25). US-registered (`registration ~ '^N[0-9]'`), US location, deduplicated by N-number (latest row).
- Junk asks (< $20,000: "$55"–"$125" rental-rate rows, a 1/5 partnership share) are excluded from every median. Piston asking prices are quoted as asks, never as sold prices.

## Hero aircraft
| Field | Value | Source |
|---|---|---|
| Tail | N8395H | `aircraft_listings.registration` |
| Listing | 260816051 (internal) | `listing_id` |
| Model / year | Piper PA-28-181 Archer II, 1981 | listing; registry year_mfr 1981, airworthiness 1981-04-29, mfr_mdl 7102807 (PA-28-181) |
| Serial | 28-8190249 | registry + report |
| Ask | **$180,000** (published price) | `asking_price_usd` |
| First ask | $220,000 | `original_asking_price_usd` + price history |
| TTAF / engine | **12,364 h / 174 h "SFRM"** (since factory rebuild) | listing row; description "Lycoming factory-rebuilt engine, 174 SFRM · 2021 paint, interior, engine" |
| Prop | 174 h SOH | listing |
| Avionics | Garmin G3X Touch (GDU 460), GTN 750Xi, GNC 255A, **GFC 500** autopilot, GI 275, GTX 345R, GMA 345 | `avionics_list` |
| Annual | "Due 3/2027" | `annual_due` (not used on air) |
| Damage flag | false; NTSB by tail or serial: 0 | listing; `ntsb_accidents` |
| Seller | **private individual**, Tallahassee FL (name kept off air and blurred) | `seller_name`, `seller_type` |
| Registered owner | a Florida LLC, Spring Hill FL, type_registrant 7, certificate **2020-06-01**, expires 2027-06-30, status V | `aircraft_master` |
| Active | first seen 2026-10-03, last seen 2026-10-25, missed scans 0 | listing row |
| Share / partnership ad | No | description checked |

## Price history (`aircraft_price_history`, listing 260816051)
| Date | From | To |
|---|---|---|
| 2026-10-09 | $220,000 | $180,000 (−$40,000, −18.2%) |
- One cut, 6 days after first listing. No jitter rows. Report Listing History card matches (✓).

## Fleet for sale — PA-28 family price ladder (latest scrape; median = "typical")
Total PA-28 family (excl. PA-32 Cherokee Six): **333 tails, 274 with a price ≥ $20,000** → on air "about 330 / about 270".
| Group (model-name match) | n | priced | Typical ask |
|---|---|---|---|
| Cherokee 140/150/160 | 76 | 70 | **$75,000** |
| Cherokee 180 | 55 | 45 | **$99,000** |
| Warrior (PA-28-161) | 45 | 27 | **$109,900** |
| Arrow (retractable, incl. Turbo) | 78 | 69 | **$128,000** |
| Archer / Archer II, 1974–1985 (clean list below, incl. hero) | — | 21 | **$138,950** |
| Dakota / Turbo Dakota | 13 | 11 | **$210,000** |
| Late-model Archer 2011+ | 6 | 4 | asks $362,900 (2011 LX) · $419,900 · $419,900 (2022 TX) · $435,000 (2024) — shown as the range |
| Archer III 1995–2006 | 4 | 3 | not on air (n=3) |
Grouping note: the category column is not used; groups are by model name. One placeholder listing (N12345, "Sample City") sits in the Cherokee 180 group; removing it does not move the median.

### Archer / Archer II, 1974–1985 — the 21 priced (US, latest scrape, one per tail)
| Tail | Year | Ask | TTAF | Engine (label) |
|---|---|---|---|---|
| N8074T | — | 80,000 | 9,122 | 1,478 SMOH |
| N2180Y | 1979 | 99,000 | 14,378 | 2,003 SMOH |
| N2226N | 1979 | 99,900 | 12,920 | 791 SMOH |
| N8401T | 1981 | 99,900 | 15,077 | 1,651 SMOH |
| N8138H | 1979 | 104,900 | 9,960 | 1,639 SMOH |
| N2816N | 1979 | 105,000 | 10,476 | 1,955 SMOH |
| N44800 | 1975 | 126,000 | 6,046 | 804 SMOH |
| N3323M | 1977 | 128,500 | 3,533 | 1,398 SMOH |
| N3016M | 1978 | 129,495 | 13,527 | 1,101 SMOH |
| N38356 | 1977 | 129,950 | 4,779 | 436 SMOH |
| N43511 | 1974 | 138,950 | 4,056 | 10 SMOH |
| N38840 | 1977 | 150,000 | 1,098 | — |
| N2435M | 1977 | 155,000 | 7,900 | 1,750 SOH |
| N5889V | 1977 | 155,000 | 7,700 | 900 SMOH |
| N38434 | 1977 | 164,900 | 4,903 | 1,545 SMOH |
| N3212Q | 1977 | 165,000 | 6,769 | 597 SFRM |
| N73TS | 1985 | 169,500 | 2,100 | 2,100 SNEW |
| N47564 | 1977 | 169,900 | 500 | 25 SMOH |
| N734X | 1974 | 179,000 | 2,007 | 35 SMOH |
| **N8395H** | 1981 | **180,000** | **12,364** | **174 SFRM** |
| N42982 | 1983 | 199,900 | 8,333 | 240 SMOH |
- Median of all 21 = **$138,950** (ladder). Interquartile range **$104,975–$164,925** → "half ask between about $105,000 and $165,000". Hero is the 2nd-highest ask; 4th-highest airframe hours.
- **High-hour group (TTAF ≥ 9,000, excl. hero), n=7:** 80,000 · 99,000 · 99,900 · 99,900 · 104,900 · 105,000 · 129,495 → **typical $99,900**; their median engine time 1,639 h.
- **Fresh-engine group (engine < 600 h, excl. hero), n=6:** 129,950 · 138,950 · 165,000 · 169,900 · 179,000 · 199,900 → **typical $167,450**; airframes 500–8,333 h.
- Hero vs high-hour typical: **+$80,100** ("about eighty thousand more").

## Valuation
| Source | Value | Notes |
|---|---|---|
| Report "Estimated Market Value" | **$124,900**, range $105,000–$160,000, "High · 88%" | Shown on air. "Adjusted value (your hours)" = $124,900, **net adjustment +$0** although 12,364 / 174 are prefilled (REPORT_ISSUES #1). Comp count not voiced (Alex 2026-10-19) and blurred. |
| Ask vs report estimate | +$55,100 (+44%) | On screen. |
| Our groups | high-hour typical $99,900; fresh-engine typical $167,450 | Voiced. |
| `model_price_forecasts` fair value | $125,671 (Oct 7) → $148,943 (Oct 14) → $134,172 (Oct 21) | Unstable; **not used**. |
| `model_price_forecasts` p_cut90 (v1.4, 2026-10-21) | **0.4605** (Oct 14: 0.538; Oct 7 at $220K: 0.78) | On air: "close to an even chance of another cut within ninety days". |

## Hours and the engine
- Report Market comparison: airframe market average 5,580 h (this 12,364, +6,784); engine market average 1,189 h (this 174, −1,015).
- Report True Cost per Mile: this aircraft $1.22/nm (174 h SMOH, 1,826 h to TBO 2,000) vs market average $1.44/nm.
- Report operating cost: engine overhaul accrual **$2,268 / 120 h = $18.90/h** (implies ~$37,800 per 2,000-h overhaul; not voiced).
- Engine value math (on air, labelled as an estimate): 1,639 (high-hour group median engine h) − 174 = **1,465 h** × $18.90 = **$27,689 ≈ $28K** → about a third of the $80,100 gap; remainder ≈ $52K = panel, autopilot, paint, interior (no NextPlane installed-cost data → not valued; "decide what those are worth to you").
- Engine age: listing says the engine (and paint/interior) are from 2021 → 174 h in ~5 years ≈ 35 h/yr.

## Flight activity (`aircraft_flight_intel`, fetched 2026-10-26 16:57Z by the first capture; identical on re-capture)
- 26 flights, 18.7 h airtime, 2024-12-08 → 2026-09-13, primary QSK, 4 airports.
- Report Flight Hours by Period: 3 mo 1 / ~0.3 h · 6 mo 5 / ~8.0 · 12 mo 13 / **~9.7** · 18 mo 19 / ~14.2 · 24 mo 25 / ~18.6.
- Monthly hours: 2024-12 2.9 · 2025-01 1.5 · 05 0.3 · 06 0.4 · 07 1.2 · 08 2.6 · 2026-02 0.3 · 03 1.4 · 05 2.8 · 06 4.9 · 09 0.3. Last 12 months (Nov 25–Oct 26) = 9.7 ✓.
- Not used: header "~13 hrs/yr" vs "10 hrs/yr" (REPORT_ISSUES #4).
- "Engines that sit tend to corrode inside" is voiced as a general maintenance read ("tend to"), not a measurement.

## Registration and ownership (`aircraft_master`, report)
- Owner a Florida LLC (Spring Hill), certificate 2020-06-01 → "over six years" (report: 6.4 yrs). Seller: private individual, Tallahassee FL.
- Liens: "No security conveyance indexed", window 2025-10-23 → 2026-10-23; not a title search. Engine/prop lien: not checked (needs engine S/N). Repossession: none. Deregistration/re-import: none.
- Report "Before you call": "Verify the registered owner matches the seller." → voiced.

## Airworthiness directives (report Airworthiness & Maintenance Program, N8395H)
- "11 ADs · 4 OEM · 4 regulatory · 0 life limits"; header "11 applicable FAA ADs · 6 conditional on installed parts".
- **2024-10-04** — inspect rear wing spar attachment bolt holes (plus forward-spar inspection if a discrepancy is found; report to FAA if corrective action). Header "Major AD · critical items: Wing spar AD inspection (one-time SB) · $2,500 · 5000 hrs". On air: "The report flags it past five thousand hours, at about twenty-five hundred dollars."
- **2024-14-03** — update Garmin GFC 500 autopilot software (applies: GFC 500 installed per listing).
- 2017-14-04 oil cooler hose inspections every 100 h (not voiced).
- Rival N42982 (1983 Archer II, $199,900) listing: "completed wing-spar eddy-current inspection/AD compliance". Hero listing (both source rows) does not mention the spar inspection.
- Compliance is not derivable from NextPlane data → "ask for proof of both".

## Service difficulty / safety
- Model (PA-28 family as matched by the report): 1,295 total, **496 in 5 years**, 85 in 12 months, 516 aircraft with reports; top parts bracket (101), skin (61), stiffener, channel. This aircraft: 0 since 1995. NTSB by tail or serial: 0.
- "PA-28s tend to fly hard in training, so a large count is expected" — phrased as a market read, not measured.

## Operating cost (report card)
120 h/yr: fuel $7,068 (120 × 9.5 gph × $6.20) · insurance $3,540 · hangar $3,973 · annual $2,365 · maintenance reserve $2,838 · engine accrual $2,268 · prop $270 · avionics $1,200 → **$23,522/yr, $196/h**. Hull value used: $180,000 (the ask).

## New price / depreciation
- Report: "MSRP data not available", "Insufficient market data" for value over time and replacement cost → **sections skipped** (no MSRP beat this week).

## Market behaviour — Archers (pre-2007), US, first listed 2026-04-26 → 2026-07-20, one per tail
Excluded: tails whose first-seen date is 2026-07-04 (the day the second source was first ingested in bulk, so "first seen" is not a listing date).
| Metric | Value |
|---|---|
| Cohort | **25** |
| Gone from the panel within 30 days | 4 (N9313K 27 d, N2562U 12, N3293Q 6, N8326C 4) — not proof of sale |
| Still listed past 90 days | **9** (N2380M, N44960, N38840, N405S, N8304L, N898DA, N44800, N32714, N8138H) |
| Net cut ≥ 1% | **8**: N405S −16.0%, N44960 −15.4%, N8268C −14.3%, N2380M −6.3%, N9313K −5.6%, N8138H −4.5%, N32714 −4.1%, N2229Q −2.5% |
| Median cut among cutters | **5.95% → "about six percent"** |
Excluded as noise: N5322X (raise then cut, net 0). Never quote a mean days-on-market.
- Hero cut 18.2% ≈ 3× the typical cut (on screen).

## Keep watching — Archers (pre-2007), 2026-10-12 → 2026-10-26
- New tails listed: **3** (N2180Y Oct 17, N3323M Oct 21, N2435M Oct 25). Price cuts: **4** (N8074T $89,500→$80,000 Oct 13; N73TS $179,000→$169,500 Oct 17; N47564 $179,900→$169,900 Oct 21; N38434 $169,900→$164,900 Oct 21). Increases: **0**.

## Seller (panel-built card; the report's seller card captured only its header)
- Private seller, Tallahassee FL; report: "Private seller · 23 days · private listings avg ~45 days · price reduced, originally $220,000"; "Before you call: use a title search + escrow; private sales have no dealer warranty; budget for an independent pre-buy."

## Offer logic (on air)
High-hour Archers typical $99,900; fresh-engine Archers typical $167,450 (with far fewer airframe hours); hero $180,000 with 12,364 h; seller already cut $40,000 in week one; p_cut90 ≈ 0.46 → **open around $160,000 (−11.1%)** — below the fresh-engine typical to account for airframe hours, above the high-hour typical plus the ≈$28K engine value — subject to pre-buy, the wing spar inspection record (and GFC 500 software AD), and the engine rebuild paperwork.

## Capture grant
`purchased_reports` row b5762dbb-5edd-4093-951a-d0dacc307b86 for N8395H on the capture account, amount 0, expires 2026-11-25.
