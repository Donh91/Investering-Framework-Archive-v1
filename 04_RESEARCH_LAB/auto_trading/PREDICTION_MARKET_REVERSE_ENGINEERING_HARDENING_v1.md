# PREDICTION MARKET REVERSE ENGINEERING HARDENING v1

Status: GENERIC RESEARCH METHOD ADDENDUM
Date: 2026-09-13
Parent method: `EXTERNAL_STRATEGY_REVERSE_ENGINEERING_PROTOCOL_v1.md`
Evidence anchors: `source_notes/AT-SRC-0014_PREDICTION_MARKET_MICROSTRUCTURE_CALIBRATION_IRL.md`, `source_notes/AT-SRC-0015_POLYMARKET_USERS_BEHAVIORAL_BENCHMARK_DATASET.md`

## Purpose

Harden the generic external-strategy reverse-engineering method for prediction markets without creating a new experiment engine.

These controls are mandatory whenever the external source trades binary/event contracts.

## H1 - separate forecast edge from execution/liquidity-provision edge

For every source action, estimate separately where data permits:

- forecast/calibration quality;
- maker/taker role;
- spread captured or paid;
- order type/aggressiveness;
- price improvement;
- fees/rebates;
- queue/resting-order advantage;
- follower execution at observable time.

Do not label total source P&L as prediction alpha.

Required decomposition:

`TOTAL_SOURCE_EDGE = FORECAST_EDGE + SELECTION_EDGE + SIZING_EDGE + TIMING_EDGE + EXECUTION/MICROSTRUCTURE_EDGE + PRODUCT/STRUCTURE_EDGE + interactions`

The equation is conceptual, not an assumption of linear additivity. Ablation/counterfactual tests determine attribution.

## H2 - condition market-probability baselines on time and product structure

Preserve and model:

- true event/game start or occurrence time;
- trade timestamp;
- exchange close time;
- administrative settlement time;
- time-to-event/time-to-expiry;
- category/sport/market type;
- single versus combo/parlay product;
- leg count where applicable;
- volume/liquidity/unique-participant proxies.

A raw contract price is not a universally calibrated probability benchmark across all these states.

Do not use settlement timestamp as a proxy for event time when the true event timing is available.

## H3 - calibration precedes expected-value and sizing claims

For probabilistic source strategies, grade at minimum:

- reliability curve;
- Brier score;
- log loss where valid;
- realized frequency by probability bucket;
- calibration conditional on TTE/category/product type.

Only after out-of-sample calibration survives should Kelly-like or confidence-scaled sizing be interpreted as evidence of rational sizing edge.

High win rate alone is insufficient.

## H4 - singles and parlays are different research objects

Never pool them into one source-alpha estimate.

For parlays preserve:

- each leg;
- leg price at construction time;
- joint/parlay execution price;
- leg count;
- same-event versus cross-event structure;
- correlation assumptions;
- source/follower modifications.

Follower parlay performance cannot validate the source model's single-market prediction quality.

## H5 - behavioral cloning precedes inverse reinforcement learning

Use increasing model complexity only when evidence supports it:

1. deterministic threshold/rank baselines;
2. regularized logistic/multinomial behavioral clone;
3. tree/boosting model if stable out-of-time lift exists;
4. optional linear/MaxEnt IRL after action and opportunity-set integrity is proven.

The supervised clone asks `can observable state predict what the source does?`

IRL asks `what reward trade-off is consistent with the observed policy?`

Neither establishes proprietary internals.

## H6 - the opportunity set is mandatory

A ledger of source bets contains only positive selections and is selection-biased.

At each source decision time reconstruct eligible non-selected markets. Without matched negatives, no claim about Oddy/another source's selection policy may be promoted beyond descriptive evidence.

## H7 - copyability uses the follower's microstructure, not the source fill

The copyability clock begins at first independent observability, not at source execution.

Reprice at realistic delay grids, including +30 seconds, +1 minute and +5 minutes when suitable, with contemporaneous spread/depth and follower order role.

A maker source copied by a taker follower is a distinct economic strategy.

## H8 - external benchmark data is control evidence, not alpha authority

Large historical datasets such as `vgregoire/polymarket-users` can define matched cohorts, maker/taker priors and behavioral distributions.

They may not substitute for the source's own immutable ledger and must be version-pinned because published research datasets can receive material corrections.

## Generic promotion rule

Prediction-market components may transfer into the Framework only if they show incremental value after:

- calibration controls;
- TTE/product controls;
- maker/taker/execution controls;
- matched market baselines;
- realistic observability/copy delay;
- frozen out-of-sample evaluation under #885.

The expected best outcome is often a small reusable component, for example a timing filter, calibration transform, execution rule, no-trade gate, or source-quality feature, not wholesale cloning of the external bot.