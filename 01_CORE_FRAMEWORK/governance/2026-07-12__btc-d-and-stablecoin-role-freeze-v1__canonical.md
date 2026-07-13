# BTC.D and Stablecoin Role Freeze v1.2

**Dato:** 2026-07-13  
**Status:** CANONICAL  
**Område:** BTC.D, stablecoin and breadth source/authority governance  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Basis:** CMC BTC.D completion, DeFiLlama history, Full Sensor Backtest, Sensor Survival Audit, Marginal Decision Value & Breadth Truth Program, and 2026-07-13 B1 reconciliation.

## Purpose

Freeze source conventions and prevent negative, redundant or latency-fragile research from being reintroduced as unsupported action logic.

## BTC.D source convention

```text
provider: CoinMarketCap
convention: CMC_DIRECT_SOURCE_CONVENTION
symbol label: CMC_GLOBAL_METRICS_BTC_DOMINANCE
TradingView CRYPTOCAP equivalence: NO
```

## BTC.D authority

```text
standalone market call: FORBIDDEN
standalone portfolio action: FORBIDDEN
B1 early pullback-warning weight: 0
B1 mechanical trim authority: 0
rotation-survival/reclaim context: SHADOW_ALLOWED
post-stress/rebound context: SHADOW_ALLOWED
```

The fixed historical B1 condition remains:

```text
BTC.D(t) - BTC.D(t-5 calendar days) >= +0.75 percentage point
rising edge only
```

It may not be loosened or optimized post hoc.

## B1 reproducibility receipt - resolved

```text
canonical fire count: 22
evaluation window: 2025-03-01 onward
additional valid date: 2025-03-04
21-row implementation status: WARMUP_TRUNCATION_ARTIFACT
source conflict: NO
resolution status: RESOLVED
```

Root cause: the 21-row simulation truncated the frame at 2025-03-01 before applying the five-day warm-up, so 2025-03-04 was dropped. The correct feature-first implementation computes the lagged BTC.D feature from available pre-window history and then filters the evaluation window. The required 2025-02-27 observation existed before the 2025-03-04 signal, so inclusion creates no look-ahead.

At 10 days, adding the 22nd row changes mean return from +2.050% to +1.786%, median from +2.740% to +2.576%, and negative rate from 28.6% to 31.8%. The role verdict is unchanged.

## Stablecoin architecture

```text
stablecoin supply change: LIQUIDITY_AVAILABILITY
one normalized DEX activity measure: REALIZED_ACTIVITY
chain-positive share: SHADOW_DISTRIBUTIONAL_CONFIRMATION
```

DEX-volume change and DEX/supply-ratio change are one activity family and may not count as two confirmations. `DEX/supply` remains a proxy and must not be called velocity.

```text
standalone prediction authority: 0
standalone portfolio action: 0
transmission-quality context: SHADOW_ALLOWED
operational-latency robustness: FAILED_HISTORICALLY
```

## Breadth architecture

```text
historical weekly frozen-universe breadth: AVAILABLE
predictive gate: NOT_SUPPORTED_ZERO_WEIGHT
descriptive participation confirmation: SHADOW_ALLOWED
daily historical breadth: DATA_MISSING
historical 30DMA breadth: DATA_MISSING
standalone action authority: 0
```

Breadth is not a required predictive gate or permission. It is a descriptive participation axis. Current constituents may not be backfilled as historical truth, and legacy alt-phase labels are not substitutes.

## Joint transmission hypothesis

```text
weight: 0
action authority: 0
promotion status: FORWARD_ONLY_NOT_PROMOTION_READY
```

## Governance boundary

This file changes source, role and reproducibility governance only. It does not change market state, portfolio state, allocations, thresholds or public Cycle Navigator output by itself.
