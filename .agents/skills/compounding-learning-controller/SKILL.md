---
name: compounding-learning-controller
description: 'Route multi-speed experiment learning after prospective evidence matures. Use for learning checkpoints, next-best experiment selection, parent/child challenger design, replication/incremental-value follow-up, autonomous research compounding, or audits of whether the framework learns from experiments over time. Differentiator: consumes existing lifecycle/adjudication owners, preserves frozen parents, forbids retrospective checkpoint replay, and routes proposals through novelty/VOI/scientific admission without scoring or promotion authority.'
---

# Compounding Learning Controller

## Purpose

Own the repeated workflow gap between mature experiment evidence and the next bounded prospective research step:

```text
mature prospective evidence
-> learning checkpoint
-> owner-grounded learning verdict
-> next-best research proposal
-> novelty / VOI / adversarial review
-> scientific admission before any new prospective execution
```

This Skill does not create a second experiment engine, scorer, market model or portfolio authority.

## Why this Skill exists

Observed repeated gap:

- Experiment Lifecycle records candidates, observations and maturity.
- Scientific Admission decides whether a hypothesis qualifies for forward execution.
- Unified Experimental Adjudication decides what mature evidence currently means.
- Prospective Evidence Ledger governs row integrity.
- Research Governance prioritizes research work.

Before Compounding Learning v1, no single procedure owned:

```text
when to revisit mature evidence
+ how to use multi-speed checkpoints
+ how to preserve parent experiments
+ how to propose the next uncertainty to test
+ how to route that proposal back into the existing governed research stack
```

The task occurs repeatedly as experiments mature, so the skill-registry expansion rule is satisfied.

## Mandatory read order

Read only current owners needed for the task:

1. `AGENTS.md`
2. `00_FMOS/COMPOUNDING_LEARNING_CONTROLLER_v1.md`
3. `00_FMOS/EXPERIMENT_LIFECYCLE_AND_EXECUTION_PLANE_v1.md`
4. `00_FMOS/EXPERIMENT_SCIENTIFIC_ADMISSION_AND_UNIFIED_ADJUDICATION_v1.md`
5. `research/experiment_lifecycle/compounding_learning/POLICY.json`
6. `research/experiment_lifecycle/compounding_learning/LATEST.json`
7. `research/experiment_lifecycle/compounding_learning/NEXT_BEST_EXPERIMENT.json`
8. `research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json`
9. `research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json`
10. `research/experiment_lifecycle/weekly_adjudication/LATEST.json` when interpretation is needed
11. the exact parent candidate / admission / evidence owner referenced by the checkpoint
12. current Research Governance state when evaluating routing or execution priority.

Do not replace current owner files with conversation memory or an old audit summary.

## Core ownership rule

```text
Experiment Lifecycle = what exists / what matured
Scientific Admission = whether a hypothesis may enter forward testing
Unified Adjudication = what a mature result currently means
Compounding Learning = when to revisit and what bounded research question comes next
Novelty / VOI = whether the next step is new and decision-relevant
Adversarial Sentinel = whether escalation is safe
Meta Orchestrator = which bounded research work gets priority
Canonical Governance = the only path to live framework change
```

Never collapse these owners into one agent judgment.

## Trigger scope

Use for:

- multi-speed experiment checkpoints;
- 7/14/30/60/90/120/180/240-day learning cadence;
- matured-outcome count checkpoints;
- `NEXT_BEST_EXPERIMENT` review;
- child/challenger or replication proposals;
- incremental-value follow-up after supportive evidence;
- failure-learning follow-up after negative evidence;
- autonomous experiment-learning architecture;
- audits of research compounding, hypothesis proliferation, repeated-testing leakage or experiment-slot efficiency;
- Astra or future-agent audits of how the framework learns from experiments.

Do not use this Skill to score a raw outcome, change a frozen forecast, create portfolio action or bypass Scientific Admission.

## 1. Resolve the parent and checkpoint

For every learning event resolve:

```yaml
candidate_id:
parent_candidate_id:
created_at_utc:
learning_profile: FAST | MEDIUM | LONG | CONFIRMATORY
checkpoint_axis: DAY | MATURED_OUTCOMES
checkpoint_threshold:
checkpoint_key:
checkpoint_post_activation: YES | NO
lifecycle_state:
scientific_admission_status:
unified_adjudication_action:
```

A pre-activation checkpoint may be recorded as baseline history only. It must never be emitted as a new learning discovery.

Required invariant:

```text
ALL_PRE_ACTIVATION_CHECKPOINTS_BASELINED_NOT_REPLAYED
```

## 2. Multi-speed profiles

Read current profile definitions from `POLICY.json`; do not hard-code stale values from this Skill.

Profiles govern review cadence only. They never redefine the test's frozen hypothesis, baseline, horizon, scorer or outcome.

`CONFIRMATORY` means operational/coverage review only unless the exact confirmatory owner explicitly preregistered an anytime-valid method.

A checkpoint is not proof of edge.

## 3. Owner-grounded learning verdict

The allowed controller vocabulary is intentionally narrow:

```text
PROMISING
INSUFFICIENT_EVIDENCE
REDUNDANT
DATA_DEFECT
FAILED
REPLICATION_REQUIRED
```

