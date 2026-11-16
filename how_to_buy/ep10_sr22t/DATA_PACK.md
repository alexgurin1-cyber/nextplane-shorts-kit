# How to Buy a Cirrus SR22T — Episode 10 — DATA PACK

- Slot: Wednesday 2026-11-18 16:00:00Z. Built 2026-11-16 (scheduled cloud run, no Mac).
- Model choice: CIRRUS FIRST (Alex 2026-11-16): SR22T → SR22 → SR20. SERIES_LOG shows Ep1 covered the SR22 (N2428E), not the SR22T, so Ep10 = **Cirrus SR22T**. Single-engine piston (target segment 2026-11-03).
- Generation: **G6** (2017–2023). Every comparison in the episode is G6 SR22T only (the report also values by generation).
- Format: PRODUCT DEMONSTRATION FIRST (Alex 2026-11-16). Report frames on screen ≈ 297 s of 421 s (≈ 70%).
- Supabase project `uiprgookspqnvyumkyse`. Latest scrape: one source last seen 2026-11-13 08:52Z, the other 2026-11-15. Internal note: listing sources are kept out of every customer-facing surface.

## Why this airplane
Candidate screen (active, priced, N-registered SR22Ts with ≥ 2 cuts or ≥ 150 days): only **N657CB** (7 recorded reductions, 179 days) and N99CP (2 cuts, earlier history polluted by a $400,000 jitter row) qualified. N657CB also has the largest offer-changing gap: ask vs the report's hours-adjusted value (+$19,526), 6 report-counted cuts, 179 days for sale, a clear seller pattern (≈ $10K a month), and the flight data says "likely trainer" while the ad says "one owner, hangar kept".

## Hero aircraft (verified row by row)
| Field | Value | Source |
|---|---|---|
| Tail | **N657CB** | `aircraft_listings.registration` (listing tap_2456198, single row) |
| Model / year / serial | Cirrus SR22T-G6 GTS (ad: "Platinum Edition"), **2023**, s/n 9069 | listing; registry year_mfr 2023, airworthiness 2023-02-22, mfr_mdl 2130004 |
| Ask | **$819,000** (published) | `asking_price_usd` |
| First ask | **$899,999** (2026-05-21) | `aircraft_price_history` (note: `original_asking_price_usd` holds a stale $844,000) |
| Airframe / engine / prop | **1,678 h** each (label "HOURS"; original engine) | listing |
| Panel | Perspective Touch+ (Garmin), GFC 700 + ESP, dual ADAHRS, ADS-B in/out, FS510; A/C, FIKI, CAPS | `avionics_list`; report specs |
| Damage | "No damage history"; accident record by tail: **0** | listing; `ntsb_accidents` |
| Service-difficulty reports on this tail | **0** | `sdr_reports.n_number` |
| Seller | **Private** owner (a person; name masked), Fort Lauderdale FL | listing; report |
| Registered owner | a Florida **LLC** (name masked), type_registrant 7, certificate **2023-05-17**, status V, expires 2030-05-31 | `aircraft_master` |
| Lien | Security agreement (S/A) recorded **2026-09-03**, no release | `conveyance_event` (2 rows, one with blank doc_id = the same document) |
| Days listed | first seen 2026-05-21, last seen 2026-11-13, missed scans 0 → **179 days** (report) | listing row |
| Share / partnership ad | No | description checked |

## Price history (`aircraft_price_history`, listing tap_2456198)
| Date | From | To | Change |
|---|---|---|---|
| 2026-05-25 | $899,999 | $889,999 | −$10,000 (−1.1%) |
| 2026-06-17 | $889,999 | $869,000 | −$20,999 (−2.4%) |
| 2026-07-17 | $869,000 | $859,000 | −$10,000 (−1.2%) |
| 2026-08-13 | $859,000 | $849,000 | −$10,000 (−1.2%) |
| 2026-08-25 | $849,000 | $844,000 | −$5,000 (−0.6%) — under 1%, the report ignores it as noise |
| 2026-09-21 | $844,000 | $834,000 | −$10,000 (−1.2%) |
| 2026-10-09 | $834,000 | $819,000 | −$15,000 (−1.8%) |
- Total −$80,999 (−9.0%). Report counts **6 cuts** (rule: moves under 1% ignored). On air: "six cuts … about one a month … most were ten thousand dollars".

