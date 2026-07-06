# BTC + ETH Spot ETF Flow Dataset - Backtest Archive

**Date added:** 2026-07-06  
**Status:** BACKTEST_READY_RAW_DATASET  
**Project:** Investering Framework  
**Domain:** ETF flows, absorption quality, transition survival, backtest research  
**Storage path:** `08_SOURCE_MATERIAL/market_data/etf_flows/`

---

## 1. Purpose

This archive entry stores BTC and ETH spot ETF flow history in a backtest-friendly format.

It is intended for ETF-era absorption research, flow persistence tests, June 2026 flush/recovery backtests, BTC survival vs ecosystem transmission studies, Forecast Ledger / RAW / PTR / FNP context, Cycle Navigator retrospective scoring, and future Research Lab audits.

This is **source data**, not a trading signal.

---

## 2. Files

```text
08_SOURCE_MATERIAL/market_data/etf_flows/2026-07-06__btc_spot_etf_flows_raw_history.csv
08_SOURCE_MATERIAL/market_data/etf_flows/2026-07-06__eth_spot_etf_flows_raw_history.csv.gz.b64
08_SOURCE_MATERIAL/market_data/etf_flows/2026-07-06__btc_eth_spot_etf_flows_backtest_dataset__README.md
```

BTC is stored directly as CSV.

ETH is stored as gzip-compressed base64 to preserve the full raw history in GitHub. To use it for backtests, decode the base64 text and then decompress it as gzip to recover `2026-07-06__eth_spot_etf_flows_raw_history.csv`.

---

## 3. Dataset schema

Each CSV row is one ETF flow observation.

Core columns:

```text
ASSET
ISO_DATE
SOURCE_DATE_RAW
<ETF ticker columns>
Total
```

Units:

```text
USD millions, as provided by source
```

Interpretation:

```text
Positive Total = net inflow
Negative Total = net outflow
Zero Total = zero / unavailable / same-day not yet updated depending on source context
```

Important same-day caveat:

```text
The 2026-07-06 row is included exactly as provided by the user/source.
Because it is same-day/recent data, it should be treated as provisional until a later source update confirms whether the 0.0 value remains final.
```

---

## 4. Coverage summary

| Asset | Rows | Coverage start | Coverage end | Computed cumulative Total | Source summary Total | File format | SHA-256 of decoded CSV |
|---|---:|---|---|---:|---:|---|---|
| BTC | 637 | 2024-01-11 | 2026-07-06 | 51131.9 | 51132.0 | CSV | `d5e9525a2dc58f4f64d0a9cba271293d4e9bb73e0750d6d9a6a69d68fc4c0bdf` |
| ETH | 499 | 2024-07-23 | 2026-07-06 | 10917.3 | 10917.3 | CSV.GZ.B64 | `8bba0ba9cd6de2e1d6cb0c9f27a5e4d2e43f44d3e91d06d0256429aab31c23bb` |

QA status:

```text
PASS
- No duplicate ISO_DATE rows detected.
- All rows parsed to valid ISO_DATE values.
- Per-row ETF column sums match Total within rounding tolerance.
- Computed cumulative totals reconcile with source summaries within rounding tolerance.
```

---

## 5. Recent update block - 2026-06-17 to 2026-07-06

This is the recent data block supplied on 2026-07-06.

### BTC

| Metric | Value |
|---|---:|
| Rows | 12 |
| Net Total | -2486.3 |
| Negative days | 10 |
| Positive days | 1 |
| Zero/provisional days | 1 |
| Last 7 rows total | -1662.3 |

Recent BTC sequence:

```text
2026-06-17: -82.2
2026-06-18: -90.7
2026-06-22: -68.3
2026-06-23: -113.8
2026-06-24: -469.0
2026-06-25: -691.7
2026-06-26: -444.5
2026-06-29: -231.0
2026-06-30: -222.6
2026-07-01: -296.0
2026-07-02: +223.5
2026-07-06: 0.0
```

### ETH

| Metric | Value |
|---|---:|
| Rows | 12 |
| Net Total | -329.3 |
| Negative days | 9 |
| Positive days | 2 |
| Zero/provisional days | 1 |
| Last 7 rows total | -108.4 |

Recent ETH sequence:

```text
2026-06-17: -29.3
2026-06-18: -12.8
2026-06-22: -66.1
2026-06-23: -82.4
2026-06-24: -30.3
2026-06-25: -81.9
2026-06-26: -12.8
2026-06-29: -29.9
2026-06-30: -27.6
2026-07-01: +14.8
2026-07-02: +29.0
2026-07-06: 0.0
```

---

## 6. Framework interpretation note

This archive entry should be read through the existing ETF-era framework hierarchy:

```text
ETF flows are high-value context for absorption quality and stress persistence.
ETF outflow persistence has stronger documented defensive value than ETF inflow persistence has offensive value.
ETF inflows do not equal rotation.
ETF outflows do not automatically equal failed absorption.
```

Flow direction must be interpreted together with:

- price survival
- ETH/BTC persistence
- BTC dominance
- breadth survival
- stablecoin deployment
- reclaim quality
- post-flush stage

Operational use:

```text
Use this dataset for research and backtests.
Do not use single-day ETF rows as standalone execution triggers.
Do not upgrade DEPLOY from ETF flows alone.
Do not call rotation from positive ETF days unless transmission survives.
```

---

## 7. Recommended future backtests

### A. ETF Flow Persistence vs BTC Drawdown

Test whether rolling ETF outflows predict next 1-3d BTC downside, next 5-7d BTC downside, failed reclaim probability and pullback wave size.

Suggested windows:

```text
1 session
3 sessions
5 sessions
7 sessions
10 sessions
```

### B. ETF Flow Stabilization after Flush

Test whether stabilization from negative to flat/positive flows improves reclaim quality, range placement, post-flush absorption classification and transition from F1 mechanical stabilization to F2 organic absorption.

### C. BTC ETF vs ETH ETF Divergence

Test whether BTC ETF stabilization without ETH ETF stabilization predicts BTC survival without ecosystem transmission.

Test whether ETH ETF improvement before BTC ETF improvement predicts early ETH-led repair attempt, but only if paired with ETH/BTC and breadth persistence.

### D. FNP / opportunity-cost research

Use ETF flow history as one input in future false-negative analysis:

```text
Was the framework too slow to reduce risk?
Was the framework too slow to prepare?
Was the framework too slow to redeploy?
Was delay justified by weak transmission?
```

---

## 8. Archive governance

Classification:

```text
SOURCE_MATERIAL
BACKTEST_READY_RAW_DATASET
NOT_CANONICAL_SIGNAL
```

Precedence:

```text
This file stores data.
It does not override DATA PING protocol, CHIEF PING, Pullback Size Policy, Rotation Survival Override, Research Lab governance or Canonical Weekly Backbone Engine.
```

Update rule:

```text
Future ETF data updates should append or replace the CSV/source files with the newest full source export.
If source format changes, preserve ISO_DATE and Total columns.
If same-day 0.0 values are present, mark them provisional until confirmed by later export.
```
