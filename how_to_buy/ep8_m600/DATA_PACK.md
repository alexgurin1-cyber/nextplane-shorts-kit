# How to Buy a Piper M600 — Episode 8 — DATA PACK

- Slot: Wednesday 2026-11-04 16:00:00Z (class: high-performance; rotation next = Piper M500/M600; Ep7 was a piston single).
- Built: 2026-11-02 (scheduled cloud run). Supabase project `uiprgookspqnvyumkyse`.
- **Live report NOT captured.** `lib/report_capture.py N665WA` exited **3 (report locked)**: the per-tail capture grant (`purchased_reports` insert for the capture account) was blocked by this run's permission check, so the capture account had no access to the N665WA report. No video was produced or uploaded. Every number below comes from Supabase; report-section numbers must be re-checked against the live report once it is captured.
- Internal note: listing sources are kept here for verification only. Never name them on air.
- "Latest scrape" = `is_active and missed_scan_count = 0 and last_seen_at >= 2026-10-27` (all sources last ran 2026-11-01). Family = `pa46_group(make, model) = 'M-CLASS-TP'` (Meridian, M500, M600, M600 SLS, M700).
- Turboprop guardrail: fleet figures below are built from individually checked listing rows (one per tail, US-registered), and are spoken as asks, never as sold prices.

## Hero aircraft
| Field | Value | Source |
|---|---|---|
| Tail | **N665WA** | `aircraft_listings.registration` |
| Listing | 260277255 (internal) | `listing_id` |
| Model / year | Piper M600 SLS (PA-46-600TP), 2021 | listing; registry year_mfr 2021, airworthiness 2021-03-26, mfr_mdl 7104650 |
| Serial | 4698165 | listing + registry |
| Ask | **$2,875,000** (published price) | `asking_price_usd` |
| First ask | $2,990,000 | `original_asking_price_usd` + price history |
| Airframe / engine | **1,010 h / 1,010 h since new** (original engine) | `total_time_airframe`, `engine_time_smoh` label SNEW |
| Prop | 1,010 h | `prop_time` |
| Avionics | Garmin G3000, GFC 700 autopilot, dual 12-inch displays, GTX 345R | `avionics_summary` |
| Annual | **"Current thru 12/2025"** — as printed, the listed annual date has passed | `annual_due` |
| Damage flag | false; accident record by tail or serial: 0; service-difficulty reports by tail or serial: 0 | listing; `ntsb_accidents`; `sdr_reports` |
| Seller | dealer, Topeka KS (business name kept internal) | `seller_type`, `location_*` |
| Registered owner | a Washington DC LLC, type_registrant 7, certificate **2025-01-13**, expires 2032-01-31, status V | `aircraft_master` |
| Ownership events | 2026-08-26 "registration_removed" + 2026-08-27 "new_registration", same owner and same certificate date → registry sync glitch, **not** an ownership change | `aircraft_transactions` |
| Active | first seen 2026-09-11, last seen 2026-11-01, missed scans 0 | listing row |
| Flight data | no `aircraft_flight_intel` row yet (the report fetches it on first view) | — |
| Listing text | one line ("2021 PIPER M600 SLS Turboprop Aircraft for sale."); no logbook, damage or warranty detail | `listing_description` |

## Price history (`aircraft_price_history`, listing 260277255)
| Date | From | To |
|---|---|---|
| 2026-10-21 | $2,990,000 | $2,875,000 (−$115,000, −3.85%) |
- One cut, 40 days after first listing. No jitter rows.

## Fleet for sale — PA-46 turboprop family ladder (latest scrape, US-registered, one per tail, priced ≥ $100,000; median = "typical")
Family total: 95 listing rows across sources → **64 US-registered tails, 53 with a price**.
| Group | US tails priced | Typical ask | Range | Years |
|---|---|---|---|---|
| Meridian | 32 | **$1,290,000** | $789,000–$1,950,000 | 2001–2015 |
| M500 | 1 | $2,095,000 (N500PE, 2015) | — | — |
| M600 / M600 SLS | 11 | **$2,998,000** | $2,369,000–$3,875,000 | 2016–2026 |
| M700 | 9 | **$4,555,811** | $3,899,000–$4,582,731 | 2024–2027 |
- On air: "about sixty-five US airplanes for sale in this family, about fifty with a price"; M500 has only one priced US example, so it is shown but not used as a benchmark.

