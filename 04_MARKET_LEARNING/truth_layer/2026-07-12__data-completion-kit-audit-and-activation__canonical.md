# Data Completion and M3 Forward Kit — Audit and Activation

**Date:** 2026-07-12  
**Status:** CANONICAL_ACTIVATION_RECEIPT  
**Input ZIP:** `INVESTERING_DATA_COMPLETION_AND_M3_FORWARD_KIT_20260712.zip`  
**Outer ZIP SHA-256:** `3cff2c2b6a8668fa43acd91597204999b07d36a15feefbc2780fcf29ae17e949`

## Independent audit

```text
ZIP_FILE_COUNT: 42
OUTER_ZIP_SHA256: PASS
PYTHON_COMPILE: 3/3 PASS
M3_BASELINE_VALIDATOR: PASS
M3_BASELINE_ELIGIBLE_ROWS: 13
M3_BASELINE_EVENT_WINDOWS: 1
M3_BASELINE_SOURCE_FAMILIES: 4
M3_LARGEST_WINDOW_SHARE: 100%
```

### Internal checksum correction

The package-level claim `ZIP-integritet: PASS` requires one qualification.

`CHECKSUMS.sha256` contains a stale self-record for `PACKAGE_MANIFEST.csv`:

```text
DECLARED_SHA256: 8391123e52f3944c07bfef140cb49f45fe723962df5d5b22efebebf15c6cf5e8
ACTUAL_SHA256:   dba85cc54b71490bc49503e5fc919c5220e6b113c5616211b5a8dcc3e61d55be
DECLARED_BYTES: 6283
ACTUAL_BYTES:   6515
```

All other package files matched their declared checksums. The mismatch is isolated to package metadata and does not alter the validated scripts, schemas or M3 baseline. It is preserved as an integrity correction rather than silently repaired.

## DeFiLlama execution activation

A hardened one-shot workflow was installed in:

```text
Donh91/Eksperimenter-framework-
```

Files:

```text
.github/workflows/fetch_defillama_history_manual.yml
scripts/fetch_defillama_history.py
README.md
```

Safety state:

```text
TRIGGER: workflow_dispatch only
SCHEDULE: none
REPOSITORY_PERMISSION: contents read
SECRETS: none
REPOSITORY_WRITE: none
ARTIFACT_RETENTION: 7 days
```

Hardenings beyond the supplied kit:

- raw SHA-256 file generated automatically;
- all 12 endpoint fetches must pass;
- each supply and DEX payload must parse;
- each requested entity must produce normalized rows;
- coverage audit and machine-readable validation are emitted;
- an audit artifact is uploaded even when validation fails;
- the final workflow step then fails truthfully if collection is incomplete;
- concurrency prevents accidental overlapping runs.

Installed commits:

```text
collector: a59c82478a865eba30ea3ebe2d267b5916339f63
workflow:  2dc5102e8ced29e05e8ff78dbbc25e01ddef1ae8
README:    15b8dc950c1f6ffa6fb821f1d1a16451b4b18fd3
```

Manual run issue:

```text
Donh91/Eksperimenter-framework-#1
```

## M3 forward evidence activation

The canonical framework now separates:

1. frozen historical baseline evidence;
2. a prospective append-only forward ledger.

New controls:

```text
04_MARKET_LEARNING/truth_layer/M3_BASELINE_EVENT_WINDOW_MAP_v0_1.csv
04_MARKET_LEARNING/truth_layer/tools/validate_m3_coverage.py
.github/workflows/validate_m3_forward_ledger.yml
```

The forward ledger schema was hardened to require:

- event-window ID;
- exact UTC issuance timestamp;
- source run/forecast ID;
- exact source excerpt;
- framework acceptance timestamp when applicable;
- source commit receipt;
- source excerpt SHA-256;
- append status;
- blank outcome status at decision creation.

Coverage remains:

```text
ELIGIBLE_ROWS_TOTAL: 13
INDEPENDENT_EVENT_WINDOWS: 1
SOURCE_FAMILIES: 4
LARGEST_WINDOW_CONCENTRATION: 100%
M3_LEDGER_COVERAGE_READY: NO
```

The CI workflow is read-only and produces an auditable validation artifact. Passing the extraction gates authorizes governance review only, not scoring or promotion.

## BTC.D status

```text
FULL_M1_BTC_D_READY: NO
BLOCKER: ONE MANUAL TRADINGVIEW DAILY CSV EXPORT
SYMBOL: CRYPTOCAP:BTC.D
INTERVAL: 1D
START: 2023-01-01
```

No direct-source series was fabricated or substituted.

## Remaining user actions

1. Manually run the installed DeFiLlama workflow and upload its artifact.
2. Export the required TradingView BTC.D CSV and upload the unedited file.

## Boundary

No market call.  
No portfolio action.  
No outcome scoring.  
No rule ratification.
