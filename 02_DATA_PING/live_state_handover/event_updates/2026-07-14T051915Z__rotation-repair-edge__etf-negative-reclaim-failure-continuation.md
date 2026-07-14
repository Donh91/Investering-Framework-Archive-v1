# Rotation Repair Edge — ETF-Negative Reclaim-Failure Continuation

**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Accepted run:** `DATA_PING_V4_20260714T051915Z`  
**Predecessor:** `DATA_PING_V4_20260713T184513Z`  
**Source cutoff:** 2026-07-14T05:19:15Z  
**Framework review time:** 2026-07-14T05:38:54Z  
**Data quality:** MEDIUM  
**Status:** MATERIAL_CONTINUATION / NO_NEW_EVENT / NO_EDGE_UPGRADE

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

## What materially changed

```yaml
btc_monday_low: 61824.97
btc_survival_gate: 61900
btc_monday_close: 62065.06
btc_current: 62785.49
btc_daily_closes_above_63300: 0
btc_daily_closes_above_61900: 11
ethbtc_current: 0.02849
ethbtc_monday_close: 0.02838
ethbtc_daily_closes_above_0275: 12
breadth_1h_pct: 85.7
breadth_24h_pct: 34.3
breadth_7d_pct: 22.9
btc_etf_latest_completed_usd_m: -424.7
btc_etf_3_sessions_usd_m: -429.6
btc_etf_5_sessions_usd_m: -493.0
btc_etf_10_sessions_usd_m: -753.4
eth_etf_latest_completed_usd_m: -15.4
btc_oi_24h_pct: 6.97
btc_global_long_short_ratio: 1.7917
btc_spot_taker_24h_usdt: -81748786.46
stablecoin_proxy_change_24h_pct: -0.5182
```

Monday produced the first intraday survival-gate breach of this event, but the completed CEST close recovered above `61.9K`. BTC also lost the `63.3K` completed-close reclaim, while the newly completed ETF session confirmed a material negative flow impulse. BTC open interest remains expanded and positioning remains long-skewed.

The Tuesday rebound improves only the shortest horizon: 1H breadth and price recovered, while 24H and 7D breadth remain below majority and the 24H taker-flow proxy remains negative. This is not broad transmission.

## Why the state remains below PRESENT

```yaml
btc_current_below_61900: NO
btc_completed_close_below_61900: NO
repeated_completed_survival_failure: NO
ethbtc_completed_close_below_0275: NO
ethbtc_repair_persistence: 12_closes
acute_funding_stress: NO
short_horizon_rebound_present: YES
market_wide_cvd: UNAVAILABLE
```

The event remains `NEAR_PRESENT` because the survival breach was intraday and recovered on the completed close, while direct ETH/BTC repair remains persistent. The negative ETF session and weak medium-horizon breadth prevent de-escalation, but do not independently satisfy the existing PRESENT rule.

## Current interpretation

```text
Repair survives, but reclaim quality failed.
Flow confirmation deteriorated materially.
The rebound is short-horizon only.
No rotation, entry, trim or deployment permission is created.
```

No threshold, sensor weight, architecture, event identity or portfolio rule is changed by this run.