# BTC.D and Stablecoin Role Freeze v1

**Date:** 2026-07-12  
**Status:** CANONICAL_GOVERNANCE_PATCH  
**Basis:** CMC BTC.D completion, DeFiLlama history and Full Sensor-Level Simulation & Backtest v1.

## Purpose

Freeze source conventions and prevent negative research results from being reintroduced later as unsupported action logic.

## BTC.D source convention

The active historical research series is:

```text
provider: CoinMarketCap
convention: CMC_DIRECT_SOURCE_CONVENTION
symbol label: CMC_GLOBAL_METRICS_BTC_DOMINANCE
```

It must not be described as TradingView `CRYPTOCAP:BTC.D` or assumed denominator-equivalent.

## BTC.D authority

```text
standalone market call: FORBIDDEN
standalone portfolio action: FORBIDDEN
B1 early pullback-warning weight: 0
B1 mechanical trim authority: 0
rotation-survival/reclaim context: SHADOW_ALLOWED
```

The fixed B1 condition may remain logged for research continuity:

```text
BTC.D(t) - BTC.D(t-5 calendar days) >= +0.75 percentage point
rising edge only
```

It may not be loosened post hoc. The completed simulation found positive BTC returns after B1 fires and no protective trim edge.

## Stablecoin architecture

Keep three fields separate:

1. stablecoin supply / liquidity availability;
2. DEX activity;
3. DEX volume divided by stablecoin supply as `STABLECOIN_DEPLOYMENT_PROXY`.

Prohibited labels:

- velocity;
- net inflow;
- exchange reserves;
- proof of deployment;
- automatic risk-on signal.

## Stablecoin authority

```text
standalone prediction authority: 0
standalone portfolio action: 0
transmission-quality context: SHADOW_ALLOWED
```

`EXPANDING_DEPLOYMENT` is descriptive. It did not show robust forward ETH/BTC prediction across regimes.

## Joint transmission hypothesis

The combination:

```text
falling BTC.D
+ expanding deployment
+ no recent dominance reclaim
```

is retained only as a forward falsification hypothesis.

```text
weight: 0
action authority: 0
promotion status: NOT_ELIGIBLE
```

The one successful July 2025 M4 episode does not generalize in the broader daily/weekly simulation.

## Required remaining confirmation axis

Historical and prospective altcoin participation breadth remains an independent required axis. Stablecoin chain breadth is not a substitute for altcoin market breadth.

## Governance boundary

This patch freezes roles and language. It does not change portfolio state, market state, thresholds, allocations or public Cycle Navigator output by itself.
