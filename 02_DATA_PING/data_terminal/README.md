# Data Terminal Phase 1 - Shadow Pilot

This directory owns source collection evidence, source health, immutable receipts, sanitized shadow snapshots and non-binding DATA PING handoff candidates.

It does **not** own market interpretation, gates, scores, accepted DATA PING state, framework ratification or portfolio action.

## Phase 1 pilot

- Source: free public FRED CSV.
- Pilot series: `DGS10`, context-only macro observation.
- Runtime: standard-library Python only.
- Missing values remain `UNKNOWN`; they are never converted to zero.
- Direct and derived values are labelled separately.
- Source substitution is explicit and disabled in the pilot.
- Payload and receipt SHA-256 values provide reproducibility evidence.
- Historical receipts and snapshots are append-only by contract.
- `latest_*` files are sanitized shadow pointers, not canonical framework pointers.

## Local deterministic run

```bash
python -m unittest discover -s tests/data_terminal -p 'test_*.py'
python scripts/data_terminal/fred_csv_collector.py \
  --fixture tests/data_terminal/fixtures/fred_csv_macro_core.csv \
  --retrieval-timestamp 2026-07-19T12:00:00Z \
  --output-dir .data-terminal-output
```

A stale, empty, malformed or unavailable source is an explicit non-PASS result. No silent fallback is permitted.
