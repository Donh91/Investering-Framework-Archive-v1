# DATA PING source record

```yaml
record_type: DATA_PING_SOURCE_RECORD
run_id: run_a6843a76a2ab4d47a32cb3e6492d03ce
snapshot_id: snap_b4ec0a26ced94e2496fb685ee6ab9be6
snapshot_utc: 2026-07-31T23:35:19.436Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
core_PASS: 56
core_PARTIAL: 1
core_STALE: 2
core_UNAVAILABLE: 1
optional_FAIL: 1
collector_predecessor_id: snap_54bda23836584972bfef107098e467ae
collector_predecessor_run_id: run_0877857fbb404762a1277c35a61f89c5
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
framework_authority: NONE_UNTIL_MAIN_FRAMEWORK_RECONCILIATION
```

## Current direct market fields

```yaml
BTCUSDT_last: 62981.94
BTCUSDT_24h_pct: -3.015
BTCUSDT_24h_low: 62466.00
ETHUSDT_last: 1864.01
ETHUSDT_24h_pct: -3.348
ETHUSDT_24h_low: 1848.70
ETHBTC_direct_last: 0.02960
ETHBTC_24h_pct: -0.303
ETHBTC_24h_low: 0.02944
ETHBTC_24h_high: 0.02986
```

## Settled Copenhagen daily rows

```yaml
settlement_end_utc: 2026-07-31T21:59:59.999Z
BTCUSDT_close: 62947.78
ETHUSDT_close: 1861.81
ETHBTC_close: 0.02957
```

## Breadth aggregate

```yaml
method_id: COINGECKO_TOP100_FILTERED_v2
included_count: 89
advancers: 12
decliners: 60
unchanged: 17
advance_ratio: 0.1348314606741573
median_return_24h_pct: -0.9
equal_weight_mean_return_24h_pct: -0.851685393258427
membership_hash: c6181d3dd25733dac92cac4c28cd55f7b6b71f214a24ffa2864caf55ff2e0e54
constituent_sidecar_transmitted: false
```

## Positioning and derivatives

```yaml
BTC_global_long_short_ratio: 2.2082
ETH_global_long_short_ratio: 2.6284
BTC_taker_buy_sell_ratio: 0.9975
ETH_taker_buy_sell_ratio: 0.9289
BTC_funding_rate: 0.00004933
ETH_funding_rate: 0.00007215
BTC_OI_24h_change_pct: 2.8525949176695375
ETH_OI_24h_change_pct: -0.5388950456143848
BTC_OI_4h_change_pct: -0.39891174644525185
ETH_OI_4h_change_pct: -0.4332812596504976
```

## Other source fields

- Settled ETF session 2026-07-30: BTC +233.1 million USD; ETH +12.8 million USD. Session 2026-07-31 remained incomplete.
- CFGI global and BTC values were stale and ETH-specific CFGI was unavailable.
- Stablecoin global total remained unavailable; chain distribution was partial.
- Realized-volatility windows were unavailable because only 13 settled hourly candles were present.

No framework state, rotation label, rebuy permission, entry permission or portfolio action is asserted by this source record.
