# Claude Top 5 backtest proposals — governance adjudication v1

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
source: CLAUDE_OPUS_5_MAX_PROPOSAL
status: ACCEPTED_AS_RESEARCH_CHALLENGE_SUITE
canonical_state_change: NONE
controlled_backtest_execution: LOCKED
```

## Executive decision

All five proposals are valuable and are admitted into the Backtest Build. None is accepted with Claude's readiness labels unchanged.

The proposals map closely to the existing architecture:

| Claude proposal | Existing framework tests | Governance decision |
|---|---|---|
| Counterfactual Deployment Ledger | BT05 + BT15 | ACCEPT, P1, blocked by event and decision-ledger completeness |
| Point-in-Time Replay with vintage macro | BT10 + GRA02 + GRA06 | ACCEPT, P0, highest governance value, currently blocked |
| Sensor independence and effective-N | BT11 + GRA03 | ACCEPT, P1, engineering may begin now |
| Range-skill decomposition and conformal replacement | BT14 | ACCEPT, P2, scoring engine may begin now; historical conclusion blocked by ledger depth |
| Specification curve and block bootstrap | BT08 robustness + new challenger layer | ACCEPT, P1, engineering may begin; economic claim remains blocked |

The main disagreement with Claude is the word `READY`.

A scaffold that can calculate rows is not the same as a scientifically ready test. Readiness also requires owner-data identity, point-in-time eligibility, complete event definitions, independent episode logic, frozen primary endpoints and a valid final holdout.

## 1. Counterfactual Deployment Ledger

### Decision

```yaml
challenge_id: CH01_COUNTERFACTUAL_DEPLOYMENT_LEDGER
priority: P1
status: ACCEPTED_BLOCKED
maps_to:
  - BT05_LAST_FLUSH_REBUY_DELAY
  - BT15_DEFENSE_VS_OPPORTUNITY_COST
```

### Why it matters

This is the clearest way to make invisible opportunity cost visible. It should record both the outcome of the framework's actual policy and the outcome of frozen alternatives.

### Required row contract

```yaml
event_id:
event_knowledge_at_utc:
policy_id:
decision_at_utc:
execution_at_utc:
entry_price:
exit_or_horizon_price:
realized_delta:
foregone_delta:
maximum_adverse_excursion:
maximum_favorable_excursion:
drawdown_avoided:
opportunity_cost:
regret_sign:
source_hashes:
```

### Frozen policy family

- actual framework policy;
- immediate deployment;
- delays of 1, 2, 3 and 5 settled sessions;
- 70/30 staged deployment;
- simple ATR-band comparator;
- buy-and-hold comparator where economically meaningful;
- confirmation-conditioned comparator.

### Blockers

- flush and de-escalation event definitions are not yet frozen;
- overlapping events are not yet deduplicated into independent episodes;
- historical framework decision coverage is incomplete;
- two of three known historical events lack complete `knowledge_at_utc` lineage.

Claude's `READY` is therefore changed to `ACCEPTED_BLOCKED`.

## 2. Point-in-Time Replay with vintage macro

### Decision

```yaml
challenge_id: CH02_POINT_IN_TIME_REPLAY
priority: P0
status: ACCEPTED_BLOCKED_LOAD_BEARING
maps_to:
  - BT10_MULTI_SENSOR_STATE_MACHINE_REPLAY
  - GRA02_TEMPORAL_DEPENDENCY_DAG
  - GRA06_STATE_TRANSITION_GRAPH
```

### Why it ranks first

This test can distinguish genuine historical decision quality from hindsight created by revised data, reconstructed states or missing decision timestamps.

### Required paired output

```yaml
timestamp:
state_point_in_time:
state_latest_vintage:
state_divergence:
decision_point_in_time:
decision_latest_vintage:
decision_would_differ:
first_divergent_input:
first_divergent_knowledge_at_utc:
```

### Important scope correction

ALFRED initial-release data solve only the macro-vintage component. They do not solve missing framework decision lineage, missing event timestamps, source substitutions, revised rule text or historical state reconstruction.

### Immediate action

Build a `DECISION_LINEAGE_REPAIR_LEDGER` that labels every historical framework row:

- `FULL_POINT_IN_TIME`;
- `PARTIAL_POINT_IN_TIME`;
- `RETROSPECTIVE_RECONSTRUCTION`;
- `UNUSABLE_FOR_BT10`.

Only `FULL_POINT_IN_TIME` rows may score the primary BT10 result.

## 3. Sensor independence and effective-N

### Decision

```yaml
challenge_id: CH03_SENSOR_INDEPENDENCE_EFFECTIVE_N
priority: P1
status: ACCEPTED_ENGINEERING_READY_ECONOMIC_LOCKED
maps_to:
  - BT11_SENSOR_ABLATION_AND_REDUNDANCY
  - GRA03_SENSOR_REDUNDANCY_GRAPH
