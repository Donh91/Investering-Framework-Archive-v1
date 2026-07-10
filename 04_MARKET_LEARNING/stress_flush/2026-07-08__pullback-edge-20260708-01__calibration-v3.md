# Pullback Edge Calibration v3 — PULLBACK_EDGE_20260708_01

**Dato:** 2026-07-08 onward  
**Status:** CALIBRATION_ACTIVE / PROVISIONAL_LEARNING_ONLY  
**Område:** pullback edge / stress detection / tactical trim calibration  
**Primary folder:** `04_MARKET_LEARNING/stress_flush/`  
**Related folders:** `02_DATA_PING/live_state_handover/`, `03_WEEKLY_OPERATIONS/canonical_backbone/`  
**Depends on:** framework-approved event anchors and DATA PING Hybrid v0.5.1 consolidated

---

## Calibration version chain

```text
VERSION_1: SUPERSEDED
VERSION_2: SUPERSEDED
VERSION_3: CORRECTED_ACTIVE
SILENT_OVERWRITE: NO
```

Correction authority: main framework.

The superseded rows are preserved through correction lineage. Version 3 is the active raw calibration record.

---

## Framework-approved anchor

```yaml
edge_event_id: PULLBACK_EDGE_20260708_01
reference_run_id: DEEP_DATA_PING_V4_20260708T140300Z
reference_time: 2026-07-08T14:03:00Z
reference_price_btc: 61784.48
reference_anchor_status: FRAMEWORK_SUPPLIED_ACCEPTED
first_resolving_time: 2026-07-08T20:06:00Z
```

Pending canonical anchors:

```yaml
canonical_first_watch_time: FRAMEWORK_PENDING_EXACT_ANCHOR
canonical_first_near_present_time: FRAMEWORK_PENDING_EARLIER_HISTORY_CHECK
earliest_source_backed_near_present_candidate_time: 2026-07-08T11:15:00Z
earliest_source_backed_near_present_candidate_run: DATA_PING_V4_20260708T111500Z
```

---

## Corrected Event Path Aggregate

Measurement cutoff for this active row: `2026-07-10T11:59:38Z`.

```yaml
EVENT_PATH_AGGREGATE:
  calibration_row_version: 3
  correction_status: CORRECTED_ACTIVE
  edge_event_id: PULLBACK_EDGE_20260708_01
  reference_time: 2026-07-08T14:03:00Z
  event_trigger_price: 61784.48
  measurement_cutoff_time: 2026-07-10T11:59:38Z
  current_price_at_cutoff: 64425.18
  event_high_so_far: 64494.84
  event_low_so_far: 61544.56
  event_low_time: 2026-07-08T15:25:00Z_MINUTE_BUCKET
  event_low_time_cest: 2026-07-08T17:25:00_CEST_MINUTE_BUCKET
  event_low_exact_second: DATA_MISSING
  time_to_event_low: 1H22M
  max_favorable_downside_excursion_pct: 0.3883
  max_adverse_upside_excursion_pct: 4.3868
  current_move_from_trigger_pct: 4.2741
  survival_gate: 61900
  hourly_intervals_with_any_trade_below_survival_gate: 6
  cumulative_clock_duration_below_survival_gate: NOT_COMPUTED
  hourly_closes_below_survival_gate: 3
  hourly_closes_above_survival_gate_after_final_reclaim: 32
  reclaim_gate: 63300
  reclaim_gate_attempts: 2_DISTINCT_ATTEMPT_CLUSTERS
  reclaim_gate_successes_current: 1
  reclaim_gate_successes_close_confirmed: 0
  ethbtc_repair_gate: 0.0275
  ethbtc_repair_gate_tests: 1_DISTINCT_TEST_CLUSTER
  ethbtc_repair_gate_losses: 0
  current_event_phase: RESOLVING_RECLAIM_HOLD_TEST
  measurement_scope: RAW_PATH_ONLY
  signal_quality_score: NOT_DETERMINED_BY_DATA_PING
```

Interval counts must not be interpreted as actual clock duration.

---

## Corrected 24H Outcome

