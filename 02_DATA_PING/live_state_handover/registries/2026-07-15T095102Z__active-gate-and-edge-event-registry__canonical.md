# Active Gate and Edge Event Registry — 2026-07-15T095102Z

**Status:** CANONICAL_RUNTIME_CONFIGURATION  
**Owner:** MAIN_FRAMEWORK / CHATGPT  
**Supersedes runtime state reviewed at:** 2026-07-14T18:31:24Z

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
  latest_framework_accepted_data_ping_id: DATA_PING_V4_20260715T095102Z
  latest_framework_review_time: 2026-07-15T10:03:26Z
  resolution_candidate: STRENGTHENED_BUT_CLOSE_VERIFICATION_BLOCKED
  current_positive_evidence:
    - BTC_CURRENT_COINGECKO_FALLBACK_ABOVE_63300
    - ETHBTC_DERIVED_ABOVE_0285
    - BREADTH_1H_74_3_PERCENT
    - BREADTH_24H_85_7_PERCENT
    - BREADTH_7D_62_9_PERCENT
    - BTC_ETF_2026_07_14_POSITIVE_181_1M
    - ETH_ETF_2026_07_14_POSITIVE_58_3M
    - PRICE_BREADTH_AND_LATEST_COMPLETED_ETF_ALIGNED_UP
  unresolved_requirements:
    - BTC_COMPLETED_2026_07_14_CEST_CLOSE_MISSING
    - ETH_COMPLETED_2026_07_14_CEST_CLOSE_MISSING
    - ETHBTC_COMPLETED_2026_07_14_CEST_CLOSE_MISSING
    - DIRECT_ETHBTC_MISSING
    - HOURLY_LEDGER_AND_PERSISTENCE_EXTENSION_MISSING
    - BINANCE_SPOT_TAKER_MISSING
    - FUTURES_FUNDING_OI_BASIS_AND_LEVERAGE_MISSING
    - ETHBTC_BELOW_0300
    - CURRENT_2026_07_15_ETF_SESSION_PENDING
    - OFFICIAL_STABLECOIN_HISTORY_MISSING
    - MARKET_WIDE_CVD_UNAVAILABLE
    - DECLARED_PREDECESSOR_20260714T203757Z_ARCHIVE_GAP
  new_pullback_alert: NO
  active_trim_signal: NO
  event_close_time: PENDING
  event_close_authority: MAIN_FRAMEWORK_ONLY
  latest_material_update: 02_DATA_PING/live_state_handover/event_updates/2026-07-15T095102Z__rotation-repair-edge__positive-flow-breadth-close-verification-blocked.md
```

## Accepted current framework state

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
RESOLUTION_CANDIDATE: STRENGTHENED — CLOSE VERIFICATION BLOCKED
BTC_RECLAIM_STATUS: CURRENT_FALLBACK_ABOVE / COMPLETED_14JUL_CLOSE_UNKNOWN
BTC_SURVIVAL_STATUS: CURRENT_FALLBACK_ABOVE / NO_NEW_CLOSE_LEDGER
ETHBTC_REPAIR_STATUS: DERIVED_ABOVE_0285 / DIRECT_AND_COMPLETED_CLOSE_UNKNOWN / BELOW_0300
BREADTH_STATUS: 1H_BROAD / 24H_BROAD / 7D_ABOVE_MAJORITY
ETF_STATUS: 14JUL_BTC_AND_ETH_POSITIVE / 15JUL_PENDING
FLOW_STATUS: LATEST_COMPLETED_ETF_IMPROVED / TAKER_AND_CVD_MISSING
DERIVATIVES_STATUS: MISSING_CURRENT_RUN
TYPE2_RESEARCH_STATUS: STRONGEST_CANDIDATE_SO_FAR / P2_TWO_NEGATIVE_SESSION_PATH_NOT_MET / NOT_CONFIRMED
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
framework_acceptance_status_current_run: ACCEPTED_LOW_OBSERVABILITY_CONTINUATION_POSITIVE_BREADTH_AND_ETF_NO_CLOSE_VERIFICATION_NO_UNLOCK
accepted_run_id: DATA_PING_V4_20260715T095102Z
accepted_declared_predecessor_run_id: DATA_PING_V4_20260714T203757Z
accepted_previous_canonical_run_id: DATA_PING_V4_20260714T182008Z
predecessor_lineage_status: GAP_PRESERVED_NO_RECONSTRUCTION
accepted_source_type: DIRECT_PROJECT_THREAD_DATA_PING_NEW_THREAD_CONTINUATION
accepted_event_id: ROTATION_REPAIR_EDGE_20260712_01
accepted_new_event: NO
accepted_new_pullback_alert: NO
accepted_portfolio_action: NO_NEW_ACTION
data_quality: LOW
```

The event remains open. Positive breadth and the completed 14 July ETF session strengthen the resolution candidate, but missing truth-layer close, hourly, taker and derivatives evidence prevents event closure or an entry-window decision.
