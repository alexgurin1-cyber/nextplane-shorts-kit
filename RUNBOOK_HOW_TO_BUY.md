# NextPlane "How to Buy a…" weekly episode — cloud runbook

This runbook is for the scheduled task "Weekly how to buy episode", which runs on Mondays. The whole run happens in a Claude cloud session: **no access to Alex's Mac is required or expected.** Do not request folder access or use Claude in Chrome.

## 0. Bootstrap
1. Clone this repository to `~/kit` (attach it first with `add_repo`, owner `alexgurin1-cyber`, repo `nextplane-shorts-kit`, access `push`, if it is not already attached).
2. Write `~/.nextplane.env` (chmod 600) from memory. It needs the same keys as RUNBOOK.md, plus `NEXTPLANE_CAPTURE_EMAIL` and `NEXTPLANE_CAPTURE_PASSWORD` from memory `reference-nextplane-capture-login`. Never commit the file or print keys.
3. Run `source ~/kit/setup.sh htb_<model_slug>`. Install Playwright if it is missing with `npm i -g playwright@1.56.0`, but do not run `playwright install`; the browser is at `/opt/pw-browsers/chromium`.

## 1. Pick the slot, the class and the model
- Read `how_to_buy/SERIES_LOG.md`. The target slot is the first Wednesday on or after today that has no shipped episode, at 16:00:00Z.
- The class alternates from the last shipped episode, so a piston single is followed by high-performance and vice versa. Take the next unused model of that class from the rotation.
- Read memory: `feedback-video-quality-bar`, `feedback-no-source-sites`, `feedback-real-visuals-only`, `project-buyer-questions-series`, `project-report-data-integrity`, and `areas/video-shorts-pipeline`.

## 2. Pick ONE real aircraft for sale (Supabase `uiprgookspqnvyumkyse`)
The aircraft must meet all of these:
- active in the latest scrape;
- a published asking price, not "call for price";
- a valid N-number;
- enough same-model comparables for the report's valuation and comps sections to populate.

Prefer an aircraft with something to teach, such as a price cut, several owners, an AD item or a damage record.

Check the ask against the raw listing row. Exclude share or partnership ads and price-jitter rows.

For the high-performance class, the jet and turboprop price guardrail still applies to fleet medians. Verify the hero's individual ask on the listing row, and quote only that.

## 3. Capture the live report
- Run `python3 $KIT/lib/report_capture.py <N-number> $WORK/report`. It signs in, captures one 1600×900 PNG per section, and writes `sections.json` with the text of each section.
- **Exit code 3 means the report is still locked.** Stop production, then:
  - build the data pack and script;
  - commit them under `how_to_buy/ep<N>_<slug>/`;
  - email Alex that the capture login needs attention.

  Never ship an episode without the real report on screen.
- Mask any private individual's name, for example with a PIL blur box over the owner or seller name when the seller is a person.

## 4. Accuracy cross-check before any section goes on screen
Compare `sections.json` against Supabase:
- price history against `aircraft_price_history`;
- the seller against `seller_name`;
- comps against a per-model IQR gate, flagging share-priced comps;
- flight activity: re-capture once and compare, because it has been nondeterministic.

Known Episode 1 bugs: the price history can show "no price changes"; the seller can be the wrong one; comps can include $65K–$85K share ads.

A section that is wrong is either omitted or replaced by a panel-built card with the correct figure. Every discrepancy goes into `REPORT_ISSUES.md`.

## 5. Script
The script runs 7–9 minutes, about 1,100–1,300 VO words, with numbers written as words and never "...".

