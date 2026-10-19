# "Is your airplane liquid?" campaign — Oct 19 to Nov 1, 2026

Alex's brief (2026-10-18): one metric per Short, never "best/worst" or "investment", catchy titles that state what sellers or buyers do, never any "blink" phrasing. The campaign sells liquidity: how long a model takes to sell, how often sellers cut the price before it sells, how much it loses per year. Seller enticement ("see how long your airplane takes to sell before you list it", "how many price cuts does your model take") and buyer enticement ("find out whether it's liquid before you buy"). Full strategy: Claude Doc "NextPlane Liquidity Campaign"; project doc `claude/liquidity-campaign-single-metric-rankings-and-10-day-plan-2026-10-18.md`.

Bridge line (verbatim, every piece): **"The list tells you the model. The report tells you the airplane."** Close: "Plug in the N-number at nextplane.us." (The long Short keeps the verbatim CTA "Before you call the broker, check the data at NextPlane.us." as the final line.)

Wording rules: "sells fastest", "sellers don't cut the price", "holds value" — never "investment", "returns", "best", "worst", "blink". Slow or often-cut models are "patient money", never "bad". Plain language (feedback-plain-language-videos). "Typical" not "median"; "in our sold data" on screen for any family under 20 sold. Flat depreciation = "the price no longer depends on the year", never "gains value". Never name Controller or any source marketplace; never call the data public.

## Data (pulled 2026-10-18, re-verify on run day)

Source table: `scratch_sold_listings_20261018` (snapshot of `analytics_listings where is_sold`; the live view times out on aggregates — always snapshot first). Filters: model years 1970–2024, price floor $150K jets/turboprops, $20K pistons, `days_on_market is not null`. Family merge v2 (regex in `campaign/liquidity/families.sql`). Thresholds: ≥20 sold singles, ≥12 others, ≥8 model years for depreciation. Cut rate = share of sold listings with `reduction_pct > 0`; avg cut = mean `reduction_pct` (0 when never cut); value lost per year = `100*regr_slope(ln(last_price), year)`.

Re-verify on run day: re-run `families.sql`; if the #1 model or a title number moves, update the title and on-screen figures; never voice a figure that is not in the run-day pull. Live listing count for the #1 model: `select count(*) from analytics_listings where is_active_listing and <family filter>`.

## The ten YouTube Shorts (weekday 11:00 run; one per slot, in order)