```

### Preregistered definitions

No single decimal `effective-N` may be reported without its definition. The engine will report a vector:

```yaml
participation_ratio: (sum_eigenvalues ^ 2) / sum_squared_eigenvalues
entropy_effective_rank: exp(-sum(p_i * ln(p_i)))
frozen_cluster_count:
conditional_incremental_information_after_price:
walk_forward_stability:
```

### Required preprocessing

- use point-in-time aligned features only;
- transform non-stationary levels where needed;
- preserve missingness and report pairwise sample counts;
- do not blend Binance and OKX derivatives into one feature;
- calculate results by era and regime before pooling;
- condition on BTC return, ETH/BTC return and volatility before claiming incremental information.

### Expected use

This study may recommend simplification or identify genuinely independent veto layers. It cannot by itself promote or remove a canonical sensor.

## 4. Range-skill decomposition and conformal replacement

### Decision

```yaml
challenge_id: CH04_RANGE_SKILL_AND_CONFORMAL
priority: P2
status: ACCEPTED_SCORING_ENGINE_READY_LEDGER_BLOCKED
maps_to:
  - BT14_FORECAST_RANGE_CALIBRATION
```

### Required primary scorecard

For every frozen forecast interval:

- daily containment;
- first breach timestamp;
- total breach duration;
- interval width;
- Winkler interval score;
- lower and upper pinball loss;
- width-normalized skill;
- empirical coverage versus target coverage;
- conditional coverage by volatility regime.

### Frozen comparator family

- naive previous-range;
- ATR grid selected only inside training folds;
- EWMA volatility band;
- realized-volatility-scaled random walk;
- GARCH(1,1) challenger;
- split-conformal interval;
- rolling conformal interval;
- current Cycle Navigator interval.

### Governance correction

Conformal coverage is finite-sample marginal coverage under stated exchangeability conditions. It is not an unconditional guarantee in a changing market regime. Coverage, width and regime failure must all be reported.

### Blocker

The forecast ledger is not yet deep enough for a strong historical claim. The scoring implementation may be built and tested synthetically now.

## 5. Specification curve and block bootstrap

### Decision

```yaml
challenge_id: CH05_SPECIFICATION_CURVE_AND_BOOTSTRAP
priority: P1
status: ACCEPTED_ENGINEERING_READY_CLAIM_BLOCKED
maps_to:
  - BT08_BUSINESS_CYCLE_TURN
  - BT11_SENSOR_ABLATION_AND_REDUNDANCY
```

### TDBC specification axes

- MACD fast length;
- MACD slow length;
- signal length;
- January-February versus February-March anchoring;
- ratio construction and source pair;
- settlement timestamp;
- neutral-band treatment;
- current incomplete-bar exclusion;
- outcome horizon;
- BTC era segmentation.

The exact grid must be frozen before outcome execution. The final holdout cannot be used to choose a winning specification.

### Required outputs

```yaml
specification_id:
training_effect:
validation_effect:
holdout_effect:
sign_stability:
independent_event_count:
survives_predeclared_materiality:
multiple_testing_family:
```

### Small-n rule

For claims with seven or fewer independent events:

- descriptive estimates remain visible;
- block or event bootstrap uncertainty is mandatory;
- no asymptotic precision language;
- external-asset analysis is labelled mechanism robustness, not BTC sample enlargement;
- one event may not dominate the conclusion without leave-one-event-out disclosure.

### External assets

Gold, copper miners, NDX and emerging markets may test whether the phase relationship reflects a general risk-asset mechanism. They do not convert a BTC-specific claim into a larger BTC sample.

## Final priority order

```yaml
P0:
  - decision_lineage_repair
  - point_in_time_replay_contract
P1:
  - statistical_engine
  - sensor_independence_engineering
  - specification_curve_engineering
  - counterfactual_policy_schema
P2:
  - range_scoring_and_conformal_engineering
P3_AFTER_GATES:
  - economic_execution
  - blind_Claude_replication
  - final_holdout
```

## Current authority

```yaml
Claude_proposals_archived: YES
research_value: HIGH
canonical_test_result: NONE
parameter_change: NONE
framework_state_change: NONE
portfolio_action: NONE
readiness_gate_G20: NO
```
