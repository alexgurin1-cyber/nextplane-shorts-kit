# Ep8 status — 2026-11-02

- **Stopped before production. No video made or uploaded.** The capture account could not open the N665WA report (`report_capture.py` exit 3, locked) because the per-tail grant insert into `public.purchased_reports` was blocked by this run's permission check.
- Done: hero picked (N665WA, 2021 Piper M600 SLS, $2,875,000 from $2,990,000, Kansas dealer), DATA_PACK.md, draft SCRIPT.md (report-dependent lines marked [REPORT]), REPORT_ISSUES.md (expected issues from the valuation RPC).
- To finish: create the grant (SQL in DATA_PACK.md, "Capture grant"), capture, cross-check, finalise SCRIPT.md, then production from Ep7's src/ (r_head.py + r_scenes.py pattern). The Wednesday 2026-11-04 16:00Z slot needs the upload by Tuesday.
