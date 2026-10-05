# M3 Cycle Navigator Skill Decomposition - Kickoff Checkpoint v1

**Mission:** `RL-CN-SKILL-BASELINE-003`  
**Date:** 2026-10-05  
**Status:** ACTIVE_RESEARCH_KICKOFF  
**Authority:** RESEARCH_ONLY / NO_PUBLIC_SCORE_REWRITE / NO_CANONICAL_EFFECT  
**Fresh framework main:** `1ad48e4d3dc8d337b1cfd658d38b0a4fafc20df3`

## Frozen question

What part of Cycle Navigator is genuine incremental skill versus a mechanical volatility/range baseline?

## Mandatory decomposition

Do not use a single blended accuracy number.

Evaluate separately:
1. weekly range placement;
2. width / containment / breach behavior;
3. directional conditions;
4. regime classification;
5. rotation / transmission interpretation.

## Historical baseline evidence - degraded, not canonical proof

The July degraded M5 sample contains 15 CN rows and 14 matched dumb-baseline rows.

Direct recomputation from:
`04_MARKET_LEARNING/range_skill/data/2026-07-08__m5-range-skill-rows-degraded-execution.csv`

shows:

### All assets

- CN mean Jaccard: ~0.357
- DUMB1.5 mean Jaccard: ~0.461
- DUMB2.0 mean Jaccard: ~0.427
- PREVWK mean Jaccard: ~0.336

- CN mean Winkler alpha10: ~96.94
- DUMB1.5: ~90.18
- DUMB2.0: ~77.23
- PREVWK: ~117.45

Paired rows:
- versus DUMB1.5, CN wins Jaccard 6/14 and loses 8/14; CN wins Winkler 5/14 and loses 9/14.
- versus DUMB2.0, Jaccard is 7/14 vs 7/14; CN wins Winkler 5/14 and loses 9/14.
- versus PREVWK, CN wins both Jaccard and Winkler 8/14 vs 6/14.

This sample is explicitly `DEGRADED`. It is evidence that CN range skill was not obviously superior to simple ATR baselines, not a final current-era estimate.

## Current range-accountability topology

The canonical Forward Range Ledger Protocol v0.1 requires every future official range to be:
- frozen pre-week;
- baseline-compared against DUMB1.5 and DUMB2.0;
- scored on verified actuals;
- subject to Winkler/Jaccard/containment/breach/width metrics.

However:

`05_CYCLE_NAVIGATOR/autonomous_calibration_v1/POLICY.json`
still points to:
`05_CYCLE_NAVIGATOR/forward_range_ledger/FORWARD_RANGE_LEDGER_v0_1.csv`

and that ledger currently contains only the example row.

Current calibration state:
- eligible_verified_row_n = 0
- selected_action = CONTINUE_CALIBRATION
- reason = insufficient verified forward rows for escalation

Meanwhile a separate:
`CN_FORWARD_RANGE_LEDGER_v2.jsonl`
contains recovered/prospective W36-W40 ranges, but not the v0.1 baseline/scoring fields.

Therefore the current range-skill-versus-baseline experiment is not visibly connected to the newer weekly production series.

## Current structural accountability

The newer internal precision layer is active and explicitly avoids one synthetic overall score.

Recent reproducible structural scores:
- completed W36: 75%
- completed W37: 90%
- completed W38: 80%
- completed W39: 60%

Internal family state after W39:
- regime: mean/median 100 across three observations
- rotation: mean ~58.33, median 50, state PERSISTENT_WEAKNESS
- breadth: mean ~66.67, median 50, WATCH
- ETH/BTC: 100, 100, 0 across three observations

For completed W39:
- weekly BTC and ETH envelopes both contained the weekly extrema;
- numeric asset/window containment score = 75% because six of eight weekly/intraday envelopes fully contained extrema;
- structural score = 60%;
- public-continuity score = 58.33%;
- decision utility remains unavailable.

These are accountability measurements. They are not automatically incremental skill versus a baseline.

## Initial Research Lab hypothesis

Current evidence is consistent with:

- **range skill:** unproven and historically weak versus simple ATR baselines;
- **regime classification:** promising but small sample and partly broad/forgiving labels;
- **rotation/transmission:** useful as disciplined non-confirmation framing, but current family score itself shows persistent weakness;
- **public/accountability value:** real and separate from forecasting alpha.

## Required Sol questions

1. Does any supplied evidence establish incremental CN range skill versus a simple frozen baseline?
2. How should the degraded historical sample be weighted relative to the newer but baseline-unpaired W39 containment result?
3. Are 75/90/80/60 structural scores evidence of forecasting skill, or mainly scoring/accountability quality?
4. Which CN components plausibly add information that a mechanical range model cannot?
5. What claims should be VERIFIED, WEAKENED, REJECTED or UNKNOWN?
6. Is there enough evidence to demote range prediction while retaining regime/rotation/accountability functions?
7. Identify the smallest evidence package needed for an honest current-era baseline tournament.

## Required Claude questions

Audit the full folder:
`05_CYCLE_NAVIGATOR/weekly/2026/`

and reconcile it with:
- `05_CYCLE_NAVIGATOR/forward_range_ledger/`
- `05_CYCLE_NAVIGATOR/autonomous_calibration_v1/`
- `05_CYCLE_NAVIGATOR/internal_learning/`
- publication contracts and range protocol.

Trace every frozen forecast, scorecard, issue/public-number binding and scoring-method change.

Determine whether current W36-W40 range freezes can be mechanically converted into the canonical baseline tournament without hindsight and whether any range-score/public-score lineage has silently changed meaning.

## Boundaries

No historical score rewrite.
No public scoreboard mutation.
No model/threshold changes.
No range promotion.
No portfolio action.
No Codex.
