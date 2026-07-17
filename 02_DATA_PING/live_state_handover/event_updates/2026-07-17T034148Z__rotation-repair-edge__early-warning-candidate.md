# Rotation Repair Edge update — 2026-07-17T034148Z

**Accepted DATA PING:** `DATA_PING_V5_20260717T034148Z`  
**Active event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Decision delta class:** `EARLY_WARNING_CANDIDATE`  
**Action changed:** `NO`

## Main-framework verdict

The repair remains structurally present, but the first valid fixed-cohort persistence comparison now shows material deterioration beneath the headline structure.

```text
FRAMEWORK_EDGE_STATE: REPAIR_PRESENT_PARTICIPATION_AND_FLOW_DETERIORATING_NOT_FAILED
EVENT_STATUS: OPEN_TRIGGERED
ALERT_STATUS: STILL_ACTIVE
EARLY_WARNING_CANDIDATE: ACTIVE
NEW_PULLBACK_ALERT: NO_RATIFIED_ALERT
ROTATION: NO_ROTATION
BROAD_RECOVERY: NOT_CONFIRMED
NEW_ENTRY_SIGNAL: NOT_ACTIVE
PORTFOLIO_ACTION: NONE
USER_ACTION: HOLD_AND_WAIT
```

## Why this is a real decision-value change

This is no longer only an observability improvement. `FIXED_RISK35_v1` now has a compatible prior observation.

- 1H positive share improved from 60.00% to 77.14%.
- 24H positive share fell from 28.57% to 17.14%.
- 7D positive share fell from 60.00% to 34.29%.
- The 24H and 7D medians are negative.
- BTC, ETH and ETH/BTC are all near the lower part of their 24H ranges.
- BTC and ETH 4H and 24H Binance taker proxies remain negative.
- ETH's latest completed ETF session turned negative.
- Short-horizon CFGI readings weakened into Fear.

This qualifies as an early-warning candidate because participation and flow weakened before the core repair gates failed.

## Why the repair has not failed

- BTC current price and the latest settled CEST close remain above 63,300 and 61,900.
- ETH/BTC remains above 0.0275.
- No settled BTC close is below 59,400.
- BTC completed ETF flow is positive for a third consecutive completed session.
- 1H fixed-cohort breadth is positive.

## Stage 1

The 16 July BTC ETF session is completed and positive at +$45.7M. This establishes a three-session positive completed streak.

Stage 1 does **not** fire because the archived requirement also requires IBIT to be positive. IBIT for 16 July is `NOT_REPORTED`.

```text
NOT_REPORTED != ZERO
NOT_REPORTED != POSITIVE
STAGE_1_STATUS: NOT_FIRED_BLOCKED_BY_UNKNOWN_IBIT_CONTRIBUTION
```

## OTA 72H shadow review

The 72H review is mature and is recorded as shadow-only:

```text
SURVIVAL: HELD
CONFIRMATION: NOT ACHIEVED
BREADTH TRANSLATION: FAILED
FLOW: CONTRADICTORY
PROMOTION: NONE
ACTION: NONE
```

The repair survived because the structure gates held. The hypothesis did not confirm because the 1H rebound failed to translate into 24H and 7D participation, spot taker flow stayed negative, ETH ETF flow turned negative, and ETH/BTC remained below 0.0300.

## Next material observations

1. Whether the next compatible fixed-cohort ping confirms or reverses the 24H and 7D deterioration.
2. Whether BTC develops failed-reclaim behavior around 63,300.
3. Whether ETH/BTC loses 0.0275.
4. Whether negative 4H and 24H spot taker flow persists.
5. The completed 17 July ETF session and any verified IBIT contribution.
6. OTA 7D review on 21 July and 12-session review around 30 July.

No new event is created. The warning remains inside the existing rotation-repair event.
