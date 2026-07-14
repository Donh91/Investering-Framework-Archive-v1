# Active Gate and Edge Event Registry

**Initial date:** 2026-07-10  
**Last framework review:** 2026-07-14T05:38:54Z  
**Status:** CANONICAL_RUNTIME_CONFIGURATION  
**Område:** DATA PING runtime handover / active gates / edge-event state  
**Primary folder:** `02_DATA_PING/live_state_handover/`  
**Related folders:** `02_DATA_PING/protocols/`, `04_MARKET_LEARNING/`  
**Depends on:** `2026-07-10__data-ping-hybrid-v0-5-1-auto-edge-escalator-consolidated__canonical.md`

---

## Ownership

```text
ACTIVE_GATE_REGISTRY_OWNER: MAIN_FRAMEWORK / CHATGPT
EDGE_EVENT_ID_OWNER: MAIN_FRAMEWORK / CHATGPT
USER_MANUAL_GATE_ANALYSIS_REQUIRED: NO
DATA_PING_MAY_INFER_OR_CHANGE_VALUES: NO
EVENT_CLOSE_AUTHORITY: MAIN_FRAMEWORK_ONLY
```

This file is runtime configuration, not permanent sensor methodology. A newer explicit main-framework registry supersedes these values.

---

## Active Gate Registry

```yaml
ACTIVE_GATE_REGISTRY:
  gate_registry_id: GATE_REGISTRY_2026W28_V1
  gate_registry_source: main_framework_current_thread_and_github_canonical_runtime
  gate_registry_timestamp: 2026-07-10T11:59:38Z
  gate_registry_confidence: HIGH
  gate_registry_status: CURRENT
  last_framework_confirmation_time: 2026-07-14T05:38:54Z
  btc_reclaim_gate: 63300
  btc_survival_gate: 61900
  btc_deterioration_gate: 59400
  ethbtc_repair_gate: 0.0275
  ethbtc_confirmation_gate: 0.0300
  notes:
    - Values remain active runtime gates into W29 unless explicitly superseded.
    - They are not permanent hard-coded levels.
    - DATA PING must not infer replacements.
```

---

## Active Edge Event

```yaml
ACTIVE_EDGE_EVENT:
  edge_event_id: ROTATION_REPAIR_EDGE_20260712_01
  edge_event_type: ROTATION_REPAIR_TEST
  event_status: OPEN_TRIGGERED
  framework_edge_state: NEAR_PRESENT
  framework_alert_status: STILL_ACTIVE
  canonical_start_time: 2026-07-12T00:39:18Z
  canonical_start_run_id: DATA_PING_HYBRID_v0_5_1_20260712T003918Z
  canonical_start_btc_price: 63780.65
  canonical_start_ethbtc: 0.027990
  canonical_first_framework_near_present_time: 2026-07-13T05:25:47Z
  canonical_first_framework_near_present_run_id: DATA_PING_V4_20260713T052547Z
  canonical_first_framework_near_present_btc_price: 62694.59
  canonical_first_framework_near_present_ethbtc: 0.028410
  latest_framework_accepted_data_ping_id: DATA_PING_V4_20260714T051915Z
  latest_framework_review_source_id: DATA_PING_V4_20260714T051915Z
  latest_framework_review_time: 2026-07-14T05:38:54Z
  current_trigger_reason:
    - BTC_CURRENT_BELOW_63300
    - BTC_LATEST_COMPLETED_CLOSE_BELOW_63300
    - BTC_INTRADAY_SURVIVAL_GATE_BREACH_RECOVERED_ON_CLOSE
    - BREADTH_24H_AND_7D_REMAIN_BELOW_MAJORITY
    - BTC_OI_EXPANDED_6_97_PERCENT_24H
    - BTC_POSITIONING_LONG_SKEWED
    - BTC_LATEST_COMPLETED_ETF_SESSION_NEGATIVE_424_7M
    - BTC_ETF_3_AND_5_SESSION_WINDOWS_NEGATIVE
    - BTC_AND_ETH_24H_SPOT_TAKER_PROXIES_NEGATIVE
    - STABLECOIN_SELECTED_ASSET_PROXY_CONTRACTING
  state_ceiling_reason:
    - BTC_CURRENT_AND_COMPLETED_CLOSE_REMAIN_ABOVE_61900
    - INTRADAY_SURVIVAL_BREACH_WAS_RECOVERED_ON_CLOSE
    - ETHBTC_DIRECT_REPAIR_GATE_0275_HOLDS_WITH_12_DAILY_CLOSES
    - SHORT_HORIZON_PRICE_AND_1H_BREADTH_REBOUND_PRESENT
    - NO_ACUTE_FUNDING_STRESS
    - MARKET_WIDE_CVD_UNAVAILABLE
  new_pullback_alert: NO
  active_trim_signal: NO
  event_close_time: PENDING
  event_close_authority: MAIN_FRAMEWORK_ONLY
  event_ledger: 02_DATA_PING/live_state_handover/2026-07-12__rotation-repair-edge-20260712-01__event-ledger.md
  latest_material_update: 02_DATA_PING/live_state_handover/event_updates/2026-07-14T051915Z__rotation-repair-edge__etf-negative-reclaim-failure-continuation.md
```

