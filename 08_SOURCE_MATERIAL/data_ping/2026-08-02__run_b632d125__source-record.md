# DATA PING source record

```yaml
run_id: run_b632d125165c4cf7a882a73f22a40333
snapshot_id: snap_3f013c5404c144e0bbeb9d7a976c364d
snapshot_utc: 2026-08-02T12:29:17.344Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
core_pass: 54
core_partial: 1
core_stale: 2
core_unavailable: 3
core_fail: 0
optional_fail: 1
freeze_count: 1
post_freeze_call_count: 0
```

## Collector lineage

```yaml
collector_predecessor_snapshot: snap_4652543565bd4c05a8e02a803a70f0e6
required_canonical_predecessor_snapshot: snap_0e19c112413d471d8270cad1a18148a7
lineage_match: NO
```

## Current owner observations

```yaml
BTCUSDT_last: 63212.01
BTCUSDT_24h_pct: 0.172
ETHUSDT_last: 1858.99
ETHUSDT_24h_pct: -0.484
ETHBTC_direct: 0.02942
ETHBTC_24h_pct: -0.608
ETHBTC_settled_Copenhagen_close: 0.02938
```

## Deterministic breadth

```yaml
method: COINGECKO_TOP100_FILTERED_v2
status: PASS
included_count: 90
advancers: 43
decliners: 28
unchanged: 19
advance_ratio: 0.477777777778
median_return_24h_pct: 0.0
equal_weight_mean_return_24h_pct: 0.374444444444
membership_hash: 016a925e6eea78a40159dec079a77a24f91d42b4a7bd5ebfe8c98980489320ae
```

## Flow and derivatives

```yaml
BTC_current_taker_ratio: 0.7586
ETH_current_taker_ratio: 0.5607
BTC_Binance_funding: 0.00009197
ETH_Binance_funding: 0.00004594
BTC_OKX_funding: -0.0000181222562211
ETH_OKX_funding: 0.0000161459405207
BTC_OI_4h_pct: -0.000776871414
ETH_OI_4h_pct: -0.983726175274
BTC_OI_24h_pct: 0.052717862007
ETH_OI_24h_pct: -1.4307672328
market_volume_change_24h_pct: -22.302487579344174
```

## Source boundaries

- BTC and ETH ETF rows were explicitly `STALE` and older than the reconciled ETF ledger.
- CFGI global, BTC and ETH were unavailable.
- Stablecoin global market cap and total DeFi TVL were unavailable.
- Realized volatility was unavailable because only thirteen settled hourly candles were present.
- The GeckoTerminal WRAP/WETH row was retained as source-QA only because of its low-reserve anomaly.

This record preserves the collector evidence without granting framework interpretation or canonical authority.