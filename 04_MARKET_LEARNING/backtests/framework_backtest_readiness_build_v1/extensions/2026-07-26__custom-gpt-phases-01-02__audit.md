# BACKTEST BUILD extension audit — Custom GPT phases 01 and 02

**Source timestamps:** 2026-07-26T21:43:18Z and 2026-07-26T22:06:15Z  
**Audit status:** `PAYLOAD_INTEGRITY_PASS / COVERAGE_EXTENSION_PASS / PACKAGE_METADATA_DRIFT_FOUND`  
**Program state:** `HISTORICAL_DATA_ACCUMULATION / TEST_EXECUTION_LOCKED`

## 1. Received packages

| Package | Bytes | SHA-256 | ZIP files | Uncompressed bytes |
|---|---:|---|---:|---:|
| `DATA_PING_BACKTEST_HISTORY_PACK_20260726T214318Z(1).zip` | 541,080 | `4f5ff5e52574106bf158bab3bb24ff70af00355051233edbf7a3e08e5cdba852` | 84 | 1,296,259 |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260726T220615Z.zip` | 1,143,790 | `82bd9761d31125e73404109a0f1af5f443c1e219f513da724d3787e84bc2e2a6` | 95 | 2,238,573 |

The 22:06 package embeds the 21:43 package byte-for-byte with the exact expected SHA-256. It also embeds the earlier 20:56 package and extraction-parts package. The 22:06 package is therefore the current cumulative source candidate; the 21:43 package is preserved as predecessor lineage and should not be counted as independent additional sample coverage.

## 2. Checksum verification

### 21:43 package

```yaml
checksum_entries: 83
checksum_mismatches: 0
missing_checksum_targets: 0
```

### 22:06 package

```yaml
checksum_entries: 94
checksum_mismatches: 0
missing_checksum_targets: 0
```

The detached `CHECKSUMS.sha256` ledgers validate all listed package files, including the final manifest bytes.

## 3. New direct source coverage

Phase 01 adds:

- 300 BTC-USDT-SWAP 1Dutc rows;
- 300 ETH-USDT-SWAP 1Dutc rows;
- 300 separately derived ETH/BTC daily rows;
- range: 2025-06-22 through 2026-04-17 UTC.

Phase 02 adds:

- 300 BTC-USDT-SWAP 1Dutc rows;
- 300 ETH-USDT-SWAP 1Dutc rows;
- 300 separately derived ETH/BTC daily rows;
- range: 2024-08-26 through 2025-06-21 UTC.

Combined phase result:

```yaml
btc_direct_swap_rows: 600
eth_direct_swap_rows: 600
ethbtc_derived_rows: 600
continuous_start_utc: 2024-08-26T00:00:00Z
continuous_end_utc: 2026-04-17T00:00:00Z
phase_boundary_gap_count: 0
duplicate_timestamp_count_per_series: 0
settled_rows: ALL
```

## 4. Independent row-level validation

For both direct instruments across both pages:

- daily timestamps are strictly increasing;
- every adjacent timestamp differs by one UTC day;
- no duplicate timestamps were found;
- all 600 rows per instrument are settled;
- no OHLC invariant violation was found;
- volume fields remain source-labelled;
- venue remains `OKX`;
- market type remains `PERPETUAL_SWAP`;
- interval remains `1Dutc`.

The derived ETH/BTC partitions also contain 600 continuous rows with no duplicate or missing daily timestamps. Their authority remains:

`DERIVED_NOT_DIRECT`

The `high_proxy` and `low_proxy` fields remain cross-divided bounds and are not represented as directly traded ETH/BTC extrema.

## 5. Important remaining method break

The new direct swap series ends on 2026-04-17.

The previously packaged 2026-04-18 through 2026-07-24 daily series is an OKX **index proxy**, not the same perpetual-swap method. Therefore the two periods must not be silently concatenated into one homogeneous price history.

The package correctly queues a future same-method task for the recent swap gap.

## 6. Package metadata drift

Although source rows and detached checksums pass, cumulative package metadata was not fully refreshed.

### 21:43 package

```yaml
actual_zip_file_count: 84
manifest_top_level_file_count: 70
new_normalized_rows_added: 900
manifest_total_rows_still: 2013
manifest_earliest_timestamp_still: 2026-04-18
actual_new_earliest_timestamp: 2025-06-22
```

### 22:06 package

```yaml
actual_zip_file_count: 95
manifest_top_level_file_count: 70
new_normalized_rows_added_across_phases: 1800
manifest_total_rows_still: 2013
manifest_earliest_timestamp_still: 2026-04-18
actual_new_earliest_timestamp: 2024-08-26
```

Under the original row-count convention, the declared total should at minimum be reconsidered from 2,013 to 3,813 after adding 1,800 normalized phase rows. No corrected value is promoted until the package builder defines its semantic row-count contract explicitly.

The manifest's internal `manifest.json` self-entry also remains one generation behind:

- the 21:43 manifest self-entry points to the predecessor manifest bytes;
- the 22:06 manifest self-entry points to the 21:43 manifest bytes.

The detached checksum ledger is correct. The defect is confined to self-referential manifest construction and stale top-level summary fields.

## 7. Readiness effect

These extensions improve the available venue-specific BTC and ETH daily history and provide useful data for future return, drawdown and relative-performance calculations.

They do **not** unlock any test because:

- collection is still active;
- more Custom GPT packages are expected;
- Claude material is pending;
- direct ETH/BTC history remains unavailable;
- recent same-method daily swap coverage remains queued;
- historical derivatives and breadth remain insufficient;
- owner datasets and test matrix are not ratified.

## 8. Decision

```yaml
source_identity: ACCEPTED
payload_integrity: PASS
phase_01_coverage: ACCEPTED_AS_OKX_SWAP_HISTORY
phase_02_coverage: ACCEPTED_AS_OKX_SWAP_HISTORY
latest_cumulative_candidate: DATA_PING_BACKTEST_HISTORY_PACK_20260726T220615Z.zip
intermediate_package_role: EMBEDDED_PREDECESSOR_LINEAGE
canonical_backtest_dataset: NOT_YET
raw_binary_repository_materialization: DEFER_UNTIL_COLLECTION_BATCH_CLOSE
test_execution: LOCKED
historical_edge_claim: NONE
framework_state_change: NONE
portfolio_action: NONE
next_gate: RECEIVE_ADDITIONAL_CUSTOM_GPT_AND_CLAUDE_PACKAGES
```
