# DATA PING Source Record

```yaml
run_id: run_20260803T153028895Z_9c714e2a
snapshot_id: snap_20260803T153028895Z_6b2d8f41
snapshot_utc: 2026-08-03T15:30:28.895Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
source_reported_PASS: 54
source_reported_PARTIAL: 3
source_reported_UNAVAILABLE: 3
optional_SKIPPED_RUNTIME_LIMIT: 1
freeze_count: 1
post_freeze_call_count: 0
collector_predecessor_run_id: run_20260803T122759180Z_7f3c9d1a
collector_predecessor_id: snap_20260803T122759180Z_4b8e2c6f
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Direct market evidence

```yaml
BTCUSDT_last: 63731.00
ETHUSDT_last: 1866.58
ETHBTC_direct: 0.02927
BTC_24h_pct: 0.958
ETH_24h_pct: 0.422
ETHBTC_24h_pct: -0.577
settled_Copenhagen_BTC_close: 63578.00
settled_Copenhagen_ETH_close: 1890.43
settled_Copenhagen_ETHBTC_close: 0.02973
```

## Same-method comparison supplied by collector

```yaml
BTC_change_from_previous_bounded_pct: 1.7557
ETH_change_from_previous_bounded_pct: 1.2844
ETHBTC_change_from_previous_bounded_pct: -0.5099
BTC_current_OI_change_from_previous_pct: -2.1696
ETH_current_OI_change_from_previous_pct: -0.2694
breadth_v1_previous: 0.20
breadth_v1_current: 0.4333333333
breadth_v1_membership_hash_match: true
```

## Derivatives and positioning

```yaml
BTC_current_funding: 0.00003136
ETH_current_funding: 0.00003175
BTC_OI_24h_change_pct: -0.08324
ETH_OI_24h_change_pct: 3.66123
BTC_global_long_short_ratio: 1.7137
ETH_global_long_short_ratio: 2.5537
BTC_futures_taker_buy_sell: 1.0170
ETH_futures_taker_buy_sell: 1.1033
```

## Breadth source output

```yaml
method_id: COINGECKO_TOP100_FILTERED_v2
filter_id: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
included_count: 90
advancers: 39
decliners: 34
unchanged: 17
advance_ratio: 0.4333333333
median_return_24h_pct: 0.0
membership_hash: 016a925e6eea78a40159dec079a77a24f91d42b4a7bd5ebfe8c98980489320ae
```

The breadth output is reproducible for the supplied v1 universe but is not the current framework universe. The compatible v1.1 universe remains the scoring owner.

## Source and temporal boundaries

- ETF pages identified 2026-07-31 as the latest settled session but did not materialize numeric net-flow values.
- ETF missing-ledger rows incorrectly reference error evidence E3, which describes CFGI unavailability rather than ETF materialization.
- CFGI GLOBAL, BTC and ETH were unavailable.
- Stablecoin chain distribution was available, but the global total was unavailable.
- Receipt actions 20-22 carry 2026-08-03T21:59:59.999Z and actions 23-25 carry 2026-08-03T15:59:59.999Z, both later than the 15:30:28.895Z freeze. These are treated as open-candle end labels, not accepted settled source timestamps.
- The actual settled daily rows remain dated 2026-08-02T21:59:59.999Z and are retained.
- Low-reserve GeckoTerminal anomalies are excluded from market interpretation.

This record preserves the user-supplied packet as summarized evidence. The full packet remains in the originating conversation transport.
