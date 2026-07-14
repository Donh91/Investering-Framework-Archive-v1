# Active Gate and Edge Event Registry — 2026-07-14T182008Z

**Status:** CANONICAL_RUNTIME_CONFIGURATION  
**Owner:** MAIN_FRAMEWORK / CHATGPT  
**Supersedes runtime state reviewed at:** 2026-07-14T16:35:20Z

## Active gates

```yaml
ACTIVE_GATE_REGISTRY:
  gate_registry_id: GATE_REGISTRY_2026W28_V1
  gate_registry_status: CURRENT
  btc_reclaim_gate: 63300
  btc_survival_gate: 61900
  btc_deterioration_gate: 59400
  ethbtc_repair_gate: 0.0275
  ethbtc_confirmation_gate: 0.0300
  note: thresholds remain runtime gates and are not permanently hard-coded
```

## Active event

```yaml
ACTIVE_EDGE_EVENT:
  edge_event_id: ROTATION_REPAIR_EDGE_20260712_01
  edge_event_type: ROTATION_REPAIR_TEST
  event_status: OPEN_TRIGGERED
  framework_edge_state: NEAR_PRESENT
  framework_alert_status: STILL_ACTIVE
  latest_framework_accepted_data_ping_id: DATA_PING_V4_20260714T182008Z
  latest_framework_review_time: 2026-07-14T18:31:24Z
  resolution_candidate: STRENGTHENED_INTRADAY_ONLY
  current_positive_evidence:
    - BTC_CURRENT_ABOVE_63300
    - BTC_SIX_CONSECUTIVE_SETTLED_HOURLY_CLOSES_ABOVE_63300
    - ETHBTC_CURRENT_ABOVE_0285
    - ETHBTC_SEVEN_DISPLAYED_SETTLED_HOURLY_CLOSES_ABOVE_0285
    - BREADTH_24H_94_3_PERCENT
    - BTC_4H_24H_SPOT_TAKER_BUY_LEAN
    - ETH_1H_4H_24H_SPOT_TAKER_BUY_LEAN
    - BTC_OI_DOWN_3_53_PERCENT_24H_WHILE_PRICE_REMAINS_ELEVATED
  unresolved_requirements:
    - BTC_COMPLETED_DAILY_CLOSE_ABOVE_63300_MISSING
    - ETHBTC_COMPLETED_DAILY_CLOSE_ABOVE_0285_MISSING
    - ETHBTC_BELOW_0300
    - BREADTH_1H_COOLED_TO_62_9_PERCENT
    - BREADTH_7D_31_4_PERCENT_BELOW_MAJORITY
    - BTC_LATEST_COMPLETED_ETF_SESSION_NEGATIVE_424_7M
    - CURRENT_ETF_SESSION_PENDING
    - STABLECOIN_PROXY_SAMPLE_CHANGED_AND_NOT_PERSISTENCE_ELIGIBLE
    - ETH_OI_EXPANDED_10_33_PERCENT_24H
    - MARKET_WIDE_CVD_UNAVAILABLE
  new_pullback_alert: NO
  active_trim_signal: NO
  event_close_time: PENDING
  event_close_authority: MAIN_FRAMEWORK_ONLY
  latest_material_update: 02_DATA_PING/live_state_handover/event_updates/2026-07-14T182008Z__rotation-repair-edge__intraday-persistence-maintained.md
```

## Accepted current framework state

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
RESOLUTION_CANDIDATE: STRENGTHENED — INTRADAY ONLY
BTC_RECLAIM_STATUS: CURRENT_ABOVE / 6_SETTLED_HOURLY_CLOSES_ABOVE / LATEST_DAILY_CLOSE_BELOW
BTC_SURVIVAL_STATUS: HOLDS
ETHBTC_REPAIR_STATUS: ABOVE_0275 / 7_HOURLY_CLOSES_ABOVE_0285 / NO_DAILY_0285_PERSISTENCE / BELOW_0300
BREADTH_STATUS: 1H_COOLED_BELOW_70 / 24H_VERY_STRONG / 7D_WEAK
ETF_STATUS: BTC_LATEST_NEGATIVE / CURRENT_SESSION_PENDING
FLOW_STATUS: 4H_24H_IMPROVED / DURABLE_CONFIRMATION_INCOMPLETE
DERIVATIVES_STATUS: BTC_OI_COOLING / ETH_OI_EXPANDED / NO_ACUTE_FUNDING_STRESS
TYPE2_RESEARCH_STATUS: STRONGEST_CANDIDATE_SO_FAR / NOT_CONFIRMED
BROAD_RECOVERY_STATUS: NOT_CONFIRMED
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
LARGE_CAP_BUY_WINDOW: WATCH_ONLY / NOT_OPEN
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
PORTFOLIO_ACTION: NONE
```

## Current-run acceptance

```yaml
framework_acceptance_status_current_run: ACCEPTED_INTRADAY_RECLAIM_PERSISTENCE_AND_24H_TRANSMISSION_MAINTAINED_NO_COMPLETED_CLOSE_NO_UNLOCK
accepted_run_id: DATA_PING_V4_20260714T182008Z
accepted_predecessor_run_id: DATA_PING_V4_20260714T154709Z
accepted_source_type: DIRECT_PROJECT_THREAD_DATA_PING
accepted_event_id: ROTATION_REPAIR_EDGE_20260712_01
accepted_new_event: NO
accepted_new_pullback_alert: NO
accepted_portfolio_action: NO_NEW_ACTION
data_quality: MEDIUM
```

The event remains open. Intraday persistence strengthened the resolution candidate, but completed-close, multi-day breadth and flow evidence still control event closure and any entry-window decision. DATA PING may not close the event or infer replacement gates.
