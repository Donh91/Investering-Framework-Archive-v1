# BACKTEST BUILD extension audit — Custom GPT phases 03 and 04

**Source timestamps:** 2026-07-27T05:04:35Z and 2026-07-27T05:40:34Z  
**Audit status:** `PAYLOAD_INTEGRITY_PASS / COVERAGE_EXTENSION_PASS / PACKAGE_METADATA_DRIFT_PERSISTS`  
**Program state:** `HISTORICAL_DATA_ACCUMULATION / TEST_EXECUTION_LOCKED`

## 1. Received packages

| Package | Bytes | SHA-256 | ZIP members | Uncompressed bytes |
|---|---:|---|---:|---:|
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T050435Z.zip` | 2,347,642 | `f1348699c9dca52eb3ab51696ffced66e6cb2840e157384320162ad8bc4916b0` | 111 | 3,784,831 |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T054034Z.zip` | 4,747,666 | `28bf9d3fa71342731b01081fe1b1ee15be87c3244e9003e8470e1b49739989a3` | 127 | 6,531,326 |

The 05:40 package embeds the 05:04 package byte-for-byte with exact SHA-256 parity. The 05:04 package likewise embeds the prior 22:06 package. The 05:40 artifact is therefore the latest cumulative candidate; predecessor packages are lineage, not independent extra observations.

## 2. Detached checksum verification

### Phase 03 cumulative package

```yaml
checksum_entries: 110
checksum_mismatches: 0
missing_checksum_targets: 0
```

### Phase 04 cumulative package

```yaml
checksum_entries: 126
checksum_mismatches: 0
missing_checksum_targets: 0
```

The detached checksum ledgers validate every listed member, including the final manifest bytes.

## 3. Phase 03 extension

Phase 03 adds:

- 300 direct BTC-USDT-SWAP daily rows;
- 300 direct ETH-USDT-SWAP daily rows;
- 300 separately derived ETH/BTC daily rows;
- coverage from 2023-10-31 through 2024-08-25 UTC;
- six raw OKX response chunks;
- phase-level continuity, adjacency and row-count validation artifacts.

Independent validation found:

```yaml
raw_rows_per_direct_instrument: 300
normalized_rows_per_direct_instrument: 300
raw_to_normalized_mismatches: 0
duplicate_timestamps: 0
daily_gaps: 0
direct_ohlc_failures: 0
settled_direct_rows: 600_of_600
```

## 4. Phase 04 extension

Phase 04 adds:

- 300 direct BTC-USDT-SWAP daily rows;
- 300 direct ETH-USDT-SWAP daily rows;
- 300 separately derived ETH/BTC daily rows;
- coverage from 2023-01-04 through 2023-10-30 UTC;
- six raw OKX response chunks;
- phase-level continuity, adjacency and row-count validation artifacts.

Independent validation found:

```yaml
raw_rows_per_direct_instrument: 300
normalized_rows_per_direct_instrument: 300
raw_to_normalized_mismatches: 0
duplicate_timestamps: 0
daily_gaps: 0
direct_ohlc_failures: 0
settled_direct_rows: 600_of_600
```

## 5. Combined same-method history

Across phases 01 through 04:

```yaml
venue: OKX
market_type: PERPETUAL_SWAP
interval: 1Dutc
continuous_start_utc: 2023-01-04T00:00:00Z
continuous_end_utc: 2026-04-17T00:00:00Z
BTC_direct_rows: 1200
ETH_direct_rows: 1200
ETHBTC_derived_rows: 1200
phase_boundary_gaps: 0
duplicate_timestamps_per_series: 0
```

All four partitions preserve the same direct schemas for BTC and ETH. The derived ETH/BTC series reproduces:

- open = ETH open / BTC open;
- close = ETH close / BTC close;
- high proxy = ETH high / BTC low;
- low proxy = ETH low / BTC high.

Maximum floating-point reconstruction error was below `1e-16`.

The derived ratio remains `DERIVED_NOT_DIRECT`. It has no authority for H7, direct ETH/BTC settlement gates, or any rule requiring an exchange-traded ETH/BTC close.

## 6. Remaining method break

The same-method swap history ends on 2026-04-17. The previously supplied 2026-04-18 through 2026-07-24 daily series is an OKX index proxy, not a perpetual-swap series.

The two periods must not be silently concatenated. A queued recent-gap task must materialize OKX swap daily rows for 2026-04-18 through 2026-07-24 before a homogeneous continuation is claimed.

## 7. Package metadata drift persists

The source rows and detached checksums pass, but cumulative top-level summaries were not rebuilt.

### 05:04 package

```yaml
actual_zip_member_count: 111
manifest_file_count: 70
new_phase_rows: 900
manifest_total_rows: 2013
actual_earliest_phase_date: 2023-10-31
manifest_earliest_timestamp: 2026-04-18
```

### 05:40 package

```yaml
actual_zip_member_count: 127
manifest_file_count: 70
cumulative_normalized_phase_rows_01_to_04: 3600
manifest_total_rows: 2013
actual_earliest_phase_date: 2023-01-04
manifest_earliest_timestamp: 2026-04-18
```

The final manifest includes the new files in its file ledger and is covered correctly by the detached checksum file. The defect concerns stale top-level summary fields and the inherited self-referential manifest design, not payload corruption.

The package's internal `backtest_readiness_matrix.csv` also predates the governing program lock and the newly received TDBC research. Its `READY_WITH_RESTRICTIONS` labels are package-authored implementation suggestions only. They do not authorize execution.

## 8. Readiness decision

```yaml
source_identity: ACCEPTED
payload_integrity: PASS
phase_03_coverage: ACCEPTED_AS_OKX_SWAP_HISTORY
phase_04_coverage: ACCEPTED_AS_OKX_SWAP_HISTORY
latest_cumulative_candidate: DATA_PING_BACKTEST_HISTORY_PACK_20260727T054034Z.zip
intermediate_package_role: EMBEDDED_PREDECESSOR_LINEAGE
canonical_backtest_dataset: NOT_YET
owner_dataset_selection: PENDING
raw_binary_repository_materialization: DEFER_UNTIL_COLLECTION_BATCH_CLOSE
test_execution: LOCKED
historical_edge_claim: NONE
framework_state_change: NONE
portfolio_action: NONE
next_bounded_source_task: PHASE_05_DAILY_OKX_SWAP_OLDER_PAGE
next_program_gate: RECEIVE_REMAINING_CUSTOM_GPT_AND_CLAUDE_MATERIAL
```

No replay, golden-fixture execution, economic backtest or strategy assessment was performed during this audit.
