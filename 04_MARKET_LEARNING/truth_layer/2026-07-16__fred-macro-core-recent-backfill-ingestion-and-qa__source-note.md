# FRED Macro Core Recent Backfill v1.0 - Ingestion, Relevance and Noise Review

**Date:** 2026-07-16  
**Status:** SOURCE_NOTE / PARTIAL_PASS / APPROVED_CURATED  
**Area:** macro truth layer / recent DATA PING gap recovery / revision-aware context  
**Source bundle:** `08_SOURCE_MATERIAL/fred/2026-07-16__fred-macro-core-recent-backfill-v1/`  
**Uploaded ZIP SHA-256:** `e1184a8c5b34dd7aef8a3db747de9094cc4660e9f5f4a7f8bdf0f2b1a475339d`

## 1. Archive decision

```text
ARCHIVE_DECISION: APPROVE_CURATED
CLASSIFICATION: SOURCE_ONLY + RECENT_BACKFILL + REVISION_AWARE_CONTEXT
FULL_HISTORICAL_ARCHIVE: NO
CONTINUOUS_LIVE_MACRO_FEED: NO
CANONICAL_MARKET_CALL: NO
PORTFOLIO_AUTHORITY: NO
RULE_PROMOTION: NO
```

The package is materially relevant because the latest accepted DATA PING V5 explicitly recorded Macro Core as unavailable. It supplies the first source-backed FRED/ALFRED recent backfill for that missing lane.

The package is not archived byte-for-byte as 106 separate repository files. GitHub receives a compact, auditable representation that preserves all normalized observations and all 58 raw Action extracts without duplicating per-series CSV views.

## 2. Independent technical QA

```text
ZIP members: 106
Listed member checksums verified: 105/105 PASS
Required series numeric PASS: 26/27
Required partial: BAA10Y metadata-only
Required failed: 0
Optional metadata-only: BAMLH0A0HYM2
Normalized rows: 227
Raw Action extracts: 58
Duplicate observation dates: 0
Ascending sorting: PASS
Raw versus normalized observation values: PASS
Yield-curve cross-check: 13/13 PASS
Python compilation: PASS
Embedded credentials: NONE
Interpolation: NO
Forward-fill: NO
Fabrication: NO
```

The package validator passed independently.

## 3. Relevant information retained

### High relevance

- nominal Treasury rates and policy rates;
- 10-year real yield;
- official 10Y-2Y and 10Y-3M curve spreads;
- 10-year breakeven inflation;
- broad dollar index;
- NFCI financial conditions;
- Fed balance sheet, reverse repo, Treasury General Account and reserve balances;
- U.S. M2, explicitly not global M2;
- inflation, labor and growth series;
- initial-release versus latest-vintage comparisons;
- exact raw Action responses and source metadata.

### Context visible in the backfill

These are descriptive source movements, not signals:

```text
DGS10: 4.40% to 4.58%, +18 bp
DFII10: 2.19% to 2.33%, +14 bp
DGS2: 4.09% to 4.18%, +9 bp
T10Y2Y: 0.31% to 0.42%, +11 bp
T10Y3M: 0.56% to 0.72%, +16 bp
DTWEXBGS: 121.0559 to 120.5046, -0.46%
NFCI: -0.510 to -0.538
```

The exact-date experimental Fed liquidity proxy increased from USD 5,843,326 million on 1 July to USD 5,958,200 million on 8 July, a change of USD 114,874 million. This is only two aligned weekly points and receives no trend or standalone signal authority.

The revision layer is relevant because it demonstrates non-trivial revisions in payrolls, industrial production, retail sales, M2, CFNAI and GDP. It supports revision-risk awareness, not retrospective timing claims.

## 4. Noise and non-promoted material

The following source-package elements are not promoted as primary GitHub artifacts:

- 28 per-series CSV files, because they duplicate `normalized/all_series_long.csv`;
- `native_frequency_changes.csv`, because percentage changes across rates, index levels, money stocks and labor counts are not directly comparable;
- duplicated JSON and Markdown catalog representations;
- the repetitive request ledger, because exact network timestamps were not exposed by the Action runtime;
- the GitHub Actions workflow, because it depends on a secret and would create unnecessary workflow proliferation;
- BAA10Y and BAMLH0A0HYM2 numeric data, because the source metadata contains redistribution restrictions.

All 58 raw Action extracts are preserved losslessly in one compact JSONL file.

## 5. QA caveats

### Recent backfill, not full history

The original request contemplated history from 2007. This package instead contains a recent missed-data recovery window:

```text
requested recent window: 2026-06-25 through 2026-07-16
actual normalized coverage: 2025-01-01 through 2026-07-15
```

Monthly series use 2026 year-to-date context, and GDP includes 2025 quarters.

### Freshness labels

The package calculates freshness from the observation date. Monthly and quarterly releases are naturally published with lag, so `STALE_QA` can overstate staleness. These labels are retained as source metadata but are not granted canonical operational meaning.

### Revision labels

FRED `output_type=3` includes both new and revised observations. Therefore `RECENT_REVISION_EVENT` does not prove that every marked row changed numerically. Numerical initial-versus-latest differences remain the authoritative revision evidence.

### Reproduction scope

The included Python script is a useful reference fetcher. It does not exactly recreate every derived, validation and documentation artifact in the uploaded package and must not be described as byte-identical reproduction.

## 6. Framework role

Permitted roles:

```text
RATES_CONTEXT
REAL_YIELD_CONTEXT
YIELD_CURVE_CONTEXT
DOLLAR_LIQUIDITY_CONTEXT
FED_LIQUIDITY_COMPONENT
FINANCIAL_CONDITIONS_CONTEXT
INFLATION_CONTEXT
LABOR_CONTEXT
GROWTH_CONTEXT
MONETARY_SUPPLY_CONTEXT
REVISION_RISK_CONTEXT
```

Forbidden interpretations:

```text
GLOBAL_M2
OFFICIAL_GLOBAL_LIQUIDITY
STANDALONE_CRYPTO_SIGNAL
CYCLE_CONFIRMATION
ROTATION_CONFIRMATION
ENTRY_OR_EXIT_TRIGGER
PORTFOLIO_ACTION
```

## 7. Final disposition

```text
SOURCE_ARCHIVE: APPROVED_CURATED
FRAMEWORK_RELEVANCE: HIGH
DATA_PING_GAP_VALUE: HIGH_FOR_RECENT_MACRO_CONTEXT
NOISE_REMOVAL: MATERIAL
FULL_HISTORY_COMPLETION: NO
CONTINUOUS_COLLECTION: NO
WORKFLOW_ACTIVATION: NO
MARKET_CALL: NONE
PORTFOLIO_ACTION: NONE
```
