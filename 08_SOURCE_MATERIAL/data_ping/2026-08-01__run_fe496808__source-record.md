# DATA PING source record

```yaml
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
run_id: run_fe496808649a7d5e3db0c033587afbc1
snapshot_id: snap_03949c287c10bc8a52c16476ea34bc03
snapshot_utc: 2026-08-01T17:51:41.284Z
collector_status: PARTIAL
collector_predecessor_id: snap_91d8483f485146cc99b8c8de39d9a0ef
planned_core_actions: 60
attempted_core_actions: 60
core_PASS: 54
core_PARTIAL: 1
core_UNAVAILABLE: 5
optional_FAIL: 1
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
```

## Current direct market fields

```yaml
BTCUSDT_last: 62777.99
ETHUSDT_last: 1861.79
ETHBTC_last: 0.02965
BTC_24h_pct: -0.581
ETH_24h_pct: -0.707
ETHBTC_24h_pct: -0.135
Copenhagen_settled_ETHBTC_close: 0.02957
```

## Breadth aggregate

```yaml
method: COINGECKO_TOP100_FILTERED_v2
raw_rows: 99
included_count: 88
advancers: 42
decliners: 30
unchanged: 16
advance_ratio: 0.4772727272727273
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: 0.34204545454545454
membership_hash: 097784fd268bcb20da77c92ac2f372fd4d9a70f6da7fa14fa1f2b6e873201c7d
prior_membership_hash: 781e82b425c3f3dbbdf63ac3a8e4981ebee1f37b04f998e8b44d0fad82d5af5a
membership_hash_changed: true
```

## Flow and derivatives

```yaml
BTC_global_long_short_ratio: 2.0562
ETH_global_long_short_ratio: 2.6127
BTC_taker_buy_sell_ratio: 0.7284
ETH_taker_buy_sell_ratio: 0.8817
BTC_funding_rate: 0.00005372
ETH_funding_rate: 0.00004660
BTC_OI_24h_change_pct: -1.7562
ETH_OI_24h_change_pct: -1.0100
BTC_OI_4h_change_pct: 0.1545
ETH_OI_4h_change_pct: 0.2517
market_volume_change_24h_pct: -48.1894
```

## Source limitations

Public-web ETF and CFGI fields were unavailable. Stablecoin global market capitalization, total DeFi TVL and realized-volatility windows were unavailable. The GeckoTerminal WRAP/WETH top-pool row has an implausible reserve-volume relationship and is retained only as source-QA evidence, not market evidence.

This file preserves the supplied packet as a bounded source record. Canonical interpretation is performed separately by the main framework.