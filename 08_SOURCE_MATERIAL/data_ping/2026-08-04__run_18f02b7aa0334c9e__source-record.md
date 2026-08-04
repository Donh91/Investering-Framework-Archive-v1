# DATA PING Source Record

```yaml
run_id: run_18f02b7aa0334c9e
snapshot_id: snap_d23ae2d89bec47a8
snapshot_utc: 2026-08-04T09:01:37.097Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
source_reported_PASS: 58
source_reported_PARTIAL: 1
source_reported_STALE: 1
optional_FAIL: 1
freeze_count: 1
post_freeze_call_count: 0
predecessor_available: false
scored_gate_permission: NOT_AUTHORIZED
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
```

## Direct market evidence

```yaml
BTCUSDT_last: 63594.01
ETHUSDT_last: 1857.77
ETHBTC_direct: 0.02922
BTC_24h_pct: 1.702
ETH_24h_pct: 0.959
ETHBTC_24h_pct: -0.680
BTC_24h_high: 64243.81
BTC_24h_low: 62445.26
ETH_24h_high: 1882.44
ETH_24h_low: 1836.75
```

## Latest settled Copenhagen session

```yaml
BTC_close: 63590.15
ETH_close: 1863.60
ETHBTC_close: 0.02931
BTC_low: 62300.00
ETH_low: 1828.62
ETHBTC_low: 0.02921
```

## Main-thread comparison with prior bounded observation

Comparison owner: main thread against `DP-20260804T062759033Z-R1`.

```yaml
BTC_change_pct: -0.362614
ETH_change_pct: -0.397815
ETHBTC_change_pct: -0.034211
BTC_current_OI_change_pct: 0.162872
ETH_current_OI_change_pct: 0.063914
```

## ETF evidence

```yaml
latest_settled_session: 2026-08-03
BTC_net_flow_usd_m: 170.1
ETH_net_flow_usd_m: -11.9
interpretive_scope: NUMERIC_SETTLED_SOURCE_EVIDENCE_NO_NEW_SESSION_DELTA
```

## Derivatives and positioning

```yaml
BTC_current_funding: 0.00007452
ETH_current_funding: 0.00006441
BTC_latest3_settled_funding_mean: 0.00003934333333
ETH_latest3_settled_funding_mean: 0.00004800666667
BTC_OI_1h_change_pct: 0.02500448
BTC_OI_4h_change_pct: -0.18755313
BTC_OI_24h_change_pct: -1.55667956
ETH_OI_1h_change_pct: 0.08176558
ETH_OI_4h_change_pct: -0.01846834
ETH_OI_24h_change_pct: -0.33485940
BTC_global_long_short_ratio: 1.4655
ETH_global_long_short_ratio: 2.3602
BTC_futures_taker_buy_sell: 1.0815
ETH_futures_taker_buy_sell: 1.1801
BTC_spot_taker_buy_share_1h: 0.42580461
BTC_spot_taker_buy_share_4h: 0.46926129
BTC_spot_taker_buy_share_12h: 0.48573948
ETH_spot_taker_buy_share_1h: 0.48350198
ETH_spot_taker_buy_share_4h: 0.56307533
ETH_spot_taker_buy_share_12h: 0.51758555
ETHBTC_spot_taker_buy_share_1h: 0.56490580
ETHBTC_spot_taker_buy_share_4h: 0.64989839
ETHBTC_spot_taker_buy_share_12h: 0.43714435
```

## Breadth source output

```yaml
method_id: COINGECKO_TOP100_FILTERED_v2
filter_id: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
included_count: 89
positive_count: 52
negative_count: 20
zero_count: 17
positive_share: 0.5842696629
mean_24h_pct: 0.7853932584
median_24h_pct: 0.5
membership_hash: 49d41929bf0ebe9b7b16c37bb1e31d6808b0b199e0f051a17b766b41c12a6b81
membership_hash_status: COMPUTED
scored_gate_permission: NOT_AUTHORIZED
```

The breadth output is reproducible and directionally informative inside its supplied universe. It still uses the superseded v1 exclusion filter. The scoring owner remains `BREADTH_FILTER_TOP100_EXCLUSIONS_v1_1`, and no constituent sidecar was supplied to reclassify the current rows. No 35%, 50% or 55% framework gate is authorized.

## Sentiment, macro and source boundaries

```yaml
CFGI_global: 44
CFGI_global_status: LIVE
CFGI_ETH: 44
CFGI_ETH_status: LIVE
CFGI_BTC: 46
CFGI_BTC_status: STALE_EXCLUDED
BTC_dominance_pct: 56.387113
ETH_dominance_pct: 9.913605
crypto_total_market_cap_usd: 2261503539026.445
crypto_total_volume_usd: 56089742383.77205
VIX_latest: 15.99
DGS2_latest: 4.28
DGS10_latest: 4.75
DGS10_minus_DGS2: 0.47
DTWEXBGS_latest: 119.7034
```

- Global stablecoin market capitalization is unavailable; chain distribution only was returned.
- BTC CFGI is stale and excluded from current-state authority.
- Long return and realized-volatility windows are unavailable under the configured payload budget.
- DeFi total TVL is optional and failed because the response exceeded the payload limit.
- OKX and Binance snapshots are non-simultaneous and used only as numerical cross-checks.
- Nonfinal public-web refresh order deviated, but `BINANCE_FINAL` remained last.
- The packet has no accepted same-thread predecessor and cannot advance the canonical longitudinal chain.

This record preserves the user-supplied packet as summarized evidence. The full packet remains in the originating conversation transport.