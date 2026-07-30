# DATA PING source record — run 5f1b7219

```yaml
record_type: USER_TRANSMITTED_DATA_PING_PACKET
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
run_id: run_5f1b7219edb64d48a5e9961ee7ce9849
snapshot_id: snap_155aa63ee97245cb8e4d763f113056e4
snapshot_utc: 2026-07-30T19:24:39.157Z
collector_status: PARTIAL
collector_predecessor_id: snap_609e377c7de24dfba3e4db211e448e46
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
framework_interpretation_by_source: DEFERRED_TO_MAIN_FRAMEWORK
```

## Execution coverage

```yaml
core_actions:
  planned: 60
  attempted: 60
  pass: 54
  partial: 1
  stale: 2
  fail: 0
  unavailable: 3
optional_actions:
  planned: 1
  attempted: 1
  fail: 1
receipt_count: 61
counts_reconciled: true
post_freeze_call_count: 0
```

## Direct market observations

```yaml
Binance_final_timestamp_utc: 2026-07-30T19:24:39.157Z
BTCUSDT:
  last: 64857.65
  change_24h_pct: 1.143
  high_24h: 65176.60
  low_24h: 63267.34
  funding_rate: 0.00004135
  open_interest_coin: 106475.316
ETHUSDT:
  last: 1924.95
  change_24h_pct: 1.067
  high_24h: 1936.99
  low_24h: 1872.00
  funding_rate: 0.00002501
  open_interest_coin: 2315304.592
ETHBTC:
  last: 0.02968
  change_24h_pct: 0.0
  high_24h: 0.02996
  low_24h: 0.02958
  distance_to_0_0300_abs: -0.00032
```

## CoinGecko and breadth

```yaml
CoinGecko_timestamp_utc: 2026-07-30T19:05:14Z
total_market_cap_usd: 2292616555992.538
total_volume_usd: 64607711547.64161
market_cap_change_24h_pct: 1.5804837677921637
BTC_price_usd: 64705
ETH_price_usd: 1917.13
BTC_dominance_pct: 56.57747438582121
ETH_dominance_pct: 10.08090589069703
ETHBTC_derived_ratio: 0.029628776756046676
breadth_method: COINGECKO_TOP100_FILTERED_v2
breadth_raw_rows: 100
breadth_included_count: 89
breadth_excluded_count: 11
breadth_advancers: 39
breadth_decliners: 36
breadth_unchanged: 14
breadth_advance_ratio: 0.43820224719101125
breadth_median_return_24h_pct: 0.0
breadth_membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
constituent_sidecar_emitted: false
```

## Short-window diagnostics

```yaml
BTC_return_12h_pct: 1.0949815779
ETH_return_12h_pct: 0.7868176487
ETHBTC_return_12h_pct: -0.3029283070
ETHBTC_return_4h_pct: -0.0674763833
ETHBTC_return_1h_pct: 0.0
BTC_taker_buy_sell_ratio: 0.9628
ETH_taker_buy_sell_ratio: 0.8962
BTC_global_long_short_ratio: 1.2482
ETH_global_long_short_ratio: 2.012
BTC_OI_change_24h_pct: 3.2310987384
ETH_OI_change_24h_pct: 1.1720468429
```

## Non-current or unavailable source fields

```yaml
ETF: STALE_AT_2026_07_27
CFGI: UNAVAILABLE
stablecoin_global_total: UNAVAILABLE
stablecoin_chain_distribution: PARTIAL_AVAILABLE
DeFi_total_TVL_optional_action: FAIL_RESPONSE_TOO_LARGE
```

## Source authority boundary

The source packet is a deterministic collector output. It does not interpret framework state and does not authorize rotation, rebuy, entry, exit or portfolio action. The full packet was supplied through chat; this archive record preserves its material observations and execution metadata but does not claim byte-for-byte chat transport verification.
