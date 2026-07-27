# BACKTEST BUILD intake audit — batch 01

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
intake_batch_id: BACKTEST_BUILD_INTAKE_20260727_BATCH_01
uploaded_files: 10
exact_existing_audit_duplicates: 7
new_lineage_checkpoints: 3
zip_crc_failures: 0
detached_checksum_mismatches: 0
owner_dataset_effect: NONE_PENDING_CORRECTED_FINAL_MASTER_UPLOAD
test_execution: LOCKED
```

## Decision

The batch is accepted as source and lineage evidence.

Seven packages match already audited GitHub identities exactly and are deduplicated by SHA-256. They are not re-added as independent datasets:

| Package role | SHA-256 | Existing audit |
|---|---|---:|
| Base checkpoint | `b70bd0c86aa76c968a06003ad3e83c63214675777d94a5af4dfb3859f6c67dcd` | PR #168 |
| OKX Phase 03 | `f1348699c9dca52eb3ab51696ffced66e6cb2840e157384320162ad8bc4916b0` | PR #173 |
| OKX Phase 04 | `28bf9d3fa71342731b01081fe1b1ee15be87c3244e9003e8470e1b49739989a3` | PR #173 |
| OKX Phase 05 | `5114f3c99bfcdf47b08f14edded44386c8ae02c2c9fc2e53d1d3cbe36496a93e` | PR #174 |
| OKX Phase 06 | `7686e30631aba300a4c1fb09ca4e79b22e753eb3880fb7b3a81a07ccb4d83f9d` | PR #174 |
| OKX Phase 07 | `27e81b820aa6a7b86071a7c4a5adf09ffbac864b9d720664f3f510dc0bef5db9` | PR #175 |
| TDBC v1 | `e83d3b95e94fba331767feae92bd052ed7f752a1a5305d63621030b293bc5d4c` | PR #171 |

Three FRED checkpoints are new lineage artifacts and were independently inspected.

## New FRED Phase 01

```yaml
package: DATA_PING_BACKTEST_HISTORY_PACK_20260727T071452Z.zip
bytes: 76624824
sha256: e8d601f9d715bd082c817e4f749541ac80da433c56dfa7e65a9baf003b5b305e
zip_members: 197
nested_predecessor_zips: 9
checksum_entries: 196
checksum_status: PASS
phase: FRED_CORE_ANNUAL_PHASE_01
```

Materialized annual averages:

- DGS2: 51 rows
- DGS10: 65 rows
- VIXCLS: 37 rows
- DTWEXBGS: 21 rows
- total normalized core annual rows: 174
- duplicate and chronology validation: PASS
- missing values remain null and are not zero-filled
- annual values are usable only after year completion and source publication

## New FRED Phase 02

```yaml
package: DATA_PING_BACKTEST_HISTORY_PACK_20260727T093706Z.zip
bytes: 153254475
sha256: 0b777204eeafd71510d8a51fc75dc3007fa2f3a106ea53adebe0d97638193d0f
zip_members: 212
nested_predecessor_zips: 10
checksum_entries: 211
checksum_status: PASS
phase: FRED_CORE_MONTHLY_PHASE_02
```

Adds 79 monthly rows for each of DGS2, DGS10, VIXCLS and DTWEXBGS, 316 rows total, covering 2020-01 through 2026-07.

The 2026-07 rows are not automatically tradable observations. Monthly aggregates require month-end and source publication. Empty source values remain null.

## New FRED Phase 03

```yaml
package: DATA_PING_BACKTEST_HISTORY_PACK_20260727T114012Z.zip
bytes: 930818
sha256: 26df6c5bba68b503ec1744b2ca03b8beecb37ce14abc8f3ced636017b2910521
zip_members: 258
nested_predecessor_zips: 0
checksum_entries: 257
checksum_status: PASS
phase: FRED_RATES_CREDIT_LIQUIDITY_ANNUAL_PHASE_03
```

This package replaces recursive predecessor ZIPs with a hash lineage ledger.

It adds 14 annual series and 504 normalized annual rows:

`DGS3MO`, `DGS5`, `DGS30`, `T10Y2Y`, `DFII10`, `T10YIE`, `BAA10Y`, `BAMLH0A0HYM2`, `DFF`, `EFFR`, `SOFR`, `WALCL`, `WTREGEN`, `RRPONTSYD`.

Independent package validation reports:

```yaml
all_14_series_validation: PASS
duplicate_dates: 0
chronology: PASS
no_zero_fill: true
derived_panel_rows: 73
T10Y2Y_reconciliation_max_abs_error_pct_points: 0.010000000000000675
nominal_real_breakeven_max_abs_residual_pct_points: 0.010000000000000231
third_party_rights_flags:
  - BAA10Y
  - BAMLH0A0HYM2
BAML_history_retention_limited: true
```

## Builder defects retained as warnings

The new FRED checkpoints inherit the same stale top-level manifest fields as the earlier cumulative packages:

- top-level `file_count` remains 70 despite 197, 212 and 258 actual ZIP members;
- total rows remain reported as 2,013;
- earliest timestamp remains 2026-04-18;
- the detached checksum ledgers are current and valid.

These defects affect package summaries, not the independently inspected payload hashes or FRED rows.

## Materialization policy

Intermediate cumulative ZIP binaries are not committed to the repository. They are checkpoints that will be superseded by the corrected final master package.

GitHub preserves:

- exact filenames;
- byte counts;
- SHA-256 identities;
- ZIP and checksum status;
- phase relationships;
- duplicate links;
- coverage and method boundaries;
- audit findings.

The expected owner candidate remains:

`DATA_PING_BACKTEST_HISTORY_PACK_FINAL_20260727T183529Z.zip`

until that exact file is uploaded and passes an independent final-master audit.

## Governance

```yaml
data_collection_declared_complete: YES
final_master_uploaded: NO
canonical_backtest_dataset: NOT_YET
owner_datasets: NOT_FINALIZED
readiness_gate: NOT_PASSED
real_backtest_execution: LOCKED
framework_state_change: NONE
portfolio_action: NONE
```
