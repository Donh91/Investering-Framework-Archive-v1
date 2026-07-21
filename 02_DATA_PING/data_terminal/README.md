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
runtime/shadow/artifacts/2026-07-21/data-terminal-shadow-29828218513.zip.b64.part-001 through part-008
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

The eight ordered `.zip.b64.part-*` files concatenate and decode to the exact original GitHub Actions artifact. Their remote Git-blob SHAs were verified individually. This archive does not advance any accepted DATA PING pointer or change framework state.

## Second live bounded capture and diagnostic mega pack

A second independent official-source contact was captured without source substitution, but this execution context could not materialize the complete authoritative raw CSV bytes. The durable package therefore preserves a bounded five-row direct capture, full first-run replay evidence, append-only storage proof and the materialization diagnostic without claiming full historical cross-run parity.

```text
runtime/shadow/artifacts/2026-07-21/second-live-bounded/
```

```yaml
run_id: DT_FRED_WEB_BOUNDED_20260721T172619Z_e053de3a2119
source_response_received: PASS
source_response_fully_materialized: FAIL
bounded_direct_rows: 5
bounded_overlap: PASS_ONE_UNCHANGED_ZERO_REVISED
append_only_storage: PASS
full_history_cross_run_parity: BLOCKED
phase1_completion: NO
archive_parts: 15
zip_sha256: 775c82da645244ba983af219f4e126f526eb229243dc4de49d8dd5e38ae591a8
authority: NON_BINDING
```

The 15 ordered archive parts reconstruct a deterministic 27-file ZIP. This diagnostic does not modify the accepted DATA PING pointer, the latest Data Terminal pointer, any workflow or schedule, framework state or portfolio action.
