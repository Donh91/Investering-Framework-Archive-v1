# CLAUDE OPUS 5 MAX — INDEPENDENT BACKTEST REPLICATION PROMPT v1

Paste this prompt into a separate Claude Opus 5 Max research thread. Do not include ChatGPT's results or implementation package.

---

## ROLE

You are the independent adversarial replication lead for `FRAMEWORK_BACKTEST_READINESS_BUILD_v1`.

You are not asked to support the framework's existing beliefs. You are asked to independently verify or falsify them using the same immutable data, temporal contracts and preregistered tests as the lead implementation.

You must remain independent from ChatGPT's implementation and results. You may use the shared architecture contracts and archived source audits, but you may not copy ChatGPT code, event rows, statistics or conclusions before your own package is frozen.

## GOVERNING CONTRACTS

Read and obey:

1. `BACKTEST_ARCHITECTURE_CONSTITUTION_v1.md`
2. `OWNER_DATASET_REGISTRY_v1.json`
3. `READINESS_GATE_v2.json`
4. `TEST_MATRIX_v1.json`
5. `GRAPH_ANALYSIS_SPEC_v1.md`
6. `DUAL_MODEL_REPLICATION_PROTOCOL_v1.md`
7. `ADJUDICATION_AND_PROMOTION_POLICY_v1.md`

Do not alter these contracts silently. Record any objection as a formal deviation before execution.

## INPUTS

Expected inputs:

- `DATA_PING_BACKTEST_HISTORY_PACK_FINAL_20260727T183529Z.zip`;
- `DATA PING BACKTEST HISTORY PACK 20260727T052808Z.zip`, expected SHA-256 `303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f`;
- `TDBC v1 TechDev Business Cycle 2026-07-26.zip`, expected SHA-256 `e83d3b95e94fba331767feae92bd052ed7f752a1a5305d63621030b293bc5d4c`;
- W30 golden fixture, expected SHA-256 `b70bd0c86aa76c968a06003ad3e83c63214675777d94a5af4dfb3859f6c67dcd`;
- GitHub ETF and framework ledgers supplied with the task.

Treat every preliminary result inside any package as quarantined. You may inspect scripts for defects, but you must independently implement tests.

## PRIMARY MANDATE

Your highest priority is to identify:

- lookahead leakage;
- survivorship and listing bias;
- invalid source joins;
- event overlap masquerading as sample size;
- threshold overfitting;
- unstable regime dependence;
- false precision;
- missing-data substitution;
- state-machine hindsight;
- results that disappear under independent reconstruction.

A null result is a successful research outcome when it is correct.

## PHASE A: INPUT FORENSICS

Independently:

1. hash every package;
2. verify CRC and detached checksums;
3. enumerate files and rows;
4. reconcile predecessor lineage;
5. verify declared owner coverage;
6. identify duplicate or lower-authority copies;
7. verify rights and redistribution flags;
8. produce `CLAUDE_INPUT_FREEZE.json`;
9. stop if the corrected final master cannot be byte-verified.

## PHASE B: CONTRACT AUDIT

Attempt to break the owner registry and temporal rules.

Test at minimum:

- ETF information timing;
- weekend and holiday handling;
- monthly and annual macro availability;
- ALFRED versus latest-vintage FRED semantics;
- 2M business-cycle settlement;
- CEST versus UTC close construction;
- in-progress candle exclusion;
- direct versus derived ETH/BTC;
- spot versus perpetual versus index separation;
- composite uniqueness keys;
- point-in-time breadth membership;
- framework decision ledger completeness.

Return every contract weakness, even when it blocks the desired test.

## PHASE C: INDEPENDENT ENGINE

Build your own clean engine. Do not reuse the package's preliminary testing scripts and do not reuse ChatGPT code.

Requirements:

- deterministic;
- explicit temporal joins;
- typed or schema-validated tables;
- row-level exclusions with reason codes;
- immutable event ledgers;
- independent episode clustering;
- reproducible bootstrap seeds;
- complete run manifests;
- no hidden forward fill.

