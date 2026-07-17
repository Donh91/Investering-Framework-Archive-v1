# Rotation Repair Edge Update — Warning Maintained, Short-Term Stabilization Unconfirmed

**Accepted log:** `DATA_PING_V5_20260717T113106Z`  
**Event:** `ROTATION_REPAIR_EDGE_20260712_01`  
**Event status:** `OPEN_TRIGGERED`  
**Decision-delta class:** `OBSERVABILITY_OR_DATA_QUALITY_DELTA`

## Main Framework verdict

The ratified pullback warning remains active. It is neither escalated nor cleared.

The current packet contains a partial short-horizon breadth rebound, but it also contains further 7D deterioration and a material loss of decision authority because Binance spot, direct ETH/BTC, canonical CEST candles and Binance spot-taker flow were unavailable.

The correct interpretation is therefore:

```text
SHORT-TERM STABILIZATION: POSSIBLE BUT UNCONFIRMED
PULLBACK WARNING: ACTIVE_RATIFIED_MAINTAINED
WARNING ESCALATION: NO
WARNING CLEARANCE: NO
REPAIR FAILURE: NO
```

## Comparable evidence

CoinGecko remained comparable with the prior CoinGecko bridge:

- BTC +0.328% since the prior packet's CoinGecko observation.
- ETH +0.038%.
- Total market cap +0.153%.
- BTC dominance +0.084 percentage points.

`FIXED_RISK35_v1` remained directly comparable:

- 1H positive share improved from 8.57% to 31.43%.
- 24H positive share improved from 5.71% to 17.14%.
- 7D positive share deteriorated from 34.29% to 25.71%.
- 1H median remained slightly negative at -0.119%.
- 24H median remained negative at -1.701%.
- 7D median deteriorated to -2.255%.

The rebound is real relative to the prior extreme reading, but absolute participation remains weak and the medium-horizon deterioration continues.

## Source degradation

Binance returned a restricted-location error. The current run therefore has no fresh:

- Binance primary price;
- direct Binance ETH/BTC;
- Binance CEST close update;
- Binance spot-taker flow.

CoinGecko and GeckoTerminal are accepted only as observation and shadow fallbacks. They do not replace the canonical close ledger or spot aggression lane.

OKX futures data are current venue-specific context only and are not comparable with the prior packet's Binance futures values.

## Structure

- CoinGecko BTC is 63,038, below 63.3K by approximately 0.41%.
- The latest stored canonical Binance CEST close remains 64,161.99, above 63.3K.
- BTC remains above 61.9K.
- No stored settled close is below 59.4K.
- Direct ETH/BTC is missing.
- Derived CoinGecko ETH/BTC is 0.029086, above 0.0275 and below 0.0300, but is observation-only for gate purposes.

Failed reclaim remains unresolved because no fresh canonical close exists.

## Flow and leverage

The verified ETF lane remains unchanged:

```text
16 Jul BTC ETF: +79.1M
16 Jul IBIT: +33.4M
16 Jul ETH ETF: -28.0M
BTC 3-session: +367.9M
BTC 5-session: +33.6M
BTC 7-session: -146.6M
BTC 10-session: +364.1M
Stage-1 ETF flow leg: COMPLETE_RATIFIED
```

Spot-taker flow is missing and has no substitute.

OKX leverage is mixed:

- BTC OI approximately +3.39% over 24H while price remains weak.
- BTC funding is marginally negative.
- BTC and ETH account-count ratios are elevated near 1.9.
- ETH OI is approximately -1.37% over 24H.

This does not confirm recovery or invalidate the warning.

## Canonical state

```text
FRAMEWORK_EDGE_STATE: REPAIR_PRESENT_PULLBACK_WARNING_ACTIVE_SHORT_TERM_STABILIZATION_UNCONFIRMED_RECLAIM_UNRESOLVED_NOT_FAILED
PULLBACK_WARNING: ACTIVE_RATIFIED_MAINTAINED_NOT_ESCALATED_NOT_CLEARED
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

1. Restoration of Binance spot and a fresh canonical CEST close relative to 63.3K.
2. Restoration of Binance 4H/24H spot-taker flow.
3. Next compatible fixed-cohort observation, particularly whether 24H participation rises above weak levels or 7D deterioration continues.
4. Direct ETH/BTC confirmation above 0.0275 or persistence above 0.0300.
5. Completed 17 July ETF session.
6. BTC retention or loss of 61.9K with confirming participation and flow evidence.

No automatic portfolio action follows.