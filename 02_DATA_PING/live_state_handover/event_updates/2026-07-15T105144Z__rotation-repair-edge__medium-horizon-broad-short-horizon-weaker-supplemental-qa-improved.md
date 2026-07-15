# Rotation Repair Edge Update — 2026-07-15T10:51:44Z

**Source:** `DATA_PING_V4_20260715T105144Z`  
**Data quality:** LOW  
**Authority:** MAIN_FRAMEWORK / CHATGPT  
**Active event:** `ROTATION_REPAIR_EDGE_20260712_01`

## Accepted interpretation

The event remains `OPEN_TRIGGERED / NEAR_PRESENT / STILL_ACTIVE`.

Medium-horizon transmission remains constructive:

- BTC CoinGecko fallback remains above 63.3K.
- Derived ETH/BTC remains above 0.0285 and below 0.0300.
- 24H breadth remains broad at 85.7%.
- 7D breadth improved to 68.6%, with ex-BTC/ETH breadth at 66.7%.
- The latest completed BTC and ETH ETF session remains positive.
- ETH ETF 3/5/7/10-session windows remain positive.
- The comparable 8-asset stablecoin proxy is marginally positive, but low-confidence.

Short-horizon evidence weakened:

- 1H breadth fell from 51.4% to 31.4%.
- BTC ETF 3/5/7/10-session windows remain negative.
- Derived ETH/BTC eased slightly cross-ping.
- DEX core-pool prices are higher over 24H while activity volume softened modestly; this is supplemental only.

## Quality-control result

Supplemental observability improved without improving the core grade:

- fixed breadth cohort preserved;
- 8/8 stablecoin proxy comparability preserved;
- exact BTC/ETH sentiment timestamps added;
- limited ETH/SOL core-pool OHLCV history added;
- Binance Spot, daily/hourly closes, spot taker and Futures remain unavailable.

Therefore:

```text
CORE QUALITY: LOW
SUPPLEMENTAL QA: IMPROVED
RESOLUTION CANDIDATE: STRENGTHENED, BUT CLOSE VERIFICATION BLOCKED
```

## Unresolved requirements

- completed 14 July CEST BTC/ETH/ETHBTC closes;
- direct ETH/BTC;
- hourly persistence extension;
- Binance spot-taker flow;
- funding, OI, basis and leverage;
- ETH/BTC confirmation at 0.0300;
- current 15 July ETF settlement;
- official stablecoin history;
- market-wide CVD.

## Framework result

```text
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
ROTATION_STATUS: NO_ROTATION
REBUY_STATUS: LOCKED
LARGE_CAP_BUY_WINDOW: WATCH_ONLY / NOT_OPEN
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
PORTFOLIO_ACTION: NONE
```

No new event, rule, gate, entry permission or portfolio action is created by this run.
