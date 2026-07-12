# Investering Agent Skills v0.2

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** agent workflows / repository operating layer / reproducibility / prospective evidence  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Related folders:** `.agents/skills/`, `00_ARCHIVE_CONTROL/`, `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `AGENTS.md`, Canonical Archive Index, Index Addendum Registry, Archive Map and Routing, Rule and Evidence Registry, Active Test Registry, Repository Safety and Backup Policy  
**Supersedes:** Agent Skills v0.1.1 behavior where contradicted by the v0.2 additions in this owner

## 1. Executive decision

Investering Agent Skills v0.2 is the active hardened pilot operating layer for repository-aware agents.

It contains four procedure Skills:

```text
canonical-context-router
prospective-evidence-ledger
archive-governance
research-lab-red-team
```

It is not:

- a new framework engine;
- a new shadow layer;
- a market model;
- a source of live thresholds;
- a scoring engine;
- an automation scheduler;
- a portfolio-action system;
- evidence of trading edge.

```yaml
stack_version: 0.2
status: PILOT_ACTIVE_HARDENED
skills: 4
stack_qualified_uses: 1
prospective_evidence_ledger_version: 0.1
prospective_evidence_ledger_qualified_uses: 0
trading_logic_changed: NO
framework_authority_changed: NO
new_engine_created: NO
new_shadow_layer_created: NO
new_test_created: NO
new_ledger_created: NO
new_score_created: NO
```

## 2. Problem addressed

The repository contains strong canonical governance, but agents can still fail operationally by:

- reading old files before current owner files;
- overlooking valid index addenda;
- reactivating superseded rules;
- treating source material as doctrine;
- creating duplicate canonical documents;
- promoting explanatory research without rows;
- relying on a connector default and writing to `main`;
- overstating backup coverage;
- treating a source row or schema as outcome evidence;
- reconstructing forecasts after outcomes;
- rewriting frozen inputs;
- scoring before a method is frozen;
- counting overlapping observations as independent;
- treating validator or coverage readiness as edge.

The Skill layer addresses procedure, not market intelligence.

## 3. Architecture

```text
Canonical repository files
= current truth and authority

CANONICAL_INDEX.md
= primary canonical navigation

INDEX_ADDENDUM_REGISTRY.md
= low-impact discovery for valid addenda

AGENTS.md
= repository-wide non-negotiable operating rules

SKILL_REGISTRY.md
= active Skill inventory, routing and pilot governance

