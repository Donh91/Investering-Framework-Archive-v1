# Compounding Learning Controller v1

**Status:** ACTIVE RESEARCH ARCHITECTURE  
**Authority:** RESEARCH_ONLY_NON_CANONICAL  
**Owner surface:** `research/experiment_lifecycle/compounding_learning/`  
**Execution owner:** existing `Framework Learning Operations` workflow  
**Governance consumer:** existing Autonomous Research Governance chain

## Purpose

The controller closes one repeated gap in the framework:

```text
mature prospective evidence
-> explicit learning checkpoint
-> normalized learning verdict
-> next-best research step
-> novelty / decision-impact / adversarial review
-> new prospective test only when existing scientific admission permits it
```

It does **not** create a new experiment engine, scorer, market model or portfolio authority. The existing Experiment Lifecycle, Scientific Admission, Unified Experimental Adjudication, Prospective Evidence Ledger, Research Governance, Experiment Execution Plane and canonical framework owners keep their current authority.

The long-run learning loop is:

```text
OBSERVE -> FREEZE -> TEST -> MATURE -> LEARN -> CHALLENGE -> RETEST -> IMPROVE
```

The compounding property is that a mature result can create a bounded, traceable proposal for the next uncertainty to test without rewriting the parent experiment.

## Mandatory owner separation

```text
Experiment Lifecycle        = what exists and what matured
Scientific Admission        = whether a hypothesis is valid for forward testing
Unified Adjudication        = what a mature experimental result currently means
Compounding Learning        = when to revisit learning and what bounded research step should come next
Novelty / VOI               = whether that next step is new and decision-relevant
Adversarial Sentinel        = whether escalation is safe
Meta Orchestrator           = which bounded research work gets priority
Canonical Governance        = the only route to live framework change
```

No layer may silently absorb another layer's authority.

## Production order

The controller reuses existing writers and schedules. No new recurring workflow is introduced.

```text
Framework Learning Operations
-> sync experiment receipts
-> mature outcomes
-> rebuild LATEST_EXPERIMENT_REGISTRY
-> run Compounding Learning Controller
-> persist research/experiment_lifecycle/compounding_learning/LATEST.json
-> persist NEXT_BEST_EXPERIMENT.json

later the same day:
Autonomous Research Governance
-> memory / novelty
-> decision-impact / VOI
-> adversarial sentinel
-> meta-orchestrator
```

This provides time separation and an authority firewall without a one-day delay or a new source of truth.

## Multi-speed learning profiles

Profiles define **review cadence only**. They do not change the scientific method, outcome definition, baseline or frozen hypothesis.

- `FAST`: horizons up to 7 days. Default checkpoints 7/14/30 calendar days and 3/5/10 matured outcomes, then recurring bounded reviews.
- `MEDIUM`: horizons up to 30 days. Default checkpoints 30/60/90 days and 5/10/20 matured outcomes.
- `LONG`: longer horizons. Default checkpoints 60/120/180/240 days and 5/10/25/50 matured outcomes.
- `CONFIRMATORY`: operational health / coverage checkpoints only. Interim performance inference is forbidden unless the specific confirmatory owner explicitly defines an anytime-valid method.

Calendar time and matured-outcome counts are separate axes. Crossing either may create a learning checkpoint. A checkpoint is not proof of edge.

## Activation floor / anti-hindsight rule

The first production run establishes an activation floor.

All checkpoints already crossed before activation are marked as seen and are **not replayed** as new learning events:

```text
ALL_PRE_ACTIVATION_CHECKPOINTS_BASELINED_NOT_REPLAYED
```

This prevents installation of the controller from turning old evidence into pseudo-prospective checkpoint discoveries.

Only post-activation crossings may enter the controller's new checkpoint queue.

## Learning verdicts

The controller uses a deliberately narrow vocabulary:

```text
PROMISING
INSUFFICIENT_EVIDENCE
REDUNDANT
DATA_DEFECT
FAILED
REPLICATION_REQUIRED
```

`ROBUST` is intentionally absent from v1. Row counts, one supportive lifecycle state or execution-plane replication may never be converted into a robust-edge claim by this controller.

The controller does not independently score outcomes. It consumes current owner states. In particular:

- supportive Unified Adjudication can become `PROMISING` and route to incremental-value testing;
- negative adjudication can become `FAILED` and route to evidence-aware retirement review;
- inconclusive or unadjudicated maturity remains `INSUFFICIENT_EVIDENCE`;
- semantic duplicates become `REDUNDANT` and cannot spawn a new child lane;
- mapping/quarantine defects route to evidence repair before further scientific claims.

## Parent -> child rule

A frozen parent is immutable.

A learning checkpoint may create a **proposal** for a bounded child/research step, for example an incremental-value challenger. The proposal must contain the parent candidate ID and preserve parent lineage.

A child proposal:

