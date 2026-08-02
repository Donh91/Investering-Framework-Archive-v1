# DATA PING source record

```yaml
run_id: run_3fe6bcb574124cdcbcd763f808c18439
snapshot_id: snap_4652543565bd4c05a8e02a803a70f0e6
snapshot_utc: 2026-08-02T09:34:39.531Z
collector_status: PARTIAL
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
planned_core_actions: 60
attempted_core_actions: 60
core_PASS: 54
core_PARTIAL: 1
core_STALE: 2
core_UNAVAILABLE: 3
core_FAIL: 0
optional_FAIL: 1
collector_predecessor: snap_25c72fb925fd427cb44886fb7f1932f9
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Current direct owner values

```yaml
BTCUSDT_last: 63292.01
ETHUSDT_last: 1872.73
ETHBTC_last: 0.02958
BTCUSDT_24h_pct: 0.284
ETHUSDT_24h_pct: 0.141
ETHBTC_24h_pct: -0.202
settled_Copenhagen_BTC_close: 62812.75
settled_Copenhagen_ETH_close: 1845.78
settled_Copenhagen_ETHBTC_close: 0.02938
```

## Breadth source state

CoinGecko global, BTC/ETH current and both top-100 pages were retrieved successfully, but the deterministic breadth aggregate was not materialized before freeze. The packet supplies neither an advance ratio nor a membership hash for this run.

```yaml
breadth_status: PARTIAL_PARSE_FAILURE
raw_rows_available: true
page_1_available: true
page_2_available: true
advance_ratio: null
membership_hash: null
error_evidence: e5
forward_fill_permitted: false
```

The previous run's 48.8889% breadth is prior evidence only and must not be represented as current breadth.

## Current positioning and derivatives

```yaml
BTC_global_long_short_ratio: 1.8944
ETH_global_long_short_ratio: 2.3568
BTC_current_taker_buy_sell_ratio: 0.4681
ETH_current_taker_buy_sell_ratio: 0.6290
BTC_Binance_funding: 0.00008497
ETH_Binance_funding: 0.00006701
BTC_OKX_funding: 0.0000229764571807
ETH_OKX_funding: 0.0000193789237702
BTC_OI_4h_pct: 0.1366773028
ETH_OI_4h_pct: 0.3288841677
BTC_OI_24h_pct: -0.0171894295
ETH_OI_24h_pct: -0.7155637457
BTC_Binance_minus_OKX_mark_bps: 12.1174
ETH_Binance_minus_OKX_mark_bps: 8.9091
```

## Stale and unavailable sources

The packet's ETF rows remain stale at BTC 2026-07-28 and ETH 2026-07-27. They are older than the reconciled framework ETF ledger and are not eligible to overwrite it. CFGI remained unavailable. Stablecoin global total and total DeFi TVL were unavailable; chain distribution and chain-TVL payloads were available only as partial support.

## Source QA events

```yaml
breadth_parse_failure: EXECUTED_PARTIAL
ETF_stale_payload: EXECUTED_STALE
CFGI_unavailable: EXECUTED_UNAVAILABLE
stablecoin_primary_transport_failure: EXECUTED_PARTIAL
response_too_large_optional: EXECUTED_FAIL
GeckoTerminal_low_reserve_anomaly: EXCLUDED_FROM_MARKET_INTERPRETATION
```
