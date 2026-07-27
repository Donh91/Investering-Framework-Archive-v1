# BACKTEST BUILD — Next Execution Plan v2

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
phase: STATISTICS_GRAPH_AND_LINEAGE_FOUNDATION
status: ACTIVE_ENGINEERING_ONLY
controlled_backtest_execution: LOCKED
```

## Workstream A — Decision lineage repair, P0

Create a row-producing `DECISION_LINEAGE_REPAIR_LEDGER` for every archived framework event, forecast and action-permission decision.

Required fields:

```yaml
record_id:
record_type:
event_time_utc:
knowledge_at_utc:
decision_at_utc:
rule_version:
input_artifact_ids:
input_hashes:
state_before:
state_after:
action_permission:
lineage_class:
exclusion_reason:
```

Allowed lineage classes:

- `FULL_POINT_IN_TIME`;
- `PARTIAL_POINT_IN_TIME`;
- `RETROSPECTIVE_RECONSTRUCTION`;
- `UNUSABLE_FOR_BT10`.

No inferred timestamp is silently promoted to exact lineage.

## Workstream B — Statistical engine, P1

Implement and validate on synthetic fixtures:

- event clustering;
- moving-block bootstrap;
- stationary bootstrap;
- purged expanding walk-forward splits;
- embargo enforcement;
- Benjamini-Hochberg false-discovery control;
- interval score;
- pinball loss;
- coverage and width metrics;
- participation ratio;
- entropy effective rank;
- leave-one-event-out summaries;
- deterministic random seeds and output hashes.

No market result is produced in this workstream.

## Workstream C — Metadata graph engine, P1

Implement first:

1. provenance DAG validation;
2. cycle detection;
3. source-to-conclusion path completeness;
4. temporal dependency propagation;
5. latest-upstream-knowledge calculation;
6. forbidden post-decision input detection;
7. deterministic node and edge exports.

These correspond to GRA01 and GRA02 and may run before the economic gate because they inspect lineage and timing, not performance.

## Workstream D — Challenger preregistration, P1–P2

Freeze exact contracts for:

- counterfactual deployment policies;
- effective-N vector;
- range interval score and comparator family;
- TDBC specification surface;
- small-n bootstrap and leave-one-event-out reporting.

## Workstream E — Final master byte gate, load-bearing

The exact binary `DATA_PING_BACKTEST_HISTORY_PACK_FINAL_20260727T183529Z.zip` must become byte-visible.

Required pass evidence:

- byte count;
- SHA-256;
- ZIP CRC;
- actual member count;
- detached final checksums;
- predecessor checksums;
- owner-dataset paths;
- source-to-normalized rebuild entry points.

No summary document can substitute for this gate.

## Workstream F — Controlled execution release

Only after the preceding workstreams and readiness gates pass:

1. freeze exact input hashes;
2. freeze primary endpoints and splits;
3. freeze ChatGPT implementation hash;
4. freeze Claude independent prompt and inputs;
5. run first economic wave;
6. freeze both result packages;
7. reconcile row and result parity;
8. run falsifiers;
9. run final holdout once;
10. submit recommendations to governance.

## First economic wave, when authorized

The initial economic wave remains:

1. BT01 ETF flow persistence;
2. BT02 ETF flow reversal;
3. BT09 weekend to next ETF session;
4. BT04 direct ETH/BTC 0.0300 gate;
5. BT03 early transmission;
6. BT07 breadth confirmation.

Claude's Challenge Suite does not replace this wave. It expands the meta, policy and robustness layers around it.

## Current authority

```yaml
statistics_engine: BUILD_NOW
graph_metadata_engine: BUILD_NOW
decision_lineage_repair: START_NOW
range_scoring_engine: BUILD_NOW_SYNTHETIC_ONLY
counterfactual_policy_rows: SCHEMA_NOW_EXECUTION_LATER
specification_curve_engine: BUILD_NOW_EXECUTION_LATER
economic_results: NONE
readiness_gate_G20: NO
framework_state_change: NONE
portfolio_action: NONE
```
