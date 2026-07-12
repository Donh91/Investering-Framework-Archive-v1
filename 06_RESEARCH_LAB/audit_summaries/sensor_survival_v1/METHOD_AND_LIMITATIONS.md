# Method, Evidence Classes and Limitations

## Inputs

- `ULTIMATE SENSOR AUDIT ROWS.csv`
- `M1 PULLBACK WEATHER ROWS 2026-07-08.csv`
- `M2 SENSOR COMBO ROWS 2026-07-08.csv`
- `btc regime.csv`
- `btc spliced.csv`
- Truth-Layer CMC BTC.D derived features
- Full Sensor Simulation M1 and M4 outputs
- DeFiLlama-derived stablecoin and DEX state frame

## Analysis design

1. Role-specific M1 timing and ablation rather than a blended score.
2. Frequency-matched random-date event alignment with 14/21/30/45-day windows.
3. BTC.D matched random-date, sign-flip, threshold, delay and circular-shift tests.
4. Weekly non-overlapping M4 samples.
5. Expanding-window out-of-sample Ridge/logistic models with horizon embargo.
6. Paired moving-block bootstrap for incremental MAE.
7. HAC-adjusted partial-correlation diagnostics.
8. Exact reconstruction of the M4 one-day-lagged, three-day-persistent strategy plus extra-latency tests.
9. Year, walk-forward regime, real-time regime and rolling 26-week transportability.

## Evidence boundary

- M1 has a small, single-cycle event sample.
- M1/M2 denominator eligibility is inconsistent unless PW01's exclusion is explicitly justified.
- M4 daily overlapping rows are descriptive; primary inference uses weekly non-overlapping samples.
- OOS results remain modest-sample and are not sufficient for threshold promotion.
- No historical frozen altcoin breadth exists, so the full rotation-survival gate cannot be evaluated.
- Stablecoin source-revision histories are unavailable; latency tests approximate operational availability but do not measure actual revisions.
- No full point-in-time holdings/action-size ledger exists; no full portfolio backtest is claimed.

## Red-team verdict class

`MODIFY_EXISTING_TESTS` — the audit refines T2/T3/T4/T6/T8/T9 and current rule owners. It is not a new engine or parallel scoring system.
