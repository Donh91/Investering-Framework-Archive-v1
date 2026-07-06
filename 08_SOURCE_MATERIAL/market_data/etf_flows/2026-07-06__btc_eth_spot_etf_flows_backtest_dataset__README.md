# BTC + ETH Spot ETF Flow Dataset - Backtest Archive

Date added: 2026-07-06
Status: BACKTEST_READY_RAW_DATASET
Project: Investering Framework
Domain: ETF flows, absorption quality, transition survival, backtest research
Storage path: 08_SOURCE_MATERIAL/market_data/etf_flows/

## Purpose

This archive entry stores BTC and ETH spot ETF flow history for future ETF-era backtest research.

Use cases:
- ETF-era absorption research
- flow persistence tests
- June 2026 flush/recovery backtests
- BTC survival vs ecosystem transmission studies
- Forecast Ledger / RAW / PTR / FNP context
- Cycle Navigator retrospective scoring
- Research Lab audits

This is source data, not a trading signal.

## Files

BTC direct CSV:
08_SOURCE_MATERIAL/market_data/etf_flows/2026-07-06__btc_spot_etf_flows_raw_history.csv

ETH compressed source file:
08_SOURCE_MATERIAL/market_data/etf_flows/2026-07-06__eth_spot_etf_flows_raw_history.csv.gz.b64

Manifest / QA note:
08_SOURCE_MATERIAL/market_data/etf_flows/2026-07-06__btc_eth_spot_etf_flows_backtest_dataset__README.md

ETH note:
The ETH file is stored as gzip-compressed base64. To use it, decode the base64 text and decompress the gzip payload to recover the CSV file named 2026-07-06__eth_spot_etf_flows_raw_history.csv.

## Schema

Each recovered CSV row is one ETF flow observation.

Columns:
- ASSET
- ISO_DATE
- SOURCE_DATE_RAW
- ETF ticker columns
- Total

Unit:
USD millions, as provided by source.

Interpretation:
- Positive Total means net inflow.
- Negative Total means net outflow.
- Zero Total means zero, unavailable, holiday or same-day not yet updated depending on source context.

Same-day caveat:
The 2026-07-06 row is included exactly as provided. Because it is same-day data, the 0.0 value should be treated as provisional until a later export confirms it.

## Coverage summary

BTC:
- Rows: 637
- Coverage: 2024-01-11 to 2026-07-06
- Computed cumulative Total: 51131.9
- Source summary Total: 51132.0
- File format: CSV
- Decoded CSV SHA-256: d5e9525a2dc58f4f64d0a9cba271293d4e9bb73e0750d6d9a6a69d68fc4c0bdf

ETH:
- Rows: 499
- Coverage: 2024-07-23 to 2026-07-06
- Computed cumulative Total: 10917.3
- Source summary Total: 10917.3
- File format: CSV.GZ.B64
- Decoded CSV SHA-256: 8bba0ba9cd6de2e1d6cb0c9f27a5e4d2e43f44d3e91d06d0256429aab31c23bb

QA status: PASS
- No duplicate ISO_DATE rows detected.
- All rows parsed to valid ISO_DATE values.
- Per-row ETF column sums match Total within rounding tolerance.
- Computed cumulative totals reconcile with source summaries within rounding tolerance.

## Recent update block, 2026-06-17 to 2026-07-06

BTC recent block:
- Rows: 12
- Net Total: -2486.3
- Negative days: 10
- Positive days: 1
- Zero/provisional days: 1
- Last 7 rows total: -1662.3

BTC sequence:
2026-06-17 -82.2
2026-06-18 -90.7
2026-06-22 -68.3
2026-06-23 -113.8
2026-06-24 -469.0
2026-06-25 -691.7
2026-06-26 -444.5
2026-06-29 -231.0
2026-06-30 -222.6
2026-07-01 -296.0
2026-07-02 +223.5
2026-07-06 0.0

ETH recent block:
- Rows: 12
- Net Total: -329.3
- Negative days: 9
- Positive days: 2
- Zero/provisional days: 1
- Last 7 rows total: -108.4

ETH sequence:
2026-06-17 -29.3
2026-06-18 -12.8
2026-06-22 -66.1
2026-06-23 -82.4
2026-06-24 -30.3
2026-06-25 -81.9
2026-06-26 -12.8
2026-06-29 -29.9
2026-06-30 -27.6
2026-07-01 +14.8
2026-07-02 +29.0
2026-07-06 0.0

## Framework interpretation note

ETF flows are high-value context for absorption quality and stress persistence.

ETF outflow persistence has stronger documented defensive value than ETF inflow persistence has offensive value.

ETF inflows do not equal rotation.

ETF outflows do not automatically equal failed absorption.

Flow direction must be interpreted together with price survival, ETH/BTC persistence, BTC dominance, breadth survival, stablecoin deployment, reclaim quality and post-flush stage.

Operational use:
- Use this dataset for research and backtests.
- Do not use single-day ETF rows as standalone execution triggers.
- Do not upgrade DEPLOY from ETF flows alone.
- Do not call rotation from positive ETF days unless transmission survives.

## Recommended future backtests

A. ETF Flow Persistence vs BTC Drawdown
Test whether rolling ETF outflows predict next 1-3d downside, next 5-7d downside, failed reclaim probability and pullback wave size.

B. ETF Flow Stabilization after Flush
Test whether stabilization from negative to flat/positive flows improves reclaim quality, range placement and transition from F1 mechanical stabilization to F2 organic absorption.

C. BTC ETF vs ETH ETF Divergence
Test whether BTC ETF stabilization without ETH ETF stabilization predicts BTC survival without ecosystem transmission. Test whether ETH ETF improvement before BTC ETF improvement predicts early ETH-led repair attempt, but only if paired with ETH/BTC and breadth persistence.

D. FNP / opportunity-cost research
Use ETF flow history as one input in future false-negative analysis.

## Archive governance

Classification:
- SOURCE_MATERIAL
- BACKTEST_READY_RAW_DATASET
- NOT_CANONICAL_SIGNAL

Precedence:
This file stores data. It does not override DATA PING protocol, CHIEF PING, Pullback Size Policy, Rotation Survival Override, Research Lab governance or Canonical Weekly Backbone Engine.

Update rule:
Future ETF data updates should append or replace the CSV/source files with the newest full source export. If source format changes, preserve ISO_DATE and Total columns. If same-day 0.0 values are present, mark them provisional until confirmed by later export.
