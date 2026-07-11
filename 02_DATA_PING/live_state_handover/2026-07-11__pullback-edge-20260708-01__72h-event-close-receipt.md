# Pullback Edge 72H Maturity and Event Close Receipt

**Event:** `PULLBACK_EDGE_20260708_01`  
**Framework close time:** 2026-07-11T14:33:24Z  
**Accepted source run:** `DATA_PING_HYBRID_v0_5_1_20260711T143324Z`  
**Status:** FRAMEWORK_ACCEPTED / EVENT_CLOSED_RESOLVED

---

## Canonical anchor

```yaml
edge_event_id: PULLBACK_EDGE_20260708_01
reference_time: 2026-07-08T14:03:00Z
reference_run_id: DEEP_DATA_PING_V4_20260708T140300Z
reference_price_btc: 61784.48
first_resolving_time: 2026-07-08T20:06:00Z
```

---

## Matured 72H outcome

```yaml
OUTCOME_MATURATION_ROW_72H:
  calibration_row_version: 1
  correction_status: NEW_MATURED_ROW
  edge_event_id: PULLBACK_EDGE_20260708_01
  measurement_horizon: 72H
  horizon_status: MATURED_ACCEPTED
  reference_time: 2026-07-08T14:03:00Z
  reference_price: 61784.48
  maturity_time: 2026-07-11T14:03:00Z
  horizon_high: 64692.83
  horizon_low: 61544.56
  horizon_close: 64248.00
  horizon_close_timestamp: 2026-07-11T14:02:59Z
  horizon_close_method: LAST_COMPLETED_1M_CLOSE_BEFORE_EXACT_HORIZON
  max_drawdown_pct: -0.3883
  max_rebound_pct: 4.7073
  close_move_from_reference_pct: 3.9873
  time_to_low: 1H22M
  survival_gate_outcome: LOST_AND_RECLAIMED
  reclaim_gate_outcome: RECLAIMED_AND_HELD_AT_HORIZON
  ethbtc_repair_gate_held: YES
  ethbtc_confirmation_gate_met: NO
  exact_sensor_state_at_horizon: DATA_MISSING
  exact_framework_state_at_horizon: DATA_MISSING
  framework_state_backfill: FORBIDDEN
  data_quality: MEDIUM
```

The missing exact state at the horizon does not invalidate the observed price and gate path. No state was retrospectively fabricated.

---

## Main-framework close decision

```yaml
EVENT_CLOSE_ROW:
  decision_authority: MAIN_FRAMEWORK
  decision_time: 2026-07-11T14:33:24Z
  source_run_id: DATA_PING_HYBRID_v0_5_1_20260711T143324Z
  prior_event_status: OPEN_RESOLVING
  final_event_status: CLOSED_RESOLVED
  prior_framework_edge_state: WATCH
  final_framework_edge_state_for_event: NONE
  prior_alert_status: RESOLVING
  final_alert_status: CLOSED
  close_reason:
    - 72H_HORIZON_MATURED
    - NO_REESCALATION
    - BTC_63300_RECLAIM_HELD_AT_HORIZON
    - BTC_61900_SURVIVAL_RECLAIMED
    - ETHBTC_0275_REPAIR_HELD
    - SHORT_TERM_BREADTH_REPAIRED_AT_REVIEW
    - LATEST_COMPLETED_BTC_AND_ETH_ETF_SESSION_POSITIVE
  active_trim_signal: NO
  new_pullback_alert: NO
  portfolio_action_change: NONE
```

---

## Interpretation boundary

```text
EVENT CLOSED does not mean:
- broad recovery confirmed;
- rotation confirmed;
- rebuy unlocked;
- large-cap deployment open;
- stablecoin deployment verified.
```

At close review, 7D breadth remained weak, ETH/BTC remained below 0.0300, stablecoin deployment was unknown and CVD was unavailable.

---

## Event-level calibration judgment

```yaml
market_stress_detection_value: PARTIALLY_SUPPORTED_SHORT_LIVED_STRESS
tactical_trim_execution_value_24h_72h: NOT_SUPPORTED
reason:
  - only 0.3883 percent additional downside followed the canonical PRESENT anchor
  - BTC then closed 3.9873 percent above the anchor at 72H
  - no active trim was justified by the matured path
final_7d_judgment: PENDING
```

The detector found real gate stress, but the matured 24H and 72H path does not support a tactical sell-a-bid execution edge for this event.

---

## Remaining follow-up

```yaml
OUTCOME_MATURATION_ROW_7D:
  horizon_status: PENDING
  maturity_time: 2026-07-15T14:03:00Z
  purpose: FINAL_CALIBRATION_ONLY
  may_reopen_closed_event: NO_UNLESS_NEW_EVENT_CRITERIA_TRIGGER
```

A later deterioration requires a new main-framework event ID rather than silently reopening this closed event.
