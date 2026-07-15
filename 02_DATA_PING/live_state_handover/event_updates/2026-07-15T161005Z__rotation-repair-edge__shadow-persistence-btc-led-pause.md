# Rotation Repair Edge — Shadow persistence with BTC-led pause

**Dato:** 2026-07-15 16:10:05 UTC / 18:10:05 CEST  
**Status:** OPERATIONAL_RUNTIME_UPDATE  
**Område:** DATA PING / active edge event  
**Primary folder:** `02_DATA_PING/live_state_handover/event_updates/`  
**Depends on:** `DATA_PING_V4_20260715T161005Z`, `ROTATION_REPAIR_EDGE_20260712_01`

## Accepted interpretation

The first full GeckoTerminal shadow-OHLC patch run materially improves supplemental observability without upgrading core data quality.

The validated shadow layer shows uninterrupted 48-hour bar coverage, small CoinGecko-versus-pool discrepancies and observation-only persistence above both the BTC 63.3K reclaim level and the ETH/BTC 0.0285 repair level. The 14 July shadow daily closes also finished above those levels.

This does not replace canonical Binance closes. It cannot update canonical persistence, close the event or unlock deployment.

## Material changes since `DATA_PING_V4_20260715T140445Z`

1. BTC rose 0.33% to 65,273 while ETH was nearly unchanged; ETH/BTC eased 0.30% to 0.0295104 and BTC dominance rose 0.1484 percentage points.
2. One-hour breadth recovered from 17.1% to 34.3% but remains below majority. Twenty-four-hour breadth cooled from 82.9% to 74.3%, while seven-day breadth remained broad at 77.1%.
3. GeckoTerminal shadow OHLC passed with 48/48 bars and no gaps. This reduces the observation gap but remains `OBSERVATION_ONLY` because canonical Binance daily/hourly ledgers are missing.

## Current evidence

### Constructive

- BTC current fallback remains 3.12% above 63.3K.
- ETH/BTC remains 3.55% above 0.0285 and only 1.63% below 0.0300.
- 24H and 7D breadth remain above 70%, including ex-BTC/ETH breadth.
- Latest completed BTC and ETH ETF sessions remain positive.
- Shadow price cross-checks passed for BTC, ETH and ETH/BTC.
- No failed-reclaim signature is present in the supplied packet.

### Cooling or contradictory

- The cross-ping move became BTC-led rather than ETH-led.
- ETH/BTC eased and BTC dominance rose.
- 1H breadth remains below 50% despite recovering.
- 24H breadth cooled by 8.6 percentage points.
- Stablecoin proxy remained near-flat over 24H and lower cross-ping.
- Ethereum and selected Solana DEX activity proxies declined.
- ETH sentiment remains stronger than realized price follow-through.

### Unresolved blockers

- 14 July canonical Binance close remains missing.
- Canonical hourly persistence remains missing.
- Direct Binance ETH/BTC remains missing.
- Futures funding, OI, basis, skew and taker data remain missing.
- Binance spot-taker and market-wide CVD remain missing.
- Current 15 July ETF session remains pending.
- Official stablecoin history remains missing.
- ETH/BTC remains below 0.0300.

## Main-framework state

```text
ACTIVE_EVENT_ID: ROTATION_REPAIR_EDGE_20260712_01
FRAMEWORK_EDGE_STATE: NEAR_PRESENT
ALERT_STATUS: STILL_ACTIVE
EVENT_STATUS: OPEN_TRIGGERED
RESOLUTION_CANDIDATE: SHADOW_PERSISTENCE_STRENGTHENED_BUT_CANONICAL_CLOSE_AND_FLOW_VERIFICATION_BLOCKED
ROTATION_STATUS: NO_ROTATION
REBUY_STATUS: LOCKED
LARGE_CAP_BUY_WINDOW: NOT_OPEN
NEW_PULLBACK_ALERT: NO
ACTIVE_TRIM_SIGNAL: NO
PORTFOLIO_ACTION: NONE
```

## Operational conclusion

This is not a fresh breakout signal and not a failed breakout. It is a high-level hold with medium-horizon participation still broad, short-horizon participation still weak and the new shadow layer providing useful observational persistence.

The correct action boundary remains hold and wait. No chase, no new deployment and no trim are authorized from this packet.

## Research effect

For the SCTA/OTA holdout, the packet strengthens observational persistence but does not convert the Type-2 candidate into confirmation. Flow necessity remains unresolved because the latest completed ETF session is positive, BTC rolling ETF windows remain negative, the current session is pending and taker/leverage data are absent.
