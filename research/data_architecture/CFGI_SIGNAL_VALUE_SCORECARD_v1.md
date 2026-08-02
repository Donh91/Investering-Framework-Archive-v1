# CFGI Signal Value Scorecard v1

Status: SHADOW-ONLY EVALUATION CONTRACT

## Purpose

Measure whether each CFGI component improves prospective forecast quality beyond existing price, breadth, derivatives and macro owners.

## Components

`score, volatility, volume, impulse, technical, social, dominance, trends, whales, orders`

Evaluated separately for `MARKET`, `BTC`, `ETH` and by `15m`, `1h`, `4h`, `1d` timeframe.

## Required evidence

No component may be promoted from collection alone. Evaluation requires frozen observations, matured outcomes, source completeness and regime labels.

Minimum review gate:

- 30 matured observations for provisional review
- 90 matured observations for frequency change
- at least 3 materially different regimes
- no unresolved look-ahead or lineage failure

## Metrics

Each component and component pair is scored on:

- directional lift versus baseline
- timing-window lift
- Brier or calibration improvement
- false-positive reduction
- false-negative reduction
- pre-pullback lead time
- failed-recovery discrimination
- rotation discrimination
- incremental information after conditioning on price, breadth and derivatives
- stability across regimes and timeframes

## Decisions

Allowed decisions are `RETAIN`, `INCREASE_EVENT_ONLY`, `REDUCE_FREQUENCY`, `REMOVE`, or `INSUFFICIENT_EVIDENCE`.

Any frequency change requires a versioned hypothesis, forward test, cost effect and rollback condition. No scorecard may change canonical framework state, model weights or portfolio action automatically.

## Review cadence

- weekly: data quality and capture completeness only
- monthly: descriptive component behaviour
- quarterly: formal signal-value review
- event-driven: only after a documented structural anomaly or source change

## Reuse

RAW, Cycle Navigator and Master Monday may consume scorecard findings as shadow calibration evidence. They must preserve uncertainty and may not treat collection density as predictive validity.
