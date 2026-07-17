# Rotation Repair Edge Update: Second Intraday Rebound, Warning Maintained

**Accepted log:** `DATA_PING_V5_20260717T162231Z`  
**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Event status:** `OPEN_TRIGGERED`  
**Decision-delta class:** `OBSERVABILITY_OR_DATA_QUALITY_DELTA`

## Main Framework verdict

The ratified pullback warning remains active and strengthened from the prior review, but this packet does not strengthen it further and does not clear it.

The fixed cohort rebounded for a second time over 1H, from 28.57% to 85.71%, while BTC returned above 63.3K on the current partial CEST candle. Short-horizon spot and futures flow improved. However, 24H and 7D breadth remain weak, 4H and 24H spot-taker flow remain negative, and 4H and 24H futures taker ratios remain below 1.

The sequence is now:

```text
FIXED_RISK35 1H POSITIVE SHARE:
88.57% -> 28.57% -> 85.71%
```

This is high intraday oscillation, not durable stabilization.

```text
PULLBACK WARNING: ACTIVE_RATIFIED_STRENGTHENED_MAINTAINED_NOT_ACTION_ESCALATED_NOT_CLEARED
SHORT-TERM STABILIZATION: SECOND_INTRADAY_REBOUND_ACTIVE_UNCONFIRMED_OSCILLATORY
REPAIR FAILURE: NO
NEW PULLBACK ALERT: NO, EXISTING ALERT MAINTAINED
```

## Participation

`FIXED_RISK35_v1` remained directly comparable:

- 1H positive share: 28.57% to 85.71%, delta +57.14 percentage points.
- 1H median: -0.24% to +0.57%.
- 24H positive share: 11.43% to 14.29%.
- 24H median: -1.86%.
- 7D positive share: 25.71%.
- 7D median: -1.50%.

The second 1H rebound is real but has not translated into medium-horizon participation.

## Structure

- Binance BTC: 63,492.01, currently above 63.3K.
- Latest settled Binance CEST BTC close: 64,161.99, above 63.3K.
- Current CEST day remains partial.
- BTC remains above 61.9K.
- No settled close below 59.4K.
- Direct Binance ETH/BTC: 0.028900.
- Direct ETH/BTC remains above 0.0275 and below 0.0300.

The reclaim is currently held on both the latest settled close and the live price, but the current day does not provide a new settled confirmation.

## Flow

Binance spot-taker proxy:

```text
BTC 1H: +5.427M
BTC 4H: -19.349M
BTC 24H: -34.982M
ETH 1H: -0.445M
ETH 4H: -8.258M
ETH 24H: -0.945M
```

All 4H and 24H values improved versus the prior ping but remained negative.

Binance futures taker ratios:

```text
BTC 1H: 1.051
BTC 4H: 0.903
BTC 24H: 0.925
ETH 1H: 1.179
ETH 4H: 0.928
ETH 24H: 0.909
```

The 1H ratios moved above 1, while the 4H and 24H ratios remained below 1. This is short-horizon improvement without medium-horizon confirmation.

The verified ETF lane is unchanged:

```text
16 Jul BTC ETF: +79.1M
16 Jul IBIT: +33.4M
16 Jul ETH ETF: -28.0M
BTC 3-session: +367.9M
BTC 7-session: -146.6M
Stage-1 ETF flow leg: COMPLETE_RATIFIED
17 Jul session: PENDING_PARTIAL
```

## Leverage

BTC OI was slightly lower and ETH OI slightly higher since the prior ping. Both remained lower over approximately 72H. Funding was positive and account ratios remained elevated. This is consistent with an intraday rebound inside a broader deleveraging process, not a clean recovery confirmation.

## Source quality

Binance spot, direct ETH/BTC, CEST candles, spot-taker flow and Binance futures all passed. Binance ETH and CoinGecko ETH differed by 0.459%, above the 0.30% conflict threshold. The conflict is preserved and overall packet quality remains LOW.

## Canonical state

```text
FRAMEWORK_EDGE_STATE: REPAIR_PRESENT_PULLBACK_WARNING_ACTIVE_SECOND_INTRADAY_REBOUND_CURRENT_ABOVE_63300_PARTIAL_NO_MEDIUM_HORIZON_TRANSLATION_NEGATIVE_4H_24H_FLOW_IMPROVING_NOT_FAILED
PULLBACK_WARNING: ACTIVE_RATIFIED_STRENGTHENED_MAINTAINED_NOT_ACTION_ESCALATED_NOT_CLEARED
SHORT_TERM_STABILIZATION: SECOND_INTRADAY_REBOUND_ACTIVE_UNCONFIRMED_OSCILLATORY
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

1. A new settled Binance CEST close relative to 63.3K.
2. Whether the second 1H breadth rebound survives the next compatible ping and translates into 24H breadth.
3. Whether 4H and 24H spot-taker flow turn positive rather than merely become less negative.
4. Direct ETH/BTC retention above 0.0275 or renewed approach to 0.0300.
5. Completed 17 July ETF session.
6. BTC retention or loss of 61.9K.
7. 7D prospective review on 21 July.

No automatic portfolio action follows.