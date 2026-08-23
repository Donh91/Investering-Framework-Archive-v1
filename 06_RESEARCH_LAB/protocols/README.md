# Research Lab Experimental Test Methods

Status: ACTIVE RESEARCH METHOD GUIDANCE
Scope: method selection for experimental sensors, Shadow layers, skills, agents, tools, models, controllers, data sources, automations and architectural ideas.
Authority: guidance only; this file does not grant market, portfolio, execution or canonical write authority.

## Purpose

This README teaches new agents how the framework evaluates experimental ideas before they are allowed to influence production or canonical decision logic.

The goal is **not** to apply the same checklist to every candidate.

The goal is to choose the **smallest credible set of tests that can falsify the candidate's claimed value and expose its important failure modes**.

Do not mechanically copy a previous experiment, pull request, repository layout or tool-specific harness. Historical implementations may inspire a test, but the current candidate's claim, failure modes, authority and evidence requirements determine the method.

This guide complements `SHADOW_IDEA_ADMISSION_RULE_v1.md` and `SHADOW_IDEA_ADMISSION_TEMPLATE_v1.json`. Where there is a conflict, the active admission rule and stronger canonical governance take precedence.

---

## Core doctrine

Every proposed addition starts as a hypothesis, not as a feature.

A candidate must answer three questions:

1. **What real problem does it solve?**
2. **Does it add measurable value beyond the current framework or the simplest relevant baseline?**
3. **Does that value remain worthwhile after complexity, fragility, cost and failure risk are included?**

A candidate that cannot answer these questions should remain Shadow, be archived, or be retired.

The framework prefers fewer independent, well-tested capabilities over many correlated or fashionable additions.

---

## Method-selection rule

Agents MUST NOT treat the method list below as a mandatory checklist.

For each candidate:

1. state the claim;
2. identify the ways that claim could be wrong;
3. identify the ways the candidate could cause harm or hidden complexity;
4. select the minimum test battery capable of detecting those failures;
5. explain why each selected method is relevant;
6. explain why materially relevant methods were omitted;
7. freeze the test plan before outcome-linked evidence is inspected where hindsight or tuning risk exists.

A large test suite is not automatically rigorous. A small, well-targeted falsification test can be stronger than a large generic suite.

---

## Universal experimental backbone

These principles apply broadly, although implementation differs by candidate type.

### 1. Problem-first definition

Define the concrete weakness, missing capability, failure mode or uncertainty the candidate is meant to address.

If the framework already solves the problem sufficiently, prefer reuse, replacement, simplification or archive over additive duplication.

### 2. Frozen identity and hypothesis

Bind the experiment to the exact candidate identity where relevant:

- source/repository and commit or package version;
- model/version;
- data-source contract;
- sensor formula;
- threshold/rule set;
- prompt/skill version;
- controller logic;
- fixture/data snapshot.

Do not silently upgrade, retune or substitute the candidate after seeing results and still call it the same experiment.

### 3. Explicit baseline

Every value claim needs a comparison target.

Possible baselines include:

- current framework without the candidate;
- simplest existing sensor or rule;
- reduced feature set;
- deterministic implementation;
- current agent workflow;
- incumbent provider/source;
- null or no-action policy.

The question is not merely whether the candidate works. The question is whether it improves the relevant baseline.

### 4. Isolation before authority

Experimental components should be evaluated outside protected decision authority whenever possible.

Use Shadow, sandbox, synthetic fixtures, read-only execution, isolated caches, temporary repositories, dry-runs, replay environments or other bounded surfaces appropriate to the candidate.

No experimental success alone grants authority over market semantics, thresholds, weights, portfolio actions, execution, outcome labels, prospective floors or other protected objectives.

### 5. Preregistered success, failure and kill criteria

Before outcome-linked testing, define what would count as:

- useful evidence;
- insufficient evidence;
- failure;
- unacceptable collateral damage;
- unacceptable complexity;
- promotion eligibility;
- retirement/kill conditions.

Negative and null results are valid outcomes. Do not repeatedly mutate a failed candidate until a nearby variant happens to pass without treating that as a new experimental condition.

