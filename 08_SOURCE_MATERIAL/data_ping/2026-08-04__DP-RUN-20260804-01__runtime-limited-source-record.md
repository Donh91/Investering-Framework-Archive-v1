# DATA PING Runtime-Limited Source Record

```yaml
run_id: DP-RUN-20260804-01
snapshot_id: DP-SNAPSHOT-20260804-01
collector_status: PARTIAL
packet_usable_for_main_thread_ingest: false
execution_order_status: FAIL
planned_core_actions: 60
passed_core_actions: 14
partial_core_actions: 5
skipped_runtime_limit_core_actions: 41
planned_optional_actions: 1
skipped_optional_actions: 1
snapshot_utc: null
freeze_recorded_at_utc: null
max_final_source_timestamp_utc: 2026-08-04T10:10:12.893Z
freeze_count: 1
post_freeze_call_count: 0
canonical_predecessor_available: false
```

## Why this run is non-decision-bearing

The collector exhausted its runtime budget before completing the required source plan. CoinGecko page 2, all FRED actions, all DeFiLlama actions, GeckoTerminal, all Binance Context actions and all OKX cross-check actions were skipped. Public-web tables were reached but no usable ETF or CFGI values were extracted. Required snapshot and freeze timestamps are null.

The run therefore cannot:

- replace the latest bounded DATA PING observation;
- advance the canonical predecessor;
- authorize breadth, rotation, entry, rebuy or portfolio gates;
- produce longitudinal deltas;
- update Master Monday, Cycle Navigator or Prospective Accumulation counts.

## Snapshot-only evidence retained

The final Binance source group completed and provides a narrow current-price diagnostic:

```yaml
BTCUSDT_last: 63538.31
ETHUSDT_last: 1857.06
ETHBTC_direct: 0.02923
BTC_funding_current: 0.00008881
ETH_funding_current: 0.00009011
BTC_open_interest: 109013.152
ETH_open_interest: 2351960.554
BTC_basis_bps: -3.334
ETH_basis_bps: -3.263
```

Comparison against the latest accepted bounded observation `run_18f02b7aa0334c9e` is diagnostic only:

```yaml
BTC_price_change_pct: -0.087587
ETH_price_change_pct: -0.038218
ETHBTC_change_pct: 0.034223
BTC_open_interest_change_pct: -0.024932
ETH_open_interest_change_pct: 0.463017
BTC_funding_rate_delta: 0.00001429
ETH_funding_rate_delta: 0.00002570
```

The narrow snapshot shows essentially flat prices, slightly higher ETH open interest and higher current funding. Because taker flow, settled windows, positioning, ETF flows, complete breadth, macro and cross-venue context are absent, no market-state inference is authorized.

## Partial breadth

Only CoinGecko page 1 was executed:

```yaml
raw_rows: 50
page_2_executed: false
membership_hash: null
advance_ratio: null
scored_gate_permission: NOT_AUTHORIZED
```

No breadth result exists and no current v1.1 reclassification is possible.

## Final classification

```yaml
classification: RUNTIME_LIMITED_NON_DECISION_OBSERVATION
market_pointer_effect: NONE
bounded_pointer_effect: NONE
canonical_state_change: NONE
portfolio_effect: NONE
operational_risk_class_change: NONE
```

The full packet remains preserved in the originating conversation transport.