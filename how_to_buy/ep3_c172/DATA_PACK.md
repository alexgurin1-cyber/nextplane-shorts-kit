# How to Buy a Cessna 172 — Episode 3 — DATA PACK

- Slot: Wednesday 2026-09-30 16:00:00Z (class: piston single; rotation next = Cessna 172)
- Built: 2026-09-28 (scheduled cloud run). Supabase project `uiprgookspqnvyumkyse`.
- **Status: PRE-PRODUCTION.** Live report capture returned exit code 3 (report locked; no cloud capture login in memory). No video was produced or uploaded. Every figure below comes from Supabase queries run on 2026-09-28; the on-screen report sections still need to be captured and cross-checked (see `REPORT_ISSUES.md` for what the report's own RPCs return today).
- Internal note: listing source is kept here for verification only. Never name it on air.

## Hero aircraft
| Field | Value | Source |
|---|---|---|
| Tail | N733JE | `aircraft_listings.registration` |
| Listing | tap_2455890 (internal) | `aircraft_listings.listing_id` |
| Model / year | Cessna 172N Skyhawk, listing year 1977 | listing row |
| FAA year_mfr | 1976 (airworthiness date 1977-01-07) | `aircraft_master` |
| Serial | 17268324 | listing + registry match |
| Location | Salisbury, MD | listing row |
| Ask | **$129,900** (published price) | `asking_price_usd` |
| TTAF / SMOH / prop | 5,500 / 1,500 SMOH / prop 3,000 SMOH | listing row |
| Damage flag | false; no NTSB record for serial 17268324 | listing row; `ntsb_accidents` (0 rows) |
| Avionics (listing text) | uAvionix skyBeacon ADS-B Out, Garmin aera 796, two Garmin G5, Garmin GMA 340 | `avionics_summary` |
| Listing notes | Interior replaced 2018; hangared last 16 years | `listing_description` |
| Annual | "Current thru 12/2025" (listing text — lapsed unless updated; ask) | `annual_due` |
| Seller type | private (seller_name blank) | listing row |
| Active | status active, last seen 2026-09-25, missed scans 0 | listing row |
| Share / partnership ad? | No (description checked) | listing row |

Query:
```sql
select * from aircraft_listings where registration='N733JE';
```

## Price history (`aircraft_price_history`, listing tap_2455890)
| Date | From | To | Change |
|---|---|---|---|
| 2026-05-21 | $150,000 | $145,000 | −3.33% |
| 2026-05-25 | $145,000 | $140,000 | −3.45% |
| 2026-07-09 | $140,000 | $137,500 | −1.79% |
| 2026-08-09 | $137,500 | $135,000 | −1.82% |
| 2026-09-17 | $135,000 | $129,900 | −3.78% |

- 5 cuts, $150,000 → $129,900 = −$20,100 (−13.4%). No jitter / flip-flop rows.
- First seen 2026-05-16 → 137 days on market at the Sep 30 publish date.
- Caveat: `original_asking_price_usd` = $140,000 and `price_reduced` = false on the listing row, both inconsistent with the history table (logged in REPORT_ISSUES).

## Registration and ownership (`aircraft_master`, `aircraft_transactions`, `report_signals`)
- Registered owner: a Maryland flight-school LLC (type_registrant 7 = LLC), certificate issued 2019-11-21 → ~6.9 years tenure. Registration expires 2029-11-30. Status V.
- No owner transfers observed since registry monitoring began (2026-05-09). The Aug 26/27 `registration_removed` / `new_registration` pair for 733JE is the known registry-sync artifact (same owner, same cert date before and after) — NOT a transfer.
- Liens: "No security conveyance indexed" in the FAA document window 2025-10-23 → 2026-09-25; releases 0; repossession docs 0. Not a title search.
- Engine on registry: code 41508 "Lycoming O-320 series, 180 hp" — this is the registry's generic catch-all code (2,903 of the registered 172Ns carry it). Do NOT claim a 180 hp conversion.
- On air, name the owner type only ("a Maryland flight-school LLC"); do not name the company.

## Fleet context (`report_history_card`)
- 172N: 5,817 airframes ever registered, 3,140 still active → 54% survival.
- 172 family: US active 19,447; ~44,000 built worldwide (source flagged "widely cited").
- 172N model safety: 400 NTSB records, 57 fatal events (model-level, not this airframe). Not used on air.

## Price ladder — active Cessna 172s, latest scrape (last_seen ≥ 2026-09-25), N-registered, priced, share ads excluded, per-variant IQR gate (1.5×IQR)
| Variant | n (gated) | Median ask | Gated range |
|---|---|---|---|
| 172 to 172L (1956–72) | 58 | $94,950 | $45,000–$135,500 |
| 172M (1973–76) | 21 | $139,000 | $79,000–$182,000 |
| **172N (1977–80)** | 19 | **$129,900** | $99,000–$169,000 |
| 172P (1981–86) | 6 | $184,000 | $159,500–$198,000 |
| 172R (1996–2008) | 5 (after dropping a $75 row and a duplicate) | $240,000 | $165,000–$299,000 (small n — use as "around") |
| 172S (1998+) | 21 | $309,900 | $215,000–$449,900 |

Note: the first-pass regex `^172R` matched 172RG Cutlass rows; corrected with `^172R( |$)` and `!~* 'RG'`.

### 172N comp set (21 active; IQR fence $86,750–$175,150 drops N739VR $189,500 and N990B $250,000)
Asks ascending: N1945F 99,000 · N5227D 100,000 · N5366J 109,900 · N3306E 119,000 · N737LR 119,900 · N733EN 119,900 · N833CB 120,000 · N73864 125,000 · N738PV 129,000 · **N733JE 129,900** · N1591E 129,900 · N739NT 134,900 · N173SK 135,000 · N1043S 137,000 · N6212G 137,500 · N739HD 142,000 · N73917 159,900 · N737HM 165,000 · N738YW 169,000 · (fenced out: N739VR 189,500 · N990B 250,000).
- Hero is the 10th of 19 gated comps → exactly the median.
- 172N medians: TTAF 7,512 (hero 5,500 — ~2,000 hr below); SMOH 1,373 (hero 1,500 — slightly above).
- No share-priced comps in the active 172N set.

## Valuations (three different numbers exist — see REPORT_ISSUES)
| Source | Value | Notes |
|---|---|---|
| AeroIntel v1.4 fair value (`model_price_forecasts`, scored 2026-09-16, ask then $135,000) | **$121,187** | pre-dates the Sep 17 cut; p_cut30 25%, p_cut90 61%, exp. ask in 90d $131,831 |
| Report valuation RPC `get_aircraft_valuation('172N',1977,'CESSNA')` | $130,450 (comp median, 64 comps, p25 $119,000 / p75 $161,250, "High") | comp list contains placeholder tails and duplicates |
| Same comp list cleaned (drop N12345 ×2 and "N/A" ×3, one row per tail) | $134,950 (52 tails) | our recompute |
| Seller-profile RPC `report_seller_profile` | expected $157,046, "−12.4% vs market" | conflicts with the two above |

**Episode verdict (defensible from every clean number):** priced AT market for a 172N — the ask equals the active-comp median and sits within 0.4% of the report's comp median — but about 7% above the AeroIntel fair value, with a high-time engine. Not a bargain, not overpriced.

## Market behavior — Cessna 172 family (non-RG), listed 2026-04-26 → 2026-06-26 (≥90 days of observation), share ads excluded
| Metric | Value |
|---|---|
| Cohort | 125 listings |
| Left the market within 30 days | 30.4% |
| Still listed past 90 days | 18.4% (N733JE is in this group) |
| Share that cut price | 28.1% |
| Median total cut among cutters | 8.0% |
- Exits measured as "no longer seen" (last_seen before 2026-09-18) — not verified sales. `status='sold'` flags are currently unreliable (223 rows flagged sold while still active; see the 2026-09-25 false-sales rollback), so they were not used. Never quote a mean days-on-market.

## Cost per mile (`report_cost_per_mile('N733JE')`, spec CES_172_SKYHAWK: O-320, TBO 2,000, overhaul $40,000, 8 gph, 112 kt, 100LL $6.50)
| | N733JE (1,500 SMOH, 500 hr left) | Market (193 peers, avg 1,024 SMOH) |
|---|---|---|
| Total | **$1.73/nm, $193/hr** | $1.38/nm, $154/hr |
| Reserves | $0.73/nm | $0.38/nm |
| Operational (fuel + maint) | $0.73/nm | $0.73/nm |
| Annual | $0.27/nm | $0.27/nm |
- +25% per mile vs the average 172, entirely from engine reserves.
- Derived: engine-life gap vs market = (1,500 − 1,024) × ($40,000 ÷ 2,000) = 476 × $20 ≈ **$9,520**. $129,900 − $9,520 ≈ $120,380 — converges with the v1.4 fair value ($121,187).
- `compute_operating_cost` returns $23,660/yr / $197/hr at 120 hr (includes insurance and hangar, 9 gph, $6.20) — a different method; not used on air.

## Airworthiness directives (`aircraft_ad_matches('N733JE')`) — 12 matched, 5 unconditional
Unconditional: 2000-06-01 fuel strainer standpipe · 2001-23-03 doorpost map-light switch insulator (repeats every 12 months) · 2011-10-09 seat rails (repeats every 100 hr / 12 months) · 2020-18-01 lower forward doorpost crack inspection at wing strut fitting (repeats every 1,000 hr / 36 months) · 80-06-03 flap follow-up cable clamp.
Conditional (7, depend on installed STCs/parts): 2008-02-18, 2008-26-10, 2011-06-02, 2024-14-03 (GFC 500 — listing does not list an autopilot), 82-07-02, 83-17-06, 86-24-07.
Compliance status is not derivable from FAA data — the buyer's logbook check.

## Service difficulty / safety
- SDRs for this tail: 0. 172N model: 627 SDRs total, 7 in the last year.
- NTSB by serial: 0.

## Flight activity
- `aircraft_flight_intel`: no rows for N733JE → the report's flight sections should be hidden (honest empty state). Verify on capture.

## Depreciation
- `pct_depreciated` returns null; `msrp_new` null in the valuation payload (while `msrp_retention_pct` = 55.0). No verifiable depreciation figure — omit from the episode.