Do not invent `ROBUST`, `PROVEN_EDGE`, `CONFIRMED_ALPHA` or equivalent strong claims.

Rules:

- supportive Unified Adjudication may route to `PROMISING` plus incremental-value review;
- negative adjudication may route to `FAILED` plus evidence-aware failure/retirement review;
- mature but unadjudicated evidence remains `INSUFFICIENT_EVIDENCE`;
- semantic duplicate remains `REDUNDANT` and gets no new child execution lane;
- mapping/quarantine defects become `DATA_DEFECT` and require evidence repair first;
- monthly supportive claims still require incremental-value / replication review before stronger interpretation.

The controller consumes owner decisions. It does not create an independent scorer.

## 4. Parent / child integrity

A parent experiment is immutable.

A child proposal must preserve:

```yaml
parent_candidate_id:
parent_preserved_immutable: true
proposal_kind:
reason:
automatic_candidate_registration: false
automatic_scientific_admission: false
automatic_promotion: false
canonical_effect: false
portfolio_execution: false
```

A child may inherit references, not rewrite frozen parent fields.

Before any child receives prospective execution, route through:

```text
Research Memory / Novelty
-> Decision Impact / VOI
-> Scientific Admission or existing owner
-> prospective freeze if authorized
-> Experiment Execution Plane when applicable
```

A child proposal is not an admitted experiment.

## 5. NEXT_BEST_EXPERIMENT semantics

`research/experiment_lifecycle/compounding_learning/NEXT_BEST_EXPERIMENT.json` is a proposal pointer only.

It may identify evidence repair, incremental-value testing, redundancy review, failure review or continued observation.

It is not canonical VOI. `research_decision_impact_router.py` remains the decision-impact / VOI owner.

Never present `NEXT_BEST_EXPERIMENT` as an execution command or promotion.

## 6. Confirmatory / T13 firewall

T13 is an external protected confirmatory owner.

This generic Skill and controller do not read T13 outcome rows or change:

- its 240-day accrual window;
- preregistration;
- estimator;
- missingness rule;
- scientific admission;
- confirmatory test;
- forecast-skill status.

For T13 itself, resolve authority inside `research/api_agent/forecast_skill/` and its preregistered owners.

The generic controller may only preserve the boundary that T13 is not its performance-inference domain.

## 7. Autonomy boundary

Allowed autonomous research behavior:

- detect new post-activation checkpoints;
- classify cadence;
- normalize existing owner states;
- identify a bounded next research step;
- propose a child or evidence-repair path;
- feed existing novelty/VOI/adversarial/meta-orchestration controls.

Forbidden autonomous behavior:

- market-rule promotion;
- threshold or model-weight change;
- portfolio state/action/execution;
- frozen-parent mutation;
- unfrozen scoring/baseline invention;
- retrospective row creation;
- manufactured forecasts to reach sample targets;
- direct child registration/admission;
- bypass of novelty, VOI, Scientific Admission, adversarial review or canonical governance.

Permanent rule:

> Research may automatically improve research. Research may not automatically promote itself into live framework authority.

## 8. Future-agent audit obligations

A future capable agent reviewing autonomy or research quality must explicitly challenge:

- whether checkpoint cadence is calibrated to information arrival;
- dependence / effective sample size across rows and event windows;
- repeated-testing and false-discovery leakage;
- child-hypothesis proliferation;
- stale adjudication or stale evidence inputs;
- whether next-step ranking actually reduces uncertainty;
- whether failures create useful next tests rather than mere archive entries;
- experiment-slot waste and redundancy;
- regime-specific overfitting;
- authority leakage;
- whether an anytime-valid / sequential method is justified for a future test family.

Improving this architecture is encouraged. Weakening its evidence or authority firewalls is not.

## 9. Required output

For a compounding-learning review return:

```yaml
parent_candidate_id:
learning_profile:
checkpoint:
checkpoint_post_activation:
owner_evidence_status:
learning_verdict:
next_best_research_step:
child_proposal_status:
novelty_status:
voi_status:
scientific_admission_status:
canonical_effect: false
portfolio_execution: false
unresolved_blockers:
```

Keep row validity, learning interpretation and promotion authority separate.

## Validation loop

1. Resolve current owner files and parent identity.
2. Verify checkpoint is post-controller activation.
3. Verify frozen parent unchanged.
4. Read lifecycle/admission/adjudication instead of independently rescoring.
5. Apply current policy profile.
6. Block duplicate/quarantined evidence appropriately.
7. Generate proposal only when a bounded next uncertainty exists.
8. Pass proposal through novelty / VOI / adversarial / scientific-admission owners.
9. Verify zero canonical/market/threshold/weight/portfolio authority.
10. Preserve T13 and other protected confirmatory owners.
11. Use archive-governance for repository writes.

## Kill / modification criteria

Modify, suspend or kill this Skill/controller if it:

- replays pre-activation checkpoints as new evidence;
- calls unadjudicated maturity edge;
- lets semantic duplicates spawn new forward lanes;
- mutates frozen parents;
- reads or changes sealed T13 outcomes/method;
- auto-registers or auto-promotes child hypotheses;
- creates market/threshold/weight/portfolio authority;
- repeatedly adds duplicate/noise work that novelty controls should suppress;
- increases research volume without measurable information gain.
