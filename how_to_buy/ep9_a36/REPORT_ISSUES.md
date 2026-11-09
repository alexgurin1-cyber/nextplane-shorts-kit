# Ep9 (N1811Y, 1981 A36 Bonanza) — report and data issues, 2026-11-09

The live report could not be captured (locked, exit 3), so the report-vs-Supabase cross-check (runbook §4) has **not** been done yet. The issues below were found in Supabase while building the data pack.

1. **Capture blocked (again).** The `purchased_reports` capture-grant insert for N1811Y was refused by the scheduled run's permission check — the same block as Ep8 (2026-11-02). `report_capture.py N1811Y` → `LOCKED`, exit 3. Fix: run the SQL in DATA_PACK.md once (or pre-grant tails in bulk), then re-run the task or the capture step.
2. **Price forecast scores a stale row.** `model_price_forecasts` for N1811Y uses ask $395,000 and counts days from 2026-07-04, i.e. the second-source row `tap_2456224` last seen 2026-07-04, not the live $360,000 listing first seen 2026-05-19. Its fair value also swings week to week ($300,893 → $386,294 → $315,178 → $382,785 → $338,803). Not used on air.
3. **Wrong AD mapping.** `airworthiness_directives` maps **2020-25-01** (a King Air / 99 / 100-series lower forward wing fitting AD) to Beechcraft **A36, B36TC and G36**. If the report's maintenance card uses this table, Bonanza reports may list a King Air AD. Check the captured card; omit or relabel it if it appears.
4. **Stale duplicate rows.** N1811Y has a second-source row (`tap_2456224`, $395,000, 10 h engine, 60 h prop) last seen 2026-07-04 but still `is_active`, `missed_scan_count = 0`. Same pattern on N72100 (stale $335,000 row). Any report section that picks "latest row by created_at" would show the wrong price/engine time.
5. **No flight data** for N1811Y in `aircraft_flight_intel`. Confirm the report hides Flight Activity (honest empty state) rather than showing zeros.
6. **Annual due "September, 2026"** on the live row — may be past due now. Not voiced; worth a buyer question.
7. **Sister ship price-less earlier listing.** N1852S was listed 2026-07-29 → 2026-10-27 by another seller with no price, then by the hero's dealer at $375,000 from 2026-10-27. Its cohort first-seen date is 2026-07-29.
