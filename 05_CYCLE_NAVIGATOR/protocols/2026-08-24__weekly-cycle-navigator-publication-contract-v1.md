# Weekly Cycle Navigator Publication Contract v1

Status: ACTIVE_PUBLICATION_CONTRACT

## Purpose

Every Monday Cycle Navigator must be generated only after the final durable Master Monday package for the completed ISO week exists. The resulting Cycle Navigator is a user-facing communication and forecast artifact derived from Master Monday, not a second source of market truth.

## Required Monday order

1. Final completed ISO-week evidence freeze.
2. Final Master Monday calibration, scorecard, operational translation and delivery pointer.
3. Cycle Navigator evaluation of the immediately preceding frozen Cycle Navigator against the just-completed week.
4. Freeze the new Cycle Navigator forecast before any future-week outcome is observed.
5. Materialize all Cycle Navigator variants from the same machine package.
6. Commit and durable-readback all artifacts.

A fixed clock time may be used only as a retry. The primary dependency is the final Master Monday delivery pointer for the target ISO week.

## Required durable artifacts per issue

Under `05_CYCLE_NAVIGATOR/weekly/YYYY/Www/`:

- `CYCLE_NAVIGATOR_MACHINE_PACKAGE.json`
- `CYCLE_NAVIGATOR_SCORECARD.json`
- `CYCLE_NAVIGATOR_FORECAST_FREEZE.json`
- `CYCLE_NAVIGATOR_READABLE.md`
- `CYCLE_NAVIGATOR_X_READY.md`
- `CYCLE_NAVIGATOR_SOURCE_MANIFEST.json`
- `CYCLE_NAVIGATOR_DELIVERY_POINTER.json`

Global pointers/ledgers:

- `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`
- `05_CYCLE_NAVIGATOR/track_record/CN_TRACK_RECORD_LEDGER.jsonl`

Published X copies remain immutable under `05_CYCLE_NAVIGATOR/published/YYYY/`. `X_READY` is never silently relabelled as `X_PUBLISHED`. An exact published copy is archived only when an external publication receipt or exact confirmed post text exists.

## Precision and reproducibility

Each issue must freeze the exact forward claims needed for next Monday's evaluation. At minimum this includes any BTC and ETH ranges, structural/regime calls, ETH/BTC conditions, breadth conditions, market-cap transmission state, anticipation windows, scoring method/version and source hashes.

The public continuity score must be stored separately from scientific evidence claims. A communication score cannot be treated as validated model edge. Missing historical artifacts remain `UNAVAILABLE`; they must never be silently reconstructed.

## User-facing retrieval semantics

When a DATA PING/main analysis thread receives:

- `master monday`: resolve the latest final `MASTER_MONDAY_REPORT.md` and present a readable user-facing summary.
- `cycle navigator`: resolve `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json` and return `CYCLE_NAVIGATOR_READABLE.md`.
- `cycle navigator til x`: return `CYCLE_NAVIGATOR_X_READY.md` for the current issue, or the immutable exact published artifact when the user explicitly asks for a prior published post.

These are user-facing outputs, not "internal" variants.

## Authority firewall

Cycle Navigator may summarize, forecast and communicate the final Master Monday state. It may not modify Master Monday evidence, canonical thresholds, portfolio execution authority, market-rule semantics or retrospective outcomes. Research/shadow evidence may be mentioned only with its recorded authority and may not be promoted by publication prose.
