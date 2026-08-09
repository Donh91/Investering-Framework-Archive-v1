# R1_07 — CODE DIFF / SCOPE AUDIT

Implementation PR: #341 — `R1: repair prospective evidence validity gating`

Base: `8a6e34808aca0e3b0fb70fef12177d1b54b87580`  
PR head: `48f2d69f8f490402ae7728a5562cb7e5c8deb365`  
Merge: `94a7c6744a759e9ad926bfe3b4d19003858d61c2`

GitHub compare scope: 4 files, +395 / -17.

## Modified

- `backtest_engine/blind_dual_run.py`: versions coverage/readiness validity, separates technical pair execution from identifying opportunity, quarantines pre-R1 v2 receipts, preserves fixed 72h math, and prevents same-capture pre-R1 overwrite through the new run-id seed.
- `scripts/daily_capture/materialize_blind_dual_run.py`: adds repository-root import bootstrap only.
- `.github/workflows/backtest-wave1-4-prospective.yml`: runs the R1 regression suite.

## Added

- `tests/backtest_engine/test_blind_dual_run_r1_validity.py`: 18 scientific-validity/runtime regressions.

## Explicitly unchanged

- `backtest_engine/rotation.py` blob remains `49979637f4be9e3acf8bbe7b335ca3642f3212c6`.
- Frozen Full 32 / Reduced 18 identities are unchanged.
- Policy registry is unchanged.
- No market rules, thresholds, gates, weights, or policy semantics changed.
- No new evaluator was created.
