# T4 Execution Microstructure Repair Protocol v0.1

**Dato:** 2026-07-31  
**Status:** FORWARD_TEST / EXISTING_TEST_REPAIR  
**Område:** Research Lab / T4 Pullback Edge Event Outcomes / execution evidence  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `PULLBACK_EDGE_20260708_01_OUTCOMES`; WP04C5C Binance Spot owner capture; Sensor Relationship & Incremental Value Standard  
**Supersedes:** none  

---

## 1. Governance classification

```yaml
test_id: PULLBACK_EDGE_20260708_01_OUTCOMES
new_test_created: false
new_engine_created: false
new_shadow_layer_created: false
new_score_created: false
runtime_authority: zero
market_state_authority: zero
gate_authority: zero
portfolio_authority: zero
new_engine_freeze_compliance: PASS
```

This protocol is a direct evidence-capture repair to existing T4. It does not create a parallel execution engine.

The purpose is narrow:

> Determine whether reproducible public-market microstructure fields add incremental value to the existing price-only T4 pullback-event interpretation.

The external OverlordEins material is treated as educational source material only. Order blocks, FVG, Fibonacci and market-maker-intention narratives are not promoted as sensors.

---

## 2. Research question

```text
During eligible T4 pullback, sweep or reclaim events, do direct aggregate-trade and point-in-time order-book observations improve:

- absorption versus liquidity-vacuum classification;
- failed-reclaim identification;
- entry efficiency;
- invalidation placement;
- fakeout filtering;

relative to the existing price-only T4 baseline?
```

A positive answer requires benchmarked outcome rows. Explanatory quality is not evidence of edge.

---

## 3. Frozen source scope

### Assets

```text
BTCUSDT
ETHUSDT
```

ETHBTC remains part of the existing settled-candle owner capture but is not included in the first microstructure source extension.

### Venue

```text
Binance Spot public market-data-only endpoint
```

### Direct inputs

```text
GET /api/v3/depth
GET /api/v3/aggTrades
```

### Existing contextual inputs

```text
settled 1H BTCUSDT candles
settled 1H ETHUSDT candles
settled 1H ETHBTC candles
existing T4 event start, state path and outcome windows
```

---

## 4. Implemented source fields

A companion source capture, `scripts/data_terminal/binance_spot_microstructure_source.py`, is attached to the already verified WP04C5C Binance Spot owner workflow without changing the owner contract or binding authority.

Raw payloads are stored and hashed before interpretation.

Derived fields are deterministic:

```text
spread_bps
best_bid
best_ask
midpoint
quote-notional depth imbalance at 5 levels
quote-notional depth imbalance at 20 levels
quote-notional depth imbalance at 50 levels
aggressive_buy_quote
aggressive_sell_quote
taker_quote_imbalance
aggregate-trade VWAP
aggregate-trade high/low/open/close
source-window timestamps
```

Taker-side mapping is frozen as:

```text
buyer_is_maker = false -> aggressive buy
buyer_is_maker = true  -> aggressive sell
```

No value may be interpolated, forward-filled or inferred when the public response is unavailable.

---

## 5. Explicit limitations

A REST depth response is a point-in-time snapshot.

It does not provide:

```text
replenishment rate
cancellation rate
queue evolution
full historical order-book reconstruction
spoof-resilience
cross-venue confirmation
```

Therefore:

```text
POINT_IN_TIME_DEPTH != REPLENISHMENT
VISIBLE_WALL != EXECUTED_DEMAND
DEPTH_IMBALANCE != BUY_OR_SELL_SIGNAL
AGGTRADE_IMBALANCE != STANDALONE DIRECTIONAL AUTHORITY
```

Replenishment and cancellation claims remain `DATA_BLOCKED` until a stream-based, replayable source exists.

---

## 6. Eligible T4 event rows

A microstructure attachment is eligible only when an existing T4 event is already open or a pre-registered event condition is met by the main framework.

The source extension may not invent an event.

Each eligible attachment must freeze:

```yaml
event_id:
event_time_utc:
asset:
existing_t4_state:
existing_price_only_classification:
source_run_id:
source_payload_hashes:
spread_bps:
depth_imbalance_5:
depth_imbalance_20:
depth_imbalance_50:
taker_quote_imbalance:
aggressive_buy_quote:
aggressive_sell_quote:
aggtrade_window_start:
aggtrade_window_end:
point_in_time_depth_only: true
microstructure_interpretation: SUPPORTS_ABSORPTION | SUPPORTS_VACUUM | MIXED | NO_VALID_DATA
```

Outcome fields are added only after the existing T4 maturity windows:

```yaml
1H_return:
4H_return:
12H_return:
24H_return:
max_adverse_excursion:
max_favorable_excursion:
reclaim_survived:
failed_reclaim:
price_only_baseline_correct:
microstructure_augmented_correct:
incremental_value:
delay_cost:
final_classification:
```

A source attachment is not an outcome row.

---

## 7. Baselines

No order-block, FVG, Fibonacci or discretionary chart label is accepted as a baseline.

Frozen baselines:

```text
B0: existing T4 price-only event interpretation
B1: settled-candle prior swing / reclaim rule
B2: no microstructure adjustment
```

The augmented reading survives only if it improves B0/B1 after delay and data-availability costs.

---

## 8. Success, promotion and kill criteria

### Minimum evidence before any promotion discussion

```text
minimum eligible source attachments: 30
minimum matured outcome rows: 20
minimum BTC matured rows: 10
minimum ETH matured rows: 10
minimum distinct event episodes: 5
```

### Promotion condition

```text
- positive incremental value versus B0 and B1;
- lower failed-reclaim or fakeout classification error;
- no material increase in delay cost;
- stable result across BTC and ETH or explicit asset-specific limitation;
- reproducible raw-payload lineage;
- main-framework ratification.
```

### Kill or compression condition

```text
- no incremental value after 20 matured rows;
- benefit disappears after delay cost;
- depth fields are redundant with price/volume fields;
- frequent source unavailability prevents valid rows;
- point-in-time depth is misread as replenishment;
- discretionary labels re-enter the process;
- microstructure output changes action without main-framework ratification.
```

If depth adds no unique value but aggTrades does, remove depth fields and retain only the surviving source family. The inverse also applies.

---

## 9. Current status

```yaml
companion_source_capture: IMPLEMENTED
fixture_tests: PASS_LOCAL
raw_payload_preservation: IMPLEMENTED
artifact_hash_readback: IMPLEMENTED
live_microstructure_runs_verified: 0
eligible_source_attachments: 0
matured_outcome_rows: 0
baseline_result: NOT_EVALUABLE
behavior_changed: false
evidence_status: SOURCE_CAPTURE_IMPLEMENTED_NOT_PROVEN
next_action: PR_CI_THEN_TWO_EXPLICIT_LIVE_READBACKS
```

No current market state, rotation state, rebuy state, forecast, gate or portfolio action changes through this protocol.