.agents/skills/*/SKILL.md
= task-specific procedures loaded when relevant

Active Test Registry
= authorized forward-test navigation

Domain ledgers
= frozen inputs, outcomes and accountability

Domain validators and scorers
= row integrity, coverage and owner-defined measurement

GitHub branches and pull requests
= reviewed execution and receipts
```

## 4. Composition

General framework work:

```text
canonical-context-router
-> task reasoning or extraction
-> research-lab-red-team when a claim or change is evaluated
-> archive-governance before repository writes
```

Active test and ledger work:

```text
canonical-context-router
-> prospective-evidence-ledger
-> existing domain validator or scorer
-> research-lab-red-team only for interpretation, test survival or promotion review
-> archive-governance before repository writes
```

## 5. Implemented files

```text
AGENTS.md
00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
.agents/skills/canonical-context-router/SKILL.md
.agents/skills/prospective-evidence-ledger/SKILL.md
.agents/skills/archive-governance/SKILL.md
.agents/skills/research-lab-red-team/SKILL.md
07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__investering-agent-skills-v0-1__canonical.md
00_ARCHIVE_CONTROL/2026-07-12__index-addendum-investering-agent-skills-v0-1.md
```

The historical filenames retain `v0-1` for path continuity. Their document headers and content identify the active stack as v0.2.

## 6. Skill responsibilities

### 6.1 canonical-context-router

Resolves:

- task domain;
- current canonical owner;
- highest active version;
- operational runtime registry;
- directly index-listed and registry-discoverable addenda;
- relevant ledgers;
- explicit overrules;
- unresolved conflicts.

It is read-only and cannot make portfolio decisions or write files.

### 6.2 prospective-evidence-ledger

Governs the lifecycle of evidence rows for already registered active tests.

It resolves:

- active test and owner;
- ledger path and schema;
- frozen input fields;
- outcome fields and maturity rule;
- source contract;
- duplicate and event-window rules;
- validator and scorer owners;
- owner-defined coverage calculation.

It enforces:

- causal pre-registration;
- exact timezone-aware timestamps;
- frozen-field immutability;
- full horizon maturity;
- source-lineage completeness;
- duplicate idempotency;
- event-window dependence disclosure;
- delegation to existing validators and scorers;
- separation of row validity, coverage readiness and promotion status.

It cannot:

- create a new test, ledger, schema or scorer;
- interpret edge;
- promote a rule;
- change live market state;
- produce portfolio action;
- schedule collection.

### 6.3 archive-governance

Controls:

- archive-worthiness;
- existing-owner search;
- create versus update versus append;
- placement and naming;
- status classification;
- explicit branch assertion before every write;
- branch and PR workflow;
- high-impact safepoint requirements;
- index versus index-addendum decisions;
- addendum registry maintenance;
- incident-aware result classification;
- backup-product and frozen-SHA truth;
- read-back and diff validation.

It cannot write without explicit user intent.

### 6.4 research-lab-red-team

Tests:

- evidence class;
- decision divergence;
- false-positive and false-negative cost;
- baselines;
- redundancy;
- falsifiers;
- promotion and kill criteria;
- authority boundaries;
- new-engine-freeze compliance.

It cannot self-promote findings or create live execution authority.

## 7. Why the fourth Skill is justified

The initial three-Skill stack targeted:

1. wrong or incomplete context;
2. wrong archive behavior;
3. unsupported framework promotion.

The current framework stage exposed a separate repeated operational gap: active tests exist, but forward row production, maturity handling, source lineage, frozen-input protection and coverage classification are distributed across multiple owners and ledgers.

The repeated gap appears across:

- M3 decision-ledger collection;
- FRLP weekly outcome rows;
- BTC Partial versus WAIT;
- cumulative FNP rows;
- Pullback Edge maturity windows;
- Transmission Matrix prospective falsification;
- TechDev claim outcomes;
- Archive Lineage Integrity.

The new Skill does not add theory. It turns existing owner contracts into a repeatable evidence-lifecycle procedure.

## 8. Prospective evidence contract

Core rule:

```text
The test owner defines the question.
The ledger owner defines the schema.
The source proves what existed.
The clock determines maturity.
The validator determines row validity.
The scorer determines the score.
Governance determines promotion.
```

Required classification boundaries:

```text
SOURCE_CLAIM_ROW != OUTCOME_ROW
FROZEN_INPUT_ROW != VALID_OUTCOME_ROW
COVERAGE_RECEIPT != PERFORMANCE_EVIDENCE
```

Required result separation:

```yaml
row_validity:
coverage_readiness:
edge_or_promotion_status:
```

A validator PASS is not a performance PASS.

A coverage gate may permit governance review but cannot automatically promote a rule.

## 9. Active-test and owner boundary

The target test must exist in:

```text
06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md
```

The new Skill may not create registry entries or new tests.

Before processing a row, it must resolve:

```yaml
test_id:
test_owner:
ledger_owner:
ledger_path:
row_identity_field:
frozen_input_fields:
mutable_outcome_fields:
effective_horizon:
evaluation_timezone:
maturity_rule:
source_contract:
duplicate_key:
event_window_rule:
validator_path:
scorer_path:
write_mode:
```

An incomplete contract produces `LEDGER_CONTRACT_INCOMPLETE`, not schema invention.

## 10. Causality and immutability

A forward-eligible row requires:

- an exact timezone-aware issued timestamp;
- source existence before the outcome window;
- frozen horizon and benchmark;
- frozen forecast or decision;
- source path and excerpt or machine row;
- source hash and commit receipt when required;
- no retrospective reconstruction.

Once frozen, the forecast, decision, horizon, invalidators, benchmark, source excerpt, hash and issued timestamp cannot be silently changed.

Corrections require an owner-defined correction row or receipt that preserves the original value and Git history.

## 11. Maturity and missing data

Outcomes may only be attached after the full owner-defined horizon has elapsed and the actual source is complete.

The Skill must not treat:

- intraday values as daily closes;
- preliminary values as settled actuals;
- partial horizons as mature;
- missing endpoints as zero;
- inferred values as observed actuals.

```text
DATA_MISSING = UNKNOWN
```

Missing data cannot become a negative signal, failed test, zero, inferred outcome, pseudo-row or eligibility PASS.

## 12. Duplicate and event-window controls

An exact duplicate is a no-op.

The same row ID with materially different content is a conflict, not a new row opportunity.

A new row ID does not prove event-window independence. Overlapping observations may remain valid observations but may not automatically increase independent-window coverage.

## 13. Validator and scorer delegation

The Skill must use existing owner-defined executable validators when available.

Current M3 example:

```text
04_MARKET_LEARNING/truth_layer/tools/validate_m3_coverage.py
.github/workflows/validate_m3_forward_ledger.yml
```

The Skill does not duplicate or manually reinterpret validator logic.

Scoring is permitted only when the method, benchmark and category are frozen by the owner. Otherwise the result is `SCORE_METHOD_UNFROZEN`.

## 14. Repository write boundary

The Skill may prepare a row and evidence decision manifest.

Any GitHub mutation requires:

```yaml
user_write_intent: EXPLICIT
archive_governance_invoked: YES
target_branch_verified: YES
```

`archive-governance` retains ownership of branch assertions, PR flow, read-back, discoverability and backup-scope reporting.

## 15. Write hardening retained

The active implementation requires:

- isolated task branch;
- explicit branch argument on every write;
- branch existence verification;
- no default or backup branch as target;
- no direct push to `main`;
- no placeholder or tool-probe files;
- no force operation;
- no hidden deletion;
- no direct `CANONICAL_INDEX.md` change without the safepoint sequence;
- pull request and read-back validation.

## 16. Pilot evaluation

Shared stack review occurs after 10 qualified tasks or 2026-08-09, whichever comes first.

The new Skill requires at least three real uses before KEEP is justified.

Recommended initial production cases:

1. one valid M3 prospective decision row;
2. one retrospective row that must be blocked;
3. one Transmission Matrix frozen input row;
4. one maturity check;
5. one duplicate attempt;
6. one event-window overlap;
7. one source-hash mismatch;
8. one FRLP actual with a frozen scorer;
9. one unfrozen-score case;
10. one coverage gate that cannot self-promote.

Synthetic evaluation cases are stored at:

```text
07_PROMPTS_AND_AGENTS/github_agent/skill_evals/2026-07-12__prospective-evidence-ledger-v0-1__eval-cases.md
```

## 17. Kill criteria

The new Skill must be immediately modified or suspended if it:

- marks a retrospective row as forward eligible;
- changes a frozen forecast or decision;
- creates duplicate evidence rows;
- counts source rows as outcomes;
- misses material source-lineage defects;
- overstates event-window independence;
- becomes a parallel scorer;
- treats coverage readiness as edge;
- creates tests or schemas without authority;
- produces market or portfolio language;
- increases archive inflation or manual repair.

## 18. Expansion gate

No further Skill is authorized merely because a workflow could theoretically be automated.

Potential later candidates such as DATA PING execution, weekly range audit, Master Monday, Cycle Navigator publication, research-package ingest and agent loops remain `NOT_AUTHORIZED_FOR_BUILD` until a separate repeated gap is demonstrated and the current stack produces pilot evidence.

## 19. Expected benefit

The expected value is operational evidence quality:

- more valid prospective rows;
- less hindsight reconstruction;
- stronger frozen-input integrity;
- fewer duplicate and pseudo-rows;
- clearer maturity handling;
- better source lineage;
- correct event-window and coverage accounting;
- reliable delegation to existing validators and scorers;
- clearer separation between evidence availability and actual edge.

No improvement in market performance is claimed from the infrastructure alone.
