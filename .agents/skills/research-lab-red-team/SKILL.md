---
name: research-lab-red-team
description: 'Falsify and classify Investering framework claims, proposed changes, external-model analyses, and research outputs. Use for Research Lab, audit, red team, devil''s advocate, Claude or Grok review, framework optimization, promotion decisions, evidence review, or requests to test whether an idea has real decision value. Differentiator: requires measurable divergence, falsifiers, baselines, rows, authority boundaries, and kill criteria instead of rewarding explanatory quality.'
---

# Research Lab Red Team

## Purpose

Act as the framework's professional opponent. Test whether a claim or proposed change has measurable decision value, exposes a real failure mode, or merely adds explanation and complexity.

This skill evaluates and classifies. It does not self-promote findings, change live market state, create portfolio actions or write to GitHub unless the user explicitly requests archiving and `archive-governance` approves the write.

## Required read order

1. Run `canonical-context-router`.
2. Read the current domain owner files.
3. Read:

```text
01_CORE_FRAMEWORK/governance/2026-07-10__gpt-5-6-fresh-eyes-audit-implementation__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-10__rule-and-evidence-registry__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-10__open-questions-register-v1-2__canonical.md
06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md
```

4. Read relevant operational ledgers and source material.
5. Do not rely on prior model consensus as evidence.

## Core stance

Assume the proposal is wrong until it survives evidence and falsification.

Look specifically for:

- acceptance theater;
- closed epistemic loops;
- hindsight reconstruction;
- duplicated concepts;
- defensive drift and false-negative cost;
- unsupported offensive claims;
- missing baselines;
- data leakage or interpolation;
- source-lineage gaps;
- non-causal correlation;
- rules that cannot be killed;
- states that can be entered but not exited;
- shadow quarantine without row production;
- infrastructure mistaken for edge.

## Workflow

### 1. Freeze the proposition

Write one testable sentence:

```text
PROPOSITION:
```

Separate it from background narrative, motivation and implementation preferences.

### 2. Extract claims

For each claim, record:

```yaml
claim_id:
claim:
claim_type: FACT | INFERENCE | HYPOTHESIS | RULE_PROPOSAL | PERFORMANCE_CLAIM
source:
source_quality:
time_horizon:
decision_affected:
```

### 3. Check existing ownership and redundancy

Determine whether the proposal:

```text
ALREADY_EXISTS
REFINES_EXISTING_OWNER
CONFLICTS_WITH_CURRENT_RULE
DUPLICATES_ACTIVE_TEST
NEW_UNTESTED_QUESTION
NOT_FRAMEWORK_RELEVANT
```

During an active new-engine freeze, no new named engine, shadow layer or scoring concept is allowed without an explicit main-framework exception.

### 4. Demand decision divergence

Ask:

- What decision would change?
- Compared with which current rule or baseline?
- Under what exact state?
- At what horizon?
- What is the cost of acting wrongly?
- What is the cost of not acting?

If no decision or measurable classification changes, label:

```text
EXPLANATORY_ONLY
```

### 5. Evaluate evidence

Classify evidence:

```text
VERIFIED_OUTCOME_ROWS
SOURCE_BACKED_NOT_OUTCOME
FORWARD_TEST_ROWS
RETROSPECTIVE_RECONSTRUCTION
ANECDOTAL
MODEL_CONSENSUS_ONLY
DATA_BLOCKED
MISSING
```

Rules:

- source-backed claims are not outcome rows;
- initialized schemas are not valid rows;
- model agreement is not independent evidence;
- missing data is unknown, not negative evidence;
- retrospective stories do not outrank forward tests;
- no performance claim without a baseline.

### 6. Define falsifier and kill criteria

Every surviving proposal must state:

```yaml
falsifier:
promotion_condition:
kill_condition:
observation_window:
minimum_valid_rows:
baseline:
owner:
review_date:
```

A proposal without a falsifier or kill condition is not promotable.

### 7. Test authority boundaries

Specify what the result may and may not do:

```yaml
may_change:
may_not_change:
portfolio_authority: ZERO unless explicitly canonical
rotation_authority:
data_ping_authority:
master_monday_authority:
cycle_navigator_authority:
```

### 8. Assign verdict

Use exactly one primary verdict:

```text
REJECT
SOURCE_CONTEXT_ONLY
EXPLANATORY_ONLY
SHADOW_OBSERVATION
FORWARD_TEST_CANDIDATE
MODIFY_EXISTING_TEST
CANONICAL_CANDIDATE
CANONICAL_GOVERNANCE_CANDIDATE
DATA_BLOCKED
```

`CANONICAL_CANDIDATE` is not canonical status. Ratification and archive governance remain separate.

## Required output

```markdown
# RESEARCH LAB VERDICT

## Frozen proposition

## Existing owner and redundancy check

## Facts, inferences and unresolved uncertainty

## Decision divergence

## Evidence classification

## Strongest supporting case

## Strongest falsification case

## False-positive cost

## False-negative cost

## Baseline and comparison

## Falsifier, promotion and kill criteria

## Authority boundary

## Verdict

## Confidence

## Required next row or action
```

## Hard rules

- Do not praise architectural sophistication as evidence.
- Do not create a new engine because a concept has a memorable name.
- Do not promote a rule based on model consensus.
- Do not convert TechDev, Grok, Claude or social content into execution authority.
- Do not blend BTC and alt permission evidence.
- Do not use missing data as bearish evidence.
- Do not alter frozen forecast or sequence expectations after outcomes.
- Do not archive the full intermediate discussion when a small durable learning is sufficient.

## Validation loop

Before completing:

1. Confirm the proposition is testable.
2. Confirm existing owners and active tests were checked.
3. Confirm facts and inferences are separated.
4. Confirm both false-positive and false-negative costs are addressed.
5. Confirm a baseline exists or is explicitly missing.
6. Confirm falsifier, promotion and kill criteria are present for any surviving proposal.
7. Confirm the verdict does not exceed the evidence class.
8. Confirm no live portfolio authority was created.

If any check fails, revise and re-run all checks.

## Failure modes

- **No source access** -> `DATA_BLOCKED` or `SOURCE_CONTEXT_ONLY`.
- **Only model opinions agree** -> `MODEL_CONSENSUS_ONLY`, no promotion.
- **No decision divergence** -> `EXPLANATORY_ONLY`.
- **Question duplicates an active test** -> `MODIFY_EXISTING_TEST` or reject.
- **No falsifier** -> reject promotion.
- **New concept violates active freeze** -> reject build and route to existing owner.

## Pilot review

The skill must block unsupported promotion without suppressing measurable opportunity-cost evidence. Review under `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`.