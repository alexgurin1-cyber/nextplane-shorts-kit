# Ep9 status — 2026-11-09 (scheduled cloud run)

- **Blocked at report capture. No video produced, nothing uploaded to YouTube.**
- Model: Beechcraft Bonanza A36 (single-engine piston target segment; SR22 already covered by Ep1).
- Hero: N1811Y, 1981 A36, dealer-listed in Tennessee, ask $360,000 (from $425,000; three cuts, −15.3%, 174 days listed). 5,100 h airframe, 19 h factory-remanufactured engine, G3X + GTN 750Xi + GFC 500. Registered to a Tennessee company since 2004-10-12. No accident record, no service-difficulty reports.
- What stopped the run: the capture grant (`purchased_reports` insert for the capture account) was refused by the run's permission check; `lib/report_capture.py N1811Y` exited 3 (LOCKED). Same block as Ep8.
- Done: DATA_PACK.md (all figures from Supabase, Bonanza/A36 only), SCRIPT.md draft v1 (≈1,270 VO words, plain-language; two **[REPORT]** lines to fill from the capture), REPORT_ISSUES.md, src/cohort.py.
- To finish: (1) Alex runs the grant SQL in DATA_PACK.md; (2) re-run capture, cross-check every section against DATA_PACK.md; (3) fill the two [REPORT] lines; (4) VO, render, QA, upload private with publishAt on the next free Wednesday 16:00Z.
