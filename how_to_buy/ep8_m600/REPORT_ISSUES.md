# Ep8 (N665WA) — report issues

The live report was **not captured** in the 2026-11-02 run (capture exit 3, report locked: the capture grant could not be written). The items below come from running the report's own RPC (`get_aircraft_valuation(..., 'M600')`) against Supabase and are expected to appear in the report. Confirm on capture.

1. **Valuation comps include the subject aircraft** (N665WA at $2,875,000 is one of its own 23 comps).
2. **Cross-source duplicates counted twice**: N501RL, N87SL, N519TL each appear twice in the 23.
3. **Stale comps**: about 10 of the 23 tails (e.g. N501RL, N325ST, N813LP, N726GB, N87SL, N35PK, N695ST, N413PN, N27WR, N271Z) are not in the latest scrape.
4. **One "N/A" registration comp** ($2,998,000, 2022, FL) that cannot be de-duplicated.
5. **New-price anchor wrong**: `msrp_new` = $2,573,439 while `model_msrp_history` has 2021 M600/SLS base $3,112,116 (equipped $3,300,000); `msrp_retention_pct` 91.0 is built on the wrong anchor.
6. **Price floor/ceiling very wide**: $1,286,720 – $4,117,502.
7. **Forecast fair value unstable** (`model_price_forecasts`): $2.70M–$3.07M between consecutive weeks (internal, not shown in report).
8. Registry sync glitch: `aircraft_transactions` shows a registration_removed / new_registration pair on Aug 26–27 2026 with the same owner and certificate date; if the report's ownership timeline shows this as a transfer, it is wrong.
