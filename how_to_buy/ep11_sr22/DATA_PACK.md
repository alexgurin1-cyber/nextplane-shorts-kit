# How to Buy a Cirrus SR22 — Episode 11 — DATA PACK

- Slot: Wednesday 2026-11-25 16:00:00Z (11:00 Eastern). Built 2026-11-23 (scheduled cloud run, no Mac).
- Model choice: CIRRUS FIRST (Alex 2026-11-16): SR22T (Ep10, done) → **SR22** → SR20. Ep1 (N2428E) was a legacy market-facts cut; SERIES_LOG allows the Cirrus-first order to revisit the SR22 as a product-demonstration episode, and the Ep10 memory names "Cirrus SR22 product-demo episode" as next. Single-engine piston (target segment 2026-11-03).
- Generation: **G3** (normally aspirated). Every comparison in the episode is G3 SR22 only (the report also values by generation: "G3 (2007–2012)").
- Format: PRODUCT DEMONSTRATION FIRST. Report/site frames on screen ≈ 311 s of 477 s (≈ 65%).
- Supabase project `uiprgookspqnvyumkyse`. Latest scrape: last_seen max 2026-11-23 05:28Z. Internal note: listing sources are kept out of every customer-facing surface.
- Tails already used in recent Shorts were avoided (N51CW, N56PE, N816PP, N25HW) as was Ep1's N2428E.

## Why this airplane
Screen: active, priced, N-registered, normally aspirated SR22s seen in the last 6 days, ranked by price cuts ≥1%. Candidates with ≥4 real cuts: N816PP (used in a Short), N2428E (Ep1), **N814LT** (4 real cuts, 221 days, −14.9%), N380SR (one real cut plus $120K/$125K jitter rows; ad says SALE PENDING), N850HL (small cuts), N322CW, N78EE, N336B, N238AR, N345JR.
N814LT has the most offer-changing report: ask 10.1% under the report's estimate (a "bargain" that the hours explain), 4 cuts in $20K steps, 221 days (5× the dealer's typical sale), a clear dealer pattern, flight data "Very light / inactive" (no tracked flights in 2025) and two live ads that disagree on price.

## Hero aircraft (verified row by row)
| Field | Value | Source |
|---|---|---|
| Tail | **N814LT** | `aircraft_listings` (two rows: 255013937 and tap_2454828 — same serial) |
| Model / year / serial | Cirrus SR22-G3 (GTS), **2010**, s/n 3568 | listing; registry year_mfr 2010, airworthiness 2010-02-17 |
| Ask | **$399,900** (listing 255013937, last seen 2026-11-23) | `asking_price_usd`. The second ad (tap_2454828, last seen 2026-11-21) still shows **$459,900** — report flags "Live ads disagree on price". |
| First ask | **$469,900** (2026-04-16) | `aircraft_price_history` |
| Airframe | **3,102 h** | both listing rows |
| Engine | **1,100 h** since overhaul (label SMOH on one ad, "TTSN" on the other — inconsistent label) | listing |
| Prop | 10 h ("new propeller" per ad) | listing |
| Panel | Cirrus Perspective (Garmin), GFC 700; A/C, FIKI, CAPS | ad text; report specs |
| Damage | ad: no damage; accident record by tail: **0** | `ntsb_accidents` |
| Service-difficulty reports on this tail | **0** | `sdr_reports.n_number` |
| Seller | **Dealer** (a large dealer, name masked), Ohio | listing seller_type dealer |
| Registered owner | a New York **LLC** (name masked), type_registrant 7, certificate **2017-09-07** (report shows Sep 6 in one place, Sep 7 in another), status V, expires 2027-09-30 | `aircraft_master` |
| Liens | **0** conveyance documents in window 2025-10-23 → 2026-11-20 | `conveyance_event` |
| Days listed | first seen 2026-04-16, last seen 2026-11-23 → **221 days** (report) | listing row |
| Share / partnership ad | No | description checked |

## Price history (`aircraft_price_history`, listing 255013937)
| Date | From | To | Note |
|---|---|---|---|
| 2026-05-17 / 05-18 | $469,900 → $250,000 → $469,900 | | jitter, reversed next day — ignored (report agrees) |
| 2026-06-02 | $469,900 | $459,900 | −$10,000 (−2.1%) |
| 2026-08-25 | $459,900 | $439,900 | −$20,000 (−4.3%) |
| 2026-09-05 | $439,900 | $419,900 | −$20,000 (−4.5%) |
| 2026-10-23 | $419,900 | $399,900 | −$20,000 (−4.8%) |
- Total −$70,000 (−14.9%), **4 cuts**. ✓ report.

