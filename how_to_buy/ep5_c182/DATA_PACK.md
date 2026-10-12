# How to Buy a Cessna 182 Skylane — Episode 5 — DATA PACK

- Slot: Wednesday 2026-10-14 16:00:00Z (class: piston single; rotation next = Cessna 182).
- Built: 2026-10-12 (scheduled cloud run). Supabase project `uiprgookspqnvyumkyse`.
- The live report was captured twice on 2026-10-12 (`lib/report_capture.py`, exit 0, 44 sections; element-level `src/capture.py`) and cross-checked; see `REPORT_ISSUES.md`. Every on-screen number traces to this pack or to a verified report section.
- Internal note: listing sources are kept here for verification only. Never name them on air.
- "Latest scrape" = `is_active and missed_scan_count = 0 and last_seen_at >= 2026-10-09` (one source last ran in full on Oct 11, the other on Oct 9).
- Family = Cessna `182 SKYLANE`, `182N`–`182T` (non-turbo, fixed gear), US, N-registered, deduplicated by N-number. Excluded: N12345 (placeholder tail), N52761 (King Katmai conversion carrying model year 2025), N700DL (1981 turbo mis-labelled 2001), N20813 (price $0), and as price outliers N2439B / N9036B (2001 and 2010 182T at $150,000, likely placeholders). Share or partnership ads: none found.

## Hero aircraft
| Field | Value | Source |
|---|---|---|
| Tail | N23383 | `aircraft_listings.registration` |
| Listing | 260073919 (internal) | `listing_id` |
| Model / year | Cessna 182S Skylane, 1998 | listing; registry year_mfr 1998, airworthiness 1998-12-16 |
| Serial | 18280406 | listing + registry match |
| Ask | **$279,000** (published price) | `asking_price_usd` |
| First ask | $329,000 | `original_asking_price_usd` + price history |
| TTAF / engine / prop | 1,699.3 / 1,699.3 SNEW / 967.8 SMOH | listing row. Engine time = airframe time, label "since new": original engine per the listing. |
| Engine | Lycoming IO-540-AB1A5, 230 hp, TBO 2,000 h / 12 yr (recommended) | report spec + maintenance program |
| Avionics | Aspen, Garmin GTN 750, GPSMAP 496, GTX 35R (ADS-B Out), KAP 140 autopilot | `avionics_summary`, `avionics_list` |
| Annual | "Fresh annual inspection 09/01/26" | `annual_due` |
| Damage flag | false; no NTSB record by tail or serial | listing row; `ntsb_accidents` (0 rows) |
| Seller | private individual, Erwin, NC (name kept off air) | `seller_name`, `seller_type` |
| Active | status active, first seen 2026-09-05, last seen 2026-10-11, missed scans 0 | listing row |
| Listing useful load | 3,100 lb (this is the max gross weight; not used) | listing row; report performance table shows 1,203 lb |

## Price history (`aircraft_price_history`, listing 260073919)
| Date | From | To |
|---|---|---|
| 2026-09-13 | $329,000 | $319,000 |
| 2026-09-17 | $319,000 | $309,000 |
| 2026-09-19 | $309,000 | $299,000 |
| 2026-10-03 | $299,000 | $289,000 |
| 2026-10-06 | $289,000 | $279,000 |
- 5 cuts of $10,000 each; −$50,000 = −15.2% in 31 days (Sep 5 → Oct 6). No jitter rows. 39 days listed at publish.

## Fleet for sale and price ladder (latest scrape; median = "typical")
| Era | n listed | n priced | Median ask |
|---|---|---|---|
| 1956–1971 | 21 | 19 | $145,000 |
| 1972–1976 (182P) | 32 | 29 | $179,900 |
| 1977–1986 (182Q/R) | 36 | 30 | $227,450 |
| 1997–2000 (182S) | 17 | 16 | **$319,950** |
| 2001–2015 (182T) | 28 | 17 | $359,900 |
| 2016–2027 (182T) | 16 | 12 | $649,250 |
| **All** | **150** | **123** | $240,000 |
- 1987–1996: Cessna built no new piston singles (historical; restart model = 182S from 1997).

### The 16 priced 182S asks (active)
224,500 · 240,000 · **279,000 (hero)** · 289,900 · 300,000 · 309,000 · 309,900 · 314,900 · 325,000 · 339,500 · 339,900 · 349,000 · 350,000 · 369,000 · 399,000 · 494,900. Median $319,950; the hero is 3rd lowest.

