# Ep3 N733JE — report issues (live capture 2026-09-28, capture@nextplane.us)

The live report was captured three times (cap1–cap3). The flight-activity text was identical across the captures. Every section below was checked against Supabase before going on screen.

## What went on screen, and how

| Section | On screen? | Notes |
|---|---|---|
| Header + verdict strip | Yes, with callouts on ask, NTSB, ownership period and liens | "Last sold" and "Location" tiles dimmed (see #2, #3). Owner name blurred. |
| Estimated Market Value | **No**. Replaced by a panel card | See #1 |
| Price history | **No**. Replaced by a panel step chart | See #4 |
| Registration & Transfer Timeline | Yes | Owner name blurred (tone choice; it is a business, not a private person) |
| Flight activity | **No**. Replaced by a panel card ("1 tracked flight") | See #6 |
| Airworthiness & Maintenance Program | Yes (summary + the 2011-10-09 and 2020-18-01 rows) | Registry tile blurred. The source-marketplace name in the assumptions footnote was cropped and blurred out (#9). |
| Service Difficulty Reports | Yes | Matches `report_signals` (0 on this tail, 627 on the model) |
| True Cost per Mile | Yes | Matches `report_cost_per_mile` exactly ($1.73 vs $1.38, 193 peers, 1,024 avg SMOH) |
| Who's Selling | **No**. Replaced by a panel card ("Private seller · Salisbury, MD" + the report's own "Before you call" checklist) | See #5 |
| Market dynamics, market velocity, comparison, competitive listings, signal comps, performance vs competitors, operating cost, depreciation | No | See #7–#12 |

## Issues (fix list for Lovable / Supabase)

| # | Section | Report shows | Truth (panel) | Severity |
|---|---|---|---|---|
| 1 | Estimated Market Value | **$140,000** from "183 active listings", range $119,900–$176,750, "High · 88%" | The cohort is every 172 generation (1956–2024), not the 172N. The 172N active median is $129,900 (n=19, IQR gate); the valuation RPC with the 172N cohort gives $130,450; the AeroIntel v1.4 fair value is $121,187. The price-distribution footer also contradicts itself: "49th percentile" vs "58th percentile" in Price position. | **High** |
| 2 | Header "LOCATION" | Hagerstown, MD | That is the registered owner's address. The aircraft is listed in Salisbury, MD. | Medium |
| 3 | Header "LAST SOLD" | Nov 2019 | That is the FAA certificate issue date, not a verified sale. | Medium |
| 4 | Price history | 5 correct dates, every amount "—" | $150,000 → $145,000 → $140,000 → $137,500 → $135,000 → $129,900 | **High** (a new variant of the Ep1 bug) |
| 5 | Who's Selling | "−12.4% vs market · expected ~$157,046 · n=40"; "private listings avg ~45 days"; "originally $140,000" | A fourth valuation that conflicts with #1. The first ask was $150,000. The 45-day mean comes from polluted sold flags. | **High** |
| 6 | Flight activity / ADS-B | 1 flight, HGR → SBY, **34 nm**, 0.0 h, "0 hrs/yr", "Recreational 60%", "Pricing impact +2.0%" | HGR–SBY is roughly 140 nm. Distance and duration are wrong, and a mission label and price impact from one flight are not meaningful. | **High** |
| 7 | Market dynamics | "45 days avg DOM · 19.2% reduced · 375 transactions" | Built on `status='sold'` rows (223 still-active 172s are flagged sold) | Medium |
| 8 | Market signal comparables | "$29", "$75", "$80", "$129" asks at "−100% vs median" | Junk price rows are not gated | Medium |
| 9 | Competitive listings table + AD-program assumptions | A **"Source" column shows the source marketplace name** on every row; the AD-program footnote also names it ("Times from listing …") | Must never be shown to customers | **High (brand rule)** |
| 10 | Original specs + Performance vs competitors | Engine "Lycoming O-320-E2D · 150hp", 120 KTAS, useful load "—" | A 172N is O-320-H2AD, 160 hp (the report's own AD program says H2AD) | Medium |
| 11 | Operating cost | Header reads "Cessna 172 172R" and uses 9.5 gph → $24,026 / $200/hr | The variant is the 172N; cost per mile uses 8 gph | Low |
| 12 | Depreciation | "MSRP data not available" with an empty value chart | — | Low (honest empty state; could hide) |
| 13 | Ownership-chain RPC | `report_ownership_chain` returns current = null | The UI timeline renders the owner correctly (from another path) | Low |
| 14 | Listing row | `original_asking_price_usd` = $140,000, `price_reduced` = false | History starts at $150,000 with 5 cuts | Medium (feeds #5) |
| 15 | Valuation comps RPC | `get_aircraft_valuation` comps include N12345 placeholders, "N/A" and duplicate tails | Clean median $134,950 (52 tails) | Medium |
| 16 | Registry artifact | `aircraft_transactions` removed/new pair on Aug 26–27 | Same owner and cert date (sync incident), not a transfer | Low |

## Capture tooling
- `lib/report_capture.py` returned 0 sections because the CSS rule `[class*=sidebar]{display:none}` hid the layout wrapper around `<main>`. Fixed in this commit: it now hides only the siblings of main's ancestors.
- The episode used an element-level capture (`capture.py`), which takes one screenshot per report card plus DOM bounding boxes for callouts and blurs. It is more reliable than the translateY frame recipe.
