# Active Gate and Edge Event Registry: 2026-07-20T054959Z

**Status:** CANONICAL_RUNTIME_CONFIGURATION  
**Owner:** MAIN_FRAMEWORK / CHATGPT  
**Latest accepted DATA PING:** `DATA_PING_V6_20260719T200033Z`  
**Latest accepted weekly closeout:** `MASTER_MONDAY_CLOSEOUT_W30_20260720T054959Z`  
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
  framework_edge_state: REPAIR_PRESENT_MATURING_SETTLED_WEEKLY_CONFIRMATION_WITH_BREADTH_AND_SHORT_HORIZON_FLOW_WEAKNESS
  framework_alert_status: ACTIVE_DE_ESCALATED_ONE_LEVEL_MAINTAINED_NOT_CLEARED
  latest_framework_accepted_data_ping_id: DATA_PING_V6_20260719T200033Z
  latest_framework_closeout_id: MASTER_MONDAY_CLOSEOUT_W30_20260720T054959Z
  latest_framework_review_time: 2026-07-20T06:09:51Z
  decision_delta_class: SETTLED_STRUCTURE_CONFIRMATION_WITH_SHORT_HORIZON_WARNING
  material_delta: W30_SETTLED_BTC_CLOSE_ABOVE_63300_AND_ETHBTC_ABOVE_0275_WITH_P1_SURVIVAL_HELD_BUT_DYNAMIC_BREADTH_WEAK_AND_1H_4H_SPOT_FLOW_NEGATIVE
  pullback_warning: ACTIVE_DE_ESCALATED_ONE_LEVEL_MAINTAINED_NOT_CLEARED
  short_term_stabilization: SETTLED_STRUCTURAL_REPAIR_CONFIRMED_SHORT_HORIZON_COOLING_ACTIVE
  reclaim_status: W30_SETTLED_WEEKLY_CLOSE_64415_75_ABOVE_63300_AND_61900
  current_positive_evidence:
    - BTC_W30_SETTLED_CLOSE_64415_75_ABOVE_63300_AND_61900
    - BTC_WEEKLY_CLV_0_6863
    - DIRECT_ETHBTC_W30_CLOSE_0_02891_ABOVE_0_0275
    - ETHBTC_HIGHER_WEEKLY_LOW_0_02821_VS_0_02758
    - P1_PROVISIONAL_RETENTION_66_50_PERCENT_REVIEW_NOT_DUE
    - NO_POST_REFERENCE_CLOSE_BELOW_62200
    - BTC_ETF_FOUR_SESSION_POSITIVE_STREAK
    - BTC_ETF_7_SESSION_SUM_PLUS_70_6M
    - BTC_AND_ETH_24H_SPOT_TAKER_POSITIVE
    - BTC_AND_ETH_24H_OI_MODESTLY_NEGATIVE_DELEVERAGING
  warning_evidence:
    - DIRECT_ETHBTC_BELOW_0_0300_CONFIRMATION
    - DYNAMIC_BREADTH_SAMPLE_CHANGED_NOT_COMPARABLE
    - DYNAMIC_BREADTH_1H_POSITIVE_SHARE_14_08_PERCENT
    - DYNAMIC_BREADTH_24H_POSITIVE_SHARE_23_94_PERCENT
    - DYNAMIC_BREADTH_7D_POSITIVE_SHARE_40_85_PERCENT
    - BTC_AND_ETH_1H_AND_4H_SPOT_TAKER_NEGATIVE
    - BTC_AND_ETH_FUTURES_TAKER_RATIOS_BELOW_OR_APPROXIMATELY_1
    - FIXED_RISK35_CANONICAL_IDENTITY_UNKNOWN
    - OFFICIAL_STABLECOIN_TOTAL_AND_HISTORY_UNAVAILABLE
    - MARKET_WIDE_CVD_UNAVAILABLE
  current_decision:
    rotation: NO_ROTATION
    broad_recovery: NOT_CONFIRMED
    large_cap_window: WATCH_ONLY_NOT_OPEN
    new_entry_signal: NOT_ACTIVE
    active_trim_signal: NO
    new_pullback_alert: NO_EXISTING_ALERT_MAINTAINED_NOT_CLEARED
    portfolio_action: NONE
    user_action: HOLD_AND_WAIT
    risk_posture: ELEVATED_VIGILANCE_DE_ESCALATED_NO_FURTHER_CLEARANCE
```

## Interpretation

The W30 settled weekly close confirms that the structural repair survived the week. BTC closed above the 63.3K reclaim and 61.9K survival gates, while direct ETH/BTC closed above 0.0275 and retained a higher weekly low. The warning is not cleared or further de-escalated because ETH/BTC remains below 0.0300, the current dynamic breadth sample is weak and changed, and Binance 1H/4H spot flow is negative. ETF flow and positive 24H spot flow prevent re-escalation at this review.

No portfolio action follows.
