# DATA PING Source Record

```yaml
run_id: run_8a4f73c1d9e64bbba275efa260803621
snapshot_id: snap_5cc75db8af16450ea9cdb89b38ff6567
snapshot_utc: 2026-08-03T06:21:29.117Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
PASS: 54
PARTIAL: 1
UNAVAILABLE: 5
optional_FAIL: 1
freeze_count: 1
post_freeze_call_count: 0
collector_predecessor_id: snap_9c2e7b4a1f6d43b8a05e9172c64fd3ab
required_canonical_predecessor_id: snap_0e19c112413d471d8270cad1a18148a7
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Direct market evidence

```yaml
BTCUSDT_last: 62840.00
ETHUSDT_last: 1859.36
ETHBTC_direct: 0.02960
BTC_24h_pct: -0.951
ETH_24h_pct: -0.872
ETHBTC_24h_pct: 0.135
settled_Copenhagen_BTC_close: 63578.00
settled_Copenhagen_ETH_close: 1890.43
settled_Copenhagen_ETHBTC_close: 0.02973
```

## Breadth

```yaml
status: PARTIAL_AGGREGATE_AVAILABLE_HASH_MISSING
included_count: 90
advancers: 22
decliners: 52
unchanged: 16
advance_ratio: 0.244444444444
median_return_24h_pct: -0.5
membership_hash: NOT_MATERIALIZED_BEFORE_FREEZE
```

## Derivatives and positioning

```yaml
BTC_Binance_funding: 0.0001
ETH_Binance_funding: 0.00001559
BTC_three_settled_funding_mean: 0.000088833333
ETH_three_settled_funding_mean: 0.000056803333
BTC_OI_change_1h_pct: 0.245805
BTC_OI_change_4h_pct: 0.110737
BTC_OI_change_24h_pct: 0.30103
ETH_OI_change_1h_pct: 0.49293
ETH_OI_change_4h_pct: 0.62765
ETH_OI_change_24h_pct: 1.05844
BTC_global_long_short_ratio: 1.9958
ETH_global_long_short_ratio: 2.5039
BTC_top_account_ratio: 2.0893
ETH_top_account_ratio: 2.0609
BTC_current_taker_ratio: 1.0482
ETH_current_taker_ratio: 1.0673
```

## Source boundaries

Public-web ETF and CFGI actions were unavailable. Stablecoin global total and DeFi total TVL were unavailable. Breadth membership hash was not materialized. VIX initially returned 502 and succeeded on bounded retry. The GeckoTerminal WRAP/WETH result is a low-reserve anomaly and is excluded from market interpretation.

This record preserves the user-supplied packet as summarized evidence. The full packet remains in the originating conversation transport.