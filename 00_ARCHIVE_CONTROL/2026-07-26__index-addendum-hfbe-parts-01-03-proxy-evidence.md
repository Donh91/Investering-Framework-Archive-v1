# Index Addendum — HFBE parts 01-03 proxy evidence

**Date:** 2026-07-26  
**Status:** `INDEX_ADDENDUM`  
**Domain:** historical backtest data extraction / truth-layer source evidence

## Framework-facing owner

```text
04_MARKET_LEARNING/truth_layer/backtest_history/2026-07-26__hfbe-parts-01-03-proxy-evidence-audit__canonical.md
04_MARKET_LEARNING/truth_layer/backtest_history/state/HFBE_ACTIVE_CONTINUATION_POINTER.json
```

## Preserved source package

```text
08_SOURCE_MATERIAL/backtest/history_extraction/HFBE_20260726T204022Z/
```

## Implementation receipt

```text
07_PROMPTS_AND_AGENTS/skill_runs/2026-07-26__hfbe-parts-01-03-archive__receipt.md
```

## Registered status

```text
ARCHIVE_ACCEPTED
+
PARTIAL_WITH_EXPLICIT_GAPS
+
CANONICAL_BACKTEST_INPUT: NO
+
CONTINUATION_REQUIRED: PARTS 01-03
```

## Boundary

The package contains 98 daily rows each for BTC index proxy, ETH index proxy and a derived ETH/BTC index ratio from 2026-04-18 through 2026-07-24.

It is not direct spot history, does not contain volume or trade count and does not unlock a full framework backtest.

No market call. No portfolio action. No canonical state change.
