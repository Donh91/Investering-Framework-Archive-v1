# BTC.D and Stablecoin Role Freeze v1.1

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** BTC.D and stablecoin source/authority governance  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Basis:** CMC BTC.D completion, DeFiLlama history, Full Sensor Backtest and Sensor Survival Audit v1.

## Purpose

Freeze source conventions and prevent negative or latency-fragile research from being reintroduced as unsupported action logic.

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

The fixed historical B1 condition may remain logged for continuity:

```text
BTC.D(t) - BTC.D(t-5 calendar days) >= +0.75 percentage point
rising edge only
```

It may not be loosened or optimized post hoc.

## B1 reproducibility receipt

```text
frozen canonical fires with price follow-through: 21
direct recomputation: 22
additional date: 2025-03-04
status: SOURCE_CONFLICT_REPRODUCIBILITY_OPEN
```

Preserve the frozen 21-fire result until the exact warm-up, eligibility or boundary cause is resolved. Do not select the more attractive version.

## Stablecoin architecture

Keep liquidity availability separate from realized activity:

```text
stablecoin supply change: LIQUIDITY_AVAILABILITY
one normalized DEX activity measure: REALIZED_ACTIVITY
chain-positive share: SHADOW_DISTRIBUTIONAL_CONFIRMATION
```

DEX-volume change and DEX/supply-ratio change are highly redundant and may not count as two confirmations. `DEX/supply` remains a proxy and must not be called velocity.

Prohibited labels include net inflow, exchange reserves, proof of deployment and automatic risk-on signal.

## Stablecoin authority and latency

```text
standalone prediction authority: 0
standalone portfolio action: 0
transmission-quality context: SHADOW_ALLOWED
operational-latency robustness: FAILED_HISTORICALLY
```

An additional one-day operational delay changed the historical expanding-deployment strategy from +17.54% to -4.98% and worsened drawdown. This blocks standalone production use.

## Joint transmission hypothesis

Falling BTC.D plus expanding deployment plus no recent dominance reclaim remains forward-falsification only:

```text
weight: 0
action authority: 0
promotion status: NOT_ELIGIBLE
```

## Required remaining confirmation axis

Historical and prospective frozen-universe altcoin participation breadth remains independently required. Stablecoin chain breadth is not a substitute.

## Governance boundary

This patch freezes roles and language. It does not change portfolio state, market state, allocations, thresholds or public Cycle Navigator output by itself.