## Report figures used on air (captured 2026-11-16, cross-checked)
| Section | Figure | Cross-check |
|---|---|---|
| Valuation (default) | Estimate **$849,900**; range (25th–75th) **$794,200 – $892,450**; net adjustment **+$0**; G6 (2017–2023) | Our own check: 30 deduplicated active G6 SR22Ts (one source, 2026-11-13) have a typical (median) ask of **$798,750** (range $599,900–$949,900), so the report's default estimate sits high; the report's own hours-adjusted value ($799,474) lands on that median. Comp count "191" not reproducible → blurred. Logged in REPORT_ISSUES. |
| Valuation after **Update valuation** (hours 1,678/1,678 prefilled) | Adjusted **$799,474**; net **−$50,426** = airframe −$7,931 + engine near overhaul −$42,495 | Report-computed; shown as captured |
| Cost per mile | This aircraft $2.72/nm (1,678 h, **322 h to overhaul**, overhaul due at 2,000 h); G6 market $1.56/nm (**727 h** avg engine time, 113 for-sale peers) | 2,000 − 1,678 = 322 ✓ |
| Flight activity (24 months) | **959 flights, 826.8 h, 40.2/month, 1.0 h average**, 40 airports, 41% local | `aircraft_flight_intel` row (fetched 2026-11-16 17:57Z, coverage complete, 24 months) ✓; second capture identical ✓ |
| Top routes | home → 11 nm (58 flights), home → 36 nm (36 flights) | report table (airport codes not voiced) |
| Flight hours by period | last 12 months ~420.3 h (461 flights); last 3 months ~40.6 h (32) | monthly_hours: Jun 61.8, Jul 28.3, Aug 14.7, Sep —, Oct 23.2 ✓ "slowed after June" |
| Summary | No accident record; ownership 3.5 yrs (cert. 2023-05-17); security conveyance, no release; CAPS 10-year repack $17,000 flagged; use type "Likely trainer"; 1 applicable AD | registry, conveyance_event ✓ |
| Seller | Private seller; 180 days on market; originally $899,999 | ✓ |
| Before You Call | verify registered owner = seller; title search + escrow, no dealer warranty; independent pre-buy | shown as captured |
| Operating cost (120 h/yr) | **$40,364/yr, $336/h**; engine overhaul accrual $3,969 | shown as captured |
| Service problems | 0 on this aircraft | `sdr_reports` ✓ |

## G6 SR22T cohort (question: "Is that normal for this airplane?") — G6 SR22T ONLY
N-registered SR22T G6 (2017–2023) listings first seen 2026-04-20 … 2026-08-15, merged by tail across sources (`src/cohort.py`). Excluded: N541BA ($120,000 placeholder), N3744U (no price), N526CW (ask raised $775K→$875K, likely a correction). **n = 87.**
- Cut their price ≥ 1%: **43 of 87 (49%)**; typical (median) cut **3.7%**, ≈ **$30,000**.
- Listed more than 90 days: **46 of 87 (53%)**. Still for sale today: 28.
- Left the market within 30 days: **10 of 87 (11%)** (an ad leaving is not proof of a sale; voiced as "left the market").
- N657CB's −9.0% is the **5th-largest cut of the 43**.

## Same-generation context (not voiced, internal)
Active G6 SR22Ts with similar hours (1,300–2,000 h) ask $649,000–$724,900 but are 2020–2021 builds (N465TX, N585TX, N211RV, N143RS). Active 2022–2023 G6 SR22Ts all show 135–600 h and ask $849,900–$949,900. N657CB is the only 2022–2023 G6 SR22T for sale with high hours.

## Offer logic (on air, grounded only in report figures; never called advice)
Estimate $849,900 (typical G6) → adjusted for this airplane's hours $799,474 → report's typical range starts $794,200 → 179 days for sale, 6 cuts about monthly → opening near **$795,000** ≈ 2.9% under the $819,000 ask, close to the typical G6 cut (3.7%). Subject to pre-buy inspection, engine logbooks, clean title. Budget for the overhaul (322 h left).
