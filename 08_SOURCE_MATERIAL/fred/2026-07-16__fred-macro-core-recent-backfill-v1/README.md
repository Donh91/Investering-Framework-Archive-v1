# FRED Macro Core Recent Backfill - Curated GitHub Source Archive

**Source package:** `FRED_MACRO_CORE_RECENT_BACKFILL_20260716T070839Z`  
**Source ZIP SHA-256:** `e1184a8c5b34dd7aef8a3db747de9094cc4660e9f5f4a7f8bdf0f2b1a475339d`  
**Archive decision:** `APPROVE_CURATED_SOURCE_ARCHIVE`  
**Role:** `MACRO_CORE_RECENT_BACKFILL_CONTEXT_ONLY`

## Why this is archived

The latest accepted DATA PING V5 still identified Macro Core as unavailable. This package is the first source-backed FRED/ALFRED recent backfill in the canonical archive and materially closes that recent-data gap.

It is not a full historical archive. The numeric package contains 227 native-frequency observations, mainly covering the missed period from 25 June through 16 July 2026, with year-to-date monthly context and GDP observations from 2025.

## Verified quality

- 106 ZIP members
- 105 listed member checksums passed
- 26 of 27 required series passed numerically
- BAA10Y is metadata-only because of redistribution restrictions
- optional BAMLH0A0HYM2 is metadata-only
- 0 duplicate observation dates
- ascending order passed
- raw observation values matched normalized native CSV values
- 13 of 13 yield-curve cross-check rows passed
- no interpolation, forward-fill or fabrication
- Python scripts compiled
- no API key or credential is embedded

## Curated storage design

The uploaded ZIP contains many duplicate representations. GitHub stores only the most useful and auditable subset:

- one long normalized table
- one latest-value snapshot
- one compact operational snapshot
- series catalog
- liquidity-component panel
- yield-curve validation
- revision summary
- compact lossless JSONL of all 58 raw Action extracts
- source validation report and original package checksums
- reference fetcher

Per-series CSV files are omitted because they duplicate `normalized/all_series_long.csv`. The mixed-semantic `native_frequency_changes.csv` is not promoted because percentage changes in rates, indices, levels and labor counts are not directly comparable.

## Interpretation boundary

The data may support:

- rates and real-yield context
- yield-curve context
- dollar-liquidity context
- Fed liquidity-component context
- inflation, labor and growth context
- revision-risk awareness

It may not independently create:

- a cycle call
- a crypto entry or exit
- a portfolio action
- a rule promotion
- a confirmed rotation signal

## Important caveats

1. This is a recent backfill, not a complete 2007-to-present history.
2. The source package marks several monthly and quarterly observations `STALE_QA` by measuring age from the observation date. That can overstate staleness for normally lagged releases and is not used as a canonical signal.
3. FRED `output_type=3` contains new and revised observations. A source-package label of `RECENT_REVISION_EVENT` does not prove that every row was numerically revised.
4. The included reproduction script is a useful source fetcher, but it does not exactly rebuild every derived and documentation file in the uploaded ZIP.
5. No live or scheduled GitHub workflow is archived or activated.
