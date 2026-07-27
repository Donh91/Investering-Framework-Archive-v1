# BACKTEST BUILD extension audit — Custom GPT phases 05 and 06

**Program:** `FRAMEWORK_BACKTEST_READINESS_BUILD_v1`  
**Program state:** `HISTORICAL_DATA_ACCUMULATION / TEST_EXECUTION_LOCKED`  
**Audit verdict:** `PAYLOAD_INTEGRITY_PASS / SAME_METHOD_COVERAGE_EXTENSION_PASS / CUMULATIVE_METADATA_REPAIR_REQUIRED`

## Supplied artifacts

| Artifact | Bytes | SHA-256 | Disposition |
|---|---:|---|---|
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T054034Z(1).zip` | 4,747,666 | `28bf9d3fa71342731b01081fe1b1ee15be87c3244e9003e8470e1b49739989a3` | exact duplicate of previously archived Phase 04 package; lineage only |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T055608Z.zip` | 9,544,646 | `5114f3c99bfcdf47b08f14edded44386c8ae02c2c9fc2e53d1d3cbe36496a93e` | Phase 05 cumulative package |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260727T062839Z.zip` | 19,137,076 | `7686e30631aba300a4c1fb09ca4e79b22e753eb3880fb7b3a81a07ccb4d83f9d` | Phase 06 latest cumulative package |

The Phase 06 package embeds the Phase 05 package byte-for-byte with the exact expected SHA-256. Phase 05 embeds Phase 04. Only Phase 05 and Phase 06 add new observation coverage.

## Detached checksum validation

```yaml
phase_05_files: 143
phase_05_checksum_entries: 142
phase_05_missing_targets: 0
phase_05_mismatches: 0

phase_06_files: 160
phase_06_checksum_entries: 159
phase_06_missing_targets: 0
phase_06_mismatches: 0
```

Every regular package member except the checksum ledger itself is covered and verified.

## New source coverage

### Phase 05

```yaml
venue: OKX
market_type: PERPETUAL_SWAP
interval: 1Dutc
start: 2022-03-10
end: 2023-01-03
BTC_USDT_SWAP_rows: 300
ETH_USDT_SWAP_rows: 300
ETHBTC_derived_rows: 300
```

### Phase 06

```yaml
venue: OKX
market_type: PERPETUAL_SWAP
interval: 1Dutc
start: 2021-05-14
end: 2022-03-09
BTC_USDT_SWAP_rows: 300
ETH_USDT_SWAP_rows: 300
ETHBTC_derived_rows: 300
```

### Cumulative Phase 01–06 result

```yaml
continuous_start_utc: 2021-05-14T00:00:00Z
continuous_end_utc: 2026-04-17T00:00:00Z
BTC_direct_swap_rows: 1800
ETH_direct_swap_rows: 1800
ETHBTC_derived_rows: 1800
phase_boundary_gaps: 0
duplicate_dates_per_series: 0
direct_OHLC_failures: 0
all_direct_rows_settled: YES
```

Independent inspection of the six new normalized files confirmed exact row counts, date ranges, uniqueness and OHLC invariants.

## Authority boundary

The BTC and ETH rows are direct venue-specific OKX perpetual-swap history. The ETH/BTC series is calculated from the two USDT swap instruments and remains:

`DERIVED_NOT_DIRECT`

It may support relative-performance research but has no authority for H7, direct ETH/BTC settlement gates or venue-specific ETH/BTC execution claims.

The existing 2026-04-18 through 2026-07-24 index-proxy period remains a different method. It must not be silently concatenated with the swap series.

## Persistent package-builder defects

The source payloads and detached checksum ledgers pass, but the inherited cumulative manifest summaries remain stale:

```yaml
phase_06_actual_regular_files: 160
manifest_file_count: 70
phase_01_to_06_normalized_extension_rows: 5400
manifest_total_rectangular_and_event_rows: 2013
actual_earliest_swap_date: 2021-05-14
manifest_earliest_materialized_timestamp: 2026-04-18
```

The manifest file inventory remains inherited rather than fully rebuilt, and the self-referential manifest design remains unsuitable. These are packaging defects, not row corruption.

## Decision

```yaml
phase_05_source_identity: ACCEPTED
phase_06_source_identity: ACCEPTED
latest_custom_gpt_cumulative_candidate: DATA_PING_BACKTEST_HISTORY_PACK_20260727T062839Z.zip
duplicate_phase_04_upload: DEDUPLICATED
canonical_backtest_dataset: NOT_YET
owner_dataset_selection: NOT_FINALIZED
raw_binary_materialization: DEFERRED_DURING_ACTIVE_CUMULATIVE_COLLECTION
test_execution: LOCKED
historical_edge_claim: NONE
framework_state_change: NONE
portfolio_action: NONE
next_collection_task: PHASE_07_DAILY_OKX_SWAP_OLDER_PAGE
next_cursor_ms: 1620950400000
```