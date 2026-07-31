# DATA PING runtime-limited source record

```yaml
record_type: DATA_PING_SOURCE_RECORD
run_id: run_0877857fbb404762a1277c35a61f89c5
snapshot_id: snap_54bda23836584972bfef107098e467ae
snapshot_utc: 2026-07-31T22:08:30Z
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 10
skipped_core_actions_runtime_limit: 50
planned_optional_actions: 1
attempted_optional_actions: 0
collector_predecessor_id: snap_14af341f78aa43ca8b34d0cd2c0b7ca8
transport_integrity: UNVERIFIED_CHAT_TRANSPORT
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
```

## Successfully transmitted current observations

```yaml
BTC_CoinGecko_usd: 62923
ETH_CoinGecko_usd: 1860.29
derived_ETHBTC: 0.02956454714492316
total_market_cap_usd: 2242753637742.5225
total_volume_usd: 65726395553.972305
market_cap_change_24h_pct: -2.37689378476427
volume_change_24h_pct: 11.68610567857086
BTC_dominance_pct: 56.236398119862265
ETH_dominance_pct: 10.004389911620272
DGS2: 4.23
DGS10: 4.68
yield_curve_10y_minus_2y: 0.45
VIXCLS: 17.09
Ethereum_chain_TVL_usd: 40842674501.22896
Ethereum_stablecoin_chain_distribution_usd: 146820286322.47012
```

## Missing decision-bearing layers

The collector did not complete direct Binance spot, direct ETHBTC owner data, Binance derivatives, OKX cross-checks, ETF, CFGI, DEX or the filtered breadth aggregate. Top-100 source rows were retrieved, but filter aggregation and membership hash generation did not complete before freeze.

```yaml
breadth_aggregate: UNAVAILABLE_RUNTIME_LIMIT
breadth_membership_hash: UNAVAILABLE_RUNTIME_LIMIT
direct_ETHBTC: UNAVAILABLE_RUNTIME_LIMIT
funding_and_OI: UNAVAILABLE_RUNTIME_LIMIT
ETF: UNAVAILABLE_RUNTIME_LIMIT
CFGI: UNAVAILABLE_RUNTIME_LIMIT
all_core_actions_attempted: false
feature_integrity_input_coverage: FAIL
```

The packet is retained as source and QA evidence. Its current CoinGecko and macro fields may be used only as bounded diagnostics and cannot establish a new framework or portfolio state.