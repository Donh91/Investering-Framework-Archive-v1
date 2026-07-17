# Rotation Repair Edge Update — Intraday Breadth Rebound, Warning Maintained

**Accepted log:** `DATA_PING_V5_20260717T142500Z`  
**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Event status:** `OPEN_TRIGGERED`  
**Decision-delta class:** `OBSERVABILITY_OR_DATA_QUALITY_DELTA`

## Main Framework verdict

The ratified pullback warning remains active. It is not escalated and not cleared.

The fixed cohort produced a strong 1H rebound, but there was no translation into the 24H horizon. Binance spot remained unavailable for a second consecutive run, so direct ETH/BTC, the canonical CEST close update and Binance spot-taker flow remain missing.

```text
SHORT-TERM STABILIZATION: INTRADAY_REBOUND_STRONG_BUT_UNCONFIRMED
PULLBACK WARNING: ACTIVE_RATIFIED_MAINTAINED_NOT_ESCALATED_NOT_CLEARED
FAILED RECLAIM: UNRESOLVED_NO_CANONICAL_CLOSE_UPDATE
REPAIR FAILURE: NO
```

## Comparable evidence

CoinGecko fallback continuity is directly comparable with the previous fallback run:

- BTC +0.362% to 63,266.
- ETH -0.416% to 1,825.92.
- Total market cap +0.307%.
- BTC dominance +0.146 percentage points.

`FIXED_RISK35_v1` remained directly comparable:

- 1H positive share rose from 31.43% to 88.57%.
- 1H median rose to +0.93%.
- 24H positive share fell from 17.14% to 14.29%.
- 24H median worsened to -2.13%.
- 7D positive share improved slightly to 28.57%, but remained weak.
- 7D median remained negative at -1.95%.

The 1H move is broad and real, but it remains an intraday rebound inside a weak 24H and 7D participation regime.

## Structure and source authority

- CoinGecko BTC is 63,266, only about 0.05% below 63.3K.
- The latest stored Binance CEST close remains 64,161.99, above 63.3K.
- BTC remains above 61.9K.
- No stored settled close is below 59.4K.
- Direct ETH/BTC is missing.
- Derived ETH/BTC is 0.028861, above 0.0275 and below 0.0300, but cannot fire direct-pair governance gates.

Because Binance remains unavailable, the reclaim test is unresolved rather than failed or restored.

## Flow and leverage

The verified ETF lane is unchanged:

```text
16 Jul BTC ETF: +79.1M
16 Jul IBIT: +33.4M
16 Jul ETH ETF: -28.0M
BTC 3-session: +367.9M
BTC 5-session: +33.6M
BTC 7-session: -146.6M
BTC 10-session: +364.1M
Stage-1 ETF flow leg: COMPLETE_RATIFIED
17 Jul session: PENDING_PARTIAL
```

Binance spot-taker flow is missing for the second consecutive run and has no substitute.

OKX leverage remains mixed:

- BTC OI +0.50% since the prior ping and approximately +3.42% over 24H.
- BTC remains below the reclaim observation while OI rises.
- ETH OI -1.53% since the prior ping and approximately -3.93% over 24H.
- Account-count ratios remain elevated at 1.82 for BTC and 1.95 for ETH.
- OKX taker legs retain raw order only; direction is not computed.

This does not confirm recovery and does not invalidate the warning.

## Canonical state

```text
FRAMEWORK_EDGE_STATE: REPAIR_PRESENT_PULLBACK_WARNING_ACTIVE_STRONG_1H_REBOUND_NO_MEDIUM_HORIZON_TRANSLATION_RECLAIM_UNRESOLVED_NOT_FAILED
PULLBACK_WARNING: ACTIVE_RATIFIED_MAINTAINED_NOT_ESCALATED_NOT_CLEARED
SHORT_TERM_STABILIZATION: INTRADAY_REBOUND_STRONG_BUT_UNCONFIRMED
ROTATION: NO_ROTATION
BROAD_RECOVERY: NOT_CONFIRMED
LARGE_CAP_WINDOW: WATCH_ONLY_NOT_OPEN
NEW_ENTRY_SIGNAL: NOT_ACTIVE
ACTIVE_TRIM_SIGNAL: NO
PORTFOLIO_ACTION: NONE
USER_ACTION: HOLD_AND_WAIT
RISK_POSTURE: ELEVATED_VIGILANCE
```

## Next resolving observations

1. Restoration of Binance spot or another approved canonical CEST-close owner.
2. A fresh canonical settlement relative to 63.3K.
3. Restoration of comparable 4H/24H spot-taker flow.
4. Whether the 1H breadth rebound translates into materially stronger 24H participation in the next compatible ping.
5. Direct ETH/BTC confirmation above 0.0275 or persistence above 0.0300.
6. Completed 17 July ETF session.
7. BTC retention or loss of 61.9K with confirming breadth and flow.

No automatic portfolio action follows.