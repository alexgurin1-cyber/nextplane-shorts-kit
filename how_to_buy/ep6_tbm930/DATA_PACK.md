# How to Buy a TBM 930 — Episode 6 — DATA PACK

- Slot: Wednesday 2026-10-21 16:00:00Z (class: high-performance; rotation next = Daher TBM 900-series).
- Built: 2026-10-19 (scheduled cloud run). Supabase project `uiprgookspqnvyumkyse`.
- The live report was captured on 2026-10-19 with `lib/report_capture.py` twice (exit 0; 43 and 45 sections) and with the element-level `src/capture.py` twice. The two element captures' report text is identical, including Flight Activity. Every on-screen number traces to this pack or to a verified report section; see `REPORT_ISSUES.md` for what was corrected or kept off screen.
- Internal note: listing sources are kept here for verification only. Never name them on air.
- "Latest scrape" = `is_active and missed_scan_count = 0 and last_seen_at >= 2026-10-15` (one source ran in full on Oct 19, the other on Oct 17).
- Family = Daher/SOCATA `TBM 700*`, `TBM 850`, `TBM 900`, `910`, `930`, `940`, `960`; US, N-registered, deduplicated by N-number. Excluded: the 1945 TBM-3 Avenger warbird (N7226C, not a Daher), N37ER (2023 TBM 960 at $499,000 — placeholder price), foreign-registered rows, and rows with missed scans.
- Turboprop price guardrail: no fleet sold medians are quoted. Every ask quoted on air was checked on its own listing row; small groups (n=2) are shown as the individual asks, not as a median.

## Hero aircraft
| Field | Value | Source |
|---|---|---|
| Tail | N24MY | `aircraft_listings.registration` |
| Listing | 259248377 (internal) | `listing_id` |
| Model / year | Daher TBM 930, 2016 | listing; registry year_mfr 2016, airworthiness 2016-10-10, FAA model "TBM 700" family (mfr_mdl 8682000) |
| Serial | 1143 | registry + report |
| Ask | **$3,295,000** (published price) | `asking_price_usd` |
| First ask | $3,395,000 | `original_asking_price_usd` + price history |
| TTAF / engine | **2,218 h / 1,650 h, label "SNEW"** | listing row. Engine is 568 h younger than the airframe since new → on air: "most likely not the original engine — ask why". The listing does not say. |
| Engine | P&WC PT6A-66D, 850 hp | report specs + registry |
| Avionics | Garmin G3000 "updated to current platform w/ Synthetic Vision" | `avionics_summary` |
| Annual | "Last Annual Inspection: May 2026" | `annual_due` (not used on air) |
| Damage flag | false; no NTSB record by tail or serial | listing row; `ntsb_accidents` (0) |
| Seller | dealer, Bakersfield, CA (business name kept off air) | `seller_name`, `seller_type` |
| Active | status active, first seen 2026-08-13, last seen 2026-10-19, missed scans 0 | listing row |
| Share / partnership ad | No | description checked |

## Price history (`aircraft_price_history`, listing 259248377)
| Date | From | To |
|---|---|---|
| 2026-09-09 | $3,395,000 | $3,295,000 (−$100,000, −2.95%) |
- One cut. No jitter rows. 67 days listed on Oct 19 (69 at publish). Report Listing History card matches (✓, amounts present this time).

## Fleet for sale and price ladder (latest scrape; median = "typical")
| Generation | n listed | n priced | Asks | Median / shown |
|---|---|---|---|---|
| TBM 700 (1994–2005 listed) | 12 | 9 | 1,250,000 · 1,350,000 · 1,650,000 · 1,690,000 · 1,700,000 · 1,945,000 · 1,975,000 · 1,995,000 · 2,200,000 | **$1,700,000** |
| TBM 850 (2006–2013) | 10 | 7 | 1,725,000 · 2,375,000 · 2,399,000 · 2,449,900 · 2,495,000 · 2,550,000 · 2,750,000 | **$2,449,900** |
| TBM 900 / 910 / 930 (2015–2019 listed) | 10 | 6 | 2,895,000 (2015 900) · 3,295,000 (hero) · 3,300,000 (2018 910) · 3,349,000 · 3,400,000 · 3,400,000 (2019 910) | **$3,324,500** |
| TBM 940 (2020–2021) | 4 | 2 | 3,695,000 · 4,200,000 | shown as the two asks |
| TBM 960 (2022–2025) | 8 | 2 (+1 excluded) | 4,925,000 · 5,225,000 | shown as the two asks |
| **All** | **44** | **26** | | |