Structure (~90 s, Tyler Cash VO, format name RANKING; build from the analyst template's ranking card, countdown 5→1):
1. Question (0–8 s): the liquidity question in the viewer's words, one number on screen.
2. The list (8–45 s): five models counted down 5→1, each with its number and one plain-word reason naming a person (who buys it and why).
3. The catch (45–65 s): live listing count of the #1 model on run day — "there are N for sale this week; on the listing site they look identical."
4. The report (65–85 s): one REAL currently listed tail of the #1 model whose nextplane.us report contradicts the model average (price cuts on this tail, long listing, short ownership, NTSB record), with the standard report snapshot (lib/report_capture.py, 1280 px). Never a tail that is merely expensive.
5. Close (85–90 s): bridge line + "Plug in the N-number at nextplane.us." + verbatim CTA.

| Slot | Run | Title | On-screen sub-line | Countdown 5 → 1 | Report tail to find |
| --- | --- | --- | --- | --- | --- |
| 1 | Mon Oct 19 | 5 piston singles where sellers don't cut the price | Ranked by how often the price gets cut before it sells | Piper Warrior 14% (avg cut 1.0%, n49) · Cessna 172S 14% (0.7%, n44) · 182Q 13% (1.0%, n63) · 182P 11% (0.8%, n73) · Cessna 400/TTx 10% (1.1%, n39) | a TTx or 182P with 2+ cuts in its price history |
| 2 | Tue Oct 20 | 5 piston singles that sell in about a month | Ranked by typical days on the market | 182Q 35 d · 172N 33 d · 177RG 31 d · 172M 29 d · Cessna 152 20 d (category typical ≈ 50 d) | a 172M or 152 listed 120+ days, or a former trainer at 200+ hr/yr |
| 3 | Wed Oct 21 | 5 piston singles that lose the least value every year | Ranked by price lost per model year | A36 Bonanza 2.1%/yr (32 yrs) · 206H/T206H 1.8% · Arrow 1.3% · Warrior 0.9% · Cessna 185 0.2% (comps: SR22 6.0%, SR22T 6.1%, TTx 5.6%, DA40 3.9%) | a Cessna 185 with an NTSB record or an owner change inside 18 months |
| 4 | Thu Oct 22 | 5 twins where "make an offer" doesn't work | Ranked by how often the price gets cut | Duke 17% (n12) · Seneca I–III 17% (avg 0.7%) · Baron G58 14% · Cessna 414/414A 12% · Navajo/Chieftain 9% (others: 310 44%, DA62 44%) | a 414 with three cuts, or a Navajo out of a charter fleet |
| 5 | Fri Oct 23 | The 5 twins that sell the fastest — one in 41 days | Ranked by typical days on the market | Baron G58 55 d · 421B/C 53 d · 414/414A 50 d · Navajo 45 d · Duke 41 d (DA62 116 d) | a Duke with engine time close to overhaul |
| 6 | Mon Oct 26 | The turboprops that sell at the asking price | Ranked by how often the price gets cut | Cheyenne 11% · King Air 200/B200/250 9% · PC-12 /45 /47 8% (n12) · TBM 700 7% (n15) · PC-12 NG/NGX 0% (n26) (others: TBM 850 36%, Caravan 36%) | two PC-12 NG at the same ask, one with a cut history |
| 7 | Tue Oct 27 | 5 turboprops that sell before the ad gets old | Ranked by typical days on the market | Cheyenne 58 d · King Air E90/F90 58 d · Caravan 208B 58 d · Conquest I 58 d (n15) · Meridian/M500/M600 56 d (TBM 850 97 d, PC-12 legacy 85 d) | a Meridian that was cut (29% are) next to one that was not |
| 8 | Wed Oct 28 | 5 jets nobody negotiates on | Ranked by how often the price gets cut | CJ2/CJ2+ 7% (avg 0.1%) · Learjet 45/45XR 6% · Challenger 300/350 6% (avg 0.1%) · Falcon 2000 family 5% · Gulfstream GIV/GIV-SP 0% (n17) (Citation I/II/SII 30%) | a GIV: ownership chain, operator history, days listed |
| 9 | Thu Oct 29 | Sold in 27 days — the 5 fastest-selling jets | Ranked by typical days on the market | GIV 53 d · Citation V/Ultra/Encore 51 d · Mustang 46 d · CJ1/CJ1+ 44 d · Learjet 45/45XR 27 d (Learjet 60 101 d, HondaJet 89, CJ4 88) | a Learjet 45 listed 90+ days |
| 10 | Fri Oct 30 | 5 twins that hold their value year after year | Ranked by price lost per model year | Baron G58 3.6%/yr · DA42 3.4% · Baron 58 2.8% · Cessna 310 flat · Navajo/Chieftain flat | a 310 whose own price history has cuts: "age isn't the problem — this tail's history is" |

Held back pending a data check (do not use): Global 5000/6000/6500 and Gulfstream G200 (median prices in the pull do not match the type). Upload private with publishAt at the next free 15:00Z slot as usual; cross-post the long Short to LinkedIn through the normal backfill.

## The daily 15-second clip (TikTok + Instagram, 6:57 run) — Format A "Liquidity check"

Replaces the PRICE JUMP / TWINS / AD LEFT OUT rotation from Oct 19 through Nov 1 (then the rotation resumes). Same production chain as templates/shorts15 (gen_vo → gen_music → render15 → mux15), new scene `liq`:
- 0–3 s question card: "Is a [model] liquid?" with a real photo of the model (lib/photos.py).
- 3–11 s three numbers drop in one by one — typical days on the market · share of sellers who cut the price · value lost per year (omit the third if "—" below) — with the one spoken sentence.
- 11–13 s verdict word: LIQUID / AVERAGE / PATIENT MONEY (never "bad").
- lookup beat + end card unchanged: "Check yours. Before you call the broker, check the data at NextPlane.us."
- No tail number is needed (model-level), so the `social_shorts15` no-reuse rule applies to the model instead. Log the row with format `liquidity_check`.
- Caption: "[Hook sentence]. [days] days to sell. [cut rate] get a price cut. [lost/yr] lost per year. Is your airplane liquid? The list tells you the model — the report tells you the airplane. Plug any N-number into nextplane.us." + at most 5 hashtags: `#aviation #generalaviation #aircraftforsale #<make> #nextplane`.

| Date | Clip | Model | Days | Cut rate | Lost/yr | Verdict | Spoken sentence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Oct 19 | A1 | Cessna 172M Skyhawk | 29 | 14% | — | Liquid | A month on the market and most sellers never touch the price. Every flight school wants one. |
| Oct 20 | A3 | Cessna 182P Skylane | 46 | 11% | 0.7% | Liquid | Nine in ten sell without a price cut. |
| Oct 21 | A5 | Cessna 400 / TTx | 53 | 10% | 5.6% | Liquid | The least-cut piston single, but it loses about six percent a year. Fast out, costly to hold. |
| Oct 22 | A2 | Cessna 152 | 20 | 17% | — | Liquid | Twenty days. The fastest-selling airplane in the country. |
| Oct 23 | A6 | Piper Warrior | 39 | 14% | 0.9% | Liquid | Holds its value and sells in six weeks. The trainer that never gets cheaper. |
| Oct 24 | A11 | Piper Dakota | 57 | 41% | 3.6% | Patient money | Four in ten sellers cut the price. Know that before you list. |
| Oct 25 | A14 | Beechcraft Duke | 41 | 17% | — | Liquid | Forty-one days. The fastest twin in our sold data. |
| Oct 26 | A15 | Diamond DA62 | 116 | 44% | 3.9% | Patient money | Four months to sell and almost half get cut. Price it right the first time. |
| Oct 27 | A17 | Pilatus PC-12 NG | 69 | 0% | — | Liquid | Zero. Not one seller in our data cut the price. |
| Oct 28 | A18 | Daher TBM 850 | 97 | 36% | — | Patient money | Three months, and a one-in-three chance of a cut. |
| Oct 29 | A12 | Cessna 414 | 50 | 12% | 4.7% | Liquid | The twin that sells at the asking price. |
| Oct 30 | A19 | Learjet 45 | 27 | 6% | — | Liquid | Twenty-seven days. The fastest jet off the market. |
| Oct 31 | A20 | Cessna Citation CJ4 | 88 | 17% | — | Patient money | Three months. The slowest Citation. |
| Nov 1 | A13 | Piper Navajo | 45 | 9% | flat | Liquid | Nine percent cut rate, and the price stopped falling years ago. |
| spare | A4 | Cessna 182Q Skylane | 35 | 13% | — | Liquid | Five weeks, and the price almost never moves. |
| spare | A7 | Piper Arrow | 49 | 20% | 1.3% | Average | Loses about one percent a year. Takes seven weeks. One in five gets cut. |
| spare | A8 | Cessna 185 Skywagon | 58 | 19% | 0.2% | Average | Loses almost nothing per year, and takes two months to sell. |
| spare | A9 | Cirrus SR22 | 53 | 22% | 6.0% | Average | Sells in under two months, one in five gets cut, loses six percent a year. |
| spare | A10 | Cirrus SR22T | 56 | 27% | 6.1% | Average | More than one in four get a price cut before they sell. |
| spare | A16 | Cessna 310 | 59 | 44% | flat | Patient money | The price can't fall with age any more, so sellers cut it instead. |

## Static posts (carousels, stat cards) — already rendered and hosted

Images live at `https://uiprgookspqnvyumkyse.supabase.co/storage/v1/object/public/rendered_videos/social/liq_<id>.png` (carousels `liq_b1_01..08` … `liq_b10_01..08`, stat cards `liq_d1..d15`, Stories poll cards `liq_c1_q/_a … liq_c12`). The full plan with captions and due times is `campaign/liquidity/plan.json`; state (which are already in Buffer) is table `public.social_campaign_posts` (post_id null = not yet scheduled).

**Daily drain (every 6:57 run, after the clip):** run `python3 ~/kit/campaign/liquidity/drain.py --auto` — it reads `plan.json` and the table, counts the Buffer queue per channel, and schedules the earliest unscheduled posts while keeping at most 8 scheduled per channel (Buffer free plan limit 10); then it prints `key post_id` lines — record them with `update public.social_campaign_posts set post_id='…', scheduled_at=now() where key='…'`. Instagram carousels go out at 18:00Z, stat cards at 22:00Z, LinkedIn carousels at 17:00Z. Stories polls (`liq_c*`) cannot be scheduled through the API; they are for manual posting from the phone (question card, then answer card).
