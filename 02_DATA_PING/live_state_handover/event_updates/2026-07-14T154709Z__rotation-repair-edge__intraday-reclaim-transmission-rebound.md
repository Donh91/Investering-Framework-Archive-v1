# Rotation Repair Edge — Intraday Reclaim and Transmission Rebound

**Accepted run:** `DATA_PING_V4_20260714T154709Z`  
**Review time:** 2026-07-14T16:35:20Z  
**Active event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Data quality:** MEDIUM

## Framework decision

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
RESOLUTION_CANDIDATE: YES — INTRADAY ONLY
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
ROTATION_STATUS: NO_ROTATION
REBUY_STATUS: LOCKED
LARGE_CAP_BUY_WINDOW: NOT_OPEN
PORTFOLIO_ACTION: NONE
```

## Material improvement

- BTC moved above the 63.3K reclaim level and held three consecutive settled hourly closes above it.
- ETH/BTC moved above 0.0285 and remained above the 0.0275 repair gate.
- Breadth improved to 88.6% on 1H and 82.9% on 24H.
- BTC spot-taker flow turned positive on 15M/1H/4H; ETH was positive on 4H/24H.
- BTC OI fell 2.86% over 24H while price rose, reducing the prior downside-OI pressure cluster.
- BTC and ETH traded near the highs of expanded CEST-day ranges.

## Why the event is not closed and no entry window opens

- The latest completed BTC daily close remains below 63.3K.
- ETH/BTC has no completed daily close above 0.0285 and remains below 0.0300.
- 7D breadth remains below majority at 48.6%.
- The latest completed BTC ETF session was -$424.7M; 3-, 5- and 10-session BTC windows remain negative.
- The current ETF session is pending.
- The stablecoin proxy remains contracting and is not persistence-eligible.
- Market-wide CVD and official stablecoin history remain unavailable.

## Interpretation

The pressure cluster materially reversed during the session and the market produced the first credible short-to-medium-horizon transmission rebound of this event. This is a resolution candidate, not a confirmed resolution. A completed BTC close above 63.3K, durable ETH/BTC acceptance above 0.0285 toward 0.0300, and non-deteriorating flow are still required before the event can be closed or the large-cap entry window can open.

CN #16 remains frozen. This run is prospective outcome evidence only.
