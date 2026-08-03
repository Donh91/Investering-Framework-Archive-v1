# DATA PING Source Record

```yaml
run_id: run_20260803T122759180Z_7f3c9d1a
snapshot_id: snap_20260803T122759180Z_4b8e2c6f
snapshot_utc: 2026-08-03T12:27:59.180Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collection_status: PARTIAL
packet_usable_for_main_thread_ingest: true
planned_core_actions: 60
attempted_core_actions: 60
PASS: 56
PARTIAL: 1
STALE: 2
UNAVAILABLE: 1
FAIL: 0
optional_FAIL: 1
freeze_count: 1
post_freeze_call_count: 0
collector_predecessor_run_id: run_20260803_mm_gapfill_001
collector_predecessor_id: snap_20260803_mm_gapfill_001
required_canonical_predecessor_run_id: run_0bc8a5d0d0464542b29b4d50f2f8e19c
required_canonical_predecessor_id: snap_0e19c112413d471d8270cad1a18148a7
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
packet_sha256: null
```

## Direct and settled market evidence

```yaml
BTCUSDT_last: 62631.42
ETHUSDT_last: 1842.91
ETHBTC_direct: 0.02942
BTC_24h_pct: -0.895
ETH_24h_pct: -0.884
ETHBTC_24h_pct: 0.034
settled_Copenhagen_session: 2026-08-02
settled_Copenhagen_BTC_close: 63578.00
settled_Copenhagen_ETH_close: 1890.43
settled_Copenhagen_ETHBTC_close: 0.02973
BTC_12h_return_pct: -1.5888
ETH_12h_return_pct: -2.4117
ETHBTC_12h_return_pct: -0.8094
BTC_12h_low: 62300.00
ETH_12h_low: 1828.62
```

## Breadth payload as supplied

```yaml
method_id: COINGECKO_TOP100_FILTERED_v2
filter_id: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
included_count: 90
advancers: 18
decliners: 49
unchanged: 23
advance_ratio: 0.20
median_return_24h_pct: -0.20
equal_weight_mean_return_24h_pct: -0.6577777778
membership_hash: 016a925e6eea78a40159dec079a77a24f91d42b4a7bd5ebfe8c98980489320ae
gate_35: false
gate_50: false
gate_55: false
```

The packet used `BREADTH_FILTER_TOP100_EXCLUSIONS_v1`. The repository's current verified economic-universe owner is `BREADTH_FILTER_TOP100_EXCLUSIONS_v1_1`; therefore the supplied 20% aggregate is preserved as raw method-specific evidence but is not allowed to replace or score against the current v1.1 breadth state.

## Spot and futures flow

```yaml
BTC_spot_taker_buy_share_1h: 0.4561183013
BTC_spot_taker_buy_share_4h: 0.55548709
BTC_spot_taker_buy_share_12h: 0.5021943434
ETH_spot_taker_buy_share_1h: 0.4273586065
ETH_spot_taker_buy_share_4h: 0.4581054029
ETH_spot_taker_buy_share_12h: 0.4493330334
ETHBTC_spot_taker_buy_share_1h: 0.0699332173
ETHBTC_spot_taker_buy_share_4h: 0.3693974419
ETHBTC_spot_taker_buy_share_12h: 0.4914085682
BTC_futures_taker_buy_sell: 0.6161
ETH_futures_taker_buy_sell: 0.9346
BTC_global_long_short: 2.1586
ETH_global_long_short: 2.5894
BTC_top_account_long_short: 2.2510
ETH_top_account_long_short: 2.1928
```

## Funding and open interest

```yaml
BTC_current_funding: 0.0000295
ETH_current_funding: -0.0000045
BTC_latest_three_settled_funding_mean: 0.0000802366667
ETH_latest_three_settled_funding_mean: 0.0000352166667
BTC_OI_change_1h_pct: 0.059286
BTC_OI_change_4h_pct: 0.785432
BTC_OI_change_24h_pct: 2.13263
ETH_OI_change_1h_pct: 0.649728
ETH_OI_change_4h_pct: 1.141586
ETH_OI_change_24h_pct: 3.941295
```

## ETF evidence

```yaml
latest_settled_session: 2026-07-31
BTC_2026_07_30_usd_m: 233.1
BTC_2026_07_31_usd_m: -265.4
ETH_2026_07_30_usd_m: 12.8
ETH_2026_07_31_usd_m: 9.0
source: FARSIDE_DIRECT_TABLE
```

These rows confirm the previously reconciled W31 ETF evidence; they do not add a post-W31 session.

## Missing and degraded fields

- CFGI global current: UNAVAILABLE.
- CFGI BTC and ETH: STALE.
- Stablecoin global market-cap total: UNAVAILABLE; chain distribution only.
- Optional DeFi total TVL: FAIL due response-size limit.
- Transport integrity: unverified chat transport; no packet SHA-256 supplied.

The full user-supplied packet remains preserved in the originating conversation transport. This record stores the decision-relevant evidence and all material source boundaries.