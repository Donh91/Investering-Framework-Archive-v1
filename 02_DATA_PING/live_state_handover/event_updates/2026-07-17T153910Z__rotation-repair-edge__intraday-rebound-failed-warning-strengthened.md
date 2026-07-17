# Rotation Repair Edge Update: Intraday Rebound Failed, Warning Strengthened

**Accepted log:** `DATA_PING_V5_20260717T153910Z`  
**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Event status:** `OPEN_TRIGGERED`  
**Decision-delta class:** `EARLY_WARNING_CANDIDATE`

## Main Framework verdict

The ratified pullback warning is strengthened, but it is not escalated to portfolio action and the repair structure has not failed.

The previous compatible ping showed 88.57% positive participation over 1H. In the next compatible ping this collapsed to 28.57%, while 24H participation fell to 11.43% and 7D participation remained weak at 25.71%. Binance spot returned and independently showed negative BTC and ETH spot-taker flow over 1H, 4H and 24H. Binance futures taker ratios were below 1 across all measured windows.

```text
PULLBACK WARNING: ACTIVE_RATIFIED_STRENGTHENED_NOT_ACTION_ESCALATED_NOT_CLEARED
SHORT-TERM STABILIZATION: FAILED_TO_PERSIST
REPAIR FAILURE: NO
NEW PULLBACK ALERT: NO, EXISTING ALERT STRENGTHENED
```

## Participation

`FIXED_RISK35_v1` remained directly comparable:

- 1H positive share: 88.57% to 28.57%, delta -60.00 percentage points.
- 1H median: +0.93% to -0.24%.
- 24H positive share: 14.29% to 11.43%.
- 24H median: -2.57%.
- 7D positive share: 25.71%.
- 7D median: -2.06%.

The prior 1H rebound did not translate into the next compatible observation and cannot be treated as durable stabilization.

## Structure

- Binance BTC: 63,280, currently 0.032% below 63.3K.
- Latest settled Binance CEST BTC close: 64,161.99, above 63.3K.
- Current CEST day remains partial.
- BTC remains above 61.9K.
- No settled close below 59.4K.
- Direct Binance ETH/BTC is restored at 0.028850.
- Direct ETH/BTC remains above 0.0275 and below 0.0300.

The 63.3K reclaim is unresolved rather than failed because the current candle is partial and the latest settled close remains above the gate.

## Flow

Binance spot-taker proxy:

```text
BTC 1H: -1.875M
BTC 4H: -28.218M
BTC 24H: -42.842M
ETH 1H: -1.732M
ETH 4H: -11.835M
ETH 24H: -4.026M
```

Binance futures taker buy/sell ratios were below 1 for BTC and ETH over 1H, 4H and 24H. This confirms venue-level sell pressure but is not market-wide CVD.

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

Binance futures show declining OI over 24H and 72H, positive funding and elevated account ratios. This is consistent with deleveraging during weakness, but does not confirm a clean reset or renewed recovery.

## Source quality

Binance spot, direct ETH/BTC, CEST candles and spot-taker flow are restored. However, Binance ETH and CoinGecko ETH differ by 0.412%, above the 0.30% conflict threshold. Both values are preserved. The direct Binance ETH/BTC pair and Binance-derived ETH/BTC agree within threshold.

The packet is therefore accepted by field with overall quality LOW rather than rejected.

## Canonical state

```text
FRAMEWORK_EDGE_STATE: REPAIR_PRESENT_PULLBACK_WARNING_ACTIVE_INTRADAY_REBOUND_FAILED_NEGATIVE_FLOW_CONFIRMED_RECLAIM_UNRESOLVED_NOT_FAILED
PULLBACK_WARNING: ACTIVE_RATIFIED_STRENGTHENED_NOT_ACTION_ESCALATED_NOT_CLEARED
SHORT_TERM_STABILIZATION: FAILED_TO_PERSIST
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

1. A settled Binance CEST close relative to 63.3K.
2. BTC retention or loss of 61.9K.
3. Whether fixed-cohort breadth remains weak across the next compatible ping.
4. Whether 4H and 24H spot-taker flow remain negative.
5. Direct ETH/BTC retention above 0.0275 or renewed approach to 0.0300.
6. Completed 17 July ETF session.
7. 7D prospective review on 21 July.

No automatic portfolio action follows.