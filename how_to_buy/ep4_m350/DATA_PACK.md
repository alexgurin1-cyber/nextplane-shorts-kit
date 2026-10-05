# How to Buy a Piper M350 — Episode 4 — DATA PACK

- Slot: Wednesday 2026-10-07 16:00:00Z (class: high-performance; rotation next = Piper M350).
- Built: 2026-10-05 (scheduled cloud run). Supabase project `uiprgookspqnvyumkyse`.
- The live report was captured three times on 2026-10-05 (`lib/report_capture.py` once, element-level `src/capture.py` twice) and cross-checked; see `REPORT_ISSUES.md`. Every on-screen number traces to this pack or to a verified report section.
- Internal note: listing sources are kept here for verification only. Never name them on air.
- "Latest scrape" in this pack = `last_seen_at >= 2026-10-03` with `missed_scan_count = 0` (one source last ran in full on Oct 3, the other on Oct 5).

## Hero aircraft
| Field | Value | Source |
|---|---|---|
| Tail | N333WR | `aircraft_listings.registration` |
| Listing | 243571307 (internal) | `listing_id` |
| Model / year | Piper M350 (PA-46-350P), 2022 | listing row; registry `PA 46-350P`, year_mfr 2022 |
| Serial | 4636809 | listing + registry match |
| Airworthiness date | 2022-10-31 | `aircraft_master.air_worth_date` |
| Ask | **$1,475,000** (published price) | `asking_price_usd` |
| First ask | $1,550,000 | `original_asking_price_usd` and price history |
| TTAF / engine / prop | 688 / 444 SNEW / 688 SNEW | listing row. Engine is 244 h younger than the airframe; the row does not say why. |
| Engine | Lycoming TIO-540-AE2A, 350 hp, TBO 2,000 h | registry + `model_cost_specs` (PA46-350) |
| Avionics | Garmin G1000 NXi, GFC 700, GI-275 standby, GTX 345R (ADS-B In/Out) | `avionics_summary`, `avionics_list` |
| Listing text | "EVERY 2023 Model Year Option installed! EXP Upgraded Interior, GWX-75 Radar, Immaculate and TURN KEY!" | `listing_description` |
| Annual | "April 2026" (ambiguous: done or due) | `annual_due` |
| Damage flag | false; no NTSB record for N333WR or serial 4636809 | listing row; `ntsb_accidents` (0 rows); `report_history_card` accident_count 0 |
| Seller | dealer, Olathe, KS (business name kept off air) | `seller_name`, `seller_type` |
| Active | status active, last seen 2026-10-03, missed scans 0, first seen 2026-06-11 | listing row |
| Share / partnership ad? | No | description checked |

```sql
select * from aircraft_listings where registration='N333WR';
```

## Price history (`aircraft_price_history`, listing 243571307)
| Date | From | To | Change |
|---|---|---|---|
| 2026-07-15 | $1,550,000 | $1,525,000 | −1.61% |
| 2026-08-21 | $1,525,000 | $1,475,000 | −3.28% |

- 2 cuts, $1,550,000 → $1,475,000 = −$75,000 (−4.84%). No jitter rows.
- First seen 2026-06-11 → 116 days listed on Oct 5, 118 at the Oct 7 publish date ("more than 115", "almost four months").
- Last change 2026-08-21 → 47 days before publish.
- Caveat: `price_reduced` = false on the listing row (inconsistent with history; logged).

## Registration and ownership (`aircraft_master`, `report_signals`, `report_history_card`)
- Registered owner: a Georgia LLC (type_registrant 7), Atlanta, GA. Certificate issued **2025-12-05**; expires 2032-12-31; status V. On air: "a Georgia company" only.
- Listed for sale 2026-06-11 = 6 months and 6 days after the certificate date. Report tile: "10 months · short holds are worth a question".
- No owner transfers observed since registry monitoring began (2026-05-09). No `aircraft_transactions` rows.
- Liens: "No security conveyance indexed", FAA document window 2025-10-23 → 2026-10-01; releases 0; repossession documents 0. Not a title search.
- Fleet (`report_history_card`): PA 46-350P — 1,015 airframes ever registered, 666 active (65.6%). Model safety: 4 NTSB records, 0 fatal. Not used on air.

