# W31 Master Monday Gap-Fill Source Record

```yaml
root_contract: MASTER_MONDAY_GAP_FILL_PACKAGE_v1
request_id: MM-GAPFILL-2026-W31-20260803-001
run_id: run_20260803_mm_gapfill_001
snapshot_id: snap_20260803_mm_gapfill_001
snapshot_utc: 2026-08-03T09:15:16.328Z
collector_status: PARTIAL
master_monday_input_status: PARTIAL_WITH_EXPLICIT_GAPS
planned_core_actions: 60
attempted_core_actions: 43
PASS: 42
PARTIAL: 1
SKIPPED_RUNTIME_LIMIT: 17
freeze_count: 1
post_freeze_call_count: 0
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Canonical predecessor handling

```yaml
predecessor_scope: CANONICAL_ACCEPTED_MARKET_PREDECESSOR
canonical_predecessor_run_id: run_0bc8a5d0d0464542b29b4d50f2f8e19c
canonical_predecessor_snapshot_id: snap_0e19c112413d471d8270cad1a18148a7
collector_predecessor_id: snap_0e19c112413d471d8270cad1a18148a7
identity_reanchor: PASS
canonical_predecessor_field_values_available: false
canonical_longitudinal_comparison_available: false
```

## Current owner evidence

```yaml
BTCUSDT_last: 62563.89
ETHUSDT_last: 1840.61
ETHBTC_direct: 0.02942
BTC_24h_pct: -1.122
ETH_24h_pct: -1.564
ETHBTC_24h_pct: -0.44
settled_Copenhagen_BTC_close: 63578.00
settled_Copenhagen_ETH_close: 1890.43
settled_Copenhagen_ETHBTC_close: 0.02973
```

## Derivatives

```yaml
BTC_current_funding: 0.00004384
ETH_current_funding: -0.00002474
BTC_three_settled_funding_mean: 0.0000802367
ETH_three_settled_funding_mean: 0.0000352167
BTC_OI_change_1h_pct: 0.5528
BTC_OI_change_4h_pct: 1.7804
BTC_OI_change_24h_pct: 1.8926
ETH_OI_change_1h_pct: 0.9412
ETH_OI_change_4h_pct: 2.1929
ETH_OI_change_24h_pct: 2.6576
BTC_global_long_short_ratio: 2.1377
ETH_global_long_short_ratio: 2.6258
BTC_futures_taker_ratio: 0.8258
ETH_futures_taker_ratio: 0.8228
```

## W31 source coverage

BTCUSDT and ETHUSDT each had 168 settled hourly rows with the already verified W31 aggregate ranges. Daily rows, timestamps and raw-row hashes were not materialized in this package.

## Explicit gaps inside the source package

- canonical predecessor identity was correct, but predecessor market field values were absent;
- breadth aggregate, membership hash and sidecars were not materialized;
- ETF, CFGI, FRED, chain TVL and DEX QA actions were skipped by runtime limit;
- stablecoin chain distribution was available, but global total was unavailable;
- 17 of 60 core actions were not attempted.

The source package did not infer, forward-fill or convert missing data to zero.