## Report figures used on air (captured live 2026-11-23, capture exit 0, standing access)
| Section | Figure | Cross-check |
|---|---|---|
| Valuation (default) | Estimate **$444,900**; 19 comps; range **$429,900 – $475,000**; net **+$0**; G3 (2007–2012); ask at 21st percentile | Our check: 17 active N-registered G3-labelled SR22s (35 incl. foreign/G2-labelled), typical ask **$430,000** — report estimate ≈3% higher; comp count 19 not exactly reproducible (close). |
| After **Update valuation** (3,102 / 1,100 prefilled) | Adjusted **$435,987**; net **−$8,913** (airframe +1,273 h vs comp avg) | report-computed; shown as captured |
| Market signal comparables | 2009 G3 3,100 h **$385,000**; 2007 G3 3,111 h **$430,000** | N138CK, N777NL listing rows ✓ |
| Market comparison | airframe avg 1,807 h (248 listings); this 3,102 h | report |
| Cost per mile | $1.60/nm, 1,100 h SMOH, **900 h to TBO 2,000**; G3 market avg 1,051 h SMOH (34 peers) $1.57/nm | 2,000 − 1,100 = 900 ✓ |
| Flight activity (24 mo) | **12 flights, 11.8 h**, 0.5/month; Very light / inactive; last 3 mo 0; last 12 mo 3 flights 4.9 h | `aircraft_flight_intel` (fetched 2026-11-23 17:57Z, coverage complete): monthly flights 2024-11 2, 2024-12 7, 2026-01 1, 2026-03 1, 2026-06 1 → **no tracked flights in calendar 2025** ✓; hours sum 11.7 ✓ |
| Summary | No accident record; ownership 9.2 yrs; no security conveyance in window; CAPS 10-yr repack $17,000 flagged; 1 applicable AD; grade B+ | registry, conveyance ✓ |
| Listing history | first $469,900, 4 cuts, −$70,000 (−14.9%), last cut Oct 23; live ads disagree ($399,900 vs $459,900) | price history ✓ |
| Seller | dealer usually +8.3% vs market (n=48); this listing −10.1%; typical sale (all aircraft) 44 days; this one 221 | report-computed dealer stats (as of 2026-11-01), not independently reproducible; "33 other SR22s in stock" NOT used (our count: 17 active SR22 tails for this dealer) — masked on screen |
| Before You Call | "This unit has sat longer than their typical sale — ask why"; "ask to compare units side by side" | shown as captured (count masked) |
| Maintenance program | AD 2024-24-11 upper power lever inspection every 110 h; CAPS parachute repack every 10 yr, due Feb 2020, next Feb 2030 | report schedule model |
| Operating cost (120 h/yr) | **$35,125/yr, $293/h**; engine overhaul accrual $3,906 | shown as captured |
| Service problems | 0 on this aircraft | `sdr_reports` ✓ |

## G3 SR22 group (questions: "What do high-hour G3s ask?" and "Is that normal for a G3?") — G3 SR22 ONLY
All N-registered, normally aspirated SR22 G3 (2007–2012, model labelled G3) tails NextPlane tracked since April, merged by tail across sources (`src/cohort.py`). Excluded: N530ET ($120,000 placeholder), N725CP (relisted higher after cuts — ambiguous), N56AH (ad priced abroad; price moves daily with currency conversion). **n = 29.**
- Cut ≥1%: **11 of 29 (38%, "about four in ten")**; typical (median) cut **4.2%**, ≈ **$25,000**. N814LT −14.9% = **largest** of the 11.
- Days listed: N814LT 221 = **3rd longest of 29**. Listed >90 days: 10 of 29.
- High-hour G3s (2,800–3,120 h): N138CK 2009 3,100 h $385,000; N975MS 2008 2,800 h $395,000; **N814LT 2010 3,102 h $399,900**; N314CP 2008 3,110 h $419,900; N412CP 2009 3,120 h $429,900; N777NL 2007 3,111 h $430,000 → asks **$385,000–$430,000**, typical $409,900.
- Active G3s under 2,700 h: typical ask $449,900 at ≈1,600 h (n=12) — the market gap for hours is far larger than the report's −$8,913 adjustment.

## Offer logic (on air, grounded only in report figures; never called advice)
Estimate $444,900 (typical G3) → adjusted for hours $435,987 → but the report's own comparables show G3s with ~3,100 h asking $385,000–$430,000 → seller cuts in $20,000 steps; 221 days for sale vs the dealer's typical 44 → opening near **$380,000** = one of the seller's own $20,000 steps under the $399,900 ask (≈5% under). Subject to a pre-buy that looks hard at an airplane that sat, the parachute (CAPS) records, and a clean title. Negotiate from $399,900, not the stale $459,900 ad.
