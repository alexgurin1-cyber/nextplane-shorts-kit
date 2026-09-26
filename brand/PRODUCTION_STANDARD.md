# NextPlane Clip Production Standard

The rule: **a clip ships only if it passes the QA gate.** No eyeballing, no "looks fine."
Five layers, each with one owner artifact. 2026-06-06.

## Layer 0 — Global brand rules (every NextPlane video, every pipeline)

Added 2026-07-05. These apply before any layer below and override anything that conflicts.

1. **Every statistic is visualized, never just narrated.** If the V/O says a number, the
   screen animates it — bar chart, line chart, timeline, heat map, or comparison graphic.
   Never raw text numbers, never spreadsheets on screen.
2. **At least one proprietary NextPlane visualization per video** (chart, timeline, heat map,
   or comparison table in brand style). The visuals ARE the brand — a viewer should recognize
   a NextPlane report before the logo appears.
3. **Website UI appears whenever a NextPlane feature is explained.** Feature claim → show the
   actual report/dashboard UI, not an abstraction.
4. **Identical ending on every video — canonical end card (locked by Alex 2026-07-23).**
   Dark navy gradient background, then in order: large compass logo (~270px, `logo_for_dark_1600.png`)
   → "NEXTPLANE" wordmark (Barlow Condensed Bold ~150px, off-white, letterspaced, full-width cyan
   underline rule) → "DON'T BUY THE STORY." (white) → "BUY THE DATA." (cyan) → "NEXTPLANE.US" in a
   cyan-outlined rounded pill (Space Mono Bold, white text). NO amber anywhere on the end card.
   Reference implementation: `endcard.py` (project folder) — reuse it, don't redraw. To retrofit a
   finished mp4, use `splice_endcard.py` (keyframe-split + tail re-render + caption-strip carry-over).
   No messaging after this scene.
5. **The CTA is always verbatim:** "Before you call the broker, check the data at NextPlane.us."
6. **The logo is always the canonical asset** from `marketing/brand_assets/` (`logo_for_dark_*.png`
   / `nextplane_logo*.svg`). Never redraw, approximate, or restyle the mark — paste the real file,
   every time it appears (end card, report UI, brand bug).
7. **Language:** never "we pulled the FAA registry" — always "we monitor every FAA transaction."
   Ongoing monitoring, not a one-time data pull. Applies to VO and on-screen copy.

## Layer 0.5 — YouTube Shorts title + description standard

