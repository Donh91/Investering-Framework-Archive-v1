# Active Gate and Edge Event Registry

**Initial date:** 2026-07-10  
**Last framework review:** 2026-07-11T00:05:00Z  
**Status:** CANONICAL_RUNTIME_CONFIGURATION  
**Område:** DATA PING runtime handover / active gates / active edge event  
**Primary folder:** `02_DATA_PING/live_state_handover/`  
**Related folders:** `02_DATA_PING/protocols/`, `04_MARKET_LEARNING/stress_flush/`  
**Depends on:** `2026-07-10__data-ping-hybrid-v0-5-1-auto-edge-escalator-consolidated__canonical.md`

---

## Ownership

```text
ACTIVE_GATE_REGISTRY_OWNER: MAIN_FRAMEWORK / CHATGPT
EDGE_EVENT_ID_OWNER: MAIN_FRAMEWORK / CHATGPT
USER_MANUAL_GATE_ANALYSIS_REQUIRED: NO
DATA_PING_MAY_INFER_OR_CHANGE_VALUES: NO
```

This file is runtime configuration. It is not permanent sensor methodology.

A newer explicit main-framework registry supersedes this file's values.

---

## Active Gate Registry

```yaml
ACTIVE_GATE_REGISTRY:
  gate_registry_id: GATE_REGISTRY_2026W28_V1
  gate_registry_source: main_framework_current_thread_and_github_canonical_runtime
  gate_registry_timestamp: 2026-07-10T11:59:38Z
  gate_registry_confidence: HIGH
  gate_registry_status: CURRENT
  last_framework_confirmation_time: 2026-07-11T00:05:00Z
  btc_reclaim_gate: 63300
  btc_survival_gate: 61900
  btc_deterioration_gate: 59400
  ethbtc_repair_gate: 0.0275
  ethbtc_confirmation_gate: 0.0300
  notes:
    - Values are active runtime gates for the current W28 context.
    - They are not permanent hard-coded price levels.
    - Main framework must issue the next registry update when active structure changes.
    - DATA PING runs after this review should not mark the registry lineage stale if they consume this exact registry identity and timestamp.
```

---

## Active Edge Event

```yaml
ACTIVE_EDGE_EVENT:
  edge_event_id: PULLBACK_EDGE_20260708_01
  edge_event_type: PULLBACK_EDGE
  event_status: OPEN_RESOLVING
  framework_edge_state: WATCH
  framework_alert_status: RESOLVING
  canonical_first_present_time: 2026-07-08T14:03:00Z
  canonical_first_present_run_id: DEEP_DATA_PING_V4_20260708T140300Z
  canonical_trigger_price_btc: 61784.48
  canonical_first_resolving_time: 2026-07-08T20:06:00Z
  canonical_first_watch_time: FRAMEWORK_PENDING_EXACT_ANCHOR
  canonical_first_near_present_time: FRAMEWORK_PENDING_EARLIER_HISTORY_CHECK
  earliest_source_backed_near_present_candidate_time: 2026-07-08T11:15:00Z
  earliest_source_backed_near_present_candidate_run: DATA_PING_V4_20260708T111500Z
  latest_framework_accepted_run_id: DATA_PING_HYBRID_v0_5_1_20260710T233405Z
  latest_framework_accepted_run_time: 2026-07-10T23:34:05Z
  latest_material_transition: BTC_FIRST_DAILY_CLOSE_ABOVE_63300_WITH_ETHBTC_REPAIR_HELD
  event_close_candidate: YES_AFTER_72H_MATURITY_IF_NO_REESCALATION
  event_close_time: PENDING
  event_close_authority: MAIN_FRAMEWORK_ONLY
```

---

## Accepted Current State

As of the latest reviewed truth-layer run:

```text
FRAMEWORK_EDGE_STATE: WATCH
ALERT_STATUS: RESOLVING
EVENT_STATUS: OPEN_RESOLVING / CLOSURE_CANDIDATE
SELL_A_BID_EDGE: INACTIVE_FOR_NEW_TRIM
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
BTC_RECLAIM_STATUS: FIRST_DAILY_CLOSE_CONFIRMED / PERSISTENCE_PENDING
ETHBTC_REPAIR_STATUS: HELD / 0.0300_CONFIRMATION_NOT_REACHED
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
LARGE_CAP_BUY_WINDOW: WATCH_ONLY / NOT_OPEN
```

Framework interpretation:

- The first completed BTC daily close above 63.3K materially de-escalates the original pullback event.
- It does not by itself prove broad recovery, rotation or deployment because 7D breadth remains weak, completed ETF flow is mixed/negative, stablecoin deployment is unknown and leverage is rebuilding.
- Preserve WATCH / RESOLVING through the 72H maturity point unless the event re-escalates.
- If the 72H row matures without renewed loss of 63.3K/61.9K, ETH/BTC repair loss or broad deterioration, main framework should review formal event close.

This state is an operational framework interpretation, not a DATA PING sensor conclusion.

---

## Current-run acceptance packet

```yaml
framework_acceptance_status_current_run: ACCEPTED
accepted_run_id: DATA_PING_HYBRID_v0_5_1_20260710T233405Z
accepted_sensor_state: WATCH
accepted_alert_status: RESOLVING
accepted_gate_registry_id: GATE_REGISTRY_2026W28_V1
accepted_gate_registry_timestamp: 2026-07-10T11:59:38Z
accepted_gate_registry_confidence: HIGH
accepted_event_id: PULLBACK_EDGE_20260708_01
accepted_new_alert: NO
accepted_portfolio_action: NO_NEW_ACTION
```

Historical field hygiene:

```text
The intermediate 2026-07-10T17:29:31Z RAW_CALIBRATION_ROW field
FRAMEWORK_ACCEPTED_ALERT_FROM_PRIOR_FEEDBACK: WATCH
was incorrect. The prior accepted alert status was RESOLVING.
Preserve the old row and append a correction; do not silently overwrite it.
```

---

## Runtime Missing/Stale Rule

If this registry becomes missing or stale:

```text
FRAMEWORK_RUNTIME_CONFIG_STATUS: MISSING / STALE
FRAMEWORK_ESCALATION_FLAG: CONFIG_REVIEW_NEEDED
RAW_DATA_COLLECTION: CONTINUE
MECHANICAL_SENSOR_COLLECTION: CONTINUE
GATE_DEPENDENT_CLASSIFICATION: MISSING / STALE
```

DATA PING must not derive replacement gates from market prices.