### 6. No cross-candidate contamination

When comparing candidates, give them equivalent starting conditions.

Do not allow one candidate's generated files, caches, labels, model outputs, tuned thresholds, prompts or learned state to affect another candidate unless the experiment explicitly studies that interaction.

Where practical, use byte-identical fixtures or independently reconstructed point-in-time inputs.

### 7. Incremental-value test

Measure marginal benefit after existing framework capability is accounted for.

Useful forms include:

- ablation;
- reduced-stack comparison;
- incremental information tests;
- duplicate/correlation analysis;
- error reduction versus baseline;
- coverage improvement;
- resilience improvement;
- token/time/cost reduction without quality loss;
- detection of failure classes the baseline misses.

### 8. Complexity tax

Measure the cost of keeping the candidate, not only the benefit of passing a test.

Relevant taxes can include:

- dependencies;
- API/token spend;
- compute and latency;
- source fragility;
- update/version churn;
- maintenance burden;
- cache/storage footprint;
- security/privacy surface;
- licensing or policy risk;
- provenance burden;
- correlated failure modes;
- agent coordination cost;
- human interpretability burden;
- rollback difficulty.

If two candidates provide comparable value, prefer the simpler and more reversible one.

### 9. Adversarial validation

Actively search for ways the candidate can appear useful while being wrong.

Examples include:

- leakage;
- stale data;
- malformed outputs;
- contradictory inputs;
- dependency outages;
- false positives;
- false negatives;
- authority escalation;
- hidden state;
- contamination;
- provider drift;
- cherry-picked regimes;
- accidental success on the scoring metric while damaging unrelated state.

### 10. Prospective evidence where the claim is predictive or causal

Historical evidence is useful for hypothesis generation and bounded validation, but it is not automatically sufficient for promotion of market-predictive claims.

If a candidate claims to anticipate future market state, rotation, risk, timing or outcome, use point-in-time availability controls and prospective/forward evidence appropriate to the claim.

---

# Test method palette

Select from this palette according to the candidate's actual claim and failure modes.

## A. Market sensors and Shadow layers

Typical relevant methods:

### Point-in-time availability audit

Verify that every input existed and was obtainable at the timestamp at which the hypothetical decision would have been made.

Use when there is any risk of revised data, backfilled data, publication lag, reconstructed labels or hindsight contamination.

### Temporal leakage audit

Search for direct and indirect future information entering features, thresholds, regimes, labels or selection logic.

Include calendar/date fingerprints and episode-duration clues when relevant.

### Frozen historical test / holdout

Separate hypothesis construction from validation data. Do not use the same episodes to invent and confirm the rule without an independent stage.

### Prospective / forward test

Required when historical results cannot establish real-time observability or when the sensor claims predictive value.

### Ablation / reduced-stack test

Compare full framework versus framework without the candidate. Ask whether actual decisions, permissions, warnings or error rates materially change.

### Redundancy and collinearity test

Determine whether the candidate is merely another expression of information already present in existing sensors.

Prefer independent information over correlated feature accumulation.

### Regime stratification

Test whether apparent value survives across materially different regimes rather than one favorable episode type.

### Negative controls / placebo tests

Use inputs or timestamps that should not contain the proposed signal. A sensor that finds strong predictive structure in deliberate nonsense may be overfit or leakage-prone.

### Threshold perturbation / robustness test

Where thresholds exist, test whether value survives reasonable perturbation. Extremely narrow parameter dependence is a warning sign.

Do not use robustness testing as permission to tune thresholds after seeing the target outcomes.

### Lead/lag and timeliness test

A statistically related sensor may still be useless if it arrives after the framework's existing signal. Measure whether it adds actionable lead time or improves confidence before the decision window closes.

### False-positive / false-negative cost analysis

Evaluate not only hit rate but the operational cost of being wrong. Use the framework's existing False Negative Penalty and scientific governance where applicable.

---

## B. Data sources and providers

Typical relevant methods:

### Provenance and source-identity test

Bind observations to source, timestamp, retrieval path and contract identity.

### Cross-source reconciliation

