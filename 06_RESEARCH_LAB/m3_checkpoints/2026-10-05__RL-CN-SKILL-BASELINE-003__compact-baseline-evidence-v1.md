# M3 Compact Baseline Evidence Packet v1

**Mission:** `RL-CN-SKILL-BASELINE-003`
**Date:** 2026-10-05
**Status:** FROZEN_RESEARCH_INPUT
**Authority:** RESEARCH_ONLY
**Framework main at freeze:** `f8c9ab9465fd7227ca76618575cfba7351fa06cf`

## Question

What part of Cycle Navigator is genuine incremental skill versus a mechanical volatility/range baseline?

Do not collapse range, regime, rotation and accountability into one accuracy number.

## A. Historical degraded range tournament

Source:
`04_MARKET_LEARNING/range_skill/data/2026-07-08__m5-range-skill-rows-degraded-execution.csv`

The kickoff checkpoint independently recomputed the matched degraded sample:

All assets:
- CN mean Jaccard ≈ 0.357
- DUMB1.5 mean Jaccard ≈ 0.461
- DUMB2.0 mean Jaccard ≈ 0.427
- PREVWK mean Jaccard ≈ 0.336

Winkler alpha10, lower is better:
- CN ≈ 96.94
- DUMB1.5 ≈ 90.18
- DUMB2.0 ≈ 77.23
- PREVWK ≈ 117.45

Paired 14-row comparison:
- CN vs DUMB1.5 Jaccard: 6 wins, 8 losses
- CN vs DUMB1.5 Winkler: 5 wins, 9 losses
- CN vs DUMB2.0 Jaccard: 7 wins, 7 losses
- CN vs DUMB2.0 Winkler: 5 wins, 9 losses
- CN vs PREVWK: 8 wins, 6 losses on both Jaccard and Winkler

Interpretation boundary:
This dataset is explicitly DEGRADED and cannot establish current-era performance.
It is nevertheless adverse evidence against claiming historically obvious range superiority over ATR baselines.

## B. Canonical baseline protocol exists but current production is disconnected

Canonical protocol requires future official range forecasts to be compared with:
- DUMB1.5
- DUMB2.0
- PREVWK where applicable
and evaluated on verified actuals using Jaccard, Winkler, containment, breaches and width.

But:
`05_CYCLE_NAVIGATOR/forward_range_ledger/FORWARD_RANGE_LEDGER_v0_1.csv`
contains only `CNxx_EXAMPLE_BTC`, explicitly example-only.

`05_CYCLE_NAVIGATOR/autonomous_calibration_v1/STATE.json`
has zero eligible verified rows for that canonical tournament and remains CONTINUE_CALIBRATION / insufficient verified rows.

A separate newer ledger:
`05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl`
contains recovered/prospective W38+ range freezes but does not contain the v0.1 dumb-baseline/scoring fields.

Therefore:
- current-era CN range accountability exists;
- current-era incremental range skill versus DUMB1.5/DUMB2.0 is not yet measured by the canonical tournament.

## C. Newer structural accountability is real but not baseline alpha

Internal scorecards explicitly state:
"No synthetic overall internal accuracy is published because aliases and correlated claims are not independent."

Recent public structural scores recorded in the current lineage:
- W36: 75%
- W37: 90%
- W38: 80%
- W39: 60%

These scores are claim-accountability measures, not comparisons against a mechanical model.

Completed W37 scorecard:
- regime 100
- breadth 100
- ETH/BTC 100
- leadership 100
- rotation 50
- altseason 100
- public structural score 90

Completed W38:
- regime 100
- ETH/BTC 100
- breadth 50
- leadership 50
- rotation 50
- altseason 100
- public structural score 80

Completed W39:
- BTC weekly range 100
- ETH weekly range 100
- ETH/BTC 0
- breadth 50
- regime 100
- rotation rows 100 and 50
- altseason 50
- each intraday range family 50
- public structural score 60

The W39 weekly BTC and ETH extrema were contained inside the frozen weekly envelopes.
That demonstrates containment for that week, not incremental superiority versus a simple volatility band.

## D. Internal family state after W39

Current internal-learning state reports roughly:
- regime mean/median: 100 / 100 across 3 observations
- rotation mean/median: 58.33 / 50, state PERSISTENT_WEAKNESS
- breadth mean/median: 66.67 / 50, WATCH
- ETH/BTC recent: 100, 100, 0
- BTC range: one valid observation, 100
- ETH range: one valid observation, 100

Interpretation:
Regime classification is promising in a tiny sample.
Rotation is not a demonstrated strength in the current family score.
Range 100s have N=1 in this state and are containment/accountability, not baseline skill.

## E. Claims to attack

C1: "Cycle Navigator has demonstrated incremental weekly range skill versus simple volatility baselines."
Current evidence pressure: NOT ESTABLISHED, historical degraded evidence is adverse.

C2: "Cycle Navigator's structural/regime layer may add value independent of exact range placement."
Current evidence pressure: PLAUSIBLE but small-N and potentially forgiving labels.

C3: "Rotation/transmission interpretation is a demonstrated forecasting strength."
Current evidence pressure: WEAK/CONFLICTED because current rotation family mean is ~58 and state PERSISTENT_WEAKNESS.

C4: "Cycle Navigator's accountability/public-value function is real even if forecast alpha is unproven."
Current evidence pressure: SUPPORTED as process/accountability value, not market alpha.

## Required Sol adjudication

Return separate verdicts for:
1. range placement/width skill vs dumb baseline;
2. regime classification;
3. rotation/transmission;
4. accountability/public trust value;
5. overall claim that CN complexity adds incremental predictive value.

Explicitly distinguish:
- predictive alpha;
- containment;
- calibration/accountability;
- useful non-confirmation;
- narrative breadth.

Do not infer alpha from a 100 score when no matched baseline exists.
Do not treat the degraded historical sample as current canonical truth.
Do not average correlated family scores into one headline skill number.

## Minimum next evidence question

What is the smallest no-hindsight tournament needed to decide current-era range skill fairly, using W36-W40 frozen ranges and a mechanical baseline frozen from only information available at each publication time?
