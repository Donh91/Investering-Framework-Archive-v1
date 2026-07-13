# Rotation Repair Edge — Material Pressure-Cluster Update

**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Recovery run:** `MISSING_DATA_RECOVERY_20260713T172341Z`  
**Source cutoff:** 2026-07-13T17:18:41.902Z  
**Framework review time:** 2026-07-13T17:23:41Z  
**Parent accepted log:** `DATA_PING_V4_20260713T150608Z`  
**Data quality after recovery:** MEDIUM  
**Status:** MATERIAL_CONTINUATION / NO_NEW_EVENT

## Framework decision

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
SELL_A_BID_EDGE: NEAR_PRESENT_NOT_ACTIONABLE
REBUY_STATUS: LOCKED
ROTATION_STATUS: NO_ROTATION
LARGE_CAP_BUY_WINDOW: NOT_OPEN
```

## Why pressure increased

```yaml
btc_spot_usdt: 62251.73
btc_cest_day_low: 62101
btc_survival_gate: 61900
btc_intraday_low_distance_above_survival_pct: 0.3247
btc_oi_change_24h_pct: 5.6446
btc_oi_change_3d_pct: 3.0191
btc_taker_ratio_1h: 0.8755
btc_taker_ratio_4h: 0.9549
btc_taker_ratio_24h: 0.8997
btc_global_long_short_ratio: 1.6983
latest_parent_packet_breadth_24h_pct: 8.6
btc_etf_10_sessions_usd_m: -773.2
stablecoin_selected_assets_change_24h_pct: -0.1069
```

BTC entered the survival-gate proximity band intraday. The previously missing derivatives layer now shows BTC open interest expanding materially while taker ratios remain below 1 across 1H, 4H and 24H and account positioning remains long-skewed. This removes the earlier de-escalating argument that BTC OI was contracting.

## Why the state remains below PRESENT

```yaml
btc_current_above_61900: YES
btc_intraday_low_above_61900: YES
btc_completed_daily_close_below_61900: NO
ethbtc_direct_current: 0.02848
ethbtc_latest_completed_1h_close: 0.02845
ethbtc_latest_completed_4h_close: 0.02842
ethbtc_completed_daily_close: 0.02835
ethbtc_completed_closes_above_0275: 11
ethbtc_repair_gate_holds: YES
ethbtc_confirmation_0300: NO
current_etf_session: PENDING
market_wide_cvd: UNAVAILABLE
```

The canonical PRESENT rule normally requires survival-gate loss or repeated survival failure plus multiple verified pressure layers. BTC has not lost 61.9K, and direct ETH/BTC continues to hold the 0.0275 repair gate. Pressure is stronger, but not yet overwhelming enough to override those two supportive offsets.

## Escalation map

```text
Upgrade review to PRESENT:
- BTC current or completed close below 61.9K; or
- repeated survival-gate failure with continued downside OI expansion and sell-lean; or
- direct ETH/BTC completed close below 0.0275; or
- additional verified pressure layers remove the remaining supportive offsets.

Downgrade review:
- BTC reclaims 63.3K with completed-close quality;
- BTC OI expansion and taker sell-skew fade;
- 24H/7D breadth repair;
- direct ETH/BTC moves materially away from 0.0275;
- verified ETF/flow support broadens.
```

No portfolio action, threshold change, event replacement or rule promotion is authorized by this supplemental recovery packet.
