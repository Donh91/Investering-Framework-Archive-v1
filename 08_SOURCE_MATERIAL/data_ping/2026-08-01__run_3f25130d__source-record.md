# DATA PING source record

```yaml
run_id: run_3f25130db9c1450b8db4b0e2ea078e75
snapshot_id: snap_685db69aef8844428134c86e180d88dd
snapshot_utc: 2026-08-01T07:39:54.779Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
core_PASS: 54
core_PARTIAL: 1
core_UNAVAILABLE: 5
core_FAIL: 0
optional_FAIL: 1
collector_predecessor_run_id: run_d90398dd4a78451a84a942a77d3ce9d6
collector_predecessor_snapshot_id: snap_d088d3d626ce4aed9b3543016ffa5474
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Current direct market observations

```yaml
BTCUSDT_last: 63041.29
BTC_24h_pct: -1.429
ETHUSDT_last: 1869.39
ETH_24h_pct: -0.898
ETHBTC_last: 0.02966
ETHBTC_24h_pct: 0.542
Copenhagen_settled_ETHBTC_close: 0.02957
```

## Breadth

```yaml
included_count: 89
advancers: 26
decliners: 47
unchanged: 16
advance_ratio: 0.29213483146067415
median_return_24h_pct: -0.1
equal_weight_mean_return_24h_pct: -0.1393258426966292
membership_hash: c6181d3dd25733dac92cac4c28cd55f7b6b71f214a24ffa2864caf55ff2e0e54
```

## Positioning and derivatives

```yaml
BTC_global_long_short_ratio: 2.2041
ETH_global_long_short_ratio: 2.6738
BTC_top_account_ratio: 2.2373
ETH_top_account_ratio: 2.1586
BTC_taker_buy_sell_ratio: 0.7228
ETH_taker_buy_sell_ratio: 1.2065
BTC_funding_rate: 0.00003639
ETH_funding_rate: 0.00002532
BTC_OI_24h_change_pct: 3.3923591655
ETH_OI_24h_change_pct: 0.3459372661
```

## Source boundaries

Public-web ETF and CFGI actions were unavailable. Stablecoin global market cap and total DeFi TVL were unavailable. The GeckoTerminal WRAP/WETH row has an implausible reserve-volume combination and is retained as source QA only.

This source record preserves the user-supplied packet as a bounded evidence summary. Framework interpretation is stored separately.