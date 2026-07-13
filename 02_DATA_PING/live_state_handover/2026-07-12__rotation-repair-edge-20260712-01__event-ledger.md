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
event_status: OPEN_TRIGGERED
framework_edge_state: NEAR_PRESENT
framework_alert_status: TRIGGERED
canonical_start_time: 2026-07-12T00:39:18Z
canonical_start_run_id: DATA_PING_HYBRID_v0_5_1_20260712T003918Z
canonical_start_btc_price: 63780.65
canonical_start_ethbtc: 0.027990
canonical_first_framework_near_present_time: 2026-07-13T05:25:47Z
canonical_first_framework_near_present_run_id: DATA_PING_V4_20260713T052547Z
canonical_first_framework_near_present_btc_price: 62694.59
canonical_first_framework_near_present_ethbtc: 0.028410
prior_event_id: PULLBACK_EDGE_20260708_01
prior_event_status: CLOSED_RESOLVED
prior_event_reopened: NO
```

This is a new event. It does not reopen the prior pullback event.

---

## Main-framework opening decision

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

The sensor's `NEAR_PRESENT` label was retained as raw opening evidence. The main framework initially moderated the live state to `WATCH` because BTC current and completed closes still held above 63.3K and ETH/BTC remained above 0.0275.

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

## Material escalation observation — 2026-07-13

```yaml
run_id: DATA_PING_V4_20260713T052547Z
timestamp: 2026-07-13T05:25:47Z
data_quality: MEDIUM
prior_framework_edge_state: WATCH
accepted_framework_edge_state: NEAR_PRESENT
prior_alert_status: WATCH
accepted_alert_status: TRIGGERED
event_status: OPEN_TRIGGERED
trigger:
  - BTC_CURRENT_BELOW_63300
  - TWO_LATEST_SETTLED_BTC_HOURLY_CLOSES_BELOW_63300
  - BREADTH_24H_AND_7D_REMAIN_WEAK
  - BTC_AND_ETH_SPOT_TAKER_PROXY_SELL_LEAN_ALL_HORIZONS
btc_current: 62694.59
btc_latest_daily_close: 63920.40
btc_distance_below_63300_pct: -0.96
btc_latest_settled_hourly_closes_below_63300: 2
btc_current_above_61900: YES
btc_current_above_59400: YES
ethbtc_current: 0.028410
ethbtc_latest_daily_close: 0.028350
ethbtc_repair_gate_holds: YES
ethbtc_confirmation_gate_met: NO
breadth_1h_pct: 51
breadth_24h_pct: 29
breadth_7d_pct: 23
btc_spot_taker_proxy: SELL_LEAN_ALL_HORIZONS
eth_spot_taker_proxy: SELL_LEAN_ALL_HORIZONS
btc_oi_24h_pct: -1.63
eth_oi_24h_pct: -1.05
funding_stress: NO_ACUTE_STRESS
etf_flow: DATA_MISSING_PENDING
market_wide_cvd: DATA_MISSING
stablecoin_persistence: DATA_MISSING
new_pullback_alert: NO
active_trim_signal: NO
sell_a_bid_edge: NEAR_PRESENT_NOT_ACTIONABLE
rebuy_status: LOCKED
rotation_status: NO_ROTATION
large_cap_buy_window: NOT_OPEN
```

The event is upgraded from `WATCH` to `NEAR_PRESENT` because the accepted escalation condition — completed hourly closes below the 63.3K reclaim gate while breadth remains weak — is now met. It is not upgraded to `PRESENT`: BTC still holds the 61.9K survival gate, ETH/BTC still holds 0.0275, OI is contracting, and no acute funding stress is present.

---

## Framework interpretation

```text
PRICE STRUCTURE:
The latest completed daily close still holds above 63.3K, but current price and the two latest settled hourly closes are below the reclaim gate. This is a material reclaim-quality deterioration, not yet a survival-gate failure.

ROTATION REPAIR:
ETH/BTC remains above 0.0275 and has not confirmed 0.0300. Relative strength is holding, but it is not broad rotation.

BREADTH:
1H breadth has repaired to a slight majority. 24H and 7D breadth remain weak, with 7D breadth deteriorating to 23%. Broad recovery remains unconfirmed.

SPOT FLOW:
BTC and ETH Binance spot taker proxies are sell-lean across all measured horizons. Market-wide CVD and current ETF confirmation are unavailable.

LEVERAGE:
BTC and ETH OI are contracting and funding is not acute. This reduces immediate liquidation fragility and is the main reason the event remains below PRESENT.
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
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: TRIGGERED
EVENT_STATUS: OPEN_TRIGGERED
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
SELL_A_BID_EDGE: NEAR_PRESENT_NOT_ACTIONABLE
BTC_RECLAIM_STATUS: CURRENT_LOST / LATEST_DAILY_CLOSE_HOLDS
BTC_SURVIVAL_STATUS: HOLDS_ABOVE_61900
ETHBTC_REPAIR_STATUS: HOLDS_ABOVE_0275
BREADTH_STATUS: 1H_SLIGHT_MAJORITY / 24H_7D_WEAK
BROAD_RECOVERY_STATUS: NOT_CONFIRMED
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
LARGE_CAP_BUY_WINDOW: WATCH_ONLY / NOT_OPEN
```

---

## Archive rule

Append only material state transitions, completed-close gate changes, corrected anchors, matured outcome rows and framework close decisions. Routine unchanged pings may remain in weekly RAW logs.
