# Rotation Repair Edge Update — Pullback Warning Ratified, Repair Not Failed

**Accepted log:** `DATA_PING_V5_20260717T063523Z`  
**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Event status:** `OPEN_TRIGGERED`  
**Decision-delta class:** `EARLY_WARNING_CANDIDATE`

## Main Framework verdict

The warning path has now become persistent and cross-family enough to ratify a near-term pullback-continuation warning.

This is not a portfolio-action signal and not a full invalidation. The latest settled Binance CEST close remains above 63.3K, BTC remains above 61.9K, and ETH/BTC remains above 0.0275. The current partial BTC price is below 63.3K, so the reclaim is under pressure but has not yet failed on a settled canonical close.

## Material delta since the prior accepted ping

- BTC fell another 1.160% to 62,929.24.
- ETH fell another 1.191% to 1,834.53.
- ETH/BTC slipped 0.069% to 0.029150.
- Fixed-cohort 1H participation collapsed from 77.14% to 8.57%.
- Fixed-cohort 24H participation fell from 17.14% to 5.71%.
- Fixed-cohort 7D participation remained weak at 34.29%, with the median falling further to -1.81%.
- BTC 24H Binance spot-taker flow worsened from -31.25M to -51.23M.
- ETH 24H Binance spot-taker flow remained deeply negative at -47.10M.
- Binance futures taker ratios are below 1 for BTC and ETH over 1H, 4H and 24H.
- BTC trades in the lower 10% of its 24H range and ETH in the lower 14%.

This is the second compatible fixed-cohort warning observation and the first with simultaneous weakness across 1H, 24H, price, spot aggression and futures aggression.

## Source-freshness correction

The Custom GPT packet still reported the provisional 16 July BTC ETF row of +45.7M and did not load the already canonical post-acceptance Farside revision.

The framework therefore accepts the packet's price, breadth, spot-flow and Binance-futures fields, but replaces the packet's ETF lane with the existing verified primary-source values:

```text
16 Jul BTC ETF total: +79.1M
16 Jul IBIT: +33.4M
16 Jul ETH ETF total: -28.0M
BTC 3-session: +367.9M
BTC 5-session: +33.6M
BTC 7-session: -146.6M
BTC 10-session: +364.1M
Stage-1 ETF flow leg: COMPLETE_RATIFIED
```

The accepted payload records this as an explicit source-freshness breach corrected by canonical source revision. No historical payload is rewritten.

## Why the warning is ratified now

The warning is no longer based on one weak price print or one temporary breadth observation. It now has persistent evidence in the existing warning lanes:

```text
BTC below 63.3K intraday
+
second compatible fixed-cohort deterioration
+
1H breadth collapse
+
24H breadth deterioration to 5.71%
+
BTC and ETH 4H/24H spot-taker flow negative
+
BTC and ETH futures taker ratios below 1
+
price near the lower edge of 24H ranges
```

The completed ETF flow leg offsets a full bearish interpretation, but it does not neutralize the breadth and spot-demand deterioration.

## Why repair is not failed

- Latest settled BTC CEST close: 64,161.99, above 63.3K.
- Current BTC: 62,929.24, still above 61.9K.
- No settled BTC close below 59.4K.
- Direct ETH/BTC: 0.029150, above 0.0275.
- Stage-1 ETF flow leg is complete.

Therefore the correct state is pressure and warning, not invalidation.

## Canonical state

```text
FRAMEWORK_EDGE_STATE: REPAIR_PRESENT_PULLBACK_WARNING_RATIFIED_RECLAIM_UNDER_PRESSURE_NOT_FAILED
PULLBACK_WARNING: ACTIVE_RATIFIED
FAILED_RECLAIM: INTRADAY_CANDIDATE_NOT_SETTLED
STAGE_1_ETF_FLOW_LEG: COMPLETE_RATIFIED
ROTATION: NO_ROTATION
BROAD_RECOVERY: NOT_CONFIRMED
LARGE_CAP_WINDOW: WATCH_ONLY_NOT_OPEN
NEW_ENTRY_SIGNAL: NOT_ACTIVE
ACTIVE_TRIM_SIGNAL: NO
PORTFOLIO_ACTION: NONE
USER_ACTION: HOLD_AND_WAIT
RISK_POSTURE: ELEVATED_VIGILANCE
```

## Next decision-changing observations

1. Canonical CEST settlement below or back above 63.3K.
2. Next compatible `FIXED_RISK35_v1` persistence delta.
3. Persistence or reversal of negative Binance 4H/24H spot-taker flow.
4. ETH/BTC hold above 0.0275 or confirmed persistence above 0.0300.
5. Completed 17 July ETF session.
6. Loss of 61.9K with confirming participation and flow weakness.

No automatic action follows from this warning.