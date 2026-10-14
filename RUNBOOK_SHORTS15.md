# NextPlane 15-Second Vertical (TikTok + Instagram Reels) — daily cloud runbook

Procedure for the "Daily NextPlane 15-second Short" scheduled task. Runs entirely in a Claude cloud session; never request access to Alex's Mac. Each run also tops up the long-Short library backfill to Instagram and LinkedIn.

Approved format (Alex, 2026-10-09): `templates/shorts15/PILOTS.md` (spec + the three pilots: SR20 price jump, A36 same-price twins, Malibu Mirage "what the ad left out"). Code: `templates/shorts15/` (`gen_vo.py`, `gen_music.py`, `render15.py`, `mux15.py`).

## 0. Bootstrap
1. Clone the kit to `~/kit` (attach with `add_repo` owner `alexgurin1-cyber`, repo `nextplane-shorts-kit`, access `push` if needed).
2. Write `~/.nextplane.env` (chmod 600) from memory — never print or commit:
   - `ELEVENLABS_API_KEY` ← `reference-elevenlabs-key`
   - `BUFFER_API_KEY`, `NP_SOCIAL_SECRET` ← `reference-buffer-api`
3. `set -a; . ~/.nextplane.env; set +a; export KIT=~/kit WORK=/tmp/s15_<slug>; mkdir -p $WORK/photos`.

## 1. Pick today's finding (one finding, one or two tails)
Read memory `feedback-plain-language-videos`, `feedback-no-source-sites`, `feedback-real-visuals-only`, `feedback-shorts-report-first`. Then query Supabase project `uiprgookspqnvyumkyse`:
- `select * from social_shorts15 order by run_date desc limit 30` — never reuse a tail number or the same format two days running.
- Rotate the three proven formats: **PRICE JUMP** (same airplane, price moved between ads / relisted higher or lower), **SAME PRICE TWINS** (two of the same model at the same ask, histories differ), **WHAT THE AD LEFT OUT** (ad claim vs NTSB record / title trail / prior ad). A new format is allowed only if it keeps the hook→one report finding→lookup→end card spine.
- The aircraft must be **currently listed** (verify in the latest scan), piston (never quote jet prices), US, not a share/partnership ad, and the finding must be verifiable row by row (ad ids, dates, prices, NTSB number + serial match). Write `$WORK/DATA.md` with the exact queries and rows.
- Never name Controller or any source marketplace.

## 2. Script (≈30–36 words, three beats)
- b1 hook: asking price + model; b2 the one finding; b3 the verbatim CTA "Before you call the broker, check the data at NextPlane dot U S."
- Plain-language standard: speak prices in plain dollars ("about three hundred fifty-five thousand dollars", never "three fifty-four nine"); exact figures go on screen; ≤20-word sentences; no jargon (say "federal accident record", not "NTSB" alone).
- Instagram caption: plain takeaway first, then "Plug the N-number into nextplane.us before you call.", then credits line, then **at most 5 hashtags** (Instagram rejects more): `#aviation #generalaviation #aircraftforsale #<make> #nextplane`. TikTok uses the same text.

## 3. Produce
- Copy `templates/shorts15/*` into `$WORK`, `cd $WORK`. Edit `gen_vo.py` (add today's slug to dict `S`; keep earlier entries, the slug argument selects one), `gen_music.py` (add one prompt to `P`, not monotone), and `render15.py`: add `CAPS[<slug>]`, a `scene_<slug>()` modeled on the closest pilot scene, and the `SCENE` / `TAILS` maps. Keep the platform safe zones (text in x 64–940, y 210–1440), `lookup()` beat and `draw_endcard` untouched.
- Landscape-only photos (common for older models): use `blur_backdrop()` + `photo_card()` as in `scene_pa32()` instead of a full-bleed crop, which upscales ~5x and looks soft. Blur other aircraft's registrations with a feathered mask.
- Photos: `python3 $KIT/lib/photos.py fetch <slug> "<make model>" $WORK/photos` — real photos of the exact model only; crop out other aircraft's registrations; record CC credits.
- `python3 gen_vo.py <slug>` (check no SMEAR; total must stay ≤15.0 s — check `python3 render15.py <slug> info`, trim beat 2 if over) → `python3 gen_music.py <slug>` → render frames in 4 workers: `for w in 0 1 2 3; do timeout 500 python3 render15.py <slug> $w 4 & done; wait` → `python3 mux15.py <slug>` → `nextplane15_<slug>.mp4`.
- QA: 12–15 s, 1080×1920, audio 48 kHz, -13.5 LUFS ±1; extract frames at 1 s, hook, finding, lookup, end card and **look at them** (numbers match DATA.md, nothing cropped by safe zones, captions legible). Fix and re-render on any failure.

## 4. Publish
- `url=$(python3 $KIT/lib/social_upload.py s15_<slug>_<yyyymmdd> nextplane15_<slug>.mp4)`.
- `python3 $KIT/lib/np_buffer.py queue` → choose the next free 16:00Z (9 AM PT) day per channel, independently for TikTok (`tt`) and Instagram (`ig`), starting tomorrow.
- `python3 $KIT/lib/np_buffer.py post tt "$url" <dueISO> caption.txt` and the same with `ig`.
- Insert a row into `social_shorts15` (run_date, slug, format, tails, hook, video_url, tt_post_id, ig_post_id, due_at). `due_at` holds the TikTok time; the Instagram time can differ (IG queue is shared with backfill), so report both in the email.

## 5. Library backfill top-up (every run)
- `select ord,slug,body,ig_tags from social_backfill where ig_post_id is null order by ord limit 1`.
- Video: `https://uiprgookspqnvyumkyse.supabase.co/storage/v1/object/public/rendered_videos/social/<slug>.mp4`.
- IG caption = body + "\n\nLook up any aircraft by N-number — link in bio.\n\n" + ig_tags. Schedule at the day after the latest scheduled backfill `ig_due` at 01:00Z (6 PM PT).
- LinkedIn caption = body + "\n\nLook up any aircraft by N-number: https://nextplane.us\n\n#GeneralAviation #AircraftSales #AviationData". Schedule the next weekday after the latest `li_due` at 15:00Z.
- Update `ig_post_id, ig_due, li_post_id, li_due`. Keep at most 8 scheduled posts per channel (Buffer free plan queue limit 10); skip the top-up if the queue is full.

## 6. Report
Email alex.gurin1@gmail.com (Gmail connector), subject "NextPlane 15s — <date>: <hook>", professional and short: the finding, the tails, scheduled times per channel, the backfill item queued, and any lines simplified for plain language. Attach nothing large; link the public video URL. On any failure, still email what failed and where it stopped. Commit improvements to the template back to the kit with a clear message.