## Flight activity (`aircraft_flight_intel`, fetched 2026-10-05 16:59Z; identical in both element captures)
- 381 flights, 384.7 h airtime, data period 2024-10-12 → 2026-10-02, 39 airports, 1% local, primary airport PDK.
- Monthly hours: 2024-10 6.8 · 2024-11 3.2 · 2025-04 1.1 · 2025-07 0.5 · 2025-10 0.9 · **2025-11 39.4 · 2025-12 18.9 · 2026-01 44.4 · 02 26.4 · 03 27.5 · 04 19.3 · 05 26.1 · 06 55.2 · 07 54.0 · 08 29.2 · 09 27.6 · 10 4.3**.
- Report card "Flight Hours by Period": last 3 months 62 flights / 61.1 h; last 6 months 188 / 196.4 h; **last 12 months 366 / 372.3 h** (Nov 2025 → Oct 2026 monthly sum = 372.3 ✓).
- On air: "372 hours in the last twelve months, nearly all of it since November" and "61 of those hours in the last three months, while the airplane has been on the market" (listed since Jun 11). 61.1 h / 3 months ≈ 20 h a month.
- Consequence used on air: the 688 h in the listing may be out of date → ask for current airframe and engine times in writing. Tracked airtime is not Hobbs time; no claim is made about the actual current total.
- Not used: the "Heavy (Commercial/Training)" label, "est. annual hours 193", route distances, pricing impact (see REPORT_ISSUES).

## Fleet for sale — Malibu Mirage + M350, US N-registered, latest scrape, deduplicated by N-number, share ads excluded
| Step | Count |
|---|---|
| Mirages and M350s for sale | **32** |
| …with a published price | **27** (no price: N14PC, N682AK, N671AG, N115DW, N776AM) |
| M350 (2015+) with a price | **9** |
| …late-model used, 2019–2023 | **4** |

Excluded as not in the latest scrape (missed 1 scan): N92728, N996C.

### Price ladder (priced, active; median ask)
| Era | n | Asks | Median |
|---|---|---|---|
| Mirage 1989–2002 | 10 | 419,000 · 455,000 · 475,500 · 545,000 · 549,000 · 550,000 · 570,000 · 585,000 · 590,000 · 825,000 | **$549,500** |
| Mirage 2011–2014 | 8 | 739,000 · 759,000 · 785,000 · 789,000 · 859,000 · 864,900 · 895,000 · 975,000 | **$824,000** |
| M350 2015–2020 | 3 | 890,000 (2015) · 1,175,000 (2019) · 1,199,000 (2020) | **$1,175,000** |
| M350 2022–2023 | 2 | 1,475,000 (hero) · 1,499,900 | shown as the two asks ("just under one and a half million") |
| M350 2025–2026 | 4 | 1,895,000 · 1,950,000 · 1,950,000 · 2,148,445 (factory new) | **$1,950,000** |

Small-n rows carry "(n=…)" on screen.

### Shortlist (the four late-model used M350s)
| Tail | Year | Ask | TTAF | Engine |
|---|---|---|---|---|
| N350TZ | 2019 | $1,175,000 | 1,390 | 1,315 |
| N350W | 2020 | $1,199,000 | 1,195 | 1,195 |
| **N333WR** | 2022 | **$1,475,000** | 688 | 444 |
| N7377G | 2023 | $1,499,900 | 230 | 230 |

- Spread $1,499,900 − $1,175,000 = $324,900 ("more than three hundred thousand apart").
- Hero vs 2019: +$300,000; vs 2020: +$276,000 ("almost three hundred thousand less").
- N7377G history has a cut to $1,400,000 (Sep 9) and a raise back to $1,499,900 (Sep 29) — jitter; only the current ask is quoted.
- N350TZ history contains a $450,000 placeholder row (Jul 21) — ignored.

### Closest comps that recently left the panel (last ask; exits are "no longer seen", not verified sales)
| Tail | Year | TTAF | Last ask | Last seen |
|---|---|---|---|---|
| N350E | 2020 | 547 | $1,295,000 | 2026-09-29 |
| N776NG | 2021 | 700 | $1,298,000 | 2026-09-25 |

- Hero − N776NG = $177,000. N7377G − hero = $24,900. 230 h / 688 h = 0.33.

