# Index Addendum — ETF Flow History Backtest Pack

**Date:** 2026-07-26  
**Status:** INDEX_ADDENDUM

## Canonical entry

```text
04_MARKET_LEARNING/truth_layer/etf_flows/2026-07-26__etf-flow-history-ingestion-and-validation__canonical.md
```

## Owner data package

```text
04_MARKET_LEARNING/truth_layer/etf_flows/2026-07-26__us-spot-crypto-etf-flow-history/
```

## Status

```text
ETF_FLOW_HISTORY_READY_FOR_BACKTEST_INPUT
+
BTC_651_SESSIONS
+
ETH_513_SESSIONS
+
STRUCTURE_VALIDATED
+
LOOKAHEAD_GUARD_ACTIVE
+
FULL_MULTI_SENSOR_BACKTEST_NOT_CLAIMED
```

## Routing

Use this package for historical ETF-flow research, replay, feature construction and source-backed backtest joins.

Do not use it as:

- a live ETF source,
- a same-session signal without publication timestamps,
- a standalone market call,
- proof that the entire framework has been fully backtested.

## Boundary

No change to DATA PING, Master Monday, Forecast Ledgers, current market state, framework rules or portfolio authority.
