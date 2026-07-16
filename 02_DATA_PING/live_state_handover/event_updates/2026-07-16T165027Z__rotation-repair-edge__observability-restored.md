# Rotation Repair Edge Update — Observability Restored, Confirmation Still Blocked

**Accepted log:** `DATA_PING_V5_20260716T165027Z`  
**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Status:** `OPEN_TRIGGERED`  
**Framework edge state:** `REPAIR_PRESENT_SHORT_TERM_COOLING_NOT_FAILED`

## Executive conclusion

The repair remains present and has not failed. The material delta in this run is not stronger market confirmation, but restored observability.

Binance primary spot, the canonical CEST candle ledger, direct ETH/BTC and the Binance spot-taker proxy all returned. This removes several technical unknowns from the previous snapshot.

The restored data confirms two consecutive settled CEST BTC closes above 64K on 14 and 15 July, so OTA v0.4 P1's close condition is now supported on the canonical CEST basis as well as the earlier shadow cross-check basis. The ETF flow condition remains satisfied by the positive completed sessions on 14 and 15 July.

However, the 16 July ETF session is still partial, ETH/BTC remains below 0.0300, short-horizon breadth is weak, rolling 24H spot-taker flow is negative for both BTC and ETH, and official stablecoin plus market-wide CVD remain missing. Stage 1 therefore has not fired.

## Material positive evidence

- BTC: 64,373.56, above 63.3K and 61.9K.
- Settled CEST BTC closes: 64,676.90 on 14 July and 64,834.31 on 15 July.
- Direct ETH/BTC: 0.029150, above 0.0275.
- Latest completed BTC ETF session: +107.7M, positive streak 2.
- Latest completed ETH ETF session: +53.9M, positive streak 2.
- ETH ETF 3/5/7/10-session aggregates remain positive.
- BTC Binance spot-taker proxy is positive over rolling 4H, +8.96M.
- Seven-day breadth remains above 50% in both cohorts.
- Source discrepancy checks show no threshold breach.
- Canonical price and close observability are restored.

## Cooling or contradictory evidence

- BTC: -0.877% over 24H.
- ETH: -1.846% over 24H.
- ETH/BTC: -0.985% over 24H and near the lower part of its range.
- ETH/BTC remains below the 0.0300 confirmation gate.
- Top-50 breadth: 20.0% positive over 1H and 34.29% over 24H.
- Top-100 breadth: 15.71% positive over 1H and 27.14% over 24H.
- BTC ETF 3/5/7-session aggregates remain negative.
- BTC Binance spot-taker proxy is -64.68M over rolling 24H.
- ETH Binance spot-taker proxy is negative over 1H, 4H and 24H.
- BTC OI is down over 1H, 24H and 72H on OKX.
- ETH OI is down over 1H and 24H on OKX.
- Funding remains positive, so the current derivatives picture is deleveraging or digestion, not clean confirmation.
- Official stablecoin history and market-wide CVD remain unavailable.

## OTA holdout cross-check

```text
P1: ACTIVE
P2: DEAD
P3: MOOT FOR THIS CASE
P1 CLOSE CONDITION: CANONICAL CEST CROSS-CHECK PASS
P1 FLOW CONDITION: PASS
72H MATURITY: 17 JUL
7D MATURITY: 21 JUL
12-SESSION VERDICT: AROUND 30 JUL
DURABILITY VERDICT: PENDING
```

This does not give OTA authority over the gate system. It only strengthens the evidence chain behind the active P1 track.

## Stage-1 status

```text
BTC ETF POSITIVE COMPLETED STREAK: 2
IBIT-LED PRIOR SESSIONS: YES
16 JUL COMPLETED SESSION: PENDING
STAGE-1: NOT FIRED
```

A displayed partial or provisional 0.0 row cannot be counted as the third completed positive session.

## Framework interpretation

```text
repair remains present
+
short-term cooling continues
+
observability restored
+
P1 close and flow conditions supported
+
rotation confirmation still blocked
```

## Action

```text
ROTATION: NO_ROTATION
BROAD_RECOVERY: NOT_CONFIRMED
LARGE_CAP_BUY_WINDOW: WATCH_ONLY / NOT OPEN
NEW_ENTRY_SIGNAL: NOT_ACTIVE
REBUY: LOCKED
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
PORTFOLIO_ACTION: NONE
USER_ACTION: HOLD_AND_WAIT
```

## Next meaningful tests

1. Completed 16 July BTC ETF settlement, including IBIT contribution.
2. 72H OTA maturity on 17 July.
3. Continued BTC hold above 63.3K without failed-reclaim behavior.
4. ETH/BTC persistence and eventual confirmation above 0.0300.
5. Recovery in 1H and 24H breadth.
6. Improvement in multi-session BTC ETF windows and repeated spot-demand evidence.
7. Seven-day holdout check on 21 July and 12-session durability verdict around 30 July.