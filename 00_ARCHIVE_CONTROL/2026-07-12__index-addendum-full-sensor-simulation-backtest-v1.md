# Index Addendum — Full Sensor Simulation & Backtest v1

**Date:** 2026-07-12  
**Status:** ARCHIVE_INDEX_ADDENDUM

## Canonical files

```text
04_MARKET_LEARNING/full_backtests/2026-07-12__full-sensor-simulation-backtest-v1__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-12__btc-d-and-stablecoin-role-freeze-v1__canonical.md
04_MARKET_LEARNING/full_backtests/data/2026-07-12__m1-b1-event-forward-returns-v1.csv
04_MARKET_LEARNING/full_backtests/data/2026-07-12__m4-transmission-state-forward-returns-weekly-v1.csv
04_MARKET_LEARNING/full_backtests/data/2026-07-12__m4-transmission-walk-forward-year-v1.csv
04_MARKET_LEARNING/full_backtests/data/2026-07-12__m4-episode-direct-forward-returns-v1.csv
04_MARKET_LEARNING/truth_layer/DATA_COMPLETION_CONTROL_STATE.json
```

## Binding research status

```text
FULL_SENSOR_LEVEL_BACKTEST: COMPLETE
M1_B1_EARLY_WARNING_EDGE: NOT_SUPPORTED
M1_B1_PROTECTIVE_TRIM: NOT_SUPPORTED
M4_JOINT_SIGNATURE_GENERALIZATION: NOT_SUPPORTED
STABLECOIN_STANDALONE_PREDICTOR: NOT_SUPPORTED
BTC_D_SURVIVAL_CONTEXT: SHADOW_ONLY
STABLECOIN_TRANSMISSION_CONTEXT: SHADOW_ONLY
FULL_PORTFOLIO_BACKTEST: BLOCKED_NOT_IDENTIFIABLE
RULE_PROMOTION: NONE
```

## Source convention

The historical BTC.D series is CoinMarketCap under `CMC_DIRECT_SOURCE_CONVENTION`. It is not TradingView `CRYPTOCAP:BTC.D` and may not be represented as denominator-equivalent.

## Operational consequence

Sunday Closeout and Master Monday must consume this addendum through their existing GitHub-first `CANONICAL_INDEX` load order. Do not add a duplicate engine or blended score.

## Remaining research priority

1. prospective breadth with frozen constituents;
2. M3 forward decision coverage;
3. FRLP eight-week forward evidence;
4. later full portfolio simulation only after point-in-time action and holdings inputs exist.

No market call. No portfolio action. No automatic rule ratification.