```yaml
OUTCOME_MATURATION_ROW_24H:
  calibration_row_version: 3
  correction_status: CORRECTED_ACTIVE
  edge_event_id: PULLBACK_EDGE_20260708_01
  measurement_horizon: 24H
  horizon_status: MATURED
  reference_time: 2026-07-08T14:03:00Z
  reference_price: 61784.48
  maturity_time: 2026-07-09T14:03:00Z
  measurement_window: 2026-07-08T14:03:00Z_TO_2026-07-09T14:03:00Z
  horizon_high: 63283.26
  horizon_low: 61544.56
  horizon_close: 63031.52
  horizon_close_method: LAST_COMPLETED_1M_CLOSE_BEFORE_EXACT_HORIZON
  horizon_close_timestamp: 2026-07-09T14:02:59Z
  horizon_close_offset_seconds: 1
  max_drawdown_pct: -0.3883
  max_rebound_pct: 2.4258
  close_move_from_reference_pct: 2.0184
  time_to_low: 1H22M
  survival_gate_outcome: LOST_AND_RECLAIMED_BEFORE_HORIZON
  survival_hourly_intervals_with_trade_below: 6
  survival_hourly_closes_below: 3
  maturity_price_above_survival_gate: YES
  reclaim_gate_outcome: APPROACH_ONLY
  reclaim_gate_high: 63283.26
  reclaim_gate_distance_below_at_high: 16.74
  reclaim_gate_touched: NO
  ethbtc_gate_outcome: HELD_REPAIR_GATE
  ethbtc_horizon_low: 0.02770
  ethbtc_horizon_value: 0.02772
  last_verified_sensor_state_before_horizon: WATCH
  last_verified_alert_status_before_horizon: RESOLVING
  last_verified_state_run_id: DATA_PING_HYBRID_v0_5_1_20260709T063200Z
  last_verified_state_timestamp: 2026-07-09T06:32:00Z
  state_measurement_offset_minutes: 451
  exact_sensor_state_at_horizon: DATA_MISSING
  exact_framework_state_at_horizon: DATA_MISSING
  framework_state_backfill: FORBIDDEN
  data_quality: MEDIUM
  signal_scoring: DEFERRED_TO_MAIN_FRAMEWORK
```

The last verified sensor state before the horizon is not an exact horizon state.

---

## Pending Outcome Rows

```yaml
OUTCOME_MATURATION_ROW_72H:
  measurement_horizon: 72H
  horizon_status: PENDING
  maturity_time: 2026-07-11T14:03:00Z

OUTCOME_MATURATION_ROW_7D:
  measurement_horizon: 7D
  horizon_status: PENDING
  maturity_time: 2026-07-15T14:03:00Z

OUTCOME_MATURATION_ROW_EVENT_CLOSE:
  measurement_horizon: EVENT_CLOSE
  horizon_status: PENDING
  maturity_time: FRAMEWORK_EVENT_CLOSE_PENDING
```

Do not fabricate, score or prematurely mature these rows.

---

## Provisional Framework Learning Candidate

This is not ratified learning.

```text
MARKET_STRESS_DETECTION_VALUE:
Provisional evidence suggests the event detector identified real but short-lived gate stress.

TACTICAL_TRIM_EXECUTION_VALUE:
Provisional evidence is weak at the 24H horizon.
Only approximately 0.3883% additional downside occurred after the canonical PRESENT anchor before a rebound of approximately 2.4258% within 24 hours.

FINAL_LEARNING_STATUS:
PENDING_72H_7D_AND_EVENT_CLOSE
```

Main framework must distinguish:

```text
MARKET_STRESS_DETECTED
from
SUFFICIENT_EXECUTION_EDGE_TO_TRIM
```

No final false-positive, false-negative, profitability or success judgment is ratified in this file.

---

## Correction Log Summary

```yaml
CALIBRATION_CORRECTION_LOG:
  correction_id: CAL_CORR_PULLBACK_EDGE_20260708_01_V3
  correction_authority: MAIN_FRAMEWORK
  correction_status: APPLIED
  superseded_versions:
    - VERSION_1
    - VERSION_2
  active_version: VERSION_3
  key_anchor_corrections:
    first_present_time: 2026-07-08T14:03:00Z
    first_present_run: DEEP_DATA_PING_V4_20260708T140300Z
    event_trigger_price: 61784.48
    event_low_so_far: 61544.56
    event_low_time: 2026-07-08T15:25:00Z_MINUTE_BUCKET
    time_to_event_low: 1H22M
  field_hygiene:
    exact_horizon_state_backfill: FORBIDDEN
    interval_count_named_as_hours: FORBIDDEN
    candidate_anchor_promoted_without_framework: FORBIDDEN
  interpretation_change: NONE
  signal_scoring_change: NONE
```
