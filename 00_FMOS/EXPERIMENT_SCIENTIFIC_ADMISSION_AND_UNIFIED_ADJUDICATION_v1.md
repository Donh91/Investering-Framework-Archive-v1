# Experiment Scientific Admission & Unified Adjudication v1

**Status:** RESEARCH_ONLY_NON_CANONICAL  
**Method reference:** `06_RESEARCH_LAB/protocols/README.md`  
**Admission rule:** `06_RESEARCH_LAB/protocols/SHADOW_IDEA_ADMISSION_RULE_v1.md`

## Purpose

Bind the existing Experiment Lifecycle & Execution Plane to the framework's current falsification-oriented research method without adding a new market-decision engine.

The architecture keeps broad idea generation, but increases admission friction before new prospective execution is allowed.

## Scientific admission before new forward execution

Every experiment candidate receives a separate immutable `EXPERIMENT_SCIENTIFIC_ADMISSION_v1` record.

The admission record freezes:

- the concrete problem to solve;
- semantic candidate identity;
- current capability overlap;
- explicit baseline;
- incremental-value claim;
- expected horizon / lead-lag role;
- success, failure and kill criteria;
- negative controls;
- point-in-time and temporal-leakage checks;
- redundancy and collinearity review;
- regime review;
- false-positive / false-negative cost review;
- complexity tax;
- authority ceiling.

Only `QUALIFIED_FOR_FORWARD_TEST` may create a new experimental forecast or cross-repository execution request.

Qualification is not promotion. A qualified candidate remains research-only and non-canonical.

## Historical candidate requalification

Existing candidates are preserved exactly as historical hypotheses.

The system adds a new admission record on top of the old candidate. It does not rewrite the candidate, alter old timestamps, rescore old outcomes or pretend the new admission contract existed at the historical freeze time.

Historical requalification therefore records:

- `historical_candidate_requalification=true`;
- `no_retroactive_rescore=true`.

Only observations after the new admission may create newly admitted forward execution.

## Semantic deduplication

The original lifecycle candidate identity remains immutable for continuity.

Scientific admission additionally computes a semantic fingerprint from canonical metric identity, component operators and thresholds, target, horizon and regime dependency.

Known wrapper aliases such as `latest_capture.market_metrics.*`, `market_metrics.*` and equivalent canonical metric paths are normalized before the scientific fingerprint is calculated.

A later candidate with the same scientific fingerprint is retained for audit history but becomes `SEMANTIC_DUPLICATE_KEEP_SHADOW` and does not receive new forward-execution budget.

## Frozen controls

New admitted forecasts preserve the existing controls and bind the admission record:

- always-wait control;
- strongest/single-component control surface;
- deterministic placebo direction;
- control freeze timestamp;
- admission-record hash;
- semantic fingerprint;
- required future redundancy, negative-control, regime, lead-lag and false-cost reviews.

## Unified weekly adjudication

The weekly `Unified Experimental Lifecycle Adjudication` runs Monday at 09:05 Europe/Copenhagen after the existing Shadow Registry and Shared Row research jobs.

It reads:

- `research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json`;
- `research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json`;
- `04_MARKET_LEARNING/shadow_registry/LATEST.json` when available;
- `06_RESEARCH_LAB/shared_row_model_tournament_v1/weekly/LATEST.json` when available.

The output is research-only and may route candidates to:

- wait for mapping;
- wait for more prospective evidence;
- archive duplicate;
- keep quarantined;
- keep shadow inconclusive;
- incremental-value and adversarial review;
- failure and retirement review;
- continue observing.

It cannot promote a market rule, alter thresholds or weights, change framework state or create portfolio execution.

## Post-adjudication Compounding Learning Controller v1

The `Compounding Learning Controller` runs only after the current Unified Experimental Lifecycle Adjudication has been persisted.

Its ownership boundary is explicit:

- **Unified Experimental Adjudication owns:** what the mature evidence says and which lifecycle action is justified.
- **Compounding Learning owns:** what was learned across semantic experiment families, what uncertainty remains, and which single prospective child test is most information-rich next.

The controller must not re-adjudicate a candidate. If the lifecycle registry, Scientific Admission registry and adjudication output have drifted out of alignment, the controller fails closed to `WAIT_FOR_REFRESHED_UNIFIED_ADJUDICATION` rather than interpreting the evidence itself.

The controller maintains these research-only products under `00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/`:

- `STATE.json`, current machine-readable `LEARNING_STATE_v1`;
- `events/LE-*.json`, append-only `LEARNING_EVENT_v1` records for material changes in mature adjudicated evidence;
- `NEXT_BEST_EXPERIMENT.json`, one bounded `NEXT_BEST_TEST_PROPOSAL_v1`;
- `LEARNING_BACKLOG.json`, persistent ranked unresolved questions and deprioritized proposals.

Every next-test proposal must expose at least:

- unresolved uncertainty;
- hypothesis;
- frozen baseline;
- explicit falsifier;
- what evidence would change the current view;
- transparent information-value ranking components;
- negative controls;
- lineage requirement;
- redundancy and complexity burden;
- false-positive / false-negative costs to freeze during Scientific Admission;
- revisit condition.

The information-value score is an auditable ranking heuristic, not a probability, forecast skill estimate or promotion score.

### Descriptive checkpoints

Every learning profile uses the common descriptive checkpoint surface:

`7 / 14 / 30 / 60 / 90 / 120 / 180 / 240 days`.

These checkpoints may summarize accrual health, data quality, concentration, maturation readiness and already-adjudicated evidence. They do not create interim scientific verdicts by themselves.

For confirmatory studies the firewall is stricter: checkpoint execution may not infer interim performance, change the scientific method, create an automatic child experiment, inspect future outcome evidence for skill inference or alter the final confirmatory test contract.

### Materiality and append-only learning

A new raw observation count is not a learning event by itself.

`LEARNING_EVENT_v1` is emitted only when mature, already-adjudicated evidence materially changes a semantic family's evidence signature or adjudicated status. Previous material events remain immutable. A failed or contradictory result is retained rather than silently removed.

### Next-test boundary

A proposed child test is never execution permission.

Every proposed child must re-enter the existing Scientific Admission path and may execute prospectively only if admitted under that owner. The controller cannot mutate the frozen parent, create retrospective prospective evidence, run automatic parameter search, promote a market rule, alter a threshold or weight, change canonical framework state or create portfolio execution.

The operational health contract is produced at `research/architecture_health/LATEST_COMPOUNDING_LEARNING_HEALTH.json`. Future agents discover the current experiment-learning stack through `research/framework_handoffs/LATEST_FRAMEWORK_HANDOFF_MANIFEST.json`, whose experiment-learning read order is:

1. Experiment Lifecycle Registry;
2. Scientific Admission Registry;
3. Unified Experimental Adjudication;
4. Compounding Learning State;
5. Next Best Test Proposal;
6. Learning Backlog;
7. Compounding Learning Health.

## Retirement principle

Age alone is not a kill criterion.

A candidate may remain dormant when the relevant regime or eligible event has not occurred. Retirement requires evidence-aware reasoning such as persistent redundancy, failed prospective comparison, leakage/hindsight dependence, unacceptable false-cost, unmappable lineage or complexity exceeding measured value.

## Relationship to PR #539

PR #539 remains a useful hostile-qualification case study for isolated agent/tool testing.

The canonical method reference for this market-sensor lifecycle is the generalized experimental method guide merged through PR #541. The market lifecycle adapts that method to point-in-time data, temporal leakage, collinearity, regime dependence, prospective evidence and false-positive / false-negative cost.
