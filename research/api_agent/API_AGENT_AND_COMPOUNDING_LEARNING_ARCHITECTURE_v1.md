# API AGENT AND COMPOUNDING LEARNING ARCHITECTURE v1

Status: SHADOW-ONLY FIRST EXECUTION LAYER

## Objective

Create a learning system whose useful evidence compounds over time. More observations must improve calibration, precision and hypothesis quality, without allowing the system to reward itself, rewrite history or silently increase authority.

## Compounding loop

1. Capture verified owner-data.
2. Produce timestamped specialist and Director observations.
3. Freeze forecasts before outcomes.
4. Score matured forecasts against owner outcomes.
5. Store errors, conflicts, missingness and regime context in Framework Memory.
6. Generate bounded hypotheses from repeated errors.
7. Test hypotheses on development data and sealed holdout rules.
8. Promote only changes that improve preregistered metrics and survive rollback gates.
9. Reuse promoted learning in future prompts, scorecards and specialist calibration.

## Memory layers

- Observation memory: immutable owner-bound rows.
- Forecast memory: frozen claims, levels, horizons and confidence.
- Outcome memory: matured results and censoring.
- Error memory: false positives, false negatives, timing errors and opportunity cost.
- Learning memory: hypotheses, experiments, verdicts and applicability regimes.
- Governance memory: versions, approvals, receipts, rollback points and rejected changes.

## Precision score

Precision is never one number alone. Every weekly scorecard must retain:

- directional accuracy;
- timing-window accuracy;
- calibration error between stated confidence and realized frequency;
- false-positive rate;
- false-negative rate;
- opportunity-cost score;
- sequence accuracy;
- data-completeness and source-health penalties;
- regime and sample-size context.

A score may improve only on matured, lineage-valid rows. Missing outcomes remain censored, not losses or wins.

## Anti-overfitting gates

- Predictions must be frozen before outcomes.
- Training, validation and final holdout remain separated.
- Parameter changes require versioned hypotheses.
- No threshold search after outcome inspection without a new experiment version.
- Promotion requires minimum sample, regime diversity and measured improvement.
- A promoted rule must have an explicit rollback condition.
- Recent performance cannot erase older regime failures.
- Specialist count cannot substitute for independent causal evidence.

## API authority

The OpenAI API may analyze, summarize, classify conflicts and propose hypotheses. It may not:

- create owner truth;
- infer missing values;
- modify canonical thresholds;
- change model weights;
- merge its own promotion;
- create portfolio action;
- access sealed outcomes outside an approved evaluation task.

All API calls pass through API Gateway v1 and produce an immutable receipt containing task, model, reasoning effort, prompt version, input hashes, output hash, token usage and estimated cost.

## Initial task classes

- DAILY_DIRECTOR_SHADOW: Luna, low reasoning.
- DAILY_CONFLICT_REVIEW: Terra, medium reasoning.
- WEEKLY_CALIBRATION_SHADOW: Terra, medium reasoning.
- MASTER_MONDAY_PREP_SHADOW: Sol, high reasoning.
- DEEP_RESEARCH_MANUAL: Sol, high reasoning, manual only.

## Promotion ladder

DRAFT -> SHADOW -> FORWARD_TEST -> VALIDATED -> CANDIDATE -> CANONICAL

No API-generated learning can skip a stage.

---

## Compounding Learning Controller extension — 2026-09-05

The architecture now has an explicit post-adjudication controller whose sole job is to decide **what should be learned or falsified next**. It does not become a second scientific adjudicator.

### Responsibility split

```text
Unified Experimental Lifecycle Adjudication
= interprets the current matured prospective evidence and decides what that evidence means.

Compounding Learning Controller
= consumes only a fresh matching adjudication and decides the next bounded learning strategy.
```

Scientific interpretation remains owned by `UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1`.

Controller implementation:

```text
scripts/research/compounding_learning_controller.py
```

Controller policy and state:

```text
00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/POLICY.json
00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/STATE.json
00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/NEXT_BEST_EXPERIMENT.json
```

### Fast learning checkpoints

The controller supports descriptive operational checkpoints so the framework does not have to wait for a long final study before learning that a research path needs more evidence, mapping, redundancy review or a new child hypothesis.

Default checkpoint profiles are:

```text
FAST:         7 / 14 / 30 days; 5 / 10 / 20 matured outcomes
STANDARD:     7 / 14 / 30 / 60 / 90 days; 5 / 10 / 20 / 40 matured outcomes
LONG:         30 / 60 / 90 / 120 / 180 / 240 days; 10 / 25 / 50 / 100 matured outcomes
CONFIRMATORY: 30 / 60 / 90 / 120 / 180 days, operational readiness only
```

A checkpoint is not a win, loss, edge claim or promotion event. It is a bounded opportunity to ask whether the frozen hypothesis should keep observing, undergo the already-authorized adversarial/incremental-value review, or generate a **new** falsifiable child proposal.

### No hindsight mutation

A historical candidate that is requalified later does not inherit its old calendar age as prospective learning time. Its day clock is disabled until an explicit forward-test start exists. Newly matured forward outcomes may still trigger event-count checkpoints.

Frozen parents are immutable:

```text
NO RETROSPECTIVE RESCORE
NO OUTCOME-AWARE THRESHOLD SEARCH
NO REWRITE OF THE ORIGINAL HYPOTHESIS
NO AUTOMATIC PARAMETER OPTIMIZATION
```

A failed or partially supported parent may inspire a new regime-specific or incremental-value child test, but that child must pass the normal research-governance and scientific-admission path before any new prospective freeze.

### Automatic compounding route

When a fresh adjudication legitimately permits a new learning proposal, the controller publishes a research-only specialist state. The existing Research Governance Stack then receives it automatically through:

```text
COMPOUNDING_LEARNING
-> RESEARCH_MEMORY_NOVELTY
-> DECISION_IMPACT_VOI
-> INDEPENDENT_ADVERSARIAL_SENTINEL
-> META_ORCHESTRATOR
-> SCIENTIFIC_ADMISSION_OR_EXISTING_OWNER
-> PROSPECTIVE_FREEZE_IF_AUTHORIZED
-> EXPERIMENT_EXECUTION_PLANE
```

This creates automatic research compounding without automatic self-promotion.

### Confirmatory-study firewall

Long confirmatory experiments remain sealed. For `FORECAST_SKILL_CONFIRMATORY_V1_3_1` and its binding v1.3.2 erratum, the 30/60/90/120/180-day controller checkpoints are restricted to:

```text
ACCRUAL_HEALTH
DATA_QUALITY
CONCENTRATION
MATURITY_READINESS
```

They may not:

- inspect interim performance to declare forecast skill;
- change the frozen estimator, endpoint, gates or sample rule;
- create an automatic child experiment from interim confirmatory performance;
- change model weights, thresholds, framework state or portfolio action.

The final preregistered confirmatory test remains the only owner of the study verdict. Until legitimate future evidence changes it under that contract, `FORECAST SKILL = UNPROVEN`.

### Future-agent and Astra audit rule

Any future agent auditing experiments, learning, calibration, forecast skill or automatic improvement should read this architecture plus the controller `POLICY.json`, `STATE.json` and `NEXT_BEST_EXPERIMENT.json` before proposing a new learning engine.

A more capable future agent may improve this controller only by proposing a versioned methodology or a new child test. It must not use its increased capability to retroactively rewrite frozen parents, re-score old evidence under newly invented rules, weaken the confirmatory firewall or bypass the existing Research Governance Stack.
