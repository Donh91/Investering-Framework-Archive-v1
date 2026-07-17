# Rotation Repair Edge Update — OTA Cross-check and Farside Source Revision

**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Latest accepted DATA PING:** `DATA_PING_V5_20260717T034148Z`  
**OTA run:** `2026-07-17T06:07:00Z`  
**Primary-source recheck:** `2026-07-17T06:34:00Z`  
**Event status:** `OPEN_TRIGGERED`

## Executive result

The OTA run strengthens the already-active early-warning candidate because its later intraday cross-check placed BTC below the 63.3K reclaim level while ETH/BTC remained above 0.0275. This is a failed-reclaim test in progress, not a settled canonical failure.

The OTA claim that the 16 July ETF settle remained pending was time-valid at the run timestamp but became outdated shortly afterward. The direct Farside table now shows a completed 16 July BTC row of +79.1M with IBIT +33.4M, FBTC +30.7M and BITB +15.0M. The direct ETH table shows -28.0M.

Therefore the Stage-1 ETF flow requirement is now complete and ratified. This does not by itself open rotation, entry or portfolio action because participation, spot-flow and confirmation evidence remain weak or contradictory.

## Source-convention discipline

The OTA price series uses Crypto.com UTC candles as a cross-check. The Main Framework keeps Binance CEST candles as the canonical close ledger. The OTA values must not overwrite canonical settled closes.

The OTA references a 62.2K holdout floor and 0.0285 structure level. These remain shadow/holdout diagnostics and are not promoted into canonical runtime gates. Canonical runtime gates remain BTC 63.3K / 61.9K / 59.4K and ETH/BTC 0.0275 / 0.0300.

## Material OTA evidence

- Crypto.com cross-check BTC around 62,975 at 06:07 UTC, with an intraday low near 62,784.
- BTC was below the 63.3K reclaim level intraday, so failed-reclaim behavior is now being tested.
- ETH/BTC near 0.02905 remained above the canonical repair gate 0.0275.
- Price had retraced approximately 4.3% from the 65.6K local top.
- OTA retention estimate was approximately 23%, but its formal 7D test remains scheduled for 21 July.
- The active early-warning candidate remains consistent with the first negative FIXED_RISK35 persistence delta.

## Verified ETF source revision

```text
14 Jul BTC ETF: +181.1M
15 Jul BTC ETF: +107.7M
16 Jul BTC ETF: +79.1M
16 Jul IBIT: +33.4M
3-session BTC total: +367.9M
5-session BTC total: +33.6M
7-session BTC total: -146.6M
10-session BTC total: +364.1M
16 Jul ETH ETF: -28.0M
```

This supersedes only the provisional ETF fields in the accepted payload. The immutable accepted payload is preserved and linked to a post-acceptance source-revision supplement.

## Framework interpretation

```text
STRUCTURE: REPAIR STILL PRESENT
INTRADAY RECLAIM TEST: UNDER PRESSURE
EARLY WARNING CANDIDATE: STRENGTHENED
RATIFIED PULLBACK ALERT: NO
STAGE_1 ETF FLOW LEG: COMPLETE / RATIFIED
ROTATION: NO_ROTATION
BROAD RECOVERY: NOT_CONFIRMED
NEW ENTRY SIGNAL: NOT_ACTIVE
ACTIVE TRIM SIGNAL: NO
PORTFOLIO ACTION: NONE
USER ACTION: HOLD_AND_WAIT
```

## Why Stage-1 flow completion does not change action

The ETF flow leg is now positive and source-verified, but:

- BTC remains below 0.0300 confirmation through the ETH/BTC pair.
- FIXED_RISK35 24H and 7D breadth remain weak.
- Binance 4H and 24H spot-taker proxies remain negative for BTC and ETH in the latest accepted DATA PING.
- Market-wide CVD remains unavailable.
- Official stablecoin history remains missing.
- The current BTC reclaim test is under pressure intraday.

The correct result is stronger evidence on one leg and weaker evidence on several others, not automatic deployment.

## Next decisive observations

1. Canonical CEST settlement relative to 63.3K.
2. Next compatible FIXED_RISK35 persistence delta.
3. Persistence or reversal of negative 4H and 24H spot-taker flow.
4. ETH/BTC hold above 0.0275 and any verified persistence above 0.0300.
5. Completed 17 July ETF session.
6. OTA 7D retention review on 21 July.
