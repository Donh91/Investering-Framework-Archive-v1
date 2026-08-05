# DATA PING Source Record

```yaml
run_id: run-4e87515bde8846aa9c51
snapshot_id: snap-bafd43eb4ab1fa90c0cb
snapshot_utc: 2026-08-05T09:10:24.002Z
freeze_recorded_at_utc: 2026-08-05T09:10:24.002Z
max_final_source_timestamp_utc: 2026-08-05T09:10:11.869Z
collector_version: 15.2.0
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
core_PASS: 57
core_PARTIAL: 2
core_STALE: 1
core_FAIL: 0
core_UNAVAILABLE: 0
optional_UNAVAILABLE: 1
execution_order_status: PASS
status_reconciliation: PASS
receipt_bijection_status: PASS
breadth_transform_status: PASS
settled_candle_filter_status: PASS
freeze_invariants_status: PASS
packet_usable_for_main_thread_ingest: true
canonical_predecessor_available: false
classification: BOUNDED_CURRENT_OWNER_OBSERVATION
packet_sha256: 46e2c7125f616fd827f3879f53b26dad63904d3d657a33348ed40ebf121afc11
```

## Direct market snapshot

```yaml
BTCUSDT: 64152.08
ETHUSDT: 1870.69
ETHBTC: 0.02917
BTC_24h_pct: 0.838
ETH_24h_pct: 0.637
ETHBTC_24h_pct: -0.205
```

Relative to the immediately preceding valid bounded observation `run_876595b84c284b3eb719f8139f56882a`:

```yaml
BTC_change_pct: -0.044826
ETH_change_pct: 0.146149
ETHBTC_change_pct: 0.275009
BTC_OI_change_pct: -0.653323
ETH_OI_change_pct: 0.385837
```

## ETF direct owner

```yaml
session: 2026-08-04
BTC_net_flow_usd_m: 211.5
ETH_net_flow_usd_m: 53.1
BTC_minus_ETH_flow_spread_usd_m: 158.4
BTC_status: PASS
ETH_status: PASS
cross_asset_same_session_comparison_permission: AUTHORIZED
```

Using the repository direct row ledger through 31 July plus the verified 3 and 4 August sessions:

```yaml
BTC_3_session_usd_m: 116.2
BTC_5_session_usd_m: 381.4
BTC_7_session_usd_m: 320.1
BTC_10_session_usd_m: -76.0
BTC_15_session_usd_m: 673.1
ETH_3_session_usd_m: 50.2
ETH_5_session_usd_m: 30.1
ETH_7_session_usd_m: 51.2
ETH_10_session_usd_m: 79.5
ETH_15_session_usd_m: 217.6
```

Both assets received positive flows on 4 August, but BTC absorbed approximately four times the ETH dollar flow. The dual-positive session improves the flow backdrop but does not establish ETH-led transmission because ETH/BTC remains below 0.0300 and the longer intraday ratio flow is still weak.

## Derivatives and positioning

```yaml
BTC_current_funding: 0.00002534
ETH_current_funding: -0.00000199
BTC_latest3_settled_funding_mean: 0.0000345767
ETH_latest3_settled_funding_mean: 0.0000379633
BTC_basis_bps_Binance: -3.8984
ETH_basis_bps_Binance: -4.5116
BTC_OI_current: 107463.826
ETH_OI_current: 2317193.659
BTC_OI_change_1h_pct: -0.642580
BTC_OI_change_4h_pct: -0.555953
BTC_OI_change_24h_pct: -1.195122
ETH_OI_change_1h_pct: 0.351243
ETH_OI_change_4h_pct: 0.221369
ETH_OI_change_24h_pct: -0.640628
BTC_global_long_short: 1.2722
ETH_global_long_short: 2.3841
BTC_futures_taker_ratio: 1.1333
ETH_futures_taker_ratio: 0.6986
```

BTC leverage continued to decline while ETH rebuilt slightly over the latest one and four hours but remained lower over 24 hours. ETH positioning remains substantially more long-heavy than BTC.

## Spot taker flow

```yaml
BTC_1h: 0.523070
BTC_4h: 0.531018
BTC_12h: 0.526082
ETH_1h: 0.573084
ETH_4h: 0.476669
ETH_12h: 0.475138
ETHBTC_1h: 0.857367
ETHBTC_4h: 0.678692
ETHBTC_12h: 0.395297
```

ETH and ETH/BTC displayed a strong short-window rebound, especially on one and four hours. The 12-hour ETH and ETH/BTC shares remain below 50%, so the improvement is classified as a short-term transmission attempt rather than confirmation.

## Breadth

The v3 transform retained the same membership hash as the preceding bounded run:

```yaml
method_id: COINGECKO_TOP100_FILTERED_v3
filter_id: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
raw_count: 100
deduplicated_count: 100
included_count: 89
advancers: 36
decliners: 39
unchanged: 14
positive_share_full_universe: 0.4044943820
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: 0.0359550562
membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
```

Within the same v3 universe, positive participation improved from 30/89 = 33.7% to 36/89 = 40.4%, and the median improved from -0.22% to 0.0%. This is valid directional evidence inside the v3 diagnostic lane.

The transform is still incompatible with the locked scoring owner `BREADTH_FILTER_TOP100_EXCLUSIONS_v1_1`, whose universe and exclusion set differ. No 35/50/55 gate authority is granted.

## Sentiment and macro

```yaml
CFGI_global: 49
CFGI_ETH: 50
CFGI_BTC: 46
CFGI_BTC_status: STALE
DGS2: 4.25
DGS10: 4.70
DGS10_minus_DGS2: 0.45
VIX: 15.86
DTWEXBGS: 119.7034
```

## Missing or partial families

- No accepted same-thread predecessor.
- Global stablecoin total unavailable after registered fallbacks.
- Optional DeFi total unavailable.
- GeckoTerminal retains two low-reserve source anomalies.
- Long-window realized volatility unavailable under the payload budget.
- BTC CFGI remains stale.

The full user-supplied inline packet remains preserved in the originating conversation transport.