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

## Verified live pilot archive

The first verified network-backed Phase 1 pilot is preserved as immutable shadow evidence:

```text
runtime/shadow/artifacts/2026-07-21/data-terminal-shadow-29828218513.zip.b64
runtime/shadow/artifacts/2026-07-21/data-terminal-shadow-29828218513.manifest.json
runtime/shadow/artifacts/2026-07-21/data-terminal-shadow-29828218513.source-health.json
```

Run identity:

```yaml
github_run_id: 29828218513
terminal_run_id: DT_FRED_20260721T115849Z_b080365d0c23
acquisition_mode: NETWORK
source: FRED_CSV_MACRO_CORE
series: DGS10
artifact_sha256: ac3e2ad49f265b1cd9ae8b16d97051b875d90974ad7199cd7105143a9bd7cd89
status: VERIFIED_SHADOW_LIVE_PILOT_ARCHIVE
authority: NON_BINDING
```

The `.zip.b64` file is the exact original GitHub Actions artifact encoded as Base64. Decode it to recover the five original JSON outputs. This archive does not advance any accepted DATA PING pointer or change framework state.
