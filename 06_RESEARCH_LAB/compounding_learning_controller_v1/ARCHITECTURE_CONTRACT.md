# Compounding Learning Controller v1 — Architecture Contract

**Status:** `DESIGN_FROZEN_FOR_ASTRA_REVIEW`  
**Scope:** research-learning orchestration only.

## 1. Position in the framework

The controller sits **above** the existing experimental evidence stack and **below** any future governed framework-change process.

```text
observations / candidates
        ↓
Scientific Admission
        ↓
prospective execution + frozen forecasts
        ↓
outcome maturation
        ↓
Unified Experimental Adjudication
        ↓
COMPOUNDING LEARNING CONTROLLER
        ↓
learning state + uncertainty map + next-best-test proposal
        ↓
existing Scientific Admission for any newly proposed experiment
```

The final arrow is mandatory: the controller cannot bypass Scientific Admission.

## 2. Single responsibility

The controller's single responsibility is:

> Convert mature, already-adjudicated evidence into a durable learning state and a bounded proposal for the next highest-information prospective test.

It is not an adjudicator, market engine, portfolio engine, optimizer with direct authority, or autonomous promoter.

## 3. Required inputs

Use current canonical owners rather than copies. The exact final paths should be rebound by Astra against then-current main.

Expected input classes:

- latest Unified Experimental Lifecycle Adjudication output;
- Experiment Lifecycle Registry;
- Scientific Admission Registry;
- matured outcome memory / settlement-bound outcome evidence;
- relevant forecast calibration summaries;
- relevant Shadow / shared-row research context where already admitted by the adjudication layer;
- prior Compounding Learning state and proposal history.

The controller should prefer immutable IDs/hashes and stable semantic identities over prose matching.

## 4. Required outputs

At minimum, produce versioned machine-readable outputs equivalent to:

### `LEARNING_STATE_v1`
For each durable hypothesis/assumption family:

- semantic identity;
- current evidence status;
- supporting evidence references;
- contradicting evidence references;
- unresolved uncertainty;
- known regime dependence;
- redundancy/collinearity warning;
- complexity burden;
- confidence class expressed conservatively;
- last material evidence change;
- explicit `canonical_effect=false`.

### `LEARNING_EVENT_v1`
Append-only event produced only when evidence materially changes the learning state:

- previous state reference;
- new state reference;
- evidence delta;
- why the change is justified;
- what did **not** change;
- no retroactive mutation.

### `NEXT_BEST_TEST_PROPOSAL_v1`
Exactly a proposal, not execution permission:

- problem / uncertainty to reduce;
- hypothesis;
- explicit baseline;
- explicit falsifier;
- expected information gain;
- expected incremental value over current capability;
- required data lineage;
- target/horizon/regime;
- negative control(s);
- redundancy risk;
- complexity tax;
- false-positive / false-negative cost;
- revisit condition;
- proposed priority;
- reason competing tests were ranked lower;
- `requires_scientific_admission=true`;
- `automatic_execution=false`;
- `canonical_effect=false`;
- `portfolio_execution=false`.

### `LEARNING_BACKLOG_v1`
A durable ranked backlog of unresolved questions and proposed tests. Preserve rejected/deprioritized ideas with reasons instead of deleting them.

## 5. Ranking objective

The controller should optimize **learning value**, not raw experiment count or short-term hit rate.

Astra should design a transparent scoring function based on dimensions such as:

- expected uncertainty reduction;
- expected incremental value over current capability;
- decision relevance;
- observability / feasibility;
- prospective sample opportunity;
- independence from already-tested information;
- regime coverage;
- falsifiability strength;
- expected time-to-learning;
- complexity tax;
- data cost / runtime cost;
- false-positive and false-negative cost.

The score must remain auditable. If a model assists ranking, the deterministic feature surface and final bounded decision contract must remain inspectable.

## 6. Compounding behavior

The system should improve automatically through **state accumulation and better test selection**, not by unrestricted self-modification.

Desired loop:

1. ingest newly mature adjudicated evidence;
2. compare against previous learning state;
3. identify only material belief/uncertainty changes;
4. update the durable learning graph/state append-only;
5. detect the most decision-relevant unresolved uncertainty;
6. rank prospective tests that can discriminate between competing explanations;
7. issue one bounded next-best-test proposal plus backlog updates;
8. send any proposed new experiment back through normal Scientific Admission;
9. observe future outcomes;
10. repeat.

This is the intended source of compounding: each test should make the *next test better chosen*.

## 7. Anti-self-deception controls

The final design must explicitly defend against:

- confirmation loops where supported hypotheses generate only supportive follow-ups;
- outcome leakage into supposedly prospective design;
- repeated variants of the same semantic test;
- regime cherry-picking;
- survivorship of only interesting experiments;
- complexity creep;
- automatic confidence inflation;
- conflating data-quality failures with market falsification;
- conflating no-event periods with negative evidence;
- changing target/horizon after outcome visibility;
- using future calibration results to rewrite old frozen assumptions;
- proposing experiments merely to meet sample-size targets.

At least one adversarial or disconfirming candidate should be considered whenever a hypothesis is strengthened.

## 8. Autonomy boundary

Allowed autonomous actions after final approval:

- read admitted/mature research outputs;
- update research-only learning state;
- rank unresolved questions;
- write research-only next-test proposals;
- maintain append-only learning history;
- open or populate candidate material for the existing Scientific Admission path if that path already allows it.

Not allowed without a separate governed promotion path:

- change canonical framework logic;
- change market thresholds or model weights;
- change portfolio action;
- alter the scientific admission contract;
- alter old forecasts/outcomes/adjudications;
- execute a new experiment that has not passed the existing admission gate.

## 9. Scheduling principle

Do not create a high-frequency parallel automation by default.

Preferred design for Astra to evaluate:

- event-driven or weekly execution **after** Unified Experimental Adjudication;
- no-op when no material new mature evidence exists;
- idempotent rebuild of compact latest state plus append-only material-change events;
- bounded runtime and bounded proposal count.

The controller should wake because there is something new to learn from, not because the clock demands another experiment.

## 10. Discoverability requirement

The finished implementation must be visible to future agents through normal repository navigation and machine-readable handoff surfaces.

Astra should decide the smallest correct integration points, likely including:

- a canonical architecture reference under existing FMOS/agent-routing ownership;
- a research folder with `README` and contracts;
- workflow/gate path coverage;
- downstream handoff manifest inclusion;
- health/observability coverage;
- tests that fail if the controller becomes disconnected from Unified Adjudication or bypasses Scientific Admission.

Avoid a new parallel documentation hierarchy if an existing canonical owner can be extended cleanly.
