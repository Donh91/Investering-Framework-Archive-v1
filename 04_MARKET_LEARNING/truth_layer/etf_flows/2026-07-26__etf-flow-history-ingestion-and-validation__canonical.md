# ETF Flow History — Ingestion and Validation

**Date:** 2026-07-26  
**Package:** `US_SPOT_CRYPTO_ETF_FLOW_HISTORY_20260726`  
**Status:** CANONICAL DATA-PACK INGESTION  
**Verdict:** ETF_FLOW_HISTORY_READY_FOR_BACKTEST_INPUT  
**Authority:** Historical source evidence and deterministic feature input only. No market call, portfolio action, sensor ratification or active-state change.

## 1. Accepted evidence

The user supplied complete daily US spot crypto ETF-flow exports for BTC and ETH.

Validated coverage:

| Asset | Sessions | First date | Last date | Duplicate dates | Null cells | Daily row-total failures |
|---|---:|---|---|---:|---:|---:|
| BTC | 651 | 2024-01-11 | 2026-07-24 | 0 | 0 | 0 |
| ETH | 513 | 2024-07-23 | 2026-07-24 | 0 | 0 | 0 |

Units are USD millions.

Every daily `Total` equals the displayed fund-column sum at one-decimal precision.

## 2. Preserved artifacts

```text
04_MARKET_LEARNING/truth_layer/etf_flows/2026-07-26__us-spot-crypto-etf-flow-history/
```

The package contains:

- full fund-level daily rows partitioned by asset and calendar year;
- deterministic feature-build and validation scripts;
- manifest and SHA-256 checksums;
- data dictionary, timing boundary and recommended backtest joins.

The original uploaded artifact hashes are retained in the manifest.

## 3. Important source-summary nuance

ETH daily totals reconcile to the supplied summary.

BTC fund and total summaries appear rounded independently. The displayed daily `Total` series sums to `51,438.7` USDm, while the supplied summary reports `51,439.0` USDm, a `0.3` USDm difference. The archive preserves both values and treats the difference as source-summary rounding, not as a corrected observation.

## 4. Lookahead boundary

The exports contain session dates but no per-row publication timestamps.

Canonical backtest rule:

```text
ETF flow dated t is assumed known only after the US session close on t.
```

Therefore:

- same-session trading attribution is prohibited without publication-time evidence;
- next-session or later forward returns are the default outcome labels;
- generated rolling features are trailing-only;
- missing sessions must not be silently converted to zero without an explicit trading-calendar rule.

## 5. Backtest capability unlocked

This package unlocks reproducible testing of the ETF-flow leg, including:

- 1, 3, 5, 10 and 20-session flow persistence;
- outflow deterioration versus subsequent downside;
- inflow persistence versus BTC survival and ecosystem transmission;
- BTC/ETH ETF-flow divergence;
- fund concentration and issuer-level dominance;
- flow reversal after cumulative inflow or outflow sequences;
- integration with verified price, ETH/BTC, BTC.D, breadth, derivatives and forecast outcomes.

## 6. Boundary

This package does **not by itself** constitute a full framework backtest.

A full multi-sensor replay still requires point-in-time aligned histories for price, dominance, breadth, derivatives, macro variables, source-QA and decision/forecast ledgers.

No current DATA PING state, Master Monday state, forecast score or portfolio instruction is changed by this ingestion.
