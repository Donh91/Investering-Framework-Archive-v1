# DATA PING source record — run f15769c0

```yaml
record_type: DATA_PING_COLLECTOR_INPUT
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
run_id: run_f15769c054e94c9d9c48a72385b5cf19
snapshot_id: snap_748607ede85744af92c3e94878539287
snapshot_utc: 2026-07-30T21:46:24.921Z
collector_status: PARTIAL
all_core_actions_attempted: true
core_pass: 54
core_partial: 1
core_stale: 2
core_unavailable: 3
core_fail: 0
collector_predecessor_id: snap_155aa63ee97245cb8e4d763f113056e4
required_accepted_predecessor_id: snap_0e19c112413d471d8270cad1a18148a7
lineage_match: false
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
framework_authority: NONE
```

## Current absolute observations

```yaml
CoinGecko_BTC_usd: 64714
CoinGecko_ETH_usd: 1920.30
CoinGecko_ETHBTC_derived: 0.029673640943227123
total_market_cap_usd: 2295520921872.1294
total_volume_usd: 59503524596.50426
BTC_dominance_pct: 56.57244779483326
ETH_dominance_pct: 10.100609626887977
Binance_BTCUSDT: 64764.38
Binance_ETHUSDT: 1921.07
Binance_ETHBTC_direct: 0.02966
Binance_ETHBTC_24h_pct: -0.303
breadth_advance_ratio: 0.7415730337078652
breadth_advancers: 66
breadth_decliners: 9
breadth_unchanged: 14
breadth_median_return_24h_pct: 1.5
breadth_membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
```

## Relative and derivatives observations

```yaml
BTC_12h_return_pct: 0.729862423
ETH_12h_return_pct: 0.3493490828
ETHBTC_12h_return_pct: -0.3693754197
BTC_taker_buy_sell_ratio: 1.1366
ETH_taker_buy_sell_ratio: 1.1108
BTC_funding_latest_three_mean: 0.0000825633333333
ETH_funding_latest_three_mean: 0.0000350166666667
BTC_OI_24h_change_pct: 3.2258712837
ETH_OI_24h_change_pct: 2.4794434385
OKX_BTC_OI_usd: 1986982613.529551
OKX_ETH_OI_usd: 1367430079.238523
VIX_latest: 20.66
VIX_change_1: 2.45
```

## Source limitations

- Farside BTC and ETH ETF rows in the packet are stale at 2026-07-27 and are not permitted to overwrite newer archived ETF evidence.
- CFGI is unavailable.
- Stablecoin global total and DeFi total TVL are unavailable.
- Breadth aggregate and membership hash are present, but no emitted constituent sidecar is retained.
- The collector predecessor is a bounded non-predecessor observation and cannot establish canonical longitudinal succession.