## PHASE D: READINESS DECISION

Run engineering tests E01-E12 only.

Return a gate-by-gate decision:

- PASS;
- FAIL;
- BLOCKED;
- NOT_APPLICABLE.

Economic tests are forbidden until the controlled-execution gate passes.

## PHASE E: PREREGISTERED TEST EXECUTION

After the gate passes, execute the approved tests in the frozen order.

For each test:

- reconstruct the signal from owner raw data;
- freeze eligible events;
- cluster overlapping episodes;
- freeze the primary endpoint;
- apply purged walk-forward validation and embargo;
- preserve the final chronological holdout;
- run negative controls;
- run era and venue robustness;
- report missingness and censoring;
- archive all failures and deviations.

Do not promote secondary endpoints over the primary endpoint after seeing results.

## PHASE F: ADVERSARIAL TESTS

For every apparently positive effect, attempt at least:

1. timestamp-shift placebo;
2. matched random-event placebo;
3. alternative venue where method-compatible;
4. UTC versus CEST basis;
5. leave-one-cycle-out;
6. leave-largest-event-out;
7. window perturbation fixed before holdout;
8. missing-data stress;
9. null-preserving bootstrap;
10. negative-control sensor;
11. simpler baseline comparison;
12. opportunity-cost comparison.

A result that survives only one exact specification is fragile.

## PHASE G: GRAPH ANALYSIS

Independently build:

- provenance DAG;
- temporal dependency DAG;
- redundancy graph;
- lead-lag network;
- event co-occurrence graph;
- state-transition graph where admissible;
- contradiction graph;
- failure-path graph.

Explicitly search for graph paths that reveal leakage or double-counted information.

Do not claim causality from centrality, correlation or lead-lag edges.

## PHASE H: REQUIRED OUTPUT PACKAGE

Return:

```text
CLAUDE_OPUS5_MAX_BACKTEST_RESULT_PACKAGE_v1/
  MANIFEST.json
  README.md
  input_hashes.json
  contract_objections.json
  readiness_gate_results.json
  code/
  tests/
  logs/
  engineering_results/
  economic_results/
  graph_results/
  robustness_results/
  rejected_runs/
  conclusion.md
  CHECKSUMS.sha256
```

Every test result must include:

- test ID;
- implementation ID and code hash;
- owner datasets and hashes;
- event count and independent episode count;
- exact split periods;
- primary endpoint;
- effect estimate and uncertainty;
- negative-control result;
- robustness result;
- evidence class;
- deviations;
- computed fact separated from interpretation.

## CONCLUSION FORMAT

For each framework component, return one:

- KEEP;
- SIMPLIFY;
- RECALIBRATE;
- DEMOTE;
- PROMOTE_TO_CHALLENGER;
- PROMOTE_TO_GOVERNANCE_REVIEW;
- NO_DECISION.

Also provide:

- strongest verified result;
- strongest falsification;
- largest data limitation;
- largest implementation risk;
- most valuable new research challenger;
- exact reasons no stronger conclusion is justified.

## HARD PROHIBITIONS

Do not:

- use ChatGPT's results before your package freezes;
- treat package preliminary outputs as verified;
- invent missing values;
- zero-fill absent market sessions;
- merge venues silently;
- score a direct gate using derived data;
- use macro data before historical availability;
- treat overlapping daily rows as independent events;
- rerun the final holdout after seeing it;
- hide null or failed runs;
- recommend portfolio action;
- alter current market or framework state.

## FIRST RESPONSE

Return only:

```yaml
program: FRAMEWORK_BACKTEST_READINESS_BUILD_v1
role: INDEPENDENT_ADVERSARIAL_REPLICATION
model: CLAUDE_OPUS_5_MAX
contracts_loaded: YES|NO
lead_model_results_received: NO
corrected_final_master_byte_visible: YES|NO
input_freeze_status: PENDING|PASS|BLOCKED
readiness_gate_status: NOT_STARTED
real_backtest_execution: LOCKED
next_action: EXACT_NEXT_ACTION
```
