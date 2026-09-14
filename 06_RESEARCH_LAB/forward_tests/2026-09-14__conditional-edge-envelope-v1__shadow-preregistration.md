# Conditional Edge Envelope v1 — Shadow Preregistration

**Dato:** 2026-09-14  
**Status:** SHADOW_ONLY  
**Lifecycle state:** SHADOW_CANDIDATE / PREREGISTRATION_STAGE_A / NO_EXECUTION  
**Område:** Research Lab / conditional base rates / statistical falsification  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `06_RESEARCH_LAB/audit_summaries/2026-09-14__luxalgo-mechanism-qualification-v1__shadow.md`, `06_RESEARCH_LAB/protocols/SHADOW_IDEA_ADMISSION_RULE_v1.md`, `06_RESEARCH_LAB/protocols/README.md`, `research/experiment_lifecycle/RESEARCH_EXECUTION_TOPOLOGY_v1.json`, `research/experiment_lifecycle/SEQUENTIAL_RESEARCH_QUEUE_v1.json`  
**Framework base SHA:** `5c3087f78192a5332ca56fe7ac4bd43a065a7ae1`  
**External prior-art binding:** `LuxAlgo/edge-stats@7cfa6d52f561e2c764ba900252e80356b03af9fe`

## 1. Candidate identity

**Candidate name:** `CONDITIONAL_EDGE_ENVELOPE_v1`  
**Candidate type:** research-evaluation mechanism, not a market sensor  
**Default lifecycle state:** `SHADOW_CANDIDATE`  
**Authority ceiling:** `RESEARCH_ONLY_NON_CANONICAL`  
**Execution status:** `FORBIDDEN_UNTIL_STAGE_B_MAPPING_AND_EXISTING_EXPERIMENT_SLOT_GATES_PASS`

This file is a preregistration design artifact. It is deliberately NOT placed in `research/experiment_lifecycle/candidates/` because the current lifecycle writer may automatically create observations, dispatch requests and frozen forecasts for executable candidates. Stage A must not create that side effect.

## 2. Problem to solve

The framework contains many falsification, forecast, sequence and regime mechanisms, but a historical claim can still be misleading when presented without a uniform denominator, unconditional base rate, sample-size uncertainty, temporal stability and trial-count context.

The candidate asks:

> Does a mandatory conditional-frequency envelope make existing framework research measurably more honest or decision-useful than the current evaluation surfaces, after accounting for overfitting, complexity and maintenance cost?

The candidate is not authorized to discover a new indicator by brute-force mining.

## 3. Frozen proposition and null

### Proposition

For predeclared framework questions, reporting `P(outcome | frozen conditions)` together with unconditional baseline, eligible N, Wilson 95% confidence interval, temporal/regime stability, held-out result and durable trial count will expose incremental information or useful falsification that the current baseline evaluation does not expose as clearly.

### Null hypothesis

The envelope provides no material incremental information, merely repackages existing framework evidence, or encourages combinatorial mining whose false-discovery and complexity cost exceeds its value.

## 4. Non-interference and data firewall

Stage A and all later Q1 work MUST NOT:

- change current market rules, thresholds, weights, regime labels or outcome labels;
- change Master Monday, Cycle Navigator, public output or portfolio semantics;
- alter `SEQUENTIAL_RESEARCH_QUEUE_v1` ordering;
- consume an experiment-execution slot before legitimate admission;
- use Round 3 restricted provider values while the analysis gate is closed;
- use prospective collection rows as historical discovery data;
- reopen or rescore closed Round 1 / Round 2 evidence contrary to current governance;
- silently substitute a public proxy for restricted evidence;
- tune conditions after seeing holdout outcomes;
- generate broker or execution authority;
- create new paid calls.

Eligible Stage B input is limited to point-in-time reconstructable closed historical evidence whose use is permitted by current source/storage/license governance, plus provider-value-free metadata needed to prove that eligibility.

## 5. Two-stage preregistration

### Stage A — this file

Freeze:

- candidate purpose and authority;
- baseline family;
- ten question classes;
- statistical output contract;
- anti-p-hacking rules;
- success/failure/kill criteria;
- mapping requirements;
- complexity tax;
- execution ordering.

Stage A MUST NOT inspect outcome-linked results for the ten questions.

### Stage B — required before any outcome query

For each question, bind:

- exact owner path(s);
- exact immutable data snapshot / commit / receipt binding;
- exact metric path(s) and units;
- availability timestamp semantics;
- exact eligibility denominator;
- exact condition definition;
- exact lookback interval;
- exact outcome definition;
- exact horizon;
- missing-data behavior;
- overlap/dependency rules;
- holdout boundary;
- regime split definition;
- number of confirmatory queries consumed.

If any of those cannot be frozen without looking at target outcomes, that question is `MAPPING_BLOCKED` and is not replaced with a nearby convenient variant during the same experiment.

## 6. Frozen ten question classes

These classes are frozen before metric mapping. Stage B may map them to existing canonical/historical owners but may not replace them based on which mappings produce attractive results.