### Shortlist — the four 2016 TBM 930s for sale
| Tail | Ask | TTAF | Engine | Notes |
|---|---|---|---|---|
| **N24MY** | **$3,295,000** | 2,218 | 1,650 SNEW | hero |
| N232MA | $3,349,000 | 1,870 | 1,870 SNEW | listing: "just came out of a recent Hot Section Inspection"; cut $3,399,000 → $3,349,000 on 2026-10-06 |
| N900RJ | $3,400,000 | 1,800 | 1,800 SNEW | first seen 2026-05-13 (~159 days) |
| N667CA | no price | 1,863 | 1,863 | private |

## Valuation
| Source | Value | Notes |
|---|---|---|
| Report "Estimated Market Value" | **$3,444,000**, range $3,361,750–$3,531,225, "6 active listings", Low · 45% | Shown on air. Of its six listings, N11MA (2018, located in Germany, last seen Sep 1), N813GG (2017, last seen May 28) and N930SR (2017, last seen Jun 2) are **no longer in the latest scan** (REPORT_ISSUES #1). |
| `get_aircraft_valuation('TBM 930',2016,'DAHER')` via SQL | $3,374,500 (median of the same six) | Differs from the report's $3,444,000 (REPORT_ISSUES #2). Not used on air. |
| **Our recompute: 2016–2019 TBM 910/930 for sale today, one per tail (5)** | 3,295,000 · 3,300,000 · 3,349,000 · 3,400,000 · 3,400,000 → **$3,349,000** | Used on air as "typical ask today". Hero −$54,000 (−1.6%). |
| Ask vs report estimate | −$149,000 (−4.3%) | not voiced |
| `model_price_forecasts` fair value | $2,522,092 → $3,287,460 → $3,033,427 → $3,565,925 → $2,853,088 across five September–October scorings | Unstable for turboprops; **not used**. |
| `model_price_forecasts` p_cut90 (v1.4, 2026-10-14) | **0.256** (earlier 0.27–0.43) | On air: "about a one in four chance of another cut within ninety days". |

**Episode verdict:** fairly priced at the low end of the market; the discount is explained by the highest airframe hours of the three priced 2016 930s and an engine hot section inspection that is close; clean history.

## Hours and the engine
- Report "Market comparison": airframe market average 1,963 h across 3 TBM 930 listings; this aircraft 2,218 h (+255). Engine market average 1,773; this aircraft 1,650 (card label says "SMOH"; the listing says SNEW — REPORT_ISSUES #6).
- Report maintenance program (Airworthiness & Maintenance Program card): **HSI — Hot section inspection, PT6A-66D, every 1,800 h, recommended**, projected Dec 2027 at the report's default 130 h/yr. 1,800 − 1,650 = **~150 h remain** (as of the listing's hours).
- Tracked pace: 256 h last 12 months / 64.6 h last 3 months ≈ 21 h/month → 150 ÷ 21 ≈ **7 months** (on air "about seven months", labelled "at this pace").
- HSI cost: no reliable figure in NextPlane data → none quoted; "get a quote from a TBM shop".
- Engine TBO: report shows 3,600 h; `component_intervals` PT6A-66D row is low-confidence (calendar 144 months only, notes "industry figure 3,500 h — confirm"). **TBO not used on air.** The program's "engine overhaul already due Feb 2026 (12-yr)" line is driven by that unverified row (REPORT_ISSUES #8) and is not shown.

## Registration and ownership (`aircraft_master`, report)
- Registered owner: a Texas LLC (type_registrant 7), Odessa, TX. Certificate **2023-03-10**, expires 2030-03-31, status V. On air: "a Texas company" only (name blurred).
- Listing by a California dealer (Bakersfield). ADS-B home base BFL.
- Liens: "No security conveyance indexed", window 2025-10-23 → 2026-10-16; not a title search. Engine/prop lien: "Not checked — enter engine S/N". Repossession none; deregistration/re-import none.

## Flight activity (`aircraft_flight_intel`, fetched 2026-10-19 16:58Z by the first capture; identical in the second capture)
- 227 flights, 435.3 h airtime, 2024-10-31 → 2026-10-11, primary BFL, 31 airports, 2% local, 9.6 flights/month.
- Report Flight Hours by Period: 3 mo 31 / 64.6 h; 6 mo 72 / 152.0; 12 mo 138 / ~255.9; 18 mo 195 / ~387.5; 24 mo 226 / ~432.4.
- Monthly hours (Nov 2025 → Oct 2026): 16.9 · 21.5 · 21.9 · 28.0 · 15.6 · (Apr 0) · 39.5 · 28.8 · 19.1 · 31.7 · 28.1 · 4.8 = 256.0 ✓.
- Top airports: BFL 160 visits, ODT (Odessa TX) 126. Top route BFL → ODT 42 flights, ODT → BFL 39.
- Not used: route distances (impossible values), "est. annual hours 221" vs "~230 hrs/yr" vs "~255.9" (REPORT_ISSUES #4–#5), "Pricing Impact −5%".

## Airworthiness directives (`aircraft_ad_matches('N24MY')`)
17 matched, 6 flagged conditional (report header "17 applicable FAA ADs · 6 conditional on installed parts" ✓). FAA model family = TBM 700 (the 900-series is certified under the TBM 700 type certificate; the report's AD card shows "SOCATA TBM 700").
- Repeating every 100 h: **2007-03-17** (frames C18 BIS / C19 inspection), **2008-19-06** (pulley drive / alternator-compressor support welds). 2007-04-13 MLG forging repeats every 175 landings once past 1,750 landings.
- Engine: **2024-04-51** (adopts Transport Canada Emergency AD CF-2024-05, second-stage power turbine blades, PT6A-66D); conditional — engine serial not in the FAA registry; verify against the engine logbook.
- Compliance is not derivable from FAA data.

## Service difficulty / safety
- SDR on this aircraft: 0 (since 1995). Model: 131 total, **2 in 5 years**, 0 in 12 months. NTSB by tail or serial: 0.

## Operating cost (report card = `aircraft_operating_cost`)
200 h/yr: fuel $61,200 (200 h × 51.0 gph × $6.00 — "fuel burn estimated from engine power") · insurance $40,245 · hangar $10,539 · annual $9,368 · maintenance reserve $21,078 · engine accrual $25,972 · prop $800 · avionics $3,000 → **$172,202/yr, $861/h**.

## New price (`model_msrp_history`, report "Original new price")
| | Value | Confidence |
|---|---|---|
| 2016 TBM 930 base / typically equipped | $4,100,000 / **$4,200,000** | sourced |
| Ask ÷ equipped | 0.7845 → "about twenty-two percent below new" (report: 21.6% off equipped) | |
| 2025 TBM 960 typically equipped | **$5,525,144** | sourced (BCA 2025 PPH) — "about five and a half million" |
- "Rising new prices tend to hold up used ones" is phrased as a market read, not a measurement.

## Market behaviour — TBM 700/850/900-series, US, first listed 2026-04-26 → 2026-07-20, deduplicated by tail
| Metric | Value |
|---|---|
| Cohort | **26** |
| Left the panel within 30 days | 3 |
| Still listed past 90 days | **14** ("more than half") |
| Cut ≥ 1% (net) | **4**: N4920Y −6.3%, N944EA −2.6%, N850VV −2.0%, N512DM −1.1% |
| Median total cut among cutters | **2.3%** ("about two percent") |
Excluded as noise: N210CL (−0.26%), N772KH (raise then cut; net +1.6%). Never quote a mean days-on-market.

## Keep watching — same family, 2026-10-05 → 2026-10-19
- New tails listed: **5** (N788RR, N700HL, N850LH, N850MR, N960JV). Price cuts: **3** (N232MA −$50,000 Oct 6, N442DS −$45,000 Oct 6, N944MD −$100,000 Oct 19). Increases: **0**.

## Seller (panel-built card; the report's seller section is thin and its capture was partial)
- Dealer listing, Bakersfield, CA, first seen 2026-08-13. Report: "dealer not yet profiled in the NextPlane Dealer Directory". Owner on the registry is a Texas company → on air: "ask whether the dealer owns it or sells it for the owner".

## Offer logic (on air)
Typical ask of the five similar 910/930s for sale today $3,349,000 → hero asks $3,295,000 but has the most hours (2,218 vs 1,870/1,800) and ~150 h to the hot section inspection → the rival with a fresh HSI (N232MA) just cut $50,000 → this seller's one cut was $100,000 → model p_cut90 ≈ 0.26 → **open around $3,200,000 (−2.9% vs ask, roughly one more step the size of the first)**, subject to pre-buy, current hours in writing and the engine logbook; seller completes the HSI before closing or its quoted cost comes off the price.

## Capture grant
`purchased_reports` row b62abcfc-0c71-4816-a1ca-011b78b3806d for N24MY on the capture account, amount 0, expires 2026-11-18.