| Beat | Content |
|---|---|
| Cold open | The one number from the report a buyer would not expect. |
| Step 1: Where this aircraft sits | Model generations and eras, the price ladder, and where the hero sits on it. |
| Step 2: Section-by-section walkthrough | Ask vs NextPlane estimated value and range, and the verdict. Valuation and comps. Hours vs market. Price history. Ownership and registration: liens, tenure, school or charter use. Flight activity. ADs and maintenance items. Damage or accident records. Cost of ownership and cost per mile. Depreciation. Who is selling (a dealer's business name only if the section is accurate). |
| Step 3: The offer | Grounded in the report plus the panel's cut share, cut size and ≤30-day / >90-day sell shares for the model. Never quote a mean days-on-market. |
| Verdict | Who this aircraft is right for. |
| Close | CTA verbatim: "Before you call the broker, check the data at NextPlane dot U S." |

Tone is transparency, not judgment. Never mock the seller or the aircraft. Every number must trace to a query or to `sections.json`.

## 6. Production (16:9, 1920×1080@30)
- **Slides:** report PNGs, gently zoom-panned, with cyan callout boxes on the figures being discussed. Brand slides in navy/cyan use the kit fonts.
- **Photos:** aircraft identity comes from the listing's photos as they appear inside the report UI, or from `lib/photos.py` (CC0/PD/CC-BY). No AI-generated aircraft or backgrounds.
- **VO and music:** VO with `templates/analyst/gen_vo.py`, using Tyler Cash, `eleven_turbo_v2_5`, 0.62 / 0.85 / 0.25 / speaker boost and word timestamps. Burned phrase captions. Music with `gen_music.py` (for a bed over 5 minutes, generate 2–3 segments and crossfade them), sidechain-ducked, with final loudness -14±1 LUFS.
- **End card:** the locked series end card from `endcard.draw_endcard`, scaled to 16:9.
- **Workspace:** keep it resumable, with separate script, VO, slides, render and assemble steps. Run ffprobe on every segment.

## 7. QA
- Run `python3 $KIT/qa/check_render.py <mp4> --max-duration=600`. Duration and aspect warnings are acceptable for long-form; loudness and stream checks must pass.
- Look at 8–10 spot frames covering every report beat. Every on-screen number must match the data pack, the captions must be in sync, and the end card must be present.

## 8. Deliver
1. Write `POST_COPY.md`:
   - title "How to Buy a <Model>";
   - a description that explains why it matters and what the viewer learns, without restating the narration, with https://nextplane.us and #nextplane first, then #buythedata #aviation #aircraftforsale #generalaviation;
   - YouTube chapters taken from the beat timestamps.
2. Write `$WORK/meta.json` with `{"title","description","publishAt":"<Wed>T16:00:00Z"}`. Then run:
   - `python3 $KIT/lib/yt.py upload <mp4> $WORK/meta.json $WORK/yt_result.json` (private, with publishAt);
   - `python3 $KIT/lib/yt.py playlist-add <id> "How to Buy a…"`;
   - `python3 $KIT/lib/yt.py thumbnail <id> <strongest report frame, 1280x720 jpg>`.
3. Commit the following to this repository under `how_to_buy/ep<N>_<slug>/`: `DATA_PACK.md`, `SCRIPT.md`, `POST_COPY.md`, `REPORT_ISSUES.md`, `FOOTAGE_CREDITS.md`, `yt_result.json` and the source scripts. Never commit the MP4 or report PNGs.
4. Update the row in `how_to_buy/SERIES_LOG.md`, then commit and push to `main`. Fetch and rebase first, because the weekday Shorts task pushes to the same repository.
5. Upload the same text files to the Google Drive folder "NextPlane Shorts" (id `1wZYvI2CODvCZpSCLSGsy-fe9QXYw5A71`). Do not upload the MP4.
6. Email Alex (alex.gurin1@gmail.com) in a concise, professional tone. The subject is "How to Buy a <Model> — ready for review". The body gives:
   - the aircraft, tail and ask;
   - NextPlane's value verdict;
   - the three most useful findings;
   - the YouTube Studio link and the publish time;
   - the report issues found.
7. Update memory with a `project-how-to-buy-ep<N>-<slug>` file.

## Rules
- Do not run scrapers in the sandbox.
- If a run fails midway, still commit what exists and email Alex what failed and where the run stopped.
