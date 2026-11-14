# NUMBER clips — market count → "Is yours one of them?" (Alex, 2026-11-03)

Why: Alex asked for variety in the daily 15-second feed ("something not monotonous every day"). Single-airplane clips
alternate with market-number clips. Each number clip states one verified count about airplanes for sale now, asks
"Is yours one of them?", and sends the viewer to plug the N-number into the report. Spine unchanged:
hook → one number → lookup → end card. Template: `scene_num()` / `NUM[...]` in `templates/shorts15/render15.py`,
slug prefix `num_` (e.g. `num_dmg_sr22`, `num_trn_sr20`, `num_own_single`, `num_up_twin`). Pilot: `num_dmg_single`.

## Kinds (definitions and SQL: `numbers.sql`)
| code | kind | hook chip | what is counted |
|---|---|---|---|
| dmg | DAMAGE HISTORY | DAMAGE HISTORY CHECK | ad discloses damage OR serial-matched federal substantial-damage record; second number = record the ad doesn't mention |
| trn | TRAINING HISTORY | TRAINER CHECK | signs of a trainer or rental life (>250 h/yr, ad history words, school-registered, instructional accident) |
| own | SELLER OWNERSHIP | OWNERSHIP CHECK | current owner registered it under 2 years ago (FAA certificate date, guardrails) |
| up  | PRICED HIGHER | PRICE HISTORY CHECK | current ask above its own first ask or above an earlier ad for the same tail (strict) |

## Subject rotation (keeps every clip's number new)
Each kind cycles through subjects; never repeat the same kind + subject within 8 weeks (check `social_shorts15.slug` AND
`social_campaign_posts` where campaign = 'numbers_pilot'). Already used: dmg / all singles — pilot `num_dmg_single`,
posted TikTok 2026-11-07 and Instagram 2026-11-08 16:00Z (Alex approved 2026-11-03); Cirrus SR22 ran 2026-11-10, so the next dmg subject is Cessna 172.
Damage counts: use tails seen in the last 7 days (drop stale `active` rows), read `damage_notes` for every disclosure
(exclude "No Damage History"/NDH false positives), and never use a stock photo whose tail is in the counted set.
Use a model only when at least 30 are for sale; otherwise use the whole category.
Training counts (2026-11-12): same 7-day freshness base; school-registered names must say flight training / school / academy of
aviation / university / flying club (drop vague "<word> ACADEMY LLC" names, e.g. FIRELIGHT ACADEMY); on 172s only 4 of 13 ad-word
hits held ("perfect flight school aircraft", "ready for a flight school" are suitability, not history).
- dmg: all singles → Cirrus SR22 (used 2026-11-10, `num_dmg_sr22`, 15 of 309) → Cessna 172 → Piper PA-28 → Beechcraft Bonanza → Cessna 182 → Mooney M20 → Cirrus SR20 → twins → turboprops
- trn: Cirrus SR20 (used 2026-11-05, `num_trn_sr20`, 37 of 116) → Cessna 172 (used 2026-11-12, `num_trn_c172`, 38 of 202) → Diamond DA40 → Piper PA-28 → Cessna 150/152 → all singles → Piper Seminole / twins
- own: all singles (used 2026-11-07, `num_own_single`, 603 of 2,687) → Cirrus SR22 → Cessna 172 → Bonanza (used 2026-11-14, `num_own_bonanza`, 35 of 257; SR22/C172 skipped that week by the two-leads-per-family cap, still next) → Cessna 182 → Mooney M20 → Piper PA-28
Ownership counts (2026-11-14): also drop tails whose listing serial differs from the FAA master serial — the registration date then belongs to another airframe (16 of 273 Bonanzas).
- up:  all singles (used 2026-11-08, `num_up_single`, 64 of 2,374; use numbers.sql §4b strict) → Cirrus → Cessna → Piper → Beechcraft → Mooney (use the category when a model has fewer than 5; single-engine pistons only per the 2026-11-03 target segment)

## Script (three beats, ≤ 15.0 s total)
- b1: "Shopping for a <single-engine airplane | Cirrus S R twenty | twin>?"
- b2: plain fraction + what it means, optional second number, then always "Is yours one of them?"
  e.g. "One in six for sale has a damage history. A hundred thirteen ads don't mention it. Is yours one of them?"
- b3: the verbatim CTA "Before you call the broker, check the data at NextPlane dot U S."
- Exact counts on screen ("479 OF 3,001"), plain fraction in the voice ("one in six"); round the fraction honestly
  (22% is "more than one in five", not "one in four"). Count airplanes (tails), never ads or events.
- No unmeasured reasons ("sellers are nervous", "they are hiding it", "flipped it"). State what the data shows.
- Seller ownership is context, not a verdict. Training history is a question to ask, not a defect.

## Production
Same as the daily clip (RUNBOOK_SHORTS15.md §3): add `NUM[slug]`, `CAPS[slug]`, `S[slug]` (gen_vo.py), `P[slug]`
(gen_music.py). Photos: real photos of the subject model (or a representative of the category); blur every visible
registration so no real tail is tied to the number. Record the query output in `campaign/numbers/DATA_<yyyymmdd>.md`.
Log to `social_shorts15` with format = `NUMBER — <KIND>` and tails = `{MODEL:<subject>}`.
