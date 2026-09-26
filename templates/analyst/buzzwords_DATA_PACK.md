# DATA PACK — "The Buzzwords" (suffix: bw)
**Autonomous weekday run 2026-09-25 (scheduled task, Alex not present) · Format: CLASSIC ANALYST (archetype #6 since rotation began; prior analysts Sep-3 survivors, Sep-9 age_tax, Sep-16 garage_plane). Buyer lens: Q1 "Am I getting a deal?" + Q4 "What do I get for the price?"**

Queue check: the task-prompt's stored queue (SR22 vs G36, killer-AD) was already consumed in July 2026 (see `project-sr22-g36-video`, `project-killer-ad-video`) — confirmed EMPTY per `project-shorts-queue` and `index.md` as of Sep-24. Mined fresh per format rotation: last shipped Sep-24 was story-of-one (`panel_flip`); classic analyst is least-recently-used (last used Sep-16 `garage_plane`), so this run is analyst, NOT story-of-one.

Topic source: flagged as a "future candidate" in `new_paint_DATA_PACK.md` (Sep-17 run): *"Complete logs" brag (940 ads): -$3,725 vs peers - worth nothing.* Re-verified fresh today and expanded into a full ladder of six common ad-marketing phrases, each matched against same make+model, model-year +/-3 peers that use NONE of the six phrases (a "plain listing" control group).

## Story
Sellers reach for the same handful of phrases to sell an airplane: "complete logs," "always hangared," "no damage history," "one owner since new," "meticulously maintained," "no accident, no corrosion." Buyers read those words as reassurance. The market doesn't price them the same way. One phrase is now so common it carries zero premium. One correlates with a real, repeatable premium. One - the reassurance phrase - actually correlates with a LOWER ask, most likely because it shows up defensively on older, harder-to-place airplanes. Honest framing throughout: this is what the market does with these words, not proof any seller is lying - and it's asking-price correlation, not sold-price causation.

## Method (re-run 2026-09-25, AEROINTEL Supabase `aircraft_listings`)
Base cohort: US listings (`location_country IN ('US','USA')`), registration matches `^N[0-9]` (kills blank/test rows), `asking_price_usd` $30,000-$2,500,000, `total_time_airframe > 0`, description present, share/partnership/fractional listings excluded by text, model year 1960-2026, **deduplicated by registration** (`DISTINCT ON (registration) ... ORDER BY registration, scraped_at DESC`, i.e. latest scrape per tail - kills the duplicate-listing corruption documented in `sr22_vs_g36` and `flip`). `category` column NOT used (documented corrupt at scale); peer grouping is `make` + `model` text match, listing year +/-3 - deliberately finer-grained than the "family" buckets used in other packs, because the question here is "vs a plain ad for the same airplane," not "vs the model line."

Base cohort after cleaning: **6,696 US listings**. Six phrase flags (case-insensitive `ILIKE`, applied to `listing_description`):
- `complete_logs`: "complete log" OR "complete and continuous log" - **449** matched
- `hangared`: "always hangar" OR "hangared since" - **242**
- `no_damage`: "no damage" OR "damage free" OR "damage history" - **482**
- `one_owner`: "one owner" OR "single owner" - **56**
- `meticulous`: "meticulous" (catches "meticulously maintained/cared for") - **199**
- `no_accident`: "no accident" OR "no corrosion" - **75**

For every flagged listing, peer_median = median `asking_price_usd` of same `make`+`model`, model-year within +/-3, excluding that listing itself and excluding ANY listing carrying one of the six phrases (a "plain ad" control), required peer n>=5 (all reported buckets clear this). Baseline = the 4,918 listings with NONE of the six phrases, gone% = share with `status='sold'` (never `is_active`/`delisted_at`, the established sold-signal per `feedback-sold-detection`).

## Verified table (2026-09-25, all n>=5, all peer-n>=5)
| Phrase (verbatim ad language) | n | Median $ gap vs plain peers | % | Gone (sold) | Baseline gone |
|---|---|---|---|---|---|
| **"meticulously maintained" / "meticulous"** | 199 | **+$10,000** | **+3.0%** | 53.3% | 48.8% |
| "always hangared" | 242 | +$5,300 | +2.5% | 51.2% | 48.8% |
| "one owner" / "single owner" | 56 | +$3,000 | +0.4% | 41.1% (small n - not a sell-through claim) | 48.8% |
| "no damage" / "damage history" | 482 | +$1,000 | +0.6% | 55.8% | 48.8% |
| **"complete logs" / "complete and continuous logs"** | 449 | **$0** | **0.0%** | 51.2% | 48.8% |
| "no accident" / "no corrosion" | 75 | **-$9,900** | **-5.7%** | 49.3% | 48.8% |
| Baseline (none of the six phrases) | 4,918 | -- | -- | 48.8% | -- |

## Honesty / confound checks (mandatory before voicing)
- **This is asking-price correlation matched by make+model+year, not a sold-price causal test.** No claim of "the words caused the price."
- **"Meticulous" skews toward newer, more heavily equipped inventory** (spot-checked: top "meticulous" SR22-G6/G7 Turbo listings are 2023-24 near-new aircraft with full GTS packages, $900K-$1.15M) - flowery, confident marketing copy correlates with higher-trim listings, which is itself informative (sellers of a genuinely loaded airplane write a different kind of ad) but is NOT proof the three words themselves add $10,000. Voice as "ads that use this language tend to sell for more," not "this phrase adds $10,000."
- **"No accident / no corrosion" skews OLDER** (avg model year 1981 vs 1991 baseline, 1994 for "meticulous") - a defensive, reassurance-style phrase that shows up more on vintage airframes trying to head off a buyer's #1 worry. The negative correlation is very plausibly the phrase being a symptom of a harder-to-place airplane, not the words themselves scaring buyers off. Frame as "the plane doesn't need reassuring; when the ad reaches for it, buyers may be reading between the lines" - transparency, not accusation.
- Small-n flags: one_owner (n=56) and no_accident (n=75) are moderate, not thin - both clear the n>=5 peer bar comfortably and hold at the aggregate level, but are voiced with an n on screen.
- "Complete logs" prevalence (449 of 6,696 = 6.7%) confirms it's now close to a baseline expectation, not a differentiator - consistent with the Sep-17 `new_paint` pack's prior read (then -$3,725, n=940 on a looser cohort/date) that flagged it "worth nothing" - direction reproduces exactly; today's cleaner matched-peer design lands at $0 rather than a small negative, which is a tighter, more defensible number, not a contradiction (both say: no real premium).

## Hero listings (real ads, spot-verified 2026-09-25)
- **N6690J** - 1968 Piper Cherokee 140, 3,805 TT, $43,000, SOLD. Ad (verbatim, in part): "TT 3805 SMOH 611, Mattituck... All AD's complied with and my new parts. Complete logbooks. No damage history. Flys great. $43,000.00" - a plain, relatable everyday airplane, and the words didn't move the number: sold at the low end of its own comp set.
- **N976TM** - 2023 Cirrus SR22T G6 Turbo, 632 TT, $950,000, SOLD. Ad (in part): "...a beautifully equipped and meticulously maintained aircraft that represents the pinnacle of modern personal aviation..." - same brand of confident language, six figures apart in stakes; illustrates the honesty caveat (loaded, late-model inventory talks like this).
- Contrast card device: same six words, two completely different airplanes - the number moves with the airplane, not the adjective.

## Beat-ready claims (what the VO says)
1. HOOK: An ad says "complete logs." Nice words. They're worth exactly $0.
2. METHOD (one line): NextPlane compared 449 "complete logs" ads to same-model, same-era listings that don't say it.
3. LADDER (ranked bars): meticulously maintained +$10,000 (n=199) -> always hangared +$5,300 (n=242) -> one owner +$3,000 (n=56) -> no damage history +$1,000 (n=482, "basically nothing") -> complete logs $0 (n=449) -> no accident/no corrosion -$9,900 (n=75).
4. TWIST: the one phrase that should reassure you the most - "no accident, no corrosion" - correlates with a LOWER price. It shows up more on older airplanes. The plane that doesn't need to say it, usually doesn't.
5. HERO CARDS: N6690J $43,000 Cherokee 140 ("complete logs, no damage history") vs N976TM $950,000 SR22T ("meticulously maintained") - same script, different stakes.
6. HONEST: this is what buyers pay next to those words, not proof the words caused it; asking prices, not sold prices; "meticulous" tracks with newer, better-equipped inventory - the adjective and the airplane travel together.
7. REPORT UI beat: a NextPlane aircraft report reads the actual maintenance and ownership record instead of the ad copy - "run the tail number, don't grade the adjectives."
8. CTA + end card verbatim.

## Not voiced / dropped this run
- Per-family breakdowns (SR22-only, Cherokee-only) for each phrase - n too thin per family once split six ways.
- "Low time" / "non-smoker" - dropped: "low time" is a real, verifiable data field elsewhere on the platform (not a pure-language test); "non-smoker" n=1, unusable.
- "Pride of ownership" (n=24) and "must see" (n=26) - too thin to report a stable median gap.

## Queries (re-run recipe)
Base CTE `clean` = `DISTINCT ON (registration)` over `aircraft_listings` with the filters above, `ORDER BY registration, scraped_at DESC`. `flagged` CTE adds the six boolean `ILIKE` flags. `peers` CTE: correlated subqueries for `peer_median` (`percentile_cont(0.5)`) and `peer_n`, keyed on `make = make AND model = model AND year BETWEEN year-3 AND year+3 AND registration <> self AND` no phrase flags true. Aggregate median gap = `percentile_cont(0.5) WITHIN GROUP (ORDER BY asking_price_usd - peer_median)`; pct = `percentile_cont(0.5)` of `asking_price_usd/peer_median - 1`. All numbers reproduced live 2026-09-25 via Supabase `execute_sql` on project `uiprgookspqnvyumkyse`.

## Gemini/Veo status this run
Not attempted - consistent depleted-credits pattern every run since 2026-07-16 (`new_paint`, `six_seat_tax`, `garage_plane`, `rent_line`, `panel_flip` all logged 429/402). Photo-only Ken Burns treatment, real Wikimedia Commons photos for aircraft identity (CC0/PD/CC-BY only). Alex should top up at aistudio.google.com/billing if fresh AI b-roll is wanted again.