### M600 / M600 SLS, US-registered, priced (latest scrape)
| Tail | Year | Ask | Airframe h | Engine h | Seller | Price changes |
|---|---|---|---|---|---|---|
| N416RL | 2016 | 2,369,000 | 1,150 | 1,150 | dealer OK | $2,395,000 → $2,369,000 on Oct 19 |
| N163GT | 2019 (registry 2018) | 2,649,000 | 1,290 | 1,290 | dealer TX | — |
| **N665WA** | 2021 | **2,875,000** | **1,010** | **1,010** | dealer KS | $2,990,000 → $2,875,000 on Oct 21 |
| N627WA | 2021 | 2,920,000 | 728 | 479 | dealer ID | — |
| N69JM | 2021 | 2,990,000 | 380 | 380 | dealer (located in France) | — |
| N778GV | 2022 | 2,998,000 | 1,295 | 1,180 | dealer TX | — |
| N61DZ | 2022 | 3,075,000 | 664 | 664 | private TX | $3,175,000 → $3,075,000 on Oct 29 |
| N519TL | 2022 | 3,100,000 | 400 | 400 | dealer TN | — |
| N706MA | 2024 (registry 2023) | 3,425,000 | 395 | 395 | dealer FL | — |
| N612TP | 2023 | 3,550,000 | 170 | 170 | dealer CA | — |
| N648MA | 2026 (new) | 3,875,000 | — | — | dealer IN | — |
- Excluded: N-reg rows without a price (N641WA, N915CJ, N231DN, N334TC), "N/A" registrations (cannot be de-duplicated), foreign registrations (C-, SP-, G-).

### The hero's closest group — 2021–2022 M600 SLS, US-registered, priced, excluding hero (n=5)
N627WA 2,920,000 · N69JM 2,990,000 · N778GV 2,998,000 · N61DZ 3,075,000 · N519TL 3,100,000
- **Typical ask $2,998,000.** Hero is the **lowest ask of the six**, **$123,000 below** typical (−4.1%).
- Their airframe hours: 380 · 400 · 664 · 728 · 1,295 → **typical 664 h**. Hero 1,010 h = second-highest of the six.
- Price per airframe hour is not used (not a NextPlane metric).

## Valuation (RPC `get_aircraft_valuation('PA-46 Meridian/M-Class', 2021, 'Piper', 2, 'M600')`, 2026-11-02)
| Field | Value | Notes |
|---|---|---|
| estimated_value | **$2,939,000** (comp median) | Hero ask is $64,000 below (−2.2%). |
| comp_p25 / p75 | $2,887,500 / $2,998,000 | |
| comp_count | 23 | includes the hero itself, 3 cross-source duplicates (N501RL, N87SL, N519TL), one "N/A" row and ~10 tails not in the latest scrape → **expect REPORT_ISSUES** |
| msrp_new | $2,573,439 | **does not match** `model_msrp_history` 2021 M600/SLS base $3,112,116 → expect REPORT_ISSUES |
| msrp_retention_pct | 91.0 | built on the wrong MSRP |
| confidence | High | |
- What we would say on air if the report matches the RPC: "NextPlane's estimate of what similar airplanes sell for is about two point nine four million dollars; this one asks about sixty thousand less." Confirm against the live report first.

## New price (`model_msrp_history`, Piper M600/SLS)
| Model year | Base | Equipped | Confidence |
|---|---|---|---|
| 2021 | **$3,112,116** | **$3,300,000** | sourced |
| 2022 | $2,936,275 | $3,305,173 | sourced |
| 2023 | $3,605,498 | $4,058,474 | sourced |
- Hero ask = **92% of the 2021 base new price**, 87% of equipped. Newest M600 for sale (N648MA, 2026, dealer) asks $3,875,000.
- On air: "Five years and about a thousand hours later, it asks about ninety-two percent of what it cost new."

## Forecast (`model_price_forecasts`, listing 260277255)
| Scored | Ask | Fair value | p_cut90 |
|---|---|---|---|
| 2026-09-16 | 2,990,000 | 2,718,714 | 0.26 |
| 2026-09-30 | 2,990,000 | 2,963,460 | 0.36 |
| 2026-10-07 | 2,990,000 | 3,071,546 | 0.43 |
| 2026-10-14 | 2,990,000 | 2,701,334 | 0.24 |
| 2026-10-21 | 2,875,000 | 2,944,982 | 0.31 |
| 2026-10-28 | 2,875,000 | 2,722,899 | **0.48** |
- Fair value swings ±$370K week to week → **not used**. p_cut90 latest 0.48 → on air "about an even chance of another cut in the next three months" (phrased as a model estimate).

## Market behaviour — PA-46 turboprops, first listed 2026-04-26 → 2026-07-20, one per tail
Tail-level: first seen = earliest row across sources, last seen = latest row; excluded 2026-07-04 (bulk first ingest of the second source) and N/A registrations. Cuts counted only where both prices ≥ $500,000 (removes rental-rate and deposit rows).
| Metric | Value |
|---|---|
| Cohort | 29 tails; D-FMOR excluded as currency jitter (51 tiny moves) → **28** |
| Gone from the panel within 30 days | **1** (N26DR, 14 days) — not proof of sale |
| Still listed past 90 days | **15 of 28** (N726WA, N176MA, N22GT, N778GV, N61DZ, N76FG, N255PG, N33FG, N700AZ, N21WA, N550CR, VH-FWA, N464C, N248DA, N118JV) |
| Net cut ≥ 1% | **5 of 28**: N1032G −7.2%, N17PL −3.7%, N61DZ −3.1%, N248DA −2.1%, N255PG −1.3% |
| Typical cut among cutters | **3.1%** |
- Hero cut 3.85% ≈ the typical cut size. Never quote a mean days-on-market.
- On air: "Of twenty-eight of these turboprops listed this spring and summer, only five cut the price, and the typical cut was about three percent. More than half were still for sale three months later."

## Keep watching — M600, 2026-10-19 → 2026-11-02
- Price cuts: **3** (N416RL Oct 19 −1.1%; N665WA Oct 21 −3.85%; N61DZ Oct 29 −3.1%).
- New US-registered M600 listings: N334TC (Oct 15, no price), N612TP (Oct 21, $3,550,000), N641WA (Oct 21, no price).

## Offer logic (draft — re-check against the live report)
Closest group typical $2,998,000 with typical 664 h; hero $2,875,000 with 1,010 h (≈350 h more); valuation $2,939,000; seller already cut $115,000; family cuts are rare and small (5 of 28, typical 3.1%); p_cut90 ≈ 0.48. → **Open around $2,750,000 (−4.3%)**, conditional on a fresh annual signed off before closing (the listed annual date has passed), logbooks, engine trend data and the report's maintenance items. The cut-size data says sellers in this family rarely move more than a few percent, so expect to land between $2.75M and the ask.

## Capture grant — NOT CREATED
The insert into `public.purchased_reports` (user 95710b00-…, N665WA, amount 0, expires now()+30 days) was denied by this run's permission check. Needed before the next capture attempt.

```sql
insert into public.purchased_reports (user_id, n_number, make, model, year, amount_cents, report_data, expires_at, email_sent_at)
values ('95710b00-dab7-489d-85d0-262f53ddd349','N665WA','PIPER','M600 SLS',2021,0,
        '{"internal":"How to Buy episode capture grant (no charge)"}'::jsonb, now()+interval '30 days', now());
```
