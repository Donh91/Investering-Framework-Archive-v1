# R1_06 — TEST REPORT

## Local isolated R1 regression

`18 / 18 PASS`

The dedicated R1 suite covered the full minimum scientific-validity matrix, including fail-closed non-identifying behavior, pre-R1 quarantine, 13-week identifying versus non-identifying coverage math, frozen dependency-map hashing, REBUY/TRIM non-synthesis, unchanged 32/18 profiles, no Minimal, fixed 72h epoch math, metadata-only receipts, child-independent coverage monitoring, and direct materializer import behavior.

## GitHub PR #341 CI

PR head: `48f2d69f8f490402ae7728a5562cb7e5c8deb365`

All nine observed pull-request workflows completed SUCCESS:

- Backtest Wave 1.2 Foundation
- Automation Production Health Gate
- Full Architecture 1-7 Gate
- Data Architecture Gate
- Backtest Engine Foundation
- Backtest Wave 1.4 Prospective Accumulation
- Storage Health Gate
- Daily Capture Architecture Gate
- Continuity Learning Gate

The prospective workflow ran 36 tests total, all PASS, including all 18 new R1 tests plus the pre-existing prospective/blinded tests.

The same workflow emitted metadata-only coverage with `paired_receipt_count = 0`, all identifying row/window counts = 0, `b2_coverage_ready = false` for every primary lane, `comparison_metrics_calculated = false`, and `b2_analysis_authorized = false`.

## Runtime collection policy

No market-data workflow was manually triggered. The import failure was repaired and CI-tested; natural scheduled post-merge readback is intentionally left to the existing cadence.
