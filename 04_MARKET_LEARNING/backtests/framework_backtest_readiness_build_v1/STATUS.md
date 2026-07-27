# FRAMEWORK BACKTEST READINESS BUILD v1

**Short name:** `BACKTEST BUILD`  
**Current phase:** `HISTORICAL_DATA_ACCUMULATION`  
**Status:** `COLLECTION_ACTIVE / TEST_EXECUTION_LOCKED`  
**Authority:** Readiness, source QA and archive coordination only. No market, forecast, portfolio or canonical-state authority.

## Governing rule

No replay, hypothesis test, economic backtest, parameter selection, significance test, rule promotion or portfolio inference may run before the program reaches:

`READY_FOR_CONTROLLED_BACKTEST_EXECUTION`

## Current gate state

```yaml
custom_gpt_collection: ACTIVE
claude_package: PENDING
additional_packages_expected: YES
source_archiving: ACTIVE
independent_integrity_audit: ACTIVE
raw_binary_materialization: LATEST_CUMULATIVE_PACK_PENDING_BATCH_CLOSE
deduplication: PARTIAL
owner_datasets: NOT_FINALIZED
point_in_time_lineage: INCOMPLETE
replay_safe_builders: NOT_READY
golden_fixture_execution: LOCKED
economic_test_execution: LOCKED
final_test_matrix: NOT_RATIFIED
framework_state_change: NONE
portfolio_action: NONE
```

## Readiness gate

The program remains locked until all of the following are complete:

1. expected Custom GPT and Claude packages received;
2. package lineage and hashes verified;
3. duplicate and superseded payloads mapped;
4. owner dataset selected for every test family;
5. point-in-time, publication-time and survivorship controls passed;
6. manifests and validation scripts repaired;
7. replay-safe builders validated against locked schemas;
8. W30 golden fixture prepared and independently approved;
9. final test matrix ratified;
10. explicit status set to `READY_FOR_CONTROLLED_BACKTEST_EXECUTION`.

## Current cumulative collection milestone

The latest received cumulative Custom GPT package is:

`DATA_PING_BACKTEST_HISTORY_PACK_20260726T220615Z.zip`

It includes its 21:43 predecessor package and earlier source packages as embedded predecessors.

Current newly verified direct daily coverage:

```yaml
venue: OKX
market_type: PERPETUAL_SWAP
instruments:
  - BTC-USDT-SWAP
  - ETH-USDT-SWAP
interval: 1Dutc
continuous_start: 2024-08-26T00:00:00Z
continuous_end: 2026-04-17T00:00:00Z
rows_per_direct_instrument: 600
derived_ethbtc_rows: 600
derived_ethbtc_authority: DERIVED_NOT_DIRECT
```

This expands data readiness. It does not unlock test execution.
