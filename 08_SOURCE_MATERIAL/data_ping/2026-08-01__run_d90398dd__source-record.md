# DATA PING source record

```yaml
record_type: DATA_PING_COLLECTOR_PACKET
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
run_id: run_d90398dd4a78451a84a942a77d3ce9d6
snapshot_id: snap_d088d3d626ce4aed9b3543016ffa5474
snapshot_utc: 2026-08-01T04:38:46.132Z
collector_status: PARTIAL
collector_predecessor_id: snap_b4ec0a26ced94e2496fb685ee6ab9be6
collector_predecessor_run_id: run_a6843a76a2ab4d47a32cb3e6492d03ce
planned_core_actions: 60
attempted_core_actions: 60
core_PASS: 54
core_PARTIAL: 1
core_UNAVAILABLE: 5
optional_FAIL: 1
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Current direct market fields

```yaml
BTCUSDT_last: 63046.01
BTCUSDT_24h_pct: -1.988
ETHUSDT_last: 1869.58
ETHUSDT_24h_pct: -1.948
ETHBTC_last: 0.02966
ETHBTC_24h_pct: 0.101
Copenhagen_settled_BTC_close: 62947.78
Copenhagen_settled_ETH_close: 1861.81
Copenhagen_settled_ETHBTC_close: 0.02957
```

## Breadth aggregate

```yaml
method_id: COINGECKO_TOP100_FILTERED_v2
included_count: 89
advancers: 28
decliners: 44
unchanged: 17
advance_ratio: 0.3146067415730337
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: -0.047191011235955066
membership_hash: c6181d3dd25733dac92cac4c28cd55f7b6b71f214a24ffa2864caf55ff2e0e54
```

## Positioning and derivatives

```yaml
BTC_global_long_short_ratio: 2.2321
ETH_global_long_short_ratio: 2.6832
BTC_taker_buy_sell_ratio: 0.6433
ETH_taker_buy_sell_ratio: 1.3866
BTC_funding_rate: 0.0000387
ETH_funding_rate: 0.00005574
BTC_OI_24h_change_pct: 3.9252613005659187
ETH_OI_24h_change_pct: 0.8388956504287393
BTC_OI_4h_change_pct: -0.4157980980700082
ETH_OI_4h_change_pct: 0.3906307113159091
```

## Source limitations

- Public-web ETF and CFGI actions were unavailable in this runtime.
- Stablecoin global market capitalization was unavailable; chain distribution only was retained.
- Realized-volatility windows were unavailable because the settled hourly window was insufficient.
- The GeckoTerminal top-pool row `WRAP / WETH` combined approximately USD 11.6k reserve with approximately USD 1.26bn reported volume. It is retained as a source-QA anomaly and is excluded from market interpretation.
- The optional total-DeFi-TVL request failed because the bounded response was too large.

## Authority boundary

The packet is collector evidence only. It claims no framework-state, rotation, rebuy, entry, exit or portfolio authority.