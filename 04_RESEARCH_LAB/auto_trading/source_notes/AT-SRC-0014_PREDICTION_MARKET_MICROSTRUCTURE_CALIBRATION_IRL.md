# AT-SRC-0014 - Prediction-market microstructure, calibration and behavioral reverse engineering

Date captured: 2026-09-13
Status: ADMITTED / HIGH VALUE RESEARCH FOUNDATION
Evidence class: 2024-2026 academic / research literature + public prediction-market methodology
Primary use: harden EdgeOnchain/Oddy reverse engineering and future external-strategy studies

## Executive verdict

The strongest new lesson is that prediction-market alpha cannot be evaluated as `pick accuracy` alone.

A rigorous decomposition must separate:

`forecast/calibration edge -> selection edge -> sizing edge -> maker/taker execution edge -> timing/TTE edge -> product-structure edge -> observable/copyable edge`

This matters directly to EdgeOnchain because a profitable source account could outperform for reasons other than superior outcome prediction, and a follower can lose the source advantage by crossing the spread, entering later, using parlays, or copying in a different time-to-event regime.

## 1. Polymarket microstructure - winners often provide liquidity

Primary paper:

- Pat Akey, Vincent Grégoire, Nicolas Harvie, Charles Martineau, 2026, `Who Wins and Who Loses In Prediction Markets? Evidence from Polymarket`
- SSRN: https://ssrn.com/abstract=6443103
- CEPR DP21615: https://cepr.org/publications/dp21615

Reported sample:

- 588 million trades;
- approximately $67B trading volume;
- Polymarket users over a large multi-year sample.

Key findings reported by the paper:

- the top 1% of profitable users capture 76.5% of total positive trading gains;
- successful traders disproportionately provide liquidity with limit orders;
- unsuccessful traders disproportionately take liquidity with market orders;
- monthly performance is only modestly persistent and may partly reflect selection rather than stable skill;
- the largest winners are not primarily explained by an insider-trading story in the authors' analysis.

### Framework transfer

For every external prediction-market strategy, including EdgeOnchain, record where data permits:

- order type;
- maker/taker role;
- quoted versus executed price;
- spread paid/earned;
- resting-order duration;
- whether the source provided or consumed liquidity;
- whether a follower would be forced to consume liquidity even when the source provided it.

This creates a mandatory distinction:

`PREDICTION_EDGE != LIQUIDITY_PROVISION_EDGE`.

A source can be profitable because it receives better fills or earns the spread. A follower who observes the filled trade later and crosses the book can therefore fail even when the source has genuine alpha.

## 2. Calibration is conditional on time to event, attention and true event timing

Primary research:

- Nicole Kagan and Rubens Baiocchi, 2026, `Calibration in Prediction Markets: Theory and Evidence`
- Kalshi Research: https://kalshi.com/research/publications/calibration
- SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7355520

Reported sample:

- complete resolved Kalshi history through mid-2026;
- 2,243,741 markets;
- eleven categories.

Key findings:

- aggregate calibration improves materially as resolution approaches;
- Brier score falls from roughly 0.08-0.09 at a three-month horizon to roughly 0.02 near close;
- calibration improves with event-level volume and number of unique traders;
- category differences matter;
- anchoring time to the true underlying event timing, rather than a delayed administrative close/settlement timestamp, improves calibration analysis, especially in sports and elections.

### Framework transfer

A market price cannot be treated as a static fair-probability benchmark independent of context.

Every prediction-market experiment should preserve:

- true event start/occurrence time;
- exchange close time;
- administrative settlement time separately;
- time-to-event/time-to-expiry at each decision;
- event volume and unique-participant count where available;
- category/sport/market type.

The baseline against which Edge is judged should therefore be `context-conditioned market probability`, not raw price alone.

## 3. Sports-market calibration changes sharply by time-to-expiry and product type

Primary paper:

- Niusha Moshrefi, Princeton, 2026, `Prices, Probabilities, and Parlays: Systematic Bias in Sports Prediction Markets`
- arXiv: https://arxiv.org/abs/2607.14430

Reported sample:

- approximately 23 million NBA, MLB and NHL moneyline trades on Kalshi.

The paper conditions calibration on five time-to-expiry buckets:

- 0-10 minutes;
- 10-30 minutes;
- 30-90 minutes;
- 90-240 minutes;
- 240+ minutes.

Important result:

