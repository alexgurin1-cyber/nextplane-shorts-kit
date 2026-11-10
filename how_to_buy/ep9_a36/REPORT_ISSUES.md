# Ep9 (N1811Y, 1981 A36 Bonanza) — live report issues, captured 2026-11-10

Report captured 2026-11-10 02:2xZ after Alex gave the capture account standing access (`profiles.subscription_status = 'active'`) plus a one-off N1811Y grant. `report_capture.py` exit 0 (52 sections); element capture `src/capture.py` (40 cards). Each section cross-checked against Supabase before going on screen.

| # | Section | Issue | On air |
|---|---|---|---|
| 1 | Estimated Market Value | **Net adjustment +$0** although 5,100 h / 19 h are prefilled (same bug as Ep7). A 19-hour engine should move the value. | Voiced "makes no adjustment for the new engine", then our own check. |
| 2 | Estimated Market Value | Price-distribution axis runs to **$2,890,000** — a 1984 turbine-converted A36 listed in Tulsa (model "A36 BONANZA TURBOPROP") sits in the A36 comp set; also a **$4,500** placeholder ask (1981, El Cajon) and an **81,702 h** airframe typo (1981, Jacksonville) appear in "Market signal comparables". | Distribution not shown; comp count blurred. |
| 3 | Valuation vs Price position | Valuation says "**50th percentile**, below median"; Price position says "**65th percentile**". The $360,000 ask is above the $299,925 estimate, so neither "50th" nor "below median" fits. | Neither percentile voiced. |
| 4 | Grade card / maintenance program | Grade says "**10 hrs SMOH … 1,690 remaining**" and the maintenance program says "Times from listing **trade-a-plane** (active)" — both read the stale July duplicate row (10 h), not the live row (19 h). Source marketplace named in fine print. | Grade not voiced; fine print blurred. |
| 5 | Maintenance program | "47 already due" includes items with odd dates (e.g. "MAY 1933" for a 400-h recurring clamp). Default utilisation 50 h/yr. | Only the count (16) and the flagged AD (2024-14-03) voiced. |
| 6 | Maintenance program | 2019-23-10 (right aileron cable end fittings, certain A36s) is **not** in the report's AD list; `airworthiness_directives` also maps the King Air AD **2020-25-01** to A36/B36TC/G36 (not shown on this report, but a table bug). | Not voiced. |
| 7 | Listing history | Names both source marketplaces and the dealer; shows "Ad removed — FAA ownership change not confirmed" on Jul 4 (artefact of the second-source bulk ingest). | Those rows and the legend blurred. |
| 8 | Seller section | Dealer location shown as **New Orleans, LA**; the listing is in Blountville, TN (other inventory in MA, IN, NC). Not verified. | Dealer not named; only the +9.2% price stance and "42% slower" voiced, attributed to NextPlane dealer data. |
| 9 | Flight activity | Header "~23 hrs/yr" vs Operational Summary "Est annual hours 20" vs Flight Hours by Period "last 12 months ~30.9 h". Subtitle names the flight-data source. Supabase `aircraft_flight_intel` was empty on 2026-11-09 and was filled live by the capture (fetched 2026-11-10 02:19Z, 92 flights, 38.8 h) — matches the report. | Period table only (31 h / ≈7 h prior year); subtitle not shown. |
| 10 | Market dynamics / velocity | "68 days avg on market, 23.9% reduced, 159 transactions" vs Market comparison "Days on market avg 100 / median 107". Mean days-on-market never quoted. | Not voiced. |
| 11 | Market comparison | "95 active A36 listings" vs Geographic "131 for sale in 34 states" vs valuation "72". | Counts not voiced from the report; on-air counts are ours (≈60 US-registered, 29 priced 1968–83). |
| 12 | Operating cost vs specs | Op-cost card uses 15.0 gph and an IO-520 engine accrual ($4,225/120 h ≈ $35.2/h); True Cost per Mile uses IO-550-B, 15.5 gph. | Voiced the op-cost card's own $35/h. |
| 13 | Original new price / depreciation | "MSRP data not available"; depreciation chart empty. | Skipped. |
| 14 | Price forecast (internal) | `model_price_forecasts` scores the stale $395,000 duplicate row; fair value swings $301K–$387K week to week. | Not used. |

Earlier issue now fixed: capture access. The weekly run can no longer write grants (refused by its permission check on 2026-11-02 and 2026-11-09); Alex set standing access on 2026-11-10.