This remains the same active event. Reclaim quality and flow confirmation deteriorated materially, but the survival breach was intraday and recovered on the completed close while direct ETH/BTC repair still holds. The canonical PRESENT threshold is therefore not satisfied.

---

## Last Closed Event

```yaml
LAST_CLOSED_EDGE_EVENT:
  edge_event_id: PULLBACK_EDGE_20260708_01
  edge_event_type: PULLBACK_EDGE
  canonical_first_present_time: 2026-07-08T14:03:00Z
  canonical_first_present_run_id: DEEP_DATA_PING_V4_20260708T140300Z
  canonical_trigger_price_btc: 61784.48
  canonical_first_resolving_time: 2026-07-08T20:06:00Z
  event_close_time: 2026-07-11T14:33:24Z
  event_close_run_id: DATA_PING_HYBRID_v0_5_1_20260711T143324Z
  horizon_72h_close: 64248.00
  horizon_72h_close_move_pct: 3.9873
  post_trigger_max_additional_downside_pct: 0.3883
  post_trigger_max_rebound_pct: 4.7073
  tactical_trim_edge_at_24h_72h: NOT_SUPPORTED
  market_stress_detection_value: PARTIALLY_SUPPORTED_SHORT_LIVED_STRESS
  final_7d_calibration: PENDING
```

---

## Accepted Current Framework State

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
SELL_A_BID_EDGE: NEAR_PRESENT_NOT_ACTIONABLE
BTC_RECLAIM_STATUS: CURRENT_LOST / LATEST_DAILY_CLOSE_LOST / 24H_TOUCH_FAILED_TO_HOLD
BTC_SURVIVAL_STATUS: INTRADAY_BREACH_TO_61824_97 / COMPLETED_CLOSE_RECOVERED_ABOVE_61900 / CURRENT_ABOVE
ETHBTC_REPAIR_STATUS: DIRECT_HOLDS_ABOVE_0275 / 12_DAILY_CLOSES / NEAR_0285 / BELOW_0300
BREADTH_STATUS: 1H_BROADLY_POSITIVE / 24H_BELOW_MAJORITY / 7D_BELOW_MAJORITY
ETF_STATUS: BTC_MATERIAL_NEGATIVE_LATEST_AND_3_5_10_SESSION / ETH_LATEST_NEGATIVE_BUT_5_7_10_SESSION_POSITIVE
DERIVATIVES_STATUS: BTC_OI_EXPANDED_AND_LONG_SKEWED / NO_ACUTE_FUNDING_STRESS / ETH_OI_CONTRACTED
BROAD_RECOVERY_STATUS: NOT_CONFIRMED
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
LARGE_CAP_BUY_WINDOW: WATCH_ONLY / NOT_OPEN
```

The latest run confirms a material reclaim-quality failure and negative flow impulse. The Tuesday rebound is short-horizon only and does not create a trim, rebuy, rotation or deployment instruction.

---

## Current-run acceptance packet

```yaml
framework_acceptance_status_current_run: ACCEPTED_ETF_NEGATIVE_RECLAIM_FAILURE_CONTINUATION_NO_EDGE_UPGRADE
accepted_run_id: DATA_PING_V4_20260714T051915Z
accepted_predecessor_run_id: DATA_PING_V4_20260713T184513Z
accepted_source_type: DIRECT_PROJECT_THREAD_DATA_PING
framework_post_review_edge_state: NEAR_PRESENT
framework_post_review_alert_status: STILL_ACTIVE
accepted_gate_registry_id: GATE_REGISTRY_2026W28_V1
accepted_gate_registry_timestamp: 2026-07-10T11:59:38Z
accepted_gate_registry_confidence: HIGH
accepted_event_id: ROTATION_REPAIR_EDGE_20260712_01
accepted_new_event: NO
accepted_new_pullback_alert: NO
accepted_portfolio_action: NO_NEW_ACTION
data_quality: MEDIUM
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