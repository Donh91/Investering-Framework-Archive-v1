# Rotation Repair Edge Event Ledger — ROTATION_REPAIR_EDGE_20260712_01

**Date:** 2026-07-12 onward  
**Status:** OPERATIONAL_EVENT_LEDGER / APPEND_ONLY  
**Area:** DATA PING rotation repair / breadth deterioration / watch-state tracking  
**Primary folder:** `02_DATA_PING/live_state_handover/`  
**Related folders:** `04_MARKET_LEARNING/`, `03_WEEKLY_OPERATIONS/canonical_backbone/`  
**Depends on:** Active Gate and Edge Event Registry; DATA PING Hybrid v0.5.1 consolidated

---

## Event identity

```yaml
edge_event_id: ROTATION_REPAIR_EDGE_20260712_01
edge_event_type: ROTATION_REPAIR_TEST
framework_owner: MAIN_FRAMEWORK_CHATGPT
sensor_source: CUSTOM_GPT_DATA_PING_TRUTH_LAYER
shadow_sources: GROK_SHADOW_ONLY / FABLE_SHADOW_ONLY
event_status: OPEN_WATCH
framework_edge_state: WATCH
framework_alert_status: WATCH
canonical_start_time: 2026-07-12T00:39:18Z
canonical_start_run_id: DATA_PING_HYBRID_v0_5_1_20260712T003918Z
canonical_start_btc_price: 63780.65
canonical_start_ethbtc: 0.027990
prior_event_id: PULLBACK_EDGE_20260708_01
prior_event_status: CLOSED_RESOLVED
prior_event_reopened: NO
```

This is a new watch event. It does not reopen the prior pullback event.

---

## Main-framework acceptance decision

```yaml
framework_acceptance_status_current_run: ACCEPTED_WITH_STATE_MODERATION
accepted_run_id: DATA_PING_HYBRID_v0_5_1_20260712T003918Z
accepted_sensor_edge_candidate: NEAR_PRESENT
accepted_sensor_alert_candidate: WATCH
framework_edge_state: WATCH
framework_alert_status: WATCH
new_event_accepted: YES
new_pullback_alert: NO
active_trim_signal: NO
sell_a_bid_edge: WATCH_ONLY_NOT_ACTIONABLE
rebuy_status: LOCKED
rotation_status: NO_ROTATION
large_cap_buy_window: NOT_OPEN
```

The sensor's `NEAR_PRESENT` label is retained as raw evidence. The main framework moderates the live state to `WATCH` because BTC current and completed closes still hold above 63.3K and ETH/BTC remains above 0.0275.

---

## Opening observation

```yaml
run_id: DATA_PING_HYBRID_v0_5_1_20260712T003918Z
timestamp: 2026-07-12T00:39:18Z
data_quality: MEDIUM
btc_current: 63780.65
btc_latest_daily_close: 64355.99
btc_consecutive_daily_closes_above_63300: 2
btc_consecutive_daily_closes_above_61900: 9
ethbtc_current: 0.027990
ethbtc_latest_daily_close: 0.028350
ethbtc_consecutive_daily_closes_above_0275: 10
ethbtc_distance_above_repair_gate_pct: 1.78
breadth_1h_pct: 9
breadth_24h_pct: 29
breadth_7d_pct: 29
btc_taker_ratio_latest: 0.7677
btc_oi_24h_pct: -2.4546
eth_oi_24h_pct: 1.5068
eth_oi_3d_pct: 4.1687
etf_flow: DATA_MISSING
spot_cvd: DATA_MISSING
stablecoin_persistence: DATA_MISSING
```

---

## Framework interpretation

```text
PRICE STRUCTURE:
BTC reclaim remains intact, but price has moved toward the lower part of the 24H range.

ROTATION REPAIR:
ETH/BTC remains above 0.0275, but proximity pressure is active and the ratio has weakened intraday.

BREADTH:
1H, 24H and 7D breadth are simultaneously negative. This is the material reason for opening the watch event.

LEVERAGE:
BTC OI is contracting, which reduces acute BTC leverage risk. ETH OI remains elevated while taker flow is sell-biased, which weakens the quality of the ETH relative-strength attempt.

FLOW:
ETF, CVD and official stablecoin persistence are unavailable, so no flow confirmation is granted.
```

---

## Escalation and resolution conditions

```yaml
upgrade_conditions:
  - ETHBTC_COMPLETED_CLOSE_BELOW_0_0275
  - BTC_COMPLETED_HOURLY_OR_DAILY_CLOSE_BELOW_63300_WITH_BREADTH_STILL_WEAK
  - BTC_CURRENT_OR_CLOSE_BELOW_61900
  - ADDITIONAL_VERIFIED_PRESSURE_LAYERS_ALIGN

watch_maintenance_conditions:
  - BTC_RECLAIM_GATE_HOLDS
  - ETHBTC_REPAIR_GATE_HOLDS
  - BREADTH_REMAINS_WEAK_OR_FLOW_REMAINS_MISSING

close_candidate_conditions:
  - BTC_RECLAIM_GATE_CONTINUES_TO_HOLD
  - ETHBTC_MOVES_MATERIALLY_AWAY_FROM_REPAIR_PROXIMITY
  - SHORT_AND_DAILY_BREADTH_REPAIR
  - NO_NEW_PRESSURE_CLUSTER
```

A framework close decision is required. DATA PING may not close or rename this event.

---

## Current framework state

```text
FRAMEWORK_EDGE_STATE: WATCH
ALERT_STATUS: WATCH
EVENT_STATUS: OPEN_WATCH
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
SELL_A_BID_EDGE: WATCH_ONLY_NOT_ACTIONABLE
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
LARGE_CAP_BUY_WINDOW: WATCH_ONLY / NOT_OPEN
```

---

## Archive rule

Append only material state transitions, completed-close gate changes, corrected anchors, matured outcome rows and framework close decisions. Routine unchanged watch pings may remain in weekly RAW logs.