Compare overlapping observations against an independent source when available. Distinguish harmless methodology differences from unexplained divergence.

### Freshness and publication-lag test

Measure whether the source is available early enough for the intended decision horizon.

### Missingness and outage simulation

Test how the framework behaves when the provider is delayed, unavailable, partially populated or returns malformed data.

### Schema / normalization drift test

Detect renamed fields, unit changes, timezone shifts, sign changes, revised history and other silent semantics changes.

### Cost and dependency test

Assess paid-call burden, quotas, rate limits, geographic restrictions, authentication fragility and replacement options.

### Restricted-data / privacy boundary test

Verify that restricted payloads, credentials or licensed values remain in the correct data plane and only permitted provenance/derived artifacts cross boundaries.

---

## C. Agents, skills, tools and external repositories

Typical relevant methods:

### Hostile qualification

Treat third-party code as untrusted until proven otherwise. Use isolated runners, synthetic fixtures, read-only permissions, secret-free environments and bounded network access where possible.

### Frozen dependency / supply-chain test

Pin versions and separately record source identity when package artifacts and repository heads do not map one-to-one.

### Functional fixture test

Give the candidate a small deterministic task with known truth before exposing it to complex framework work.

### Baseline bake-off

Compare candidate versus current workflow on identical tasks. Measure correctness first, then token use, tool calls, latency, filesystem writes, failure clarity and maintenance burden.

### Property-based invariant test

Generate many valid/invalid cases to test invariants instead of a handful of handpicked examples.

### Mutation test

Deliberately inject faults into code, contracts or tests. A test system that cannot detect plausible mutations may be giving false confidence.

### Prompt-injection / authority-escalation test

Try to make the candidate exceed its declared authority, ignore governance, access secrets, modify protected paths, self-promote or reinterpret evidence rules.

### Clean-tree / collateral-damage test

A tool that solves its assigned task but damages unrelated repository state has failed.

### Telemetry / data-egress test

Determine what leaves the runner, whether telemetry/sharing can be disabled and whether code, paths, prompts, outputs or secrets can be transmitted externally.

### Reproducibility test

Repeat the same task from clean state and determine whether outcome variance is acceptable for the intended role.

---

## D. Models, scoring systems and controllers

Typical relevant methods:

### Frozen evaluation set

Evaluate on tasks/examples that were not selected after observing candidate-specific failures where possible.

### Reduced-model / ablation comparison

Ask whether additional model complexity materially changes decisions or merely restates the same information.

### Calibration test

Compare confidence to observed correctness. High-confidence wrong outputs deserve special scrutiny.

### Blind adjudication

When comparing multiple agents/models/implementations, hide candidate identity from the evaluator where practical to reduce preference bias.

### Independent implementation diversity

For high-risk logic, multiple independent implementations can expose shared assumptions or coding mistakes. Use only when the expected error-reduction benefit justifies the added cost.

### Out-of-distribution / regime test

Test behavior when inputs differ from the conditions represented in the development examples.

### Deterministic contract validation

Separate substantive AI judgment from machine-verifiable schema, identity, authority, evidence-binding and execution constraints.

---

## E. Automations and operational workflows

Typical relevant methods:

### Idempotence test

Running the same job twice should not silently duplicate or corrupt state unless duplication is explicitly intended.

### Retry / partial-failure test

Simulate network failures, timeouts, partial writes and transient provider errors.

### Concurrency / race test

Test overlapping writers, stale-base commits, scheduler collisions and lock behavior.

### Schedule semantics test

Verify timezone, cadence, daylight-saving behavior, owner schedule and late/catch-up semantics.

### Permission-minimization test

Grant only the permissions required for the operation. Research workflows should not become main writers merely for convenience.

### Rollback / reversibility test

Confirm that a failed rollout or bad artifact can be disabled, reverted or quarantined without damaging evidence history.

---

## F. Architectural patterns and large refactors

Typical relevant methods:

### Replacement-before-addition analysis

Ask whether the new layer can remove or simplify existing machinery instead of adding another permanent layer.

### Blast-radius analysis

Map owners, writers, contracts, downstream consumers and failure domains before implementation.

