# ETF Flow History Backtest Pack — Skill-Run Receipt

**Date:** 2026-07-26  
**Repository:** `Donh91/Investering-Framework-Archive-v1`  
**Branch:** `agent/task-20260726-etf-flow-history-backtest-pack`  
**Run status:** READY_FOR_PR

## Scope

Archive user-supplied BTC and ETH ETF histories as a source-preserving, deterministic and backtest-ready truth-layer package.

## Validation

```text
BTC rows: 651
BTC coverage: 2024-01-11 to 2026-07-24
ETH rows: 513
ETH coverage: 2024-07-23 to 2026-07-24
duplicate dates: 0
null cells: 0
daily row-total reconciliation failures: 0
validator: PASS
```

## Files and routing

- canonical ingestion record created;
- owner data package created;
- index addendum created;
- addendum registry updated;
- full fund-level daily history partitioned by year;
- deterministic build and validation scripts included;
- lookahead boundary documented;
- original uploaded file hashes retained in the manifest.

## Governance

```text
MARKET_STATE_CHANGED = NO
PORTFOLIO_ACTION = NO
DATA_PING_CONTRACT_CHANGED = NO
MASTER_MONDAY_CHANGED = NO
SENSOR_RATIFIED = NO
FULL_MULTI_SENSOR_BACKTEST_CLAIMED = NO
```