- cannot mutate parent fields;
- cannot automatically register a candidate;
- cannot grant scientific admission;
- must pass existing semantic deduplication / novelty controls;
- must pass decision-impact / VOI routing;
- must pass Scientific Admission or an existing owner contract before prospective execution;
- gains no market, weight, threshold or portfolio authority.

This is the compounding mechanism: learn from one experiment, then prospectively test the next uncertainty without contaminating the old experiment.

## NEXT_BEST_EXPERIMENT semantics

`research/experiment_lifecycle/compounding_learning/NEXT_BEST_EXPERIMENT.json` is a research proposal pointer, not an execution command.

The controller ranks due checkpoint work by bounded learning urgency, such as repairing evidence machinery before interpreting it and reviewing mature supportive evidence before low-value observation work.

It deliberately does **not** claim to compute canonical value-of-information. Existing Research Decision Impact / VOI remains the owner of decision relevance and prioritization.

## T13 / Forecast Skill firewall

T13 remains outside this generic controller's runtime inputs.

The controller does **not** read:

```text
research/api_agent/forecast_skill/COHORT_ACTIVATION_v1.json
research/api_agent/forecast_skill/LATEST_STUDY_STATUS.json
T13 outcome rows
```

and does not change T13's 240-day window, preregistration, estimator, missingness rule, admission contract or confirmatory test.

T13 is referenced only as a protected external confirmatory owner so future agents understand the boundary.

A future explicit integration may expose non-inferential health metadata to this controller, but it must preserve the sealed T13 contract and require its own governed review.

## Autonomy boundary

The controller may automatically:

- classify learning cadence;
- detect new post-activation time/evidence checkpoints;
- normalize owner-produced learning states;
- identify a bounded next research step;
- propose evidence repair, incremental-value review, redundancy review or continued observation;
- preserve parent/child lineage;
- feed existing autonomous research governance.

It may not automatically:

- promote a rule;
- change a market state;
- change a threshold or model weight;
- change portfolio logic or execute a portfolio action;
- alter a frozen parent;
- invent an unfrozen scorer or baseline;
- manufacture evidence or forecasts to hit sample targets;
- admit a new experiment;
- bypass novelty, VOI, Scientific Admission, adversarial review, PR/CI or canonical governance.

The invariant is:

> **Research may automatically improve research. Research may not automatically promote itself into live framework authority.**

## Idempotency and duplicate schedules

The controller fingerprints substantive lifecycle/admission/adjudication/monthly-learning inputs while ignoring mere generated timestamps.

If no new checkpoint is crossed and the substantive input fingerprint is unchanged, a repeated schedule run returns a no-op and preserves prior bytes. This prevents the existing closely spaced Framework Learning Operations schedules from generating meaningless commits.

## Future-agent / Astra audit entry points

Any agent reviewing research, learning architecture, experiment quality, framework autonomy or self-improvement must read:

1. this document;
2. `.agents/skills/compounding-learning-controller/SKILL.md`;
3. `research/experiment_lifecycle/compounding_learning/POLICY.json`;
4. `research/experiment_lifecycle/compounding_learning/LATEST.json`;
5. `research/experiment_lifecycle/compounding_learning/NEXT_BEST_EXPERIMENT.json`;
6. `00_FMOS/EXPERIMENT_LIFECYCLE_AND_EXECUTION_PLANE_v1.md`;
7. `00_FMOS/EXPERIMENT_SCIENTIFIC_ADMISSION_AND_UNIFIED_ADJUDICATION_v1.md`;
8. current Research Governance state.

A capable future auditor should specifically challenge:

- checkpoint calibration and whether learning profiles should change;
- hidden dependence between rows/windows;
- false discovery and repeated-testing leakage;
- child-experiment incentives and hypothesis proliferation;
- stale or weak adjudication inputs;
- whether next-step ranking genuinely reduces uncertainty;
- whether failures are learned from rather than merely archived;
- redundancy and experiment-slot waste;
- regime-specific overfitting;
- any authority leakage toward canonical or portfolio behavior;
- whether a stronger sequential/anytime-valid method is justified for a future test family.

Improvements may be proposed freely. Changing live scientific or framework authority still follows the normal governed path.

## Validation / kill criteria

v1 must be modified, suspended or killed if it:

- replays pre-activation checkpoints as new evidence;
- labels unadjudicated maturity as edge;
- lets a semantic duplicate spawn a new forward lane;
- mutates a frozen parent;
- reads or alters sealed T13 outcomes/method;
- auto-registers or auto-promotes a child;
- creates market/threshold/weight/portfolio authority;
- repeatedly creates duplicate research that novelty controls should suppress;
- adds more noise than information to the Research Governance queue.

## High-impact implementation safepoint

This architecture changes a production workflow and therefore follows Repository Safety Policy v1.1. The implementation task uses an isolated source branch and a source-repository safepoint from the exact same pre-change main commit. No recovery/Vault destructive operation is part of this implementation.