Every Short ships with a title and description in this exact format (paste-ready block lives in
the video's `*_POST_COPY.md`).

**Title** — `[Myth or hook question]. [Data payoff or challenge]` — ≤ 70 characters so nothing
truncates on mobile, sentence case, no clickbait caps, no emoji, no "#Shorts" tag (auto-detected).
The hook must match the video's opening beat so the promise pays off in the first 3 seconds.

**Description** — the description is NOT a summary of the video. Never repeat the video's
statistics or retell its story — the video already did that. The description has one job:
convert the viewer into a visit to nextplane.us. Four blocks, in order:
1. HOOK LINE (≤ 100 chars, above the fold): the question the viewer is now asking themselves.
2. BRIDGE TO ACTION (1–2 sentences): what they can DO about it right now — run any tail number
   at NextPlane and see the full ownership history for themselves. Tease, don't spoil.
3. CTA verbatim + link: "Before you call the broker, check the data at NextPlane.us" → https://nextplane.us
4. SOURCE LINE ("Data: FAA Aircraft Registry — NextPlane monitors every FAA transaction.")
   + CC-BY footage credits, then standard hashtags `#aviation #generalaviation #aircraftforsale
   #airplaneownership #nextplane` + 2–4 video-specific tags. Nothing after.

## Layer 1 — Asset library (quality backgrounds)

Every beat has aviation footage behind it. No black voids.

- Location: `media-library/video-broll/<category>/` (cockpit, exterior, runway, interior, mechanic, scenic, dashboard)
- Target: **15–20 clips minimum**, 1080x1920-croppable, ≥4s each, 24–30fps
- Manifest: `media-library/broll_manifest.json` — per clip: category, tags (brand/model if identifiable), mood, license source, safe-crop region
- Grade: every clip passes through one brand filter (the V3 `saturate(0.7) brightness(0.55)` + navy gradient) so footage from different sources looks like one product
- Sources: Pexels/Coverr (free, commercial OK), own airport footage, stills with Ken Burns moves as fallback
- Selection is automatic: brief JSON names a category, render script picks from manifest — never hardcode a file path in a template

## Layer 2 — Design system (one locked template)

One template, brand-locked. Variants come from data, not from new templates.

- Tokens: navy `#0a0e14` / off-white `#fafafa` / cyan `#4cc8d4`. **No amber** — purge `#f5a623` from RedesignedBeatsV3
- Typography scale: hook 96–120px, data value 140px, caption 44px, source line 28px — minimum readable on a 6" phone
- Safe zones enforced in the root layout component: top 15%, bottom 12%, right 10% kept clear of text
- Skeleton per beat: b-roll background → content card → persistent brand strip → source/methodology band
- Captions component: word-synced, always on (see Layer 4)

## Layer 3 — Charts as code (amazing data visuals)

Charts are **rendered natively in Remotion** — never screenshots. Native = crisp at 1080p, animatable, brand-colored.

Brief JSON carries a `chart` spec:

```json
{
  "chart": {
    "type": "line | bar | comp_dots | gauge",
    "title": "PA-34 Seneca — asking price, 90 days",
    "series": [{ "label": "This aircraft", "points": [[0, 339000], [45, 325000], [78, 301000]] }],
    "highlight": { "point": [78, 301000], "label": "-$38K" },
    "source": "Based on 4,670 active listings"
  }
}
```

Chart component standards:
- Axis lines draw on (0→full width over ~20 frames), values count up, highlight point pulses once
- One highlighted number per chart — the number IS the story; everything else is context
- Always a source line ("Based on N listings, FAA registry") — credibility is the brand
- Reuse the same RPCs that power the report (market_velocity, valuation, comp matrix) so clip data always matches what a buyer sees for $9.99

## Layer 4 — Render standard (the spec every file must meet)

| Property | Standard |
|---|---|
| Resolution / fps | 1080x1920 @ **30 fps** |
| Duration | 12–35s, video length = audio length ±0.5s |
| Audio loudness | **-14 LUFS** integrated (ffmpeg `loudnorm`) |
| Voiceover | covers ≥90% of duration, no silent tail |
| Music bed | -28 to -24 dB under V/O, ducked |
| Captions | burned in, word-synced (Whisper timestamps), inside safe zones |
| Background | aircraft media ≥80% of frames — no black-void frames |
| Encode | h264 CRF 18, yuv420p, AAC 192k |

Post-render audio chain (in `render_from_queue.ts`):
`V/O gen → Whisper align → trim comp to V/O → mix music bed → loudnorm -14 LUFS → mux`

## Layer 5 — QA gate (automated, blocks bad renders)

`brief_pipeline/qa/check_render.py` — runs after every render, exits nonzero on failure:

1. fps == 30, resolution == 1080x1920 (ffprobe)
2. |video_duration − audio_duration| ≤ 0.5s
3. Integrated loudness within -15…-13 LUFS, max true peak ≤ -1 dB
4. Black-frame detection: no frame >90% black after frame 10 (ffmpeg blackdetect)
5. First-frame + mid-frame extracted as PNGs for the approval UI
6. On pass → brief_queue status `ready_for_review`; on fail → `render_failed` + reason

Human approval stays where it is (approval UI) but reviewers now only judge *message*, not technical quality — the gate already guaranteed that.

## Pipeline end-to-end

```
Supabase candidate row
  → brief_generator.py (brief JSON incl. chart spec + broll category)
  → anonymizer gate (exists)
  → Remotion render (V3 template, locked design system)
  → audio chain (V/O + captions + music + loudnorm)
  → QA gate (check_render.py)        ← NEW, blocks bad output
  → approval UI (message review only)
  → Ayrshare post → posted_stories metrics → hook learning loop
```

## Build order

1. `check_render.py` QA gate — catches everything else from day one
2. Fix render command fps + audio chain in `render_from_queue.ts`
3. Chart components (line + bar first; comp_dots, gauge later) + `chart` field in brief schema
4. Captions component with Whisper alignment
5. Purge amber, lock tokens
6. Fill b-roll library + manifest (10–15 clips)
