# Rotation Repair Edge Update — 2026-07-15T221843Z

**Accepted log:** `DATA_PING_V5_20260715T221843Z`  
**Raw source snapshot:** `DATA_PING_V4_20260715T221843Z`  
**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Status:** `OPEN_TRIGGERED`  
**Framework edge:** `PRESENT_REPAIR_NOT_CONFIRMATION`  
**Portfolio authority:** none

## Material change

The first complete packet in the canonical V5 thread restores Binance primary spot, canonical CEST daily/hourly close observability and a Binance-only spot-taker proxy.

This resolves the largest technical blocker inherited from V4. The repair edge is therefore upgraded from `NEAR_PRESENT` to `PRESENT_REPAIR_NOT_CONFIRMATION`.

It does **not** confirm rotation or open a deployment window.

## Constructive evidence

- BTC latest settled CEST close: `64,834.31`, above the `63,300` reclaim gate.
- BTC remains above the `61,900` survival gate.
- Direct Binance ETH/BTC: `0.029640`, above the `0.0275` repair gate and near `0.0300`.
- ETH/BTC rose `+2.172%` over 24H and closed near the top of its 24H range.
- Fixed breadth cohort improved without sample change:
  - 1H positive share `+28.57 pp`
  - 24H positive share `+5.71 pp`
  - 7D positive share `+2.86 pp`
- 24H breadth is positive but uneven, 7D breadth is positive.
- ETH ETF rolling 3/5/7/10-session windows are all positive.
- ETH Binance spot-taker proxy is positive over 24H.
- Source discrepancy checks passed.
- OKX v1.3 remains operational as venue-specific derivatives input.
- User-supplied CFGI.io screenshot restores 1D sentiment at `62 / GREED`, date-level only.

## Cooling and contradictory evidence

- ETH/BTC remains below the `0.0300` confirmation gate.
- BTC ETF rolling 3/5/7/10-session windows remain negative.
- BTC Binance spot-taker proxy is negative over 15M, 1H, 4H and 24H.
- BTC and ETH mark/index basis are slightly negative on OKX.
- BTC OI is lower over 1H, 24H and 72H.
- ETH OI is lower over 24H.
- Top-100 1H breadth remains below 50%.
- Market-wide CVD is unavailable.
- Official stablecoin history and macro core remain missing.
- Current CEST daily/hourly candles are partial.
- The 15 July ETF session is pending and must not be treated as zero.

## Framework conclusion

```text
REPAIR EDGE: PRESENT
ROTATION: NO_ROTATION
BROAD RECOVERY: NOT_CONFIRMED
REBUY: LOCKED
LARGE-CAP BUY WINDOW: WATCH_ONLY / NOT_OPEN
NEW ENTRY SIGNAL: NOT ACTIVE
PULLBACK ALERT: NO
ACTIVE TRIM: NO
PORTFOLIO ACTION: NONE
USER ACTION: HOLD AND WAIT
```

## Next unlock conditions

The event remains open. Material confirmation requires a combination of:

1. ETH/BTC verified persistence above `0.0300`.
2. Breadth survival beyond the current mixed short-horizon state.
3. BTC flow stabilization beyond a single completed positive ETF session.
4. No failed-reclaim signature around `63.3K`.
5. Better market-wide flow or repeated Binance spot-demand confirmation.
6. Continued canonical close persistence.

No threshold, gate or portfolio rule is promoted by this update.