## Valuation
| Source | Value | Notes |
|---|---|---|
| Report "Estimated Market Value" = `get_aircraft_valuation('M350',2022,'PIPER')` | **$1,296,500**, 25th–75th pct $1,199,000–$1,588,500, "20 active listings", High 88% | Matches the RPC exactly. The 20 rows are model years 2019–2025 and include 4 duplicate tails, 1 non-US row and ~10 rows that are no longer active (see REPORT_ISSUES #1). |
| Our recompute: one row per US tail, latest ask, 2019–2025 (15 tails) | **$1,298,000** median | Within 0.1% of the report figure, so the estimate is used on air; the "20 active listings" tile is cropped out. |
| Ask vs estimate | +$178,500 = **+13.8%** | 1,475,000 − 1,296,500 |
| Seller-profile RPC | expected $1,368,329, +11.4%, n=14 | A second, different estimate; not used on air. |
| `model_price_forecasts` fair value | $915,508 → $1,260,562 → $1,159,617 → $1,145,728 across four scorings in September | Unstable for this class; **not used**. |
| `model_price_forecasts` p_cut90 (v1.4, 2026-09-30) | 0.517 (Sep 16: 0.530; Sep 9: 0.508) | On air: "about an even chance of another price cut in the next ninety days". |

**Episode verdict:** priced about 14% above NextPlane's estimate but inside the comparable range; clean history; three open questions (short hold, engine younger than the airframe, current hours).

## New-price context (`model_msrp_history`, variant M350)
| Model year | Base | Standard equipped | Confidence |
|---|---|---|---|
| 2022 | $1,147,588 | **$1,291,765** | sourced (Piper 2022 comparison table) |
| 2025 | $1,830,079 | **$2,060,000** | sourced (BCA 2025 Purchase Planning Handbook) |

- Ask ÷ 2022 standard-equipped = 1.1418 → "about fourteen percent more". The aircraft's actual invoice is unknown and it carries options, so on air the comparison is always to the "standard-equipped" price.
- 2025 ÷ 2022 = 1.595 → "sixty percent more".
- A factory-new 2026 M350 is listed at $2,148,445 (N350SA) — ladder only.

## Cost per mile (`report_cost_per_mile('N333WR')`, spec PA46-350: TBO 2,000 h, overhaul $90,000, 20 gph, 200 kt, 100LL $6.50)
| | N333WR (444 h, 1,556 h to TBO) | Market (80 for-sale peers, avg 746 h) |
|---|---|---|
| Total | **$1.60/nm**, $321/h | **$1.67/nm**, $335/h |
| Reserves | $0.30/nm | $0.37/nm |
- 746 − 444 = 302 more hours of engine life. 302 × ($90,000 ÷ 2,000 = $45/h) = **$13,590** ("about thirteen and a half thousand").

## Operating cost (`aircraft_operating_cost('N333WR')` — matches the report card)
120 h/yr: fuel $14,880 · insurance $20,375 · hangar $3,864 · annual $2,300 · maintenance reserve $2,760 · engine accrual $4,410 · prop $270 · avionics $2,900 → **$51,759/yr, $431/h**. Hull value $1,475,000.

## Airworthiness directives (`report_signals` / `aircraft_ad_matches('N333WR')`)
6 matched rows = 5 active + 1 superseded (2021-04-07 → 2021-09-02). Active: 2021-09-02 (stall-warning heat; applies if the left wing was replaced), 98-04-26 (AFM icing revision), and three conditional on installed parts: 2011-06-10 (T.I.T. system), 2011-13-03 (turbocharger), 89-15-10 (fuel tee fitting). Report header: "5 applicable FAA ADs · 3 conditional on installed parts" ✓. Compliance is not derivable from FAA data.

## Service difficulty / safety
- SDRs for this tail: 0. Model: 229 total, 16 in 5 years, 1 in 12 months, 155 aircraft with reports. NTSB by tail or serial: 0.

## Market behaviour — Mirage + M350, US, first listed 2026-04-26 → 2026-07-07 (≥ 90 days of observation), deduplicated by tail, share ads excluded
| Metric | Value |
|---|---|
| Cohort | 24 |
| Left the panel within 30 days | 3 |
| Still listed past 90 days | 10 |
| Cut price at least once | **10 of 24** |
| Median total cut among cutters | **2.8%** ("under three percent") |
Small cohort, so counts are quoted, not percentages. Never quote a mean days-on-market.

## Seller (panel-built card; the report's seller section was not shown)
- Dealer listing in Kansas. The dealer has 28 tracked listings; all **15** current ones (latest scrape) are PA-46 family: Meridian 6, JetProp 4, Mirage 2, Matrix 2, M350 1.
```sql
select model, count(*) n, count(*) filter (where is_active and last_seen_at>='2026-10-03' and missed_scan_count=0) act
from aircraft_listings where seller_name ilike '<the listing dealer>%' group by 1;
```

## Keep watching — Mirage + M350, US, 2026-09-21 → 2026-10-05
- New listings (distinct tails): **6**. Price cuts (new < old): **4** (N92728, N1937B, N996C, N725ED). One raise (N7377G) excluded.

## Offer logic (on air)
Estimate $1,296,500 + engine credit $13,590 = $1,310,090 → "around one point three one million", in line with the last asks of the two closest comps ($1,295,000 and $1,298,000). Conditions: current hours in writing, engine logbook, pre-buy at a shop the buyer chooses.
