# Rotation Repair Edge Update: V6 Activation and Warning De-escalation

**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Accepted DATA PING:** `DATA_PING_V6_20260719T200033Z`  
**Reviewed:** 2026-07-19T21:38:21Z  
**Authority:** MAIN_FRAMEWORK

## Decision delta

The first complete V6 raw packet was accepted by field and V6 became the active DATA PING source version.

The prior strengthened pullback warning is de-escalated by one level but remains active and is not cleared.

## Positive changes

- Five consecutive settled BTC CEST closes above 63.3K.
- All six settled current-week BTC closes above 61.9K.
- BTC ETF four-session positive streak through 17 July.
- BTC ETF seven-session sum turned positive at +70.6M USD.
- IBIT seven-session sum is +290.9M USD.
- BTC and ETH Binance spot taker flow is positive over 4H and 24H.
- V6 source coverage upgraded overall data quality from LOW to MEDIUM.

## Remaining blockers

- Sunday CEST weekly candle is partial and not settled.
- ETH/BTC is above 0.0275 but below 0.0300.
- Dynamic breadth is positive over 1H but weak over 24H and 7D.
- BTC and ETH Binance futures taker ratios remain below 1 across 1H, 4H and 24H.
- Official stablecoin total/history and market-wide CVD remain unavailable.
- CFGI observations are stale and not persistence-eligible.
- Canonical FIXED_RISK35 identity remains unknown and reconstruction is forbidden.

## Current state

```yaml
pullback_warning: ACTIVE_DE_ESCALATED_ONE_LEVEL_NOT_CLEARED
short_term_stabilization: STRUCTURAL_REPAIR_HELD_INTRADAY_FLOW_MIXED
rotation: NO_ROTATION
broad_recovery: NOT_CONFIRMED
large_cap_window: WATCH_ONLY_NOT_OPEN
new_entry_signal: NOT_ACTIVE
portfolio_action: NONE
user_action: HOLD_AND_WAIT
risk_posture: ELEVATED_VIGILANCE_DE_ESCALATED
```

No portfolio action follows from this DATA PING.
