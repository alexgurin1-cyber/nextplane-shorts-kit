# Ep4 N333WR — report issues (live captures 2026-10-05, capture@nextplane.us)

The live report was captured three times: `lib/report_capture.py` (50 sections, exit 0) and the element-level `src/capture.py` twice. Section text was identical between the two element captures, including flight activity. Every section below was checked against Supabase before going on screen.

## What went on screen, and how

| Section | On screen? | Notes |
|---|---|---|
| Header + verdict strip | Yes, callouts on ask, NTSB, liens, ownership period | Owner name blurred (tone choice). The "(Commercial/Training)" half of the use-type tile is blurred (#5). "Last sold" is not highlighted (#3). |
| Estimated Market Value | Yes, the adjusted-value box only ($1,296,500, range $1,199,000–$1,588,500) | The tile row and the percentile footer are cropped out (#1, #2). Our clean recompute is $1,298,000. |
| True Cost per Mile | Yes | Matches `report_cost_per_mile` exactly ($1.60 vs $1.67, 80 peers, 746 h avg). |
| Original new price | Yes, top row only (base, equipped, current asking) | The "+-14.2%" row is cropped out (#7). |
| Replacement cost chart | Yes | Re-captured with the pointer parked so no hover tooltip shows. |
| Price history | **No** — replaced by a panel step chart | #4 |
| Registration & Transfer Timeline | Yes | Owner name blurred. |
| Flight activity | Yes: "Flight Hours by Period" and the monthly chart | Both match `aircraft_flight_intel`. The header line naming the tracking vendor, Top Routes, Pricing Impact and Operational Summary are not shown (#5, #6). |
| Airworthiness & Maintenance Program | Yes, the six summary tiles only | Registry tile blurred. The assumptions panel is cropped out because its footnote names a source marketplace (#8). |
| Service Difficulty Reports | Yes | Matches `report_signals` (0 on this tail, 229 on the model). |
| Estimated Annual Operating Cost | Yes | Matches `aircraft_operating_cost` ($51,759, $431/h). Footer "(active_listing)" cropped. |
| Who's Selling | **No** — replaced by a panel card ("Dealer listing · 15 of 15 current listings: PA-46 family") | #9 |
| Price position, market dynamics, market velocity, competitive listings, signal comps, performance vs competitors, depreciation curve, original specs, investment grade | No | #2, #7, #8, #10–#14 |

## Issues (fix list for Lovable / Supabase)

| # | Section | Report shows | Truth (panel) | Severity |
|---|---|---|---|---|
| 1 | Estimated Market Value | "20 active listings" | The 20 comp rows include 4 duplicate tails (N377ST, N350W, N350E, N636SP listed twice), 1 non-US row with no N-number, the hero itself, and about 10 rows no longer in the latest scrape (several last seen in May or June, e.g. N458KD, N2369A, N636SP, N377ST). Only 7 of the tails are active today. The median happens to survive cleaning ($1,298,000 over 15 unique US tails vs $1,296,500), but the "active" label is wrong and the RPC should filter on last-seen and dedupe by tail. | **High** |
| 2 | Price position / percentile | Header card "86th percentile of comps, comp set 43, $/hour $2,144 vs median $662 (+224%)"; valuation footer "N333WR sits at the 50th percentile · Below median" | The two percentiles contradict each other, and the ask is above the median, not below. The 43-comp set mixes 1989 Mirages with 2025 M350s, so $/hour is not comparable. | **High** |
| 3 | Header "LAST SOLD" | Dec 2025 | That is the FAA certificate issue date, not a verified sale (same as Ep3 #3). | Medium |
| 4 | Price history | Two correct dates (Jul 15, Aug 21), both amounts "—" | $1,550,000 → $1,525,000 → $1,475,000. Same bug as Ep3 #4. | **High** |
| 5 | Use type / utilization | "Heavy (Commercial/Training)" in the verdict strip and Operational Summary, while Mission Profile says "Business · 60%"; "Est annual hours 193" | The label is a frequency heuristic; nothing in the data indicates commercial or training use, and it contradicts the mission-profile card. 193 h is the 24-month average; the last 12 months are 372.3 h. | **High** (reputational for owners) |
| 6 | Top Routes | PDK → LZU "1,583 nm", PDK → HHH "7,948 nm", HHH → PDK "7,784 nm" | Average distances are impossible (PDK–LZU is roughly 20 nm; legs of 0.3 h). Looks like a sum instead of an average, or a unit error. Same family as Ep3 #6. | **High** |
| 7 | Depreciation | "OFF EQUIPPED MSRP +-14.2%", "OFF BASE MSRP +-28.5%"; "Depreciation since new −$0 (+0.0%)", "$1,291,765 new → $1,291,765 estimated today"; value chart is a single point | Sign formatting bug; the ask is 14.2% ABOVE the 2022 equipped price. The value-over-time estimate is not computed (it should use the valuation, not the MSRP). | Medium |
| 8 | Competitive listings + AD-program assumptions | A **"Source" column shows the source marketplace name** on every row; the AD-program footnote reads "Times from listing <marketplace> (active)" | Must never be shown to customers (repeat of Ep3 #9). | **High (brand rule)** |
| 9 | Who's Selling | "Established 2026 · 0 yrs in business · FAA-certificated since 2026"; "13 sold this yr · typical 54 days · 19% slower"; "+11.4% vs market, expected ~$1,368,329, n=14"; "What they carry: Meridian 11 active …" | "2026" is the first year of our panel, not the dealer's founding. Sales counts and days-to-sell come from `status='sold'` flags, which are unreliable. The expected price is a second valuation that conflicts with #1. The "active" counts by model are tracked totals (24), not the 15 actually active. | **High** |
| 10 | Performance vs. Competing Models | M350 shown at 260 kts, 1,018 nm, 30,000 ft, MTOW 5,092 lb against a TBM 850 and a PC-12 | Those are turboprop (M500-class) figures. The report's own spec card says 213 KTAS, 1,343 nm, 25,000 ft, 4,340 lb. A piston M350 should be compared with piston peers. | Medium |
| 11 | Original specifications | A "CAPS" chip on a Piper M350 | CAPS is the Cirrus airframe parachute; the M350 has none. | Medium |
| 12 | Market dynamics / velocity | "60 days avg DOM · 30.6% reduced · 72 transactions"; "Median price $777,400" | Built on sold flags and a mean days-on-market; labelled "PA-46 Meridian/M-Class". | Medium |
| 13 | Market signal comparables | "Fresh engine: 2025, $2,098,059, 0 hrs, Des Moines" etc.; "Longest sit 171 days" rows for listings that left the panel in June | Stale rows presented as current. | Medium |
| 14 | Header title | "2022 Piper PA-46 Meridian/M-Class (M350)" | A piston M350 is labelled with the turboprop family name throughout (valuation footer, depreciation, operating cost). | Low |
| 15 | Listing row | `price_reduced` = false | Two cuts in the history table. | Low |
| 16 | Ownership-chain RPC | `report_ownership_chain` returns current = null | The UI timeline renders the owner from another path (same as Ep3 #13). | Low |
| 17 | Price model | `model_price_forecasts.fair_value` for this listing moved $915,508 → $1,260,562 → $1,159,617 → $1,145,728 in four September scorings; class recorded as `single_piston` and once `turboprop` | Not stable enough to quote for this class; only p_cut90 was used. | Medium |

## Capture tooling
- `lib/report_capture.py` worked unchanged (exit 0). Its per-section text is thin for most cards, so the cross-check used `src/capture.py`, which also saves every leaf text box per card for callouts and blurs.
- Recharts tooltips appear if the pointer rests over a chart; `src/recap.py` parks the pointer at (5,5) and clips the screenshot.
