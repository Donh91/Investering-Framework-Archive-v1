# Pullback Edge Event Ledger — PULLBACK_EDGE_20260708_01

**Dato:** 2026-07-08 onward  
**Status:** OPERATIONAL_EVENT_LEDGER / APPEND_ONLY  
**Område:** DATA PING edge event / state transitions / source lineage  
**Primary folder:** `02_DATA_PING/live_state_handover/`  
**Related folders:** `04_MARKET_LEARNING/stress_flush/`, `03_WEEKLY_OPERATIONS/canonical_backbone/`  
**Depends on:** DATA PING Hybrid v0.5.1 consolidated; Active Gate and Edge Event Registry

---

## Event identity

```yaml
edge_event_id: PULLBACK_EDGE_20260708_01
edge_event_type: PULLBACK_EDGE
event_status: OPEN_RESOLVING
framework_owner: MAIN_FRAMEWORK_CHATGPT
sensor_source: CUSTOM_GPT_DATA_PING_TRUTH_LAYER
shadow_sources: GROK_SHADOW_ONLY
```

Do not create a new event merely because the state changes. Continue this event until main framework formally closes it.

---

## Canonical framework anchors

```yaml
canonical_first_present_time: 2026-07-08T14:03:00Z
canonical_first_present_run_id: DEEP_DATA_PING_V4_20260708T140300Z
canonical_trigger_price_btc: 61784.48
canonical_first_resolving_time: 2026-07-08T20:06:00Z
canonical_first_watch_time: FRAMEWORK_PENDING_EXACT_ANCHOR
canonical_first_near_present_time: FRAMEWORK_PENDING_EARLIER_HISTORY_CHECK
earliest_source_backed_near_present_candidate_time: 2026-07-08T11:15:00Z
earliest_source_backed_near_present_candidate_run: DATA_PING_V4_20260708T111500Z
event_close_time: PENDING
```

The 11:15Z row is a source-backed candidate and is not promoted to canonical first NEAR_PRESENT without framework acceptance.

---

## State transition ledger

### 2026-07-08T11:15:00Z — source-backed pre-alert candidate

```yaml
run_id: DATA_PING_V4_20260708T111500Z
source_role: CUSTOM_GPT_TRUTH_LAYER
sensor_state_candidate: NEAR_PRESENT
framework_state_at_review: NEAR_PRESENT
alert_status: WATCH_HIGH
btc_gate_status: ABOVE_61900_MARGINAL / BELOW_63300
ethbtc_gate_status: HOLDS_0275
breadth_status: 1H_REPAIRED / 24H_VERY_WEAK / 7D_STRONG
etf_status: LATEST_POSITIVE / BTC_7D_NEGATIVE
notes: Source-backed early warning candidate; exact canonical first NEAR_PRESENT remains pending earlier-history check.
```

### 2026-07-08T14:03:00Z — canonical first PRESENT

```yaml
run_id: DEEP_DATA_PING_V4_20260708T140300Z
source_role: CUSTOM_GPT_TRUTH_LAYER
sensor_edge_candidate: PRESENT
framework_accepted_state: PRESENT
alert_status: TRIGGERED
btc_price: 61784.48
btc_gate_status: SURVIVAL_LOST_INTRADAY_CURRENT_BELOW / CLOSE_NOT_CONFIRMED
ethbtc_gate_status: HOLDS_REPAIR
breadth_status: 24H_VERY_WEAK
cfgi_status: FEAR_PRESSURE
derivatives_status: TAKER_SELL_SKEW / OI_NOT_EXPANDING_AGGRESSIVELY
etf_status: BTC_PRINT_POSITIVE_TREND_UNCONFIRMED / ETH_CONFIRMED
framework_note: Stress alert accepted. Tactical trim interpretation remains framework-owned.
```

