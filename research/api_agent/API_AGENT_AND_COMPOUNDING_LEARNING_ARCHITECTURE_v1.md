# API AGENT AND COMPOUNDING LEARNING ARCHITECTURE v1

Status: SHADOW-ONLY FIRST EXECUTION LAYER

## Objective

Create a learning system whose useful evidence compounds over time. More observations must improve calibration, precision and hypothesis quality, without allowing the system to reward itself, rewrite history or silently increase authority.

## Compounding loop

1. Capture verified owner-data.
2. Produce timestamped specialist and Director observations.
3. Freeze forecasts before outcomes.
4. Score matured forecasts against owner outcomes.
5. Store errors, conflicts, missingness and regime context in Framework Memory.
6. Generate bounded hypotheses from repeated errors.
7. Test hypotheses on development data and sealed holdout rules.
8. Promote only changes that improve preregistered metrics and survive rollback gates.
9. Reuse promoted learning in future prompts, scorecards and specialist calibration.

## Memory layers

- Observation memory: immutable owner-bound rows.
- Forecast memory: frozen claims, levels, horizons and confidence.
- Outcome memory: matured results and censoring.
- Error memory: false positives, false negatives, timing errors and opportunity cost.
- Learning memory: hypotheses, experiments, verdicts and applicability regimes.
- Governance memory: versions, approvals, receipts, rollback points and rejected changes.

## Precision score

Precision is never one number alone. Every weekly scorecard must retain:

- directional accuracy;
- timing-window accuracy;
- calibration error between stated confidence and realized frequency;
- false-positive rate;
- false-negative rate;
- opportunity-cost score;
- sequence accuracy;
- data-completeness and source-health penalties;
- regime and sample-size context.

A score may improve only on matured, lineage-valid rows. Missing outcomes remain censored, not losses or wins.

## Anti-overfitting gates

- Predictions must be frozen before outcomes.
- Training, validation and final holdout remain separated.
- Parameter changes require versioned hypotheses.
- No threshold search after outcome inspection without a new experiment version.
- Promotion requires minimum sample, regime diversity and measured improvement.
- A promoted rule must have an explicit rollback condition.
- Recent performance cannot erase older regime failures.
- Specialist count cannot substitute for independent causal evidence.

## API authority

The OpenAI API may analyze, summarize, classify conflicts and propose hypotheses. It may not:

- create owner truth;
- infer missing values;
- modify canonical thresholds;
- change model weights;
- merge its own promotion;
- create portfolio action;
- access sealed outcomes outside an approved evaluation task.

All API calls pass through API Gateway v1 and produce an immutable receipt containing task, model, reasoning effort, prompt version, input hashes, output hash, token usage and estimated cost.

## Initial task classes

- DAILY_DIRECTOR_SHADOW: Luna, low reasoning.
- DAILY_CONFLICT_REVIEW: Terra, medium reasoning.
- WEEKLY_CALIBRATION_SHADOW: Terra, medium reasoning.
- MASTER_MONDAY_PREP_SHADOW: Sol, high reasoning.
- DEEP_RESEARCH_MANUAL: Sol, high reasoning, manual only.

## Promotion ladder

DRAFT -> SHADOW -> FORWARD_TEST -> VALIDATED -> CANDIDATE -> CANONICAL

No API-generated learning can skip a stage.