- the 30-90 and 90-240 minute regimes were visually close to perfect calibration in the sample;
- the final 0-10 minutes showed large, systematic, step-like distortion consistent with late hedging/insurance demand, although alternative mechanisms cannot be ruled out by the paper;
- cross-game parlays were systematically overpriced relative to the product of contemporaneous leg prices even when the underlying legs came from the well-calibrated 30-240 minute regime;
- median parlay overpricing became increasingly visible beyond roughly five legs and reached around 1.22x at ten legs and around 1.31x at eleven legs in the reported sample;
- the paper estimates roughly 3% median multiplicative inflation per extra leg over its fitted range;
- empirical parlay win rates sat below quoted parlay prices in the sample.

### Framework transfer

For EdgeOnchain:

- singles and parlays must never be pooled into one alpha statistic;
- the follower `$1k -> $85k/$93k` parlay narrative cannot validate Oddy's single-market prediction edge;
- time-to-event must be a mandatory feature in the selection-policy reconstruction;
- parlay leg count/product type must be a mandatory feature or separate experiment;
- any apparent advantage concentrated in late-event markets must be tested against the known TTE-conditioned market distortion rather than credited automatically to the model.

## 4. Calibration matters more than headline accuracy for betting systems

Primary paper:

- Conor Walsh and Alok Joshi, 2024, `Machine learning for sports betting: Should model selection be based on accuracy or calibration?`
- DOI: https://doi.org/10.1016/j.mlwa.2024.100539
- arXiv: https://arxiv.org/abs/2303.06021

The authors report that selecting NBA prediction models using calibration rather than classification accuracy produced materially better betting results in their experiment. They also emphasize that Kelly-style staking requires calibrated probabilities.

### Framework transfer

For any model whose claimed mechanism is probability estimation:

Primary diagnostics should include:

- reliability/calibration curve;
- Brier score;
- log loss where appropriate;
- expected calibration error or equivalent bucketed diagnostic;
- realized expectancy by quoted/model-probability bucket.

Win rate remains descriptive, not a promotion metric.

`Kelly-like sizing` is inadmissible as a claimed sizing edge unless probability calibration is first demonstrated out-of-sample.

## 5. Inverse reinforcement learning is a valid later-stage tool for opaque strategy behavior

Primary paper:

- Kubilay Karacam and Mehmet Yasin Ulukus, 2026, `Inferring latent trading motivations in Borsa Istanbul: A comparative inverse reinforcement learning approach`
- DOI: https://doi.org/10.1016/j.bir.2026.100834

The paper applies linear and maximum-entropy inverse reinforcement learning to brokerage behavior and compares it with supervised behavioral-cloning baselines. Its goal is to infer an interpretable latent reward function from observed actions under market states, rather than only predict the next action.

### Framework transfer

For external-strategy reverse engineering use a model-complexity ladder:

1. transparent deterministic/rule baseline;
2. regularized logistic/multinomial behavioral clone;
3. tree/boosting model only if it adds stable out-of-time explanatory value;
4. optional linear or MaxEnt IRL only after the opportunity set and state/action ledger are robust.

IRL should answer a narrower question:

`What observable state features are consistent with the source behaving as though it optimizes a particular reward trade-off?`

It must not be described as recovering proprietary source code or hidden model internals.

## 6. Research consequences for EdgeOnchain

The Edge/Oddy case is now stronger as a scientific test because the literature provides explicit falsifiers.

The source must be decomposed into at least:

- probability calibration / forecast quality;
- market selection policy;
- stake sizing;
- time-to-event policy;
- maker/taker and order-placement behavior;
- product choice, especially singles versus parlays;
- source execution advantage;
- signal observability delay;
- follower execution/copy decay.

A positive Edge result requires incremental advantage after these controls.

If source performance is explained by limit-order liquidity provision, a known TTE pricing distortion, or parlay/product effects, that is still potentially useful research, but it must be classified as the correct edge family rather than `AI prediction alpha`.

## 7. Highest-value generic framework lessons

### Lesson A - execution style is part of the strategy

For copy-research, maker/taker role is not implementation detail. It may determine whether the source edge is transferable at all.

### Lesson B - probability baselines must be state-conditioned

Prediction-market prices are not uniformly calibrated across time-to-event, attention and product structure. Controls must condition on these dimensions.

### Lesson C - calibration precedes sizing

A calibrated probability model can support expected-value and Kelly-like sizing research. A high-hit-rate but miscalibrated model cannot justify aggressive sizing.

### Lesson D - clone behavior before inferring motives

First test whether observable state can reproduce the external strategy's actions. Only then use IRL to study a latent reward approximation.

### Lesson E - copyability is a microstructure experiment

A source can have valid prediction alpha yet be uncopiable because the follower loses queue priority, spread, maker rebates/edge, or reacts after repricing.

## Admission decision

`ACCEPT / HIGH VALUE GENERIC RESEARCH`

Do not create a new trading engine from these papers.

Use the findings to harden the existing external-strategy reverse-engineering protocol and the #885 scientific lifecycle.