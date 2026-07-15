# Rotation Repair Edge — Medium-Horizon Hold, Short-Horizon Cooling

**Accepted run:** `DATA_PING_V4_20260715T100211Z`  
**Review date:** 2026-07-15  
**Active event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Data quality:** LOW

## Framework decision

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
RESOLUTION_CANDIDATE: STRENGTHENED_BUT_CLOSE_VERIFICATION_BLOCKED
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
ROTATION_STATUS: NO_ROTATION
REBUY_STATUS: LOCKED
LARGE_CAP_BUY_WINDOW: NOT_OPEN
PORTFOLIO_ACTION: NONE
```

## What remains constructive

- CoinGecko fallback BTC remains above the 63.3K reclaim gate.
- Derived ETH/BTC remains above 0.0285 and below 0.0300.
- 24H breadth remains broad at 85.7%.
- 7D breadth remains above majority at 60.0%, materially stronger than before the July-14 impulse.
- The latest completed ETF session remains positive for both BTC (+181.1M) and ETH (+58.3M).
- ETH ETF rolling windows are positive across 3, 5, 7 and 10 sessions.
- The eight-asset stablecoin proxy is slightly positive over 24H, although low confidence and not official.

## What cooled or still blocks confirmation

- 1H breadth cooled from 74.3% to 51.4%, so the impulse is no longer broad at the shortest horizon.
- BTC ETF rolling windows remain negative over 3, 5, 7 and 10 sessions despite the positive latest session.
- Binance Spot and Futures remain unavailable because of an explicit eligibility-location error.
- The completed 14 July CEST closes for BTC, ETH and ETH/BTC remain missing from the truth layer.
- Direct ETH/BTC, hourly persistence, spot-taker flow, funding, open interest, basis and leverage remain unavailable.
- The current 15 July ETF session is pending.
- Official stablecoin history and market-wide CVD remain missing.

## Interpretation

The constructive medium-horizon picture persists: price remains above reclaim, derived relative structure remains above 0.0285, 24H and 7D breadth remain supportive, and the latest completed BTC and ETH ETF session is positive. The eleven-minute continuation does not add a new market event, but it confirms that the prior improvement has not immediately disappeared.

The shortest horizon cooled sharply, and the BTC ETF rolling windows remain negative. More importantly, the missing Binance close and derivatives layers prevent completed-close verification, persistence extension or leverage assessment. Missing evidence is treated as UNKNOWN, not negative, but it blocks event closure and any entry-window promotion.

## OTA / SCTA holdout implication

```text
HOLDOUT_ID: SCTA_20260714
P1_FLOW_STATUS: IMPROVED_LATEST_SESSION_POSITIVE_BUT_BTC_ROLLING_WINDOWS_NEGATIVE
P2_TWO_NEGATIVE_ETF_SESSIONS: NOT_MET
P3_FLOW_NECESSITY_FALSIFIER: WATCH_ONLY
TYPE2_STATUS: STRONGEST_CANDIDATE_SO_FAR_NOT_CONFIRMED
REDUNDANCY_COUNTER: 0_OF_5_MATURED_EVENTS
```

The positive 14 July ETF settlement prevents the frozen two-negative-session P2 path from firing. It does not by itself complete P1 because the truth-layer close conditions remain unavailable and BTC rolling flow remains mixed-to-negative. The holdout remains open until its frozen maturity checkpoints.

## Operational decision

- Keep the active event open.
- Do not create a new event or pullback alert.
- Do not alter the canonical gate registry.
- Do not open the large-cap or new-entry window.
- Preserve CN #16 unchanged as a frozen prospective forecast.
- Accept this ping as low-observability prospective outcome evidence.
