# BACKTEST BUILD — Statistics, graph and ledger foundation v1

```yaml
work_package: STATISTICS_GRAPH_AND_LINEAGE_FOUNDATION_v1
source_challenge_suite: CLAUDE_TOP5_ADJUDICATION_v1
status: IMPLEMENTED_PENDING_CI
market_data_used: NONE
economic_results: NONE
```

## Implemented statistical primitives

- pinball loss;
- Winkler interval score;
- empirical interval coverage;
- mean interval width;
- moving-block bootstrap indices;
- stationary bootstrap indices;
- purged expanding walk-forward splits;
- embargo accounting;
- Benjamini-Hochberg false-discovery control;
- PCA participation-ratio calculation from supplied eigenvalues;
- entropy effective rank from supplied eigenvalues;
- leave-one-event-out means;
- deterministic seeds.

The module intentionally does not select market parameters or execute an economic hypothesis.

## Implemented graph primitives

- deterministic topological ordering;
- cycle rejection;
- provenance owner-path validation;
- method-identity requirements for feature, event, test and result nodes;
- latest upstream `knowledge_at_utc` propagation;
- detection of information becoming available after a decision;
- deterministic provenance outputs.

These primitives support GRA01 and GRA02 only. Lead-lag, redundancy and state-transition graphs remain locked until point-in-time feature and decision ledgers exist.

## Implemented lineage contracts

`DecisionLineageRow` now enforces the four allowed classes:

- `FULL_POINT_IN_TIME`;
- `PARTIAL_POINT_IN_TIME`;
- `RETROSPECTIVE_RECONSTRUCTION`;
- `UNUSABLE_FOR_BT10`.

Only `FULL_POINT_IN_TIME` rows count as BT10-eligible.

`CounterfactualDeploymentRow` enforces:

`event knowledge <= decision <= execution < label end`

and requires positive prices, source hashes and an explicit regret sign.

## Synthetic red-team coverage

The tests include:

- deterministic bootstrap reproduction;
- invalid interval and quantile inputs;
- purge and embargo separation;
- multiple-testing monotonicity;
- graph-cycle rejection;
- result nodes without owner lineage;
- post-decision source information;
- incomplete point-in-time lineage;
- counterfactual temporal ordering.

## Explicit non-actions

```yaml
market_dataset_loaded: NO
sensor_effect_calculated: NO
effective_N_market_value_reported: NO
range_model_ranked: NO
counterfactual_policy_scored: NO
TDBC_specification_curve_run: NO
final_holdout_touched: NO
framework_state_change: NONE
portfolio_action: NONE
readiness_gate_G20: NO
```