### 2026-07-08T16:33:00Z — PRESENT still active

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260708T163300Z
sensor_edge_candidate: PRESENT
framework_accepted_state: PRESENT
alert_status: STILL_ACTIVE
btc_gate_status: BELOW_61900_CURRENT / CLOSE_NOT_CONFIRMED
ethbtc_gate_status: HOLDS_0275
breadth_status: 24H_6PCT / 7D_62PCT
derivatives_status: SELL_SKEW_LESS_EXTREME / OI_MIXED
downgrade_check: NO_DOWNGRADE
```

### 2026-07-08T20:06:00Z — first resolving downgrade

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260708T200600Z
sensor_edge_candidate: NEAR_PRESENT
framework_accepted_state: NEAR_PRESENT
alert_status: RESOLVING
btc_gate_status: RECLAIMED_61900_CURRENT / CLOSE_NOT_CONFIRMED
ethbtc_gate_status: HOLDS_0275
breadth_status: 1H_AND_7D_REPAIRED / 24H_STILL_WEAK
derivatives_status: SELL_SKEW_FADED_TO_MIXED
downgrade_check: DOWNGRADE_TO_NEAR_PRESENT
```

### 2026-07-09T06:32:00Z — downgrade to WATCH

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260709T063200Z
sensor_edge_candidate: WATCH
framework_accepted_state: WATCH
alert_status: RESOLVING
btc_gate_status: CURRENT_AND_DAILY_CLOSE_ABOVE_61900 / BELOW_63300
ethbtc_gate_status: HOLDS_0275
breadth_status: 1H_REPAIRED / 24H_REPAIRED / 7D_NOT_CONFIRMED
derivatives_status: SELL_SKEW_FADED_TO_MIXED / OI_NOT_EXPANDING
downgrade_check: DOWNGRADE_TO_WATCH
```

### 2026-07-09T17:48:00Z — WATCH maintained

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260709T174800Z
sensor_edge_candidate: WATCH
framework_accepted_state: WATCH
alert_status: WATCH
btc_gate_status: ABOVE_61900 / APPROACH_63300_NOT_RECLAIMED
ethbtc_gate_status: HOLDS_0275_NEAR_GATE
breadth_status: 1H_100 / 24H_76 / 7D_44
derivatives_status: MIXED_TO_BUY_DEFENSE
etf_status: BTC_LATEST_NEGATIVE / ETH_LATEST_POSITIVE
```

### 2026-07-10T04:39:00Z — current reclaim, close pending

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260710T043900Z
sensor_edge_candidate: WATCH_FADING
framework_accepted_state: WATCH
alert_status: RESOLVING
btc_gate_status: CURRENT_ABOVE_63300 / DAILY_CLOSE_NOT_CONFIRMED
ethbtc_gate_status: HOLDS_0275_NEAR_GATE
breadth_status: 24H_STRONG_REPAIR / 7D_NOT_CONFIRMED
derivatives_status: BUY_DEFENSE / OI_EXPANDING_MODERATELY
etf_status: LATEST_BTC_AND_ETH_NEGATIVE
```

### 2026-07-10T09:45:53Z — hourly reclaim hold

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260710T094553Z
sensor_edge_candidate: WATCH_FADING
framework_accepted_state: WATCH
alert_status: RESOLVING
btc_gate_status: CURRENT_AND_HOURLY_ABOVE_63300 / DAILY_CLOSE_PENDING
ethbtc_gate_status: GATE_TEST_DEFENDED / HOLDS_0275
breadth_status: 1H_69 / 24H_83 / 7D_57
derivatives_status: BUY_DEFENSE / BTC_OI_EXPANDING / LEVERAGE_REBUILDING
etf_status: LATEST_BTC_AND_ETH_NEGATIVE / 10JUL_PENDING
```

### 2026-07-10T11:59:38Z — WATCH maintained, no new alert

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260710T115938Z
sensor_edge_candidate: WATCH
framework_edge_state_baseline: WATCH
alert_status: RESOLVING
new_alert: NO
btc_gate_status: CURRENT_AND_HOURLY_ABOVE_63300 / DAILY_CLOSE_NOT_CONFIRMED
ethbtc_gate_status: HOLDS_0275
breadth_status: 1H_ROLLOVER / 24H_STRONG / 7D_WEAK
derivatives_status: OI_EXPANDING / FUNDING_POSITIVE / TAKER_NEUTRAL
etf_status: LATEST_BTC_AND_ETH_NEGATIVE / 10JUL_PENDING
downgrade_check: HOLD_WATCH / NO_NEW_ALERT
```

### 2026-07-10T17:29:31Z — hourly reclaim persistence, daily close pending

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260710T172931Z
sensor_edge_candidate: WATCH
framework_accepted_state: WATCH
alert_status: RESOLVING
new_alert: NO
btc_gate_status: CURRENT_AND_6_COMPLETED_HOURLY_CLOSES_ABOVE_63300 / DAILY_CLOSE_PENDING
ethbtc_gate_status: ABOVE_0275 / BELOW_0300
breadth_status: 1H_43 / 24H_83 / 7D_43
derivatives_status: FUNDING_POSITIVE / BTC_OI_24H_PLUS_4_42 / TAKER_NEUTRAL
etf_status: LATEST_COMPLETED_NEGATIVE / 10JUL_PENDING
framework_acceptance_note: Accepted retrospectively as unchanged WATCH / RESOLVING evidence.
field_hygiene_note: Prior-alert field was incorrectly written as WATCH; accepted prior alert status was RESOLVING.
```

### 2026-07-10T19:42:43Z — short-term breadth repair, daily close pending

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260710T194243Z
sensor_edge_candidate: WATCH
framework_accepted_state: WATCH
alert_status: RESOLVING
new_alert: NO
btc_gate_status: CURRENT_AND_HOURLY_ABOVE_63300 / DAILY_CLOSE_PENDING
ethbtc_gate_status: ABOVE_0275 / BELOW_0300
breadth_status: 1H_74 / 24H_77 / 7D_40
derivatives_status: FUNDING_POSITIVE / OI_EXPANDING / TAKER_NEUTRAL
etf_status: LATEST_COMPLETED_NEGATIVE / 10JUL_INCOMPLETE
downgrade_check: HOLD_WATCH / LONGER_BREADTH_AND_DAILY_CLOSE_PENDING
```

### 2026-07-10T23:34:05Z — first daily close above reclaim gate

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260710T233405Z
source_role: CUSTOM_GPT_TRUTH_LAYER
sensor_edge_candidate: WATCH
framework_accepted_state: WATCH
alert_status: RESOLVING
framework_acceptance_status: ACCEPTED
new_alert: NO
btc_current: 64185.23
btc_completed_daily_close: 64011.99
btc_gate_status: CURRENT_HOURLY_AND_FIRST_DAILY_CLOSE_ABOVE_63300
btc_consecutive_closes_above_61900: 8
btc_consecutive_closes_above_63300: 1
ethbtc_current: 0.027980
ethbtc_completed_daily_close: 0.028030
ethbtc_gate_status: NINE_DAILY_CLOSES_ABOVE_0275 / BELOW_0300
breadth_status: 1H_49 / 24H_80 / 7D_34
derivatives_status: FUNDING_POSITIVE / BTC_OI_24H_PLUS_3_72 / LATEST_TAKER_SELL_SKEW
etf_status: LATEST_COMPLETED_NEGATIVE / 10JUL_INCOMPLETE
framework_interpretation: Original pullback edge materially de-escalated; broad recovery and rotation remain unconfirmed.
event_close_candidate: YES_AFTER_72H_MATURITY_IF_NO_REESCALATION
downgrade_check: HOLD_WATCH_THROUGH_72H_MATURITY
```

---

## Current framework state

```text
FRAMEWORK_EDGE_STATE: WATCH
ALERT_STATUS: RESOLVING
EVENT_STATUS: OPEN_RESOLVING / CLOSURE_CANDIDATE
ACTIVE_TRIM_SIGNAL: NO
SELL_A_BID_EDGE: INACTIVE_FOR_NEW_TRIM
BTC_RECLAIM_STATUS: FIRST_DAILY_CLOSE_CONFIRMED / PERSISTENCE_PENDING
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
EVENT_CLOSE: REVIEW_AT_72H_MATURITY_IF_NO_REESCALATION
```

---

## Archive rule

Append only material truth-layer transitions, corrected anchors, matured outcome rows and framework event-close decisions.

Routine unchanged pings may remain in weekly RAW logs and do not require a separate canonical index entry.
