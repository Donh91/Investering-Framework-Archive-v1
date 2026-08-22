# Tournament Preregistration

## Objective
Determine which candidate architecture preserves the most reproducible decision information after dependence, robustness and complexity accounting. Simplification is not the objective and SIMPLE_3 receives no preference.

## Shared-row invariant
Every eligible candidate comparison uses the same event, observation timestamp, information cutoff, source version, outcome definition, catalyst tag, missing-data policy and evaluation horizons.

## Frozen horizons
24h, 72h and 7d. Divergence horizons may never be changed after event creation.

## Required metrics
Precision, recall, false-positive rate, false-negative rate, first-signal lead-time, stable-confirmation delay, missed-opportunity cost, MAE, MFE, regime robustness, catalyst robustness, source/version robustness, candidate disagreements, incremental information and complexity accounting.

## Catalyst views
1. ALL_EVENTS
2. VERIFIED_CATALYST_ONLY
3. CATALYST_EXCLUDED
4. STRUCTURAL_REGIME_SPLIT, especially pre-ETF vs post-ETF.

## Win rule
Full Stack wins if reproducible incremental edge survives dependence, provider-removal, catalyst and leakage controls. Complexity cannot disqualify it by itself.

## Terminal enum
`SPARSE_STACK_SUPPORTED`, `FULL_STACK_INCREMENTAL_EDGE_SUPPORTED`, `TASK_DEPENDENT_PARETO_FRONT`, or `INSUFFICIENT_EVIDENCE` only.