### Shadow dual-run

Run old and new paths in parallel without changing decision authority, then compare outputs and failure behavior.

### Migration reversibility

Avoid one-way migrations until value is demonstrated and rollback has been tested.

### Complexity budget

Architectural elegance is not enough. Quantify ongoing files, workflows, dependencies, agents, permissions and governance burden added or removed.

---

# Fast selector for agents

Use this as a reasoning aid, not a rigid matrix.

| Candidate claim / risk | High-value methods |
| --- | --- |
| Predicts future market behavior | point-in-time audit, leakage audit, holdout, prospective test, regime stratification |
| Adds a new sensor | baseline ablation, redundancy/collinearity, negative controls, lead/lag, prospective evidence |
| Adds a data provider | provenance, cross-source reconciliation, freshness, outage, schema drift, cost/privacy |
| Adds third-party code | hostile qualification, frozen dependency, secret-free fixture, collateral-damage, telemetry/egress |
| Adds an AI skill/agent | baseline bake-off, adversarial authority tests, reproducibility, mutation/property tests where relevant |
| Adds a model/controller | frozen eval, ablation, calibration, blind adjudication, OOD/regime tests |
| Adds automation | idempotence, retry, concurrency, schedule semantics, permission minimization, rollback |
| Adds architecture | blast radius, dual-run, replacement analysis, reversibility, complexity budget |
| Appears highly accurate historically | leakage, negative controls, regime tests, prospective evidence |
| Adds complexity but little new information | ablation, redundancy analysis, complexity tax; likely archive/retire |

---

# Evidence packet expected from a serious experiment

A mature experimental package should normally make the following auditable, as relevant:

- candidate ID and version;
- problem statement;
- claimed benefit;
- authority ceiling;
- baseline;
- frozen hypothesis/contract;
- exact test methods selected;
- why each method was selected;
- materially relevant methods omitted and why;
- frozen success/failure/kill criteria;
- point-in-time data/source identity where relevant;
- contamination controls;
- results, including negative/null results;
- incremental-value assessment;
- complexity tax;
- security/privacy/provenance findings;
- limitations and unresolved uncertainty;
- rollback/retirement criteria;
- evidence sufficiency for the next lifecycle stage.

Do not hide failed attempts. Failed adapters, confounds, contamination, stale assumptions and unexpected side effects are research findings and should improve the next experimental design.

---

# Lifecycle interpretation

Passing a qualification test does **not** mean production adoption.

Possible outcomes remain governed by the active Shadow admission and stronger framework governance, including states such as:

- `ARCHIVE_ONLY`;
- `SHADOW_CANDIDATE`;
- `SHADOW_TESTING`;
- `FORWARD_TEST`;
- `OPERATIONAL_HELPER`;
- `CANONICAL_CANDIDATE`;
- `CANONICAL`;
- `RETIRED`.

The correct next state depends on the claim and evidence. A market-predictive sensor normally requires stronger and more prospective evidence than a non-market operational helper.

---

# Anti-patterns

Agents should actively avoid these behaviors:

- importing a popular repository directly into production;
- using a previous PR as a template without re-deriving the current failure modes;
- evaluating only whether a candidate can run;
- declaring value without a baseline;
- measuring only successful cases;
- tuning after every failed historical episode until the rule fits;
- using one candidate's generated state in another candidate's supposedly independent test;
- promoting from synthetic evidence when the claim requires prospective real-world evidence;
- adding several correlated sensors because each looks individually plausible;
- weakening a gate merely to obtain a green CI result;
- treating complexity as free;
- allowing a successful task result to excuse collateral damage or authority violations.

---

# Default instruction to future agents

When the owner proposes a new idea, do not ask "How do we add it?" first.

Ask:

> **What is the candidate claiming, what could make that claim false, and what is the smallest isolated experiment that could prove it does not deserve admission?**

Then select the relevant methods from this guide, freeze the experiment, collect evidence, compare against the baseline, include the complexity tax, and let the governed lifecycle process decide whether the candidate should advance, remain Shadow, be archived or be retired.

The framework should learn from experiments without becoming larger by default.
