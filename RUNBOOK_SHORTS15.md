# NextPlane 15-Second Vertical (TikTok + Instagram Reels) — daily cloud runbook

> **Positioning (Alex, 2026-11-16):** read `brand/POSITIONING.md` before writing any script, title, caption or description. The line is "Know what to offer before you call the seller." Never call the product a history report. The closing line "Don't buy the story, buy the data." is unchanged.

Procedure for the "Daily NextPlane 15-second Short" scheduled task. Runs entirely in a Claude cloud session; never request access to Alex's computer or use Claude in Chrome. The library backfill top-up is STOPPED (Alex, 2026-11-15; see §5).

Approved format (Alex, 2026-10-09): `templates/shorts15/PILOTS.md` (spec + the three pilots: SR20 price jump, A36 same-price twins, Malibu Mirage "what the ad left out"). Code: `templates/shorts15/` (`gen_vo.py`, `gen_music.py`, `render15.py`, `mux15.py`). Market-number clips (added 2026-11-03): `campaign/numbers/` + `scene_num()`, pilot `num_dmg_single`.

## 0. Bootstrap
1. Clone the kit to `~/kit` (attach with `add_repo` owner `alexgurin1-cyber`, repo `nextplane-shorts-kit`, access `push` if needed).
2. Write `~/.nextplane.env` (chmod 600) from memory — never print or commit:
   - `ELEVENLABS_API_KEY` ← `reference-elevenlabs-key`
   - `BUFFER_API_KEY`, `NP_SOCIAL_SECRET` ← `reference-buffer-api`
3. `set -a; . ~/.nextplane.env; set +a; export KIT=~/kit WORK=/tmp/s15_<slug>; mkdir -p $WORK/photos`.

## 1. Pick today's finding (one finding, one or two tails)
Read memory `feedback-plain-language-videos`, `feedback-no-source-sites`, `feedback-real-visuals-only`, `feedback-shorts-report-first`. Then query Supabase project `uiprgookspqnvyumkyse`:
- `select * from social_shorts15 order by run_date desc limit 30` — never reuse a tail number or the same format two days running.
- **SLOT FIRST, THEN TOPIC (Alex, 2026-11-15 — standing).** Run `python3 $KIT/lib/np_buffer.py freeday` first. It returns the
  POST DAY: the first Pacific day (from tomorrow) whose 9:00 AM Pacific slot (16:00Z PDT / 17:00Z PST; a post due 15:00–18:59Z
  counts as that morning's clip) is free on BOTH TikTok and Instagram. Both channels get the clip on that day at
  `np_buffer.py slot <day>`. The topic lane is the lane of the POST DAY's weekday, not of today. If the POST DAY is more than
  seven days ahead, or a channel already holds 10 scheduled posts (Buffer free plan), produce nothing and send the ACTION NEEDED
  email (§6). Never move, edit or delete posts this run did not create.
- **Topic lanes by weekday of the POST DAY (Alex approved 2026-11-15; changed 2026-11-16 to put product demonstrations first):**

  | POST DAY | Lane | Formats |
  |---|---|---|
  | Mon | REPORT DEMO | §1d — live report on one Cirrus (until 2026-11-30) for sale now |
  | Tue | ONE AIRPLANE, ONE FINDING | always SELLER STRATEGY (§1b), alternating DEALER / OWNER |
  | Wed | BUYER EDUCATION | NUMBER — DAMAGE / TRAINING / SELLER OWNERSHIP / PRICED HIGHER (§4c) or NUMBER — LIQUIDITY (§1c), LIQUIDITY every other Wednesday |
  | Thu | REPORT DEMO | §1d; WHAT THE AD LEFT OUT, SAME PRICE TWINS or PRICE HISTORY may be the demo's angle, but the report must be on screen |
  | Fri | REPORT DEMO | §1d |
  | Sat | DIRECTOR ON CAMERA | produced separately in Google Vids — skip to the next free day, unless Saturday is today/tomorrow and empty (then ONE DOLLAR FIGURE) |
  | Sun | ONE DOLLAR FIGURE | §4c number template with a dollar figure (`dollar=True` in `NUM`), pilot `num_dol_c182cut` |

  COST OF OWNING is no longer in the rotation (fallback only). Fallback order: REPORT DEMO → ONE DOLLAR FIGURE → BUYER EDUCATION → COST OF OWNING.
  Evening STAND CONVERSATION clips (Tue/Thu 22:00Z) are produced separately and do not occupy the morning slot.
  If a lane has no candidate that verifies, use the next lane in the list and record `fallback=` in notes.
- **Target segment (Alex, 2026-11-03):** single-engine pistons only (Cirrus SR20/SR22/SR22T; Cessna 172/182, 150/152, 177, 206,
  210; Bonanza A36/G36/F33A/V35; Piper PA-46 piston, PA-28, PA-32; Mooney M20; Diamond DA40/DA20). Never twins, turboprops
  (incl. M500/M600/M700, TBM, PC-12, Caravan), jets or helicopters, not even in a comparison or count. No family leads more than
  two clips in a week (count the 22:00Z stand clips too); favour Cirrus, Cessna 182/172, Bonanza, PA-46.
- **ONE DOLLAR FIGURE:** one verified dollar amount about one popular model (typical price cut in dollars, depreciation per day,
  top vs bottom ask for the same model and year). Exact figure on screen, plain dollars in the VO, basis on screen in a few words
  ("ASKING PRICES · US · <date>"); asking prices are never called sale prices. Kinds so far: typical cut (`num_dol_c182cut`, `num_dol_pa46cut`;
  `dollar=True`) and same model + same year, lowest vs highest ask (`num_dol_g36gap`, `range=[asks]` + `axis=` in `NUM`: price
  axis with one dot per airplane, bracket, the gap); check FAA year/serial and every ad of each tail before using a range.
  Keep `grid_note` and `subject` short (about 45 / 38 characters) or they run past the panel edge; drop parts planes and
  odd currency-converted first asks (count the cut from the next recorded price).
  If the VO runs over 15.0 s, set a per-slug `SPEED` (≤ 1.1) in gen_vo.py rather than cutting the opening question. Opening: the buyer's question about that model,
  then the number; end on why the report matters for that airplane (stamp e.g. "SEE EVERY CUT ON YOURS"), not "Is yours one of them?".
- **Single-airplane angles (now only as the angle of a Thursday REPORT DEMO):** PRICE HISTORY: prefer an airplane now priced **higher** than before (relisted higher, or raised in the same ad —
  Alex 2026-11-03 liked the SR20 N881PF case, $279,900 → $354,900) when one verifies row by row (both ads, dates and
  prices, not a reverted cut); otherwise a cut sequence. Older log rows use format "PRICE JUMP"; treat them as PRICE HISTORY.
  Never reuse a tail from `social_shorts15`.
- **Opening rule (Alex, 2026-11-15, memory feedback_plain_language_videos):** the first two seconds state the buyer's situation
  and one doubt as a direct question; never "you want to make sure". SELLER STRATEGY keeps its own opening and CTA.
- The aircraft must be **currently listed** (verify in the latest scan), piston (never quote jet prices), US, not a share/partnership ad, and the finding must be verifiable row by row (ad ids, dates, prices, NTSB number + serial match). Write `$WORK/DATA.md` with the exact queries and rows.
- Never name Controller or any source marketplace.

## 1b. SELLER STRATEGY (Tuesday; lane ONE AIRPLANE, ONE FINDING — Alex approved 2026-11-15)
Pilots and reasoning: project doc `claude/seller-side-samples-dealer-and-llc-2026-11-15.md`. The clip is about the SELLER, with one
airplane as the example. Alternate (check the last `subformat=` in `social_shorts15.notes`):
- **DEALER** — `dealer_stats_monthly` latest snapshot: avg_pct_vs_market (scored_listings >= 5), pct_with_price_cut, median_dom_sold
  (sold_total >= 5), listings and sales since first_listing_seen, vs the median US dealer meeting the same thresholds (2026-11-01:
  about +3% vs market, about 27% cut, about 58 days). Types: HOLDS FIRM (>= +10%, cuts <= 20%), STARTS HIGH THEN CUTS (>= +10%,
  cuts >= 40%), PRICES TO SELL (at/below market, sells <= 45 days), VOLUME DEALER (50+ listings). Example: one of its listed
  single-engine airplanes (days for sale, cut or not, from aircraft_listings / aircraft_price_history) — never its asking price.
- **OWNER** (for sale by owner) — all three must hold: ad seller_type private; registered owner (aircraft_master, LLC or
  individual) holds exactly 1 aircraft; the ad seller_name appears on exactly 1 tail in aircraft_listings this year. Say "an LLC
  [a private owner] with no other airplane for sale this year" (data starts April 2026: "this year", never "in the last year").
  Screen: chips FOR SALE BY OWNER / AN LLC / NO OTHER AIRPLANE FOR SALE IN <year>, the price step chart from the start of beat 2,
  a stamp such as "3 CUTS SINCE JUNE".
- Script (~30–38 words): b1 "Do you know the selling strategy of the dealer [owner] behind this airplane?"; b2 measured behaviour
  only (model: "This one asks a quarter above market and rarely cuts. This Skylane: seven months, no cut."); b3 own CTA
  "Before you call the broker, find out their strategy at NextPlane dot U S." (owner: "Before you call, find out their strategy at
  NextPlane dot U S."). Never voice a motive or a prediction.
- Anonymity: never show or say the dealer's/owner's name, city, state, the tail, or anything identifying; model photos only (not
  the ad's), every registration blurred; lookup card "YOUR N-NUMBER". Same dealer or tail not within eight weeks (store dealer_id
  and tail in `basis=`; also check `social_campaign_posts` campaign = seller_strategy_pilot: dealer of N735AB, and N9020G).
- Production: `hook_question()`, `scene_dlr5()` (dealer), `scene_llc6()` (owner) in render15.py (lookup title "FIND OUT THEIR
  STRATEGY", end card from "at NextPlane", 2.6 s). If the kit lacks scene_dlr5, apply Drive file 1zpQZFBY6qHuVVJQtBwiiPSCj68I6L9ye
  ("nextplane-kit-patch-seller-strategy-2026-11-15.patch") with `git am` and push. Copy the scene per clip; change only numbers,
  word anchors, chips, photos.
- Caption: the same question, the seller's numbers in one or two sentences, one sentence of buyer meaning inside the data, "plug the
  N-number into nextplane.us before you call", credits, <= 5 hashtags.

## 1c. NUMBER — LIQUIDITY (BUYER EDUCATION, every other Wednesday — Alex approved 2026-11-15)
Question: "How fast does a <model> sell, and how many sellers cut the price?" for ONE single-engine piston model/family, in the
style of the October Piper Dakota clip. Figures: median days on market of sold listings and the share of sold listings with at
least one cut (optionally yearly value change), from the same sold-listing SQL as the October liquidity_check clips
(`campaign/liquidity/` queries and the `liq*` render template) — never run `campaign/liquidity/drain.py`, never rank models, no
twins/turboprops/jets. Needs >= 20 sold airplanes; show the count ("of 66 sold"). No model reused within eight weeks (check
`social_shorts15` notes and the October liquidity_check rows). Log format = BUYER EDUCATION, subformat = NUMBER — LIQUIDITY.

## 1d. REPORT DEMO (Mon/Thu/Fri — Alex, 2026-11-16; first edition demo_sr22n656, 2026-11-17)
Positioning: "Know what to offer before you call the seller", $29 per airplane. Show the live report on ONE single-engine piston
for sale right now (status active, last_seen_at within 4 days, US N-number, asking price, not a share ad).
- CIRRUS FIRST: until 2026-11-30 every demo is an SR20/SR22/SR22T, rotating model and generation (G2, G3, G5, G6, G7), never the
  same model in two consecutive demos; from 2026-12-01 at least every other demo is a Cirrus. Never reuse a tail from
  social_shorts15 (check ALL rows, including old SAME PRICE TWINS pairs), social_campaign_posts or a YouTube video.
- Pick the candidate whose report most changes the offer, verified row by row: ask >= 5% off the report's estimated value, 2+ cuts,
  90+ days for sale, an accident record the ad omits, a clear seller pattern, or two live ads that disagree on price.
- Capture: `python3 $KIT/lib/report_capture.py <tail> $WORK/report` (capture login from memory reference-nextplane-capture-login).
  Exit 3 (locked): one other candidate, then the next lane with fallback=REPORT DEMO (capture locked). Never fake a report screen.
- Panels: `python3 demo_crop.py $WORK/report/sec_XX_*.png $WORK/rc/<name>.png x0,y0,x1,y1 --blur ...` — crop NARROW (about
  400–550 px of the 1600 px section, so the text is about 2x on the vertical frame), blur seller/dealer/owner names, phones,
  addresses and source labels/fine print, and look at every crop. Charts with dealer legends: crop the legend out. Leave >= 15 px
  of margin left and right: the gentle push-in (1.035) clips the panel edges. Before choosing a tail also check the How to Buy
  cohort lists (how_to_buy/*/src/cohort.py) — tails in a published YouTube chart count as used. `psize` in DEMO shrinks the hook
  price for 7-figure asks (168 for $1,084,900).
- Script (30–38 words, ≤ 15.0 s total; the CTA beat alone is ~4.1 s, so b1 + b2 must stay under ~9 s): b1 names the airplane
  and asks one doubt (rotate price, time on market, seller, accident record, usage, engine); b2 "The report: ..." the one answer;
  b3 the verbatim CTA. Further figures (e.g. the estimated value) go on screen only.
- Render: add `DEMO[<slug>]` (hook photo, backdrop, label, price, question, panels with their word anchors, callout boxes in
  940-px panel coordinates, chip, stamp) and `CAPS[<slug>]` in render15.py; slugs start `demo_` → `scene_demo()`, GAP 0.75 s
  before the CTA, lookup card shows the real tail and "$29 PER AIRPLANE".
- Caption: the same question, the report's answer in one or two sentences, "Plug the N-number into nextplane.us before you call —
  $29 per airplane.", credits, <= 5 hashtags. Data pack: `campaign/demo/DATA_<yyyymmdd>_<tail>.md`.
- Log format = REPORT DEMO, subformat = PRICE | TIME ON MARKET | SELLER | ACCIDENT RECORD | USAGE | ENGINE.

## 2. Script (≈30–36 words, three beats)
- b1 hook: asking price + model; b2 the one finding; b3 the verbatim CTA "Before you call the broker, check the data at NextPlane dot U S."
- Plain-language standard: speak prices in plain dollars ("about three hundred fifty-five thousand dollars", never "three fifty-four nine"); exact figures go on screen; ≤20-word sentences; no jargon (say "federal accident record", not "NTSB" alone).
- Instagram caption: plain takeaway first, then "Plug the N-number into nextplane.us before you call.", then credits line, then **at most 5 hashtags** (Instagram rejects more): `#aviation #generalaviation #aircraftforsale #<make> #nextplane`. TikTok uses the same text.
- **LINK RULE (Alex, 2026-10-26, every post on every channel):** each caption carries the tracked report link `https://nextplane.us/aircraft-report?utm_source=<platform>&utm_medium=social` (platform = tiktok | instagram | linkedin | youtube). On Instagram and TikTok, where caption URLs are not tappable, the caption also carries the line "Run any N-number — link in bio." directly above the URL (the bio link on both profiles points at the same page). `lib/np_buffer.py post` and `lib/yt.py upload` add the block automatically through `lib/np_link.py` when it is missing, placing it after the body and before the hashtags; do not write your own link line, and confirm the URL is present in the Buffer post text returned by `np_buffer.py queue`. Report the URL used per channel in the summary email.

## 3. Produce
- Copy `templates/shorts15/*` into `$WORK`, `cd $WORK`. Edit `gen_vo.py` (add today's slug to dict `S`; keep earlier entries, the slug argument selects one), `gen_music.py` (add one prompt to `P`, not monotone), and `render15.py`: add `CAPS[<slug>]`, a `scene_<slug>()` modeled on the closest pilot scene, and the `SCENE` / `TAILS` maps. Keep the platform safe zones (text in x 64–940, y 210–1440), `lookup()` beat and `draw_endcard` untouched.
- Landscape-only photos (common for older models): use `blur_backdrop()` + `photo_card()` as in `scene_pa32()` instead of a full-bleed crop, which upscales ~5x and looks soft. Blur other aircraft's registrations with a feathered mask.
- Photos: `python3 $KIT/lib/photos.py fetch <slug> "<make model>" $WORK/photos` — real photos of the exact model only; blur other aircraft's registrations with `python3 $KIT/lib/blur_reg.py in.jpg out.jpg x0,y0,x1,y1` (check a crop of the result); record CC credits.
- `python3 gen_vo.py <slug>` (check no SMEAR; total must stay ≤15.0 s — check `python3 render15.py <slug> info`, trim beat 2 if over) → `python3 gen_music.py <slug>` (retries 429s on its own) → render frames in 4 workers: `for w in 0 1 2 3; do timeout 500 python3 render15.py <slug> $w 4 & done; wait` → `python3 mux15.py <slug>` → `nextplane15_<slug>.mp4`.
- QA: 12–15 s, 1080×1920, audio 48 kHz, -13.5 LUFS ±1; extract frames at 1 s, hook, finding, lookup, end card and **look at them** (numbers match DATA.md, nothing cropped by safe zones, captions legible). Fix and re-render on any failure.

## 4. Publish
- `url=$(python3 $KIT/lib/social_upload.py s15_<slug>_<yyyymmdd> nextplane15_<slug>.mp4)`.
- Both channels on the POST DAY from §1: `due=$(python3 $KIT/lib/np_buffer.py slot <POST_DAY>)`, then
  `python3 $KIT/lib/np_buffer.py post tt "$url" $due caption.txt` and the same with `ig` (never different days per channel).
  Confirm the link block with `np_buffer.py queue <tt_id> <ig_id>`.
- Insert a row into `social_shorts15` (run_date, slug, format, tails, hook, video_url, tt_post_id, ig_post_id, due_at, notes) — see §6 for format and notes.

## 4b. First-of-the-month PRICE CUTS set (Alex, 2026-10-30 — standing)
**Segment update (Alex, 2026-11-03, standing): all three clips are single-engine piston — (1) all single-engine pistons, (2) Cirrus
SR20/SR22/SR22T, (3) Cessna 172/182 (swap for Bonanza, Piper singles, Mooney or Diamond when that family had more airplanes cut);
no twin or turboprop clip any more; add a make/model filter to price_cuts.sql for the family clips. First automatic edition Dec 1.**
Original 2026-10-30 set (superseded): `cuts_single`, `cuts_twin`,
`cuts_turboprop` ("So you want to buy a <category>? <N> got a price cut in <last month>. <M> in <month before>...").
- Numbers: run `campaign/price_cuts/price_cuts.sql` with m0 = first day of the month three months back, m1 = first day of
  this month. Count airplanes, not cuts. Claim a rise only when the month-over-month change is large (≥25%); otherwise state
  the two counts. Record the table in `campaign/price_cuts/DATA_<yyyymm>.md` (template: DATA.md).
- Production: same template; edit the three `CUTS[...]` entries in `render15.py` (months, share chip, word indices), the
  three `S[...]` scripts in `gen_vo.py` (month names and spoken counts) and the captions in `campaign/price_cuts/cap_*.txt`
  (month names, counts, share, photo credits). Keep the hook photos (registration blurred) or fetch new ones for variety.
- Schedule: TikTok and Instagram at 16:00Z on the next three free consecutive days, single → twin → turboprop
  (`np_buffer.py queue` first). Log the six post ids in `public.social_campaign_posts` with campaign = `price_cuts_monthly`
  (key `cuts_<cat>_<yyyymm>_<tt|ig>`); do **not** insert into `social_shorts15` (run_date is its primary key).
- The daily rotation resumes on the 2nd. No backfill (stopped 2026-11-15).
- Idempotency: before producing, check `select key from social_campaign_posts where campaign='price_cuts_monthly' and key like 'cuts_%_<yyyymm>_%'`
  (yyyymm = the month just ended). If the six rows already exist (e.g. the Oct 2026 edition, produced manually on 2026-10-30 and
  queued Nov 2–4), skip production entirely: no rotation clip and no cuts clips that day — only the backfill top-up and the email.

## 4c. NUMBER clips (BUYER EDUCATION Wednesdays and the ONE DOLLAR FIGURE template — Alex, 2026-11-03, lanes 2026-11-15)
Spec, kinds, subject rotation and wording rules: `campaign/numbers/README.md`. SQL: `campaign/numbers/numbers.sql`
(replace `{category}` / `{model_re}`, one kind per call). Pilot: slug `num_dmg_single` (`NUM`, `CAPS`, `S`, `P` entries).
- Pick the next subject for the day's kind from the README rotation that has not run in the last 8 weeks
  (`select slug, run_date from social_shorts15 where slug like 'num_<kind>%' order by run_date desc`, plus
  `select key from social_campaign_posts where campaign='numbers_pilot'` — the pilot num_dmg_single used dmg / all singles).
- Run the kind's query, write `campaign/numbers/DATA_<yyyymmdd>.md` (query, output row, the plain fraction and how it
  was rounded) and commit it. Row-check: open 5 counted tails and confirm each one meets the definition (for `dmg`, the
  NTSB number and serial; for `trn`, the reason it counted; for `up`, both prices and dates). Drop the clip and use the
  next kind if the rows do not hold up.
- Script per the README (b2 always ends "Is yours one of them?"; exact counts on screen, plain fraction spoken).
- Production as §3 with `scene_num()`; `TAILS` is automatically `YOUR N-NUMBER`. Blur every visible registration in the
  photos so no real airplane is tied to the number.
- Caption: plain takeaway first ("One in six single-engine airplanes for sale has a damage history. 113 ads don't
  mention a federal accident record."), then "Is yours one of them? Plug the N-number into nextplane.us before you
  call.", credits, ≤ 5 hashtags. Link rule as §2.
- Publish as §4; log to `social_shorts15` with format `NUMBER — <KIND>`, tails `{MODEL:<subject>}`, hook = the count line.

## 5. Library backfill top-up — STOPPED (Alex, 2026-11-15)
Do not run it: queue no older long Shorts to Instagram and none to LinkedIn, and leave `social_backfill` untouched. Reason: too
many posts of the same type; the evening backfill repeated the single-airplane lane and LinkedIn consumer clips were not watched.
The October liquidity campaign is also over (no campaign posts, no `drain.py`); only §1c LIQUIDITY clips are allowed.

## 6. Report (Alex, 2026-11-15 — standing)
No routine summary email. The "NextPlane morning social brief" task reads `social_shorts15`, so the row is the report:
- format = the lane name exactly: REPORT DEMO, ONE DOLLAR FIGURE, ONE AIRPLANE, ONE FINDING, BUYER EDUCATION, COST OF OWNING.
- notes = `lane=<lane>; subformat=<PRICE | TIME ON MARKET | SELLER | ACCIDENT RECORD | USAGE | ENGINE (REPORT DEMO) | WHAT THE AD LEFT OUT | SELLER STRATEGY — DEALER | SELLER STRATEGY — OWNER | NUMBER — DAMAGE HISTORY | NUMBER — LIQUIDITY | ... | none>; source=NextPlane render pipeline (real photos, synthetic voice); length_s=<s>; post_day=<YYYY-MM-DD>; basis=<table/view, filter and date behind the on-screen figure; dealer_id/tail for seller clips>; title=<= 60 chars>; fallback=<planned lane or none>`
- hook, tails, video_url, tt_post_id, ig_post_id, due_at as before.
Email only when the run fails or needs a decision: to avg@nextplane.us only, subject "ACTION NEEDED — NextPlane daily clip …",
formal register, stating what failed and where it stopped (also when the POST DAY is > 7 days out or a channel holds 10 posts).
Commit improvements to the template back to the kit with a clear message.