| ID | Question class | Intended outcome family | Why included |
|---|---|---|---|
| CEE-Q01 | Rotation survival | persistence vs failure of an already-defined rotation state over a fixed forward horizon | tests whether joint rotation evidence adds conditional information beyond unconditional survival |
| CEE-Q02 | Rotation failure / reversion | failure or reversion after an already-defined rotation attempt | captures false-positive cost, not only successful rotations |
| CEE-Q03 | Pullback recovery | recovery after an already-defined stress/pullback state | tests recovery base rates instead of narrative reconstruction |
| CEE-Q04 | Drawdown escalation | deeper adverse move after an already-defined risk/stress state | tests defensive warning value and false-negative cost |
| CEE-Q05 | Reclaim durability | persistence after an already-defined reclaim/recovery condition | distinguishes transient reclaim from durable recovery |
| CEE-Q06 | Relative-strength persistence | persistence of an already-defined ETH/BTC or alt-relative-strength state | tests whether rotation leadership survives beyond the initial observation |
| CEE-Q07 | Breadth persistence | continuation vs collapse after an already-defined breadth expansion | tests whether breadth provides independent survival information |
| CEE-Q08 | Flow / price transmission | whether an already-defined flow state is followed by the predeclared price/relative outcome | complements, but must not duplicate, existing ETF transmission research |
| CEE-Q09 | Macro-to-crypto transmission | whether an already-defined macro stress/easing condition changes a predeclared crypto outcome rate | tests conditional transmission without creating a new macro sensor |
| CEE-Q10 | Exit opportunity cost | damage avoided vs missed upside / false-exit cost under an already-defined defensive condition | forces action-value accounting instead of hit-rate-only evaluation |

### Duplicate gate

If a question is already fully answered by an active or closed current owner using materially equivalent denominator, conditioning, outcome, horizon and uncertainty treatment, classify it `DUPLICATE_OWNER` and count that as a valid null finding. Do not invent a substitute question to maintain a ten-question sample.

## 7. Baselines and controls

Every mapped confirmatory question must include, where logically applicable:

1. **Unconditional base rate** — same outcome and eligibility without the candidate condition.
2. **Current-framework baseline** — current owner/evaluator output without the conditional envelope.
3. **Best single-condition control** — for multi-condition claims, compare against the strongest predeclared single component without selecting it from the holdout.
4. **Deterministic placebo** — time-shifted or otherwise causally implausible control frozen before outcome evaluation.
5. **Always-wait / no-action control** — only for decision/action questions where applicable.

Controls are evaluation references, not new market signals.

## 8. Statistical output contract

No confirmatory result may be emitted as a bare percentage.

Each question must report at minimum:

```text
question_id
mapping_status
eligibility_definition
condition_definition
outcome_definition
horizon
source_binding
N_conditioned
successes_conditioned
conditioned_rate
wilson_95_ci
N_unconditional
successes_unconditional
unconditional_rate
absolute_lift
relative_lift
best_single_condition_control
placebo_result
early_period_result
late_period_result
regime_breakdown
holdout_result
trial_count_used
multiple_testing_status
false_positive_cost
false_negative_cost
complexity_notes
verdict
```

Allowed per-question verdicts:

`REPLICATED | FRAGILE | NO_EDGE | FALSIFIED | INSUFFICIENT_N | MAPPING_BLOCKED | DUPLICATE_OWNER | DATA_BLOCKED`

## 9. Sample-size and uncertainty rules

Stage B must freeze minimum-N handling before outcomes are queried.

Default design preference, subject to exact Stage B mapping:

- always expose N and Wilson 95% CI;
- do not call a wide interval "edge";
- withhold confirmatory edge language where sample size is too small for a useful interval;
- preserve counts even when the estimate is withheld;
- do not pool materially different regimes merely to increase N;
- do not manufacture independence from overlapping event windows.

No fixed N threshold is invented in Stage A because eligible event frequency differs by question class. Stage B must justify each minimum using the event structure before outcome inspection.

## 10. Anti-p-hacking and multiplicity firewall

### Confirmatory budget

Exactly the mapped subset of CEE-Q01..Q10 may be confirmatory. Questions classified `MAPPING_BLOCKED`, `DUPLICATE_OWNER` or `DATA_BLOCKED` remain in the ledger and are not replaced.

Stage B must record one durable trial number for every confirmatory condition/outcome query attempted, including failed or null queries.

### No combinatorial search

Forbidden inside the confirmatory experiment:

- searching many thresholds and retaining the best;
- varying horizons until significance appears;
- trying many condition subsets and reporting the winner;
- changing eligibility after seeing failures;
- excluding inconvenient regimes post hoc;
- hiding null/negative results;
- treating exploratory discoveries as confirmatory.

### Exploratory escape hatch

A new pattern discovered during analysis may be recorded only as a NEW shadow candidate with a new frozen identity and future validation. It contributes zero confirmatory evidence to CEE-v1.

### Multiple-testing status

Stage B must predeclare the correction/reporting method appropriate to the final number of confirmatory questions. Uncorrected exploratory p-values, if any are produced, cannot determine promotion.

## 11. Holdout and temporal stability

For every question with sufficient history:

