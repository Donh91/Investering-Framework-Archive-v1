# DATA PING Mandatory-Owner-Unavailable Source Record

```yaml
run_id: dprun_20260804_134800_01
snapshot_id: dpsnap_20260804_134800_01
snapshot_utc: 2026-08-04T13:48:00Z
freeze_recorded_at_utc: 2026-08-04T13:48:00Z
contract: DATA_PING_RUN_FIRST_STATELESS_v1
version: 15.1.1
runtime: DATA_PING_LONGITUDINAL_COLLECTOR_v1
collector_status: PARTIAL
planned_core_actions: 60
attempted_core_actions: 60
source_reported_PASS: 23
source_reported_PARTIAL: 3
source_reported_UNAVAILABLE: 34
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

The run also lacks usable settled ETF values, a completed breadth aggregate and membership hash, a global stablecoin total and an accepted predecessor. The packet therefore declares itself unusable for main-thread ingest and cannot replace the latest valid bounded observation or advance the canonical chain.

## Current diagnostics retained

### CoinGecko

```yaml
BTC_price_usd: 63953
ETH_price_usd: 1871.27
ETHBTC_derived_ratio: 0.029260754
BTC_24h_pct: 1.831627
ETH_24h_pct: 1.360254
BTC_dominance_pct: 56.497521
ETH_dominance_pct: 9.948181
total_market_cap_usd: 2272722955017.972
total_volume_usd: 55895487859.56221
```

Diagnostic comparison against the latest valid bounded observation `run_18f02b7aa0334c9e`:

```yaml
BTC_price_change_pct: 0.564503
ETH_price_change_pct: 0.726678
ETHBTC_derived_change_pct: 0.139473
```

These deltas are cross-owner diagnostics only. The prior observation used Binance direct values, while this run uses CoinGecko and a derived ratio.

### OKX current cross-check

```yaml
BTC_last: 63867.8
BTC_mark: 63833.4
BTC_index: 63888.2
BTC_basis_bps: -8.5779
BTC_funding_rate: 0.0001
BTC_open_interest_usd: 2028080636.0000087
ETH_last: 1867.61
ETH_mark: 1866.23
ETH_index: 1868.11
ETH_basis_bps: -10.0636
ETH_funding_rate: 0.0000063853622319
ETH_open_interest_usd: 1341871935.8878434
```

OKX is retained as a current venue diagnostic. It cannot substitute for the missing mandatory Binance owner package or create longitudinal feature deltas.

## Sentiment and macro

```yaml
CFGI_global: 49
CFGI_global_status: PASS
CFGI_ETH: 57
CFGI_ETH_status: PASS
CFGI_BTC: 46
CFGI_BTC_status: PARTIAL_OLD_SOURCE_DATE
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