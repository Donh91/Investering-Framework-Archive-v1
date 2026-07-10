# Active Gate and Edge Event Registry

**Dato:** 2026-07-10  
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
  gate_registry_source: main_framework_current_thread
  gate_registry_timestamp: 2026-07-10T11:59:38Z
  gate_registry_confidence: HIGH
  gate_registry_status: CURRENT
  btc_reclaim_gate: 63300
  btc_survival_gate: 61900
  btc_deterioration_gate: 59400
  ethbtc_repair_gate: 0.0275
  ethbtc_confirmation_gate: 0.0300
  notes:
    - Values are active runtime gates for the current W28 context.
    - They are not permanent hard-coded price levels.
    - Main framework must issue the next registry update when active structure changes.
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
  event_close_time: PENDING
  event_close_authority: MAIN_FRAMEWORK_ONLY
```

---

## Accepted Current State

As of the latest reviewed truth-layer run in this audit window:

```text
FRAMEWORK_EDGE_STATE: WATCH
ALERT_STATUS: RESOLVING
SELL_A_BID_EDGE: WATCH / FADING
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
```

This state is an operational framework interpretation, not a DATA PING sensor conclusion.

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
