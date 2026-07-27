# BACKTEST ADJUDICATION AND PROMOTION POLICY v1

```yaml
policy_id: BACKTEST_ADJUDICATION_AND_PROMOTION_POLICY_v1
status: FROZEN_BEFORE_RESULTS
portfolio_authority: NONE
```

## 1. Purpose

The policy prevents attractive historical results from bypassing source quality, replication, robustness and governance.

A result is evaluated on five separate dimensions:

1. data validity;
2. implementation validity;
3. statistical stability;
4. practical framework value;
5. independent replication.

A weakness in one dimension cannot be hidden by strength in another.

## 2. Evidence classes

### `INVALID`

A blocking defect exists in source identity, time alignment, implementation or result lineage.

### `INSUFFICIENT_DATA`

The number of independent episodes, history depth or regime coverage is too small for the declared claim.

### `NULL_OR_UNSTABLE`

The primary effect is absent, reverses across folds or is reproduced by negative controls.

### `DESCRIPTIVE_ONLY`

An interpretable pattern exists, but it is not sufficiently independent, stable or point-in-time complete.

### `REPLICATED_WEAK`

Independent implementations agree on a small or regime-limited effect that may support observation but not framework authority.

### `REPLICATED_MATERIAL`

Independent implementations agree on a practically meaningful effect with acceptable uncertainty and negative controls.

### `ROBUST_CANDIDATE`

The effect survives walk-forward validation, era removal, plausible method alternatives and final holdout.

### `CANONICAL_PROMOTION_ELIGIBLE`

The result is a robust candidate, its framework role is clearly defined, operational complexity is justified and governance explicitly approves promotion.

## 3. Required promotion evidence

A result cannot become `ROBUST_CANDIDATE` unless all are true:

- owner dataset gates PASS;
- point-in-time gates PASS;
- independent sample or event-cluster count meets the test-specific minimum;
- primary endpoint was frozen before execution;
- effect direction is stable across a declared majority of walk-forward validation folds;
- practical effect meets the preregistered materiality threshold;
- confidence interval and bootstrap distribution do not indicate a fragile sign;
- negative-control signals do not reproduce the same result;
- effect is not explained entirely by one exceptional market episode;
- independent model replication passes;
- final chronological holdout does not materially contradict the claim.

## 4. Multiple-testing policy

Tests are grouped into hypothesis families before execution:

- ETF flow;
- ETH/BTC transmission and gates;
- flush and rebuy timing;
- derivatives confirmation;
- breadth and rotation;
- business cycle;
- framework-state and policy utility;
- graph-discovered challengers.

Within each family:

- the primary endpoint receives priority;
- secondary endpoints are diagnostic;
- exploratory lag scans are labelled exploratory;
- false-discovery adjustment is applied to the declared family;
- the final holdout is not used for parameter selection.

A result cannot be rescued by selecting a favorable horizon after seeing all horizons.

## 5. Practical materiality

The system reports effect sizes relevant to framework decisions, including:

- probability improvement in confirmation or survival;
- reduction in maximum adverse excursion;
- reduction in false-transition density;
- reduction in drawdown;
- improvement in range calibration;
- opportunity cost created by a lock or veto;
- added complexity, latency and missing-data sensitivity.

A statistically detectable but operationally negligible effect is not promoted.

## 6. Gate-value adjudication

A gate may improve one objective and worsen another. Each gate must therefore report a vector, not one score:

```yaml
confirmation_precision:
false_positive_rate:
false_negative_rate:
median_delay:
drawdown_avoided:
opportunity_cost:
coverage_loss:
missing_data_failure_rate:
```

Promotion requires a declared acceptable trade-off. A gate that merely reduces activity may appear accurate while adding no useful discrimination.

## 7. Policy-value adjudication

For rebuy, entry, rotation, trim or defensive policies, compare against explicit baselines:

- always inactive;
- always active after the base event;
- fixed delay;
- random matched-date control;
- simple price-only rule;
- current framework rule.

Report both economic and behavioral utility. A policy that avoids drawdown but misses nearly all recovery can be protective yet inefficient. A policy that maximizes return but creates unacceptable tail risk is not automatically superior.

## 8. Disagreement handling

When ChatGPT and Claude disagree:

1. freeze both result packages;
2. compare input and event rows;
3. identify the first divergent artifact;
4. classify the difference using the replication protocol;
5. repair only the proven defect;
6. rerun both implementations from the frozen inputs;
7. preserve the original conflicting runs.

No averaging, majority vote or narrative compromise is allowed.

## 9. New research generation

A test may create a new research idea only when the idea is linked to a specific observed failure, contradiction or missing relationship.

New ideas must include:

- source result or graph edge that motivated the idea;
- falsifiable hypothesis;
- required data;
- point-in-time rule;
- expected sample limitation;
- primary endpoint;
- reason it is not already answered by an existing test;
- status `RESEARCH_CHALLENGER_NOT_AUTHORIZED`.

Graph mining may propose ideas, but no graph-derived threshold is tested on the same full sample without a new holdout.

## 10. Framework learning outputs

Final synthesis separates:

- `KEEP`: evidence supports retaining the current rule;
- `SIMPLIFY`: a sensor is redundant or adds complexity without value;
- `RECALIBRATE`: direction is supported but threshold/window needs a new prospective challenger;
- `DEMOTE`: evidence is unstable or contradicted;
- `PROMOTE_TO_CHALLENGER`: enough evidence for forward testing;
- `PROMOTE_TO_GOVERNANCE_REVIEW`: robust replicated candidate;
- `NO_DECISION`: evidence insufficient.

No automatic canonical changes are permitted.

## 11. Archive requirements

For every test and loop, GitHub retains:

- preregistration;
- input hashes;
- code hash;
- environment manifest;
- eligible-event ledger;
- excluded rows and reasons;
- results and uncertainty;
- robustness and negative controls;
- ChatGPT package;
- Claude package;
- discrepancy report;
- adjudication;
- final recommendation;
- rejected variants.

## 12. Final authority boundary

```yaml
result_publication: ALLOWED_AFTER_AUDIT
framework_recommendation: ALLOWED
canonical_rule_change: REQUIRES_SEPARATE_GOVERNANCE
portfolio_action: NONE
market_state_change: NONE
```