## Valuation
| Source | Value | Notes |
|---|---|---|
| Report "Estimated Market Value" (`get_aircraft_valuation('182S',1998,'CESSNA')`) | **$319,000**; range $299,700–$354,750 on screen; "71 active listings"; High 88% | RPC returns 53 comp rows incl. duplicates, two non-US and stale listings (REPORT_ISSUES #2). The "71 active listings" tile is blurred on screen. |
| Our recompute: 16 active priced 182S, one per tail | **$319,950** median, IQR ≈ $297,500–$349,250 | Within 0.3% of the report → estimate used on air. |
| Ask vs estimate | −$40,000 = **−12.5%** | below the 25th percentile |
| `model_price_forecasts` v1.4 (2026-10-07) | fair value **$289,524**; p_cut30 0.31; **p_cut90 0.75** | On air: "lands in the same place"; "about a three in four chance of another cut within ninety days". |

### Engine adjustment (on air)
- Report cost per mile (`report_cost_per_mile`): spec CES_182S_T, TBO 2,000 h, overhaul **$65,000**, 140 kt, 13 gph. Subject 1,699 h SMOH, **301 h** remaining → **$2.67/nm**; market (113 for-sale peers, avg 805 h SMOH, **1,195 h** remaining) → **$1.51/nm**.
- 1,195 − 301 = 894 h × ($65,000 ÷ 2,000 = $32.50/h) = **$29,055**.
- $319,000 − $29,055 = **$289,945** ("about two hundred ninety thousand").
- 182S listings since Apr 12 with engine ≥ 1,400 h (excluding hero; last ask, one per tail): N86RP 1999 1,822 h $240,000 (active) · N251ME 2000 1,673 h $274,900 · N2380Y 1999 1,499 h $282,000 · N821DH 2000 1,470 h $299,900 · N926WB 2000 1,598 h $309,900 → median **$282,000** (n=5).

### Overhaul math
- $279,000 + $65,000 = **$344,000**. N2449C, 1999 182S, 0 h since a fresh overhaul (1,941 TT), asks **$339,900** (active).

## Registration and ownership (`aircraft_master`, report)
- Registered owner: a North Carolina corporation (type_registrant 3), Knightdale, NC. Certificate **2023-04-28**, expires 2030-04-30, status V. On air: "a North Carolina company" only (name blurred).
- Seller on the listing is a private individual (different name from the registered owner) → "confirm the seller can sign for the company".
- No ownership transfers observed since 2026-05-09. Liens: "No security conveyance indexed", FAA document window 2025-10-23 → 2026-10-09; not a title search. Repossession 0, deregistration/re-import none.

## Flight activity (`aircraft_flight_intel`, fetched 2026-10-12 16:59Z by the first capture)
- 91 flights, 43.6 h airtime, 2024-10-23 → 2026-09-01, home FAY.
- Monthly hours: 2024-10 0.5 · 11 5.9 · 12 2.7 · 2025-01 6.0 · 02 5.9 · 03 11.7 · 05 3.1 · 06 0.3 · 08 0.3 · 11 1.4 · 2026-04 0.9 · 06 0.9 · 08 0.6 · 09 3.5.
- Nov 2024–Mar 2025 = **32.2 h**; Apr 2025–Sep 2026 = **11.0 h** (on air "about eleven hours").
- Lifetime pace: 1,699 h in ~28 years ≈ 60 h/yr (not used on air).
- Not used: "Weekend Flyer" label, "~43 hrs/yr" vs "23 hrs/yr", period-card hours, route distances (REPORT_ISSUES #6–#7). The monthly chart on screen is flights per month and is labelled so.

## Airworthiness directives (`aircraft_ad_matches('N23383')`)
11 matched, 7 conditional (report header "11 applicable FAA ADs · 7 conditional on installed parts" ✓). Unconditional for every 182S: **2000-04-01** and **2013-11-11** (oil pressure switch), **2007-05-10** (crew seat lock), **98-01-14** (exhaust mufflers). Compliance is not derivable from FAA data.

## Service difficulty / safety
- SDR on this aircraft: 1 (2000-03-27, autopilot roll servo found defective during service-bulletin compliance). Model: 120 total, 0 in 5 years. NTSB by tail or serial: 0.

## Operating cost (`aircraft_operating_cost('N23383')`, matches the report)
120 h/yr: fuel $9,300 · insurance $4,827 · hangar $3,973 · annual $2,365 · maintenance $2,838 · engine accrual $2,898 · prop $270 · avionics $1,200 → **$27,671/yr, $231/h**. 301 h ÷ 120 h/yr ≈ 2.5 years to TBO.

## Market behaviour — Skylane family, first listed 2026-04-26 → 2026-07-07, deduplicated by tail
| Metric | Value |
|---|---|
| Cohort | 143 |
| Left the panel within 30 days | 22 |
| Still listed past 90 days | 82 |
| Cut at least once (cuts > 30% excluded as jitter) | **54 (38%, "about four in ten")** |
| Median total cut among cutters | **6.7%** ("under seven percent") |
Never quote a mean days-on-market.

## Keep watching — Skylane family, 2026-09-28 → 2026-10-12
- New tails listed: **14**. Price cuts: **22** (19 tails). Price increases: **2**.

## Offer logic (on air)
Engine-adjusted value ≈ $290,000 → closest match N86RP (1999, original engine 1,822 h) asks $240,000 after 100+ days → seller's own pattern is $10,000 steps → model p_cut90 0.75 → **open around $265,000 (−5.0% vs ask)**, subject to pre-buy, oil analysis and borescope; if the engine fails, ask for the overhaul (~$65,000) off or walk away.

## Capture grant
`purchased_reports` row 3ca46d11-4310-4b81-9ca6-779f3962bf39 for N23383 on the capture account, amount 0, expires 2026-11-11.
