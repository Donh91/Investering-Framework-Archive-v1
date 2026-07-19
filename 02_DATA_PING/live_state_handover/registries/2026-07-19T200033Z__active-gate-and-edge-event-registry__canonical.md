# Active Gate and Edge Event Registry: 2026-07-19T200033Z

**Status:** CANONICAL_RUNTIME_CONFIGURATION  
**Owner:** MAIN_FRAMEWORK / CHATGPT  
**Accepted log:** `DATA_PING_V6_20260719T200033Z`  
**Source version:** `V6 ACTIVE`

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
  stage_1_etf_flow_requirement: THREE_CONSECUTIVE_POSITIVE_COMPLETED_BTC_ETF_SESSIONS_WITH_IBIT_POSITIVE
  stage_1_etf_flow_leg_status: COMPLETE_RATIFIED
  authority: CURRENT_EVENT_ONLY_NOT_UNIVERSAL
```

## Active event

```yaml
ACTIVE_EDGE_EVENT:
  edge_event_id: ROTATION_REPAIR_EDGE_20260712_01
  edge_event_type: ROTATION_REPAIR_TEST
  event_status: OPEN_TRIGGERED
  framework_edge_state: REPAIR_PRESENT_MATURING_MEDIUM_HORIZON_SPOT_AND_ETF_TRANSLATION_WITH_CROSS_SECTIONAL_AND_FUTURES_CONFIRMATION_MISSING
  framework_alert_status: ACTIVE_DE_ESCALATED_ONE_LEVEL_NOT_CLEARED
  latest_framework_accepted_data_ping_id: DATA_PING_V6_20260719T200033Z
  latest_framework_review_time: 2026-07-19T21:38:21Z
  decision_delta_class: MATERIAL_MARKET_INPUT_DELTA_AND_SOURCE_QUALITY_UPGRADE
  material_delta: V6_ACTIVATED_FIVE_SETTLED_BTC_CLOSES_ABOVE_63300_ETF_7_SESSION_FLOW_POSITIVE_AND_SPOT_4H_24H_POSITIVE_BUT_24H_7D_BREADTH_WEAK_AND_FUTURES_TAKER_BELOW_1
  pullback_warning: ACTIVE_DE_ESCALATED_ONE_LEVEL_NOT_CLEARED
  short_term_stabilization: STRUCTURAL_REPAIR_HELD_INTRADAY_FLOW_MIXED
  reclaim_status: FIVE_CONSECUTIVE_SETTLED_CLOSES_ABOVE_63300_CURRENT_ABOVE_63300_SUNDAY_CANDLE_PARTIAL
  current_positive_evidence:
    - BTC_CURRENT_64392_70_ABOVE_63300_AND_61900
    - FIVE_CONSECUTIVE_SETTLED_BTC_CEST_CLOSES_ABOVE_63300
    - SIX_CURRENT_WEEK_SETTLED_BTC_CEST_CLOSES_ABOVE_61900
    - DIRECT_ETHBTC_02888_ABOVE_0275
    - BTC_ETF_FOUR_SESSION_POSITIVE_STREAK
    - BTC_ETF_7_SESSION_SUM_PLUS_70_6M
    - IBIT_7_SESSION_SUM_PLUS_290_9M
    - BTC_AND_ETH_SPOT_TAKER_4H_AND_24H_POSITIVE
    - DYNAMIC_BREADTH_1H_POSITIVE_SHARE_62_86_PERCENT
    - V6_RAW_SOURCE_QUALITY_UPGRADED_TO_MEDIUM
  warning_evidence:
    - SUNDAY_CEST_WEEKLY_CANDLE_PARTIAL_NOT_SETTLED
    - DIRECT_ETHBTC_BELOW_0300_CONFIRMATION
    - DYNAMIC_BREADTH_24H_POSITIVE_SHARE_35_71_PERCENT
    - DYNAMIC_BREADTH_7D_POSITIVE_SHARE_31_43_PERCENT
    - DYNAMIC_BREADTH_24H_AND_7D_MEDIANS_NEGATIVE
    - BTC_AND_ETH_15M_SPOT_TAKER_NEGATIVE
    - ETH_1H_SPOT_TAKER_NEGATIVE
    - BTC_AND_ETH_FUTURES_TAKER_RATIOS_BELOW_1_ACROSS_1H_4H_24H
    - OFFICIAL_STABLECOIN_TOTAL_AND_HISTORY_UNAVAILABLE
    - MARKET_WIDE_CVD_UNAVAILABLE
    - CFGI_STALE_NOT_PERSISTENCE_ELIGIBLE
    - FIXED_RISK35_CANONICAL_IDENTITY_UNKNOWN
  current_decision:
    rotation: NO_ROTATION
    broad_recovery: NOT_CONFIRMED
    large_cap_window: WATCH_ONLY_NOT_OPEN
    new_entry_signal: NOT_ACTIVE
    active_trim_signal: NO
    new_pullback_alert: NO_EXISTING_ALERT_DE_ESCALATED_NOT_CLEARED
    portfolio_action: NONE
    user_action: HOLD_AND_WAIT
    risk_posture: ELEVATED_VIGILANCE_DE_ESCALATED
```

## Interpretation

Structure and medium-horizon source flow have improved materially. BTC has five consecutive settled CEST closes above 63.3K, the BTC ETF seven-session sum is positive, and Binance spot taker flow is positive over 4H and 24H for BTC and ETH. The prior strengthened pullback warning is therefore de-escalated by one level. It is not cleared because the Sunday weekly candle remains partial, ETH/BTC remains below 0.0300, 24H and 7D breadth remain weak, and Binance futures taker ratios remain below 1.

No portfolio action follows.
