# DATA PING Mandatory-Owner-Unavailable Source Record

```yaml
run_id: dprun_20260804_142430_01
snapshot_id: dpsnap_20260804_142430_01
snapshot_utc: 2026-08-04T14:24:30Z
freeze_recorded_at_utc: 2026-08-04T14:24:30Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
source_reported_PASS: 21
source_reported_PARTIAL: 3
source_reported_UNAVAILABLE: 36
optional_UNAVAILABLE: 1
execution_order_status: PASS
receipt_reconciliation_status: PASS
freeze_count: 1
post_freeze_call_count: 0
canonical_predecessor_available: false
packet_usable_for_main_thread_ingest: false
classification: MANDATORY_DIRECT_OWNER_UNAVAILABLE_NON_DECISION_OBSERVATION
```

## Why the run is non-decision-bearing

All planned actions were attempted and the source-group order passed. The run nevertheless lost every Binance Context and Binance Final owner action because Binance returned a geographic eligibility restriction. This removed the mandatory direct BTC, ETH and ETH/BTC feeds, settled candles, books, funding history, open-interest anchors, positioning and taker-flow evidence.

The run also lacks usable settled ETF values, all current CFGI values, a completed breadth aggregate and membership hash, a global stablecoin total and an accepted predecessor. The packet therefore declares itself unusable for main-thread ingest and cannot replace the latest valid bounded observation or advance the canonical chain.

## Current diagnostics retained

### CoinGecko

```yaml
BTC_price_usd: 63750
ETH_price_usd: 1862.96
ETHBTC_derived_ratio: 0.029222221
BTC_24h_pct: 0.606022
ETH_24h_pct: 0.364106
BTC_dominance_pct: 56.455258
ETH_dominance_pct: 9.918070
total_market_cap_usd: 2262731620347.088
total_volume_usd: 55311665920.43433
```

Comparison with the immediately prior mandatory-owner-unavailable run `dprun_20260804_134800_01`:

```yaml
BTC_price_change_pct: -0.317421
ETH_price_change_pct: -0.444083
ETHBTC_derived_change_pct: -0.131688
```

These deltas are diagnostic only and do not create a framework transition.

### OKX current cross-check

```yaml
BTC_last: 63693.4
BTC_mark: 63681.3
BTC_index: 63695.8
BTC_basis_bps: -2.27645
BTC_funding_rate: 0.0001
BTC_open_interest_usd: 1997168928.776829
ETH_last: 1860.85
ETH_mark: 1861.13
ETH_index: 1861.88
ETH_basis_bps: -4.02819
ETH_funding_rate: 0.0000077320527897
ETH_open_interest_usd: 1320816562.0007834
```

Relative to the prior same-lane run, OKX BTC and ETH prices fell approximately 0.27% and 0.36%, while BTC and ETH open interest fell approximately 1.52% and 1.57%. Basis became less negative on both assets. These are venue diagnostics only; OKX cannot substitute for the missing mandatory Binance owner package.

## Sentiment and macro

```yaml
CFGI_global: null
CFGI_BTC: null
CFGI_ETH: null
VIX_latest: 15.86
DGS2_latest: 4.28
DGS10_latest: 4.75
DGS10_minus_DGS2: 0.47
DTWEXBGS_latest: 119.7034
```

## Missing authority

- Binance direct spot, books and derivative owners: unavailable because of geographic restriction.
- Settled return windows, funding history, OI anchors, taker flow and positioning: unavailable.
- ETF latest settled values: pages reached, rows not extracted.
- CFGI current values: source identity not resolved.
- Breadth: 100 raw rows collected, but filtering, aggregate values and membership hash were not completed.
- Stablecoin global total: unavailable; tertiary chain structure only.
- Accepted same-thread predecessor: unavailable.

## Final classification

```yaml
market_pointer_effect: NONE
bounded_pointer_effect: NONE
canonical_state_change: NONE
portfolio_effect: NONE
A_class_increment: 0
shadow_dual_run_increment: 0
operational_risk_class_change: NONE
```

The full user-supplied packet remains preserved in the originating conversation transport.