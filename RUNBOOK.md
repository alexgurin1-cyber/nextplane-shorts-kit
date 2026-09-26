# NextPlane Weekday Short — cloud runbook

This is the procedure for the "Weekday NextPlane Short" scheduled task. It runs entirely in a Claude cloud session: **no access to Alex's Mac is required or expected.** Do not request folder access to the Mac.

## 0. Bootstrap (about 2 minutes)

1. Clone this repository: `git clone https://github.com/alexgurin1-cyber/nextplane-shorts-kit.git ~/kit`. If the repository is not attached to the session, attach it with `add_repo` (owner `alexgurin1-cyber`, repo `nextplane-shorts-kit`) and clone again.
2. Read the credentials from memory and write `~/.nextplane.env` (chmod 600), one `KEY="value"` per line:
   - `ELEVENLABS_API_KEY` ← memory `reference-elevenlabs-key`
   - `GEMINI_API_KEY` ← memory `reference-gemini-key`
   - `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` ← memory `reference-youtube-oauth`
   Never commit this file or print keys into deliverables.
3. `source ~/kit/setup.sh <topic_slug>` exports `KIT` and `WORK=/tmp/<topic_slug>`, copies the fonts, the logo and `endcard.py` into `$WORK`, and verifies YouTube authentication.
4. Optionally run `python3 $KIT/qa/smoke_test.py`, a zero-cost environment check.

## 1. Topic

Read memory in this order: `project-shorts-queue`, `feedback-format-rotation`, `feedback-shorts-topic-lens`, `feedback-cost-first-structure`, `feedback-no-source-sites`, and the most recent `project-*-video` files. The newest file names the next format and any open candidate topics.
- Rotate the five formats: CLASSIC ANALYST, QUIZ, POV BUYER, STORY-OF-ONE, AD TEARDOWN. Never use the same skeleton twice in a row.
- Check for repeats against memory and against the channel's recent titles: `python3 $KIT/lib/yt.py slots 50`.
- If the queue is empty, mine Supabase (project `uiprgookspqnvyumkyse`) for a fresh, verifiable anomaly specific to a brand or model, framed through the buyer's four questions: deal, resale, ownership cost, value for price.

## 2. Data pack

Pull every number from Supabase through the Supabase connector, with the corruption guardrails:
- Never quote jet listing prices or jet sold medians. Piston asking prices are clean.
- Exclude share and partnership ads and price-jitter pairs.
- Control every comparison for age or generation.
- The category column is corrupt, so match on model names.
- Verify small-n headline numbers listing by listing.
- Never name Controller or any other source marketplace; attribute data to NextPlane.

Write `$WORK/<slug>_DATA_PACK.md` with the queries behind every claim. See `templates/analyst/buzzwords_DATA_PACK.md` for the expected depth.

## 3. Production

Copy the template for today's format into `$WORK`:

| Format | Template |
|---|---|
| CLASSIC ANALYST | `templates/analyst/` (full set: render, gen_vo, gen_music, mux, fetch, upload, make_logo) |
| STORY-OF-ONE | `templates/story/render.py` |
| QUIZ | `templates/quiz/render.py` |
| POV BUYER | `templates/pov/render.py` |
| AD TEARDOWN | `templates/teardown/render.py` |

Adapt the copy by setting `ROOT = os.environ["WORK"]` in place of the hard-coded `/tmp/...`, then change the beats, scenes and numbers. For formats other than analyst, reuse `gen_vo.py`, `gen_music.py` and `mux.py` from `templates/analyst/`.

- **Voiceover:** Tyler Cash, ElevenLabs `eleven_turbo_v2_5` with-timestamps, settings 0.62 / 0.85 / 0.25 / speaker boost. Word timestamps drive the captions and overlay anchors. Never write "..." in VO text.
- **Photos:** use `python3 $KIT/lib/photos.py fetch <slug> "<short query>" $WORK/photos`. Wikimedia returns 429 to cloud IPs, so this tool falls back to CC BY / CC0 Flickr images through Openverse. Real aircraft only; never AI-generated backgrounds. Record every credit.
- **Veo b-roll:** optional, atmosphere and detail beats only. A 429 or 402 from Gemini means the credits are depleted; skip it and note that in the summary.
- **Music:** ElevenLabs Music `/v1/music` with an exact `music_length_ms`, sidechain-ducked under the VO. Run it in the foreground with a long timeout, never backgrounded.
- **Layer 0:**
  - Every statistic is animated.
  - Navy and cyan brand colors; amber only in product UI.
  - Include a report-UI beat.
  - Use the identical end card via `endcard.draw_endcard`.
  - The CTA is verbatim: "Before you call the broker, check the data at NextPlane.us."
- **Rendering:** parallelize with `timeout 500 python3 render.py <s> <NF> 4 &` across 4 processes, then run the mux step.

## 4. QA (required)

- Run `python3 $KIT/qa/check_render.py $WORK/nextplane_<slug>.mp4 --max-duration=105`. It must pass, with a target of 75–100 s at -14±1.5 LUFS.
- Extract 5–7 spot frames with ffmpeg and look at each one to confirm every data beat renders correctly before shipping.

## 5. Deliver

1. Write `<slug>_POST_COPY.md`: three hook-style titles of 70 characters or fewer (question, comparison or dollar-figure format), plus a Layer 0.5 description that converts to nextplane.us rather than summarizing the statistics. Also write `<slug>_FOOTAGE_CREDITS.md`.
2. Write `$WORK/meta.json` as `{"title","description"}`, then upload with `python3 $KIT/lib/yt.py upload $WORK/nextplane_<slug>.mp4 $WORK/meta.json $WORK/<slug>_yt_result.json`. The upload is always private with publishAt set to the next free daily 15:00Z slot at least 24 hours out.
3. Upload the DATA_PACK, POST_COPY, FOOTAGE_CREDITS and yt_result files to the Google Drive folder **"NextPlane Shorts"** (folder id `1wZYvI2CODvCZpSCLSGsy-fe9QXYw5A71`; pass it as parentId). **Do not upload the MP4.** YouTube is the video's home, which keeps Drive storage flat.
4. Email Alex (alex.gurin1@gmail.com) through the Gmail connector. Use a concise, professional tone. Include the topic and format, the one key statistic, the three title options, the YouTube Studio link, the scheduled publish time, and anything that needs his review, such as depleted Veo credits or any data caveat.
5. Update memory: write a new `project-<slug>-video` file and update `project-shorts-queue` if a queued topic was consumed.

## Rules

- Tone is transparency, not judgment.
- Never fabricate or extrapolate beyond the queried data. If the planned topic does not verify, say so and pivot.
- Do not run scrapers in the sandbox.
- If a run fails midway, still email Alex with what failed and where the run stopped.