- hypothesis/mapping period and untouched holdout must be separated chronologically;
- early vs late period comparison is mandatory;
- regime stratification is required where an existing framework regime owner can be bound point-in-time;
- availability lag must be respected;
- revised/backfilled information unavailable at decision time is forbidden;
- forward horizon overlap must be identified and handled so nominal N is not presented as independent N when it is not.

If a valid untouched holdout cannot be constructed, the result ceiling is `HISTORICAL_HYPOTHESIS_ONLY` and cannot establish predictive edge.

## 12. Success criteria

The mechanism qualifies as useful only if the complete experiment shows at least one of the following without violating the anti-overfit firewall:

- exposes a reproducible incremental conditional relationship that survives baseline, placebo, temporal and holdout tests and is decision-relevant;
- falsifies an existing assumed relationship in a way that materially improves future research or prevents an avoidable framework error;
- detects an important uncertainty/sample-size/stability failure that current evaluation surfaces routinely obscure;
- enables a simpler evaluation standard that can replace duplicated bespoke statistical reporting.

Any surviving benefit must remain worthwhile after complexity tax.

## 13. Failure and kill criteria

Kill or archive the candidate if any of these dominate:

- no material information beyond unconditional/current-framework baselines;
- placebo/time-shift controls reproduce the apparent edge;
- holdout or late-period result materially contradicts the discovery-period result;
- apparent value is driven by hindsight labels, revised data or temporal leakage;
- most question classes are unmappable without inventing new semantics;
- multiplicity makes the evidence non-credible;
- the same benefit already exists in current owners;
- operational complexity or maintenance burden exceeds measured value;
- the candidate encourages free-form mining more than it improves falsification discipline.

A null result is terminal learning, not permission to retune CEE-v1 until it passes.

## 14. Complexity tax

Measure before any promotion proposal:

- new code/files required;
- runtime dependency count;
- compute and wall time;
- storage footprint;
- maintenance/version churn;
- statistical-method maintenance;
- provenance burden;
- source fragility;
- security/privacy exposure;
- licensing implications;
- agent/tool coordination burden;
- false-discovery governance burden;
- rollback difficulty.

Preferred implementation if value is proven: synthesize the smallest useful statistical-envelope logic into an existing Research Lab/evaluation owner rather than installing the full LuxAlgo stack.

## 15. Selected adversarial checks

Required for Stage B/execution:

- `POINT_IN_TIME_AVAILABILITY`
- `TEMPORAL_LEAKAGE`
- `HOLDOUT_INTEGRITY`
- `EVENT_WINDOW_OVERLAP`
- `REDUNDANCY_COLLINEARITY`
- `REGIME_STRATIFICATION`
- `NEGATIVE_CONTROL_PLACEBO`
- `MULTIPLE_TESTING_TRIAL_LEDGER`
- `FALSE_POSITIVE_FALSE_NEGATIVE_COST`
- `DATA_SOURCE_AND_LICENSE_ELIGIBILITY`
- `ROUND3_FIREWALL`

## 16. Stage B mapping gate

Before any outcome query, produce a deterministic mapping manifest with one row for CEE-Q01..Q10 and these fields:

```text
question_id
status
owner_path
source_dataset_id_or_binding
source_commit_or_snapshot
metric_paths
units
availability_semantics
eligibility
conditions
lookback
outcome
horizon
missingness_rule
overlap_rule
holdout_boundary
regime_split
minimum_N_rule
confirmatory_trial_number
```

The mapping manifest must be reviewed for leakage and current-owner duplication before the candidate enters executable lifecycle state.

## 17. Lifecycle and queue rule

This Stage A preregistration does NOT create an `EXPERIMENT_CANDIDATE_v1`, active-test-registry entry, observation, forecast, dispatch request or queue mutation.

Only after Stage B mapping passes may the existing lifecycle be asked to admit a bounded executable candidate. Admission must respect the current single experiment-execution slot and existing queue ordering.

`PDLT -> SPAR -> SPAR-FRAGILITY -> ETF-ABSORPTION-TRANSMISSION` remains untouched unless independent current governance changes it.

## 18. Promotion ceiling

Even a successful historical/held-out CEE experiment does not by itself create a market rule.

Possible next states after evidence:

- `ARCHIVE_ONLY`
- `SHADOW_TESTING`
- `FORWARD_TEST`
- bounded `OPERATIONAL_HELPER` for statistical reporting only
- stronger governance review if a market-semantic change is ever proposed

Automatic portfolio execution authority is permanently outside this candidate's scope.

## 19. Stage A completion test

Stage A is complete when:

- this artifact is merged and read back from `main`;
- the ten question classes remain frozen;
- no target outcomes have been inspected for those mappings;
- no executable lifecycle candidate was created;
- the experiment queue is unchanged;
- Stage B cannot start without exact data/metric mapping and anti-leakage review.

## 20. Next bounded action

Perform Stage B **mapping only** against existing current owner files and eligible closed historical evidence. Stop before outcome-linked queries. If exact point-in-time mapping cannot be established for a question without inspecting the target outcome, mark it blocked rather than improvising a replacement.
