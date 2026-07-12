---
name: prospective-evidence-ledger
description: 'Capture, mature, classify, validate, and route prospective evidence rows for active Investering tests and ledgers. Use when the user asks to freeze a forecast or decision, add a forward row, attach verified actuals, close an outcome horizon, update M3, FRLP, FNP, Pullback Edge, Transmission Matrix, or another registered forward ledger, reconcile source lineage, or check coverage readiness. Differentiator: enforces active-owner discovery, causal pre-registration, frozen-field immutability, outcome maturity, source lineage, duplicate and event-window controls, existing-validator delegation, and strict no-promotion boundaries before any row is counted.'
---

# Prospective Evidence Ledger

## Purpose

Govern the lifecycle of prospective evidence for existing Investering tests and ledgers.

This skill determines whether a proposed input, source, decision or outcome row is:

- attached to the correct active owner;
- causally prospective;
- frozen before the outcome;
- mature at the declared horizon;
- source-backed;
- non-duplicative;
- valid under the owner-defined schema;
- eligible for the relevant coverage calculation.

The skill does not create tests, invent schemas, define scoring methods, interpret edge, ratify rules, make market calls or produce portfolio actions.

## Core principle

```text
The test owner defines the question.
The ledger owner defines the schema.
The source proves what existed.
The clock determines maturity.
The validator determines row validity.
The scorer determines the score.
Governance determines promotion.
```

A valid row is not proof of edge.

A passed coverage gate is not rule promotion.

A source-backed claim is not an outcome row.

## Required composition

Run in this order:

```text
canonical-context-router
-> prospective-evidence-ledger
-> existing domain validator or scorer
-> archive-governance before any repository write
```

Use `research-lab-red-team` only when the user asks what the collected evidence means, whether a test should survive, or whether promotion should be considered.

## Mandatory read order

Before processing a row:

1. Read `AGENTS.md`.
2. Run `canonical-context-router`.
3. Read `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`.
4. Read `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`.
5. Read `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`.
6. Read `01_CORE_FRAMEWORK/governance/2026-07-10__rule-and-evidence-registry__canonical.md`.
7. Read `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`.
8. Read the active test owner.
9. Read the ledger schema or current header.
10. Read the owner-defined validation and scoring rules.
11. Read the current ledger state and relevant source material.

Do not load unrelated ledgers or the full archive.

## Trigger scope

Use this skill for requests such as:

```text
Add this forward row
Freeze this decision
Update the M3 ledger
Attach the verified actual
Close the 7-day outcome
Mature the Pullback Edge event
Update FRLP with the weekly actual
Add an FNP opportunity-cost row
Update the Transmission Matrix
Check whether this row is eligible
Reconcile the forecast lineage
Run the coverage validator
```

Do not use this skill to:

- create a new test;
- create a new engine or shadow layer;
- design a new market indicator;
- define an unfrozen score;
- ingest an unrelated research package;
- interpret general market state;
- ratify a framework rule;
- schedule automated collection;
- generate a portfolio action.

## Active-test gate

The target test must exist in:

```text
06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md
```

Resolve:

```yaml
test_id:
test_status:
question:
owner:
required_fields:
benchmark:
blocked_by:
next_review:
promotion_condition:
kill_condition:
```

If the test is absent, stop with:

```text
ACTIVE_TEST_NOT_REGISTERED
```

Do not create a registry entry inside this skill. A new or replacement test requires a separate Research Lab and governance decision.

## Ledger-contract discovery

Before preparing or validating any row, construct:

```yaml
test_id:
test_owner:
ledger_owner:
ledger_path:
ledger_status:
row_identity_field:
row_type:
schema_fields:
frozen_input_fields:
mutable_outcome_fields:
correction_fields:
effective_horizon:
evaluation_timezone:
maturity_rule:
source_contract:
duplicate_key:
event_window_rule:
validator_path:
scorer_path:
write_mode:
promotion_gate:
kill_condition:
```

Allowed `write_mode` values:

```text
APPEND_INPUT_ROW
APPEND_OUTCOME_ROW
POPULATE_EMPTY_OUTCOME_FIELDS
APPEND_CORRECTION_ROW
READ_ONLY
```

The owner file, ledger schema or canonical protocol must explicitly support the selected mode.

If any field required for the requested operation is unresolved, return:

```text
LEDGER_CONTRACT_INCOMPLETE
```

Do not invent a schema, scorer, maturity rule or write mode.

## Operation classification

Classify the request as exactly one primary operation:

```text
FREEZE_INPUT
APPEND_SOURCE_ROW
ATTACH_OUTCOME
CLOSE_HORIZON
RECONCILE_LINEAGE
VALIDATE_ROW
VALIDATE_COVERAGE
CORRECT_WITH_AUDIT_TRAIL
READ_ONLY_STATUS
```

The following are outside authority:

```text
CREATE_TEST
DEFINE_NEW_SCORE
PROMOTE_RULE
CHANGE_LIVE_STATE
CREATE_PORTFOLIO_ACTION
```

Route those requests to the appropriate owner instead.

## Evidence-row types

Classify the proposed material as one of:

```text
FROZEN_INPUT_ROW
SOURCE_CLAIM_ROW
OUTCOME_ROW
SCORE_ROW
CORRECTION_ROW
COVERAGE_RECEIPT
NOT_A_LEDGER_ROW
```

Do not collapse these categories.

```text
SOURCE_CLAIM_ROW != OUTCOME_ROW
FROZEN_INPUT_ROW != VALID_OUTCOME_ROW
COVERAGE_RECEIPT != PERFORMANCE_EVIDENCE
```

## Causal pre-registration gate

A prospective row is eligible only when the required input existed before the relevant outcome became observable.

Verify:

```yaml
issued_timestamp_present: YES
issued_timestamp_timezone_aware: YES
source_existed_before_outcome_window: YES
effective_horizon_frozen: YES
forecast_or_decision_frozen: YES
source_path_present: YES
source_excerpt_or_machine_row_present: YES
source_hash_present_when_required: YES
commit_receipt_present_when_required: YES
retrospective_reconstruction: NO
```

If the timestamp lacks an exact timezone, the row cannot be prospectively eligible.

If the forecast, action, horizon or invalidator was reconstructed after the event, classify:

```text
RETROSPECTIVE_INELIGIBLE
```

The material may remain historical research but may not count as a forward row.

## Frozen-field immutability

Once an input row has been frozen, never change:

- forecast values;
- action labels;
- sequence expectations;
- effective horizon;
- invalidators;
- benchmark;
- source excerpt;
- original source hash;
- original issued timestamp;
- original market state;
- original test identity.

Outcome fields may only be populated when:

1. the horizon is mature;
2. the canonical owner allows the write mode;
3. the source is verified;
4. the existing field is empty or a formal correction process is used.

Never silently replace a non-empty outcome.

Corrections must preserve:

```yaml
original_row_id:
original_value:
corrected_value:
correction_reason:
correction_source:
correction_timestamp:
correction_receipt:
```

Use an owner-defined correction row or receipt. Preserve Git history.

## Row lifecycle

Use these lifecycle states in the Skill output:

```text
DRAFT_NOT_WRITTEN
FROZEN_PENDING_MATURITY
MATURED_UNRECONCILED
OUTCOME_ATTACHED_PENDING_VALIDATION
VALIDATED_ELIGIBLE
VALIDATED_INELIGIBLE
VALIDATION_FAILED
BLOCKED_DATA_MISSING
CLOSED
```

Do not write these labels into a ledger unless its canonical schema supports them.

## Outcome-maturity gate

Before attaching or closing an outcome, verify:

```yaml
horizon_start:
horizon_end:
evaluation_timezone:
current_or_source_cutoff_time:
full_horizon_elapsed: YES | NO
actual_source_complete: YES | NO
actual_source_revision_status:
partial_window_used: NO
```

A horizon must contain the full owner-defined period.

Do not treat:

- intraday values as daily closes;
- preliminary prints as settled actuals;
- a partially elapsed horizon as mature;
- a missing endpoint as zero;
- an inferred value as observed actual.

If the horizon has not closed, return:

```text
OUTCOME_NOT_MATURE
```

State the exact next eligible evaluation time when it can be derived from the frozen contract.

## Source-lineage gate

Record, where applicable:

```yaml
source_provider:
source_convention:
source_path_or_url:
source_file:
source_run_or_forecast_id:
source_timestamp:
verification_timestamp:
exact_source_excerpt:
source_content_sha256:
source_commit_receipt:
source_status:
data_quality:
revision_status:
```

Rules:

- Use the source convention declared by the owner.
- Do not silently substitute another provider.
- Do not relabel CoinMarketCap BTC.D as TradingView `CRYPTOCAP:BTC.D`.
- Do not use a model summary as an independent actual.
- Do not use conversation memory when repository or original-source evidence exists.
- Do not treat a later archive summary as proof of the original issue timestamp unless lineage is explicit.
- Preserve source conflicts rather than choosing the convenient value.

If lineage is incomplete, classify:

```text
SOURCE_LINEAGE_UNRESOLVED
```

## Missing-data discipline

```text
DATA_MISSING = UNKNOWN
```

Never convert missing data into:

- a negative signal;
- a failed test;
- a zero;
- an inferred outcome;
- a valid pseudo-row;
- an eligibility PASS.

If required data is unavailable, use:

```text
BLOCKED_DATA_MISSING
```

and identify the exact missing fields.

## Duplicate and idempotency gate

Before any proposed write, construct the owner-defined duplicate key.

When no owner-defined key exists, use only for detection, not as a new canonical rule:

```text
test_id
+ row_identity
+ issued_timestamp
+ effective_horizon
+ source_content_sha256
```

Classify:

```text
NO_DUPLICATE
EXACT_DUPLICATE_NOOP
CONFLICTING_DUPLICATE
DUPLICATE_ID_DIFFERENT_SOURCE
```

Rules:

- An exact duplicate creates no new row.
- The same row ID with different material content is a conflict.
- Do not generate a new ID merely to bypass a duplicate.
- Preserve both sources when a genuine source conflict exists.

## Event-window independence

When a test uses event windows, record:

```yaml
event_window_id:
independent_event_window:
overlap_start:
overlap_end:
overlapping_row_ids:
independence_basis:
```

Never infer independence from a new row ID.

Overlapping observations may remain valid observations while being non-independent for coverage or sample-diversity purposes.

Use:

```text
EVENT_WINDOW_INDEPENDENT
EVENT_WINDOW_DEPENDENT
EVENT_WINDOW_UNRESOLVED
```

Only the owner validator or frozen event-window rule may determine how the row counts.

## Eligibility classification

The Skill may assign one procedural classification:

```text
FORWARD_ELIGIBLE
SOURCE_BACKED_NOT_OUTCOME
PENDING_MATURITY
RETROSPECTIVE_INELIGIBLE
SOURCE_LINEAGE_UNRESOLVED
DATA_MISSING
DUPLICATE_NOOP
CONFLICTING_DUPLICATE
EVENT_WINDOW_DEPENDENT
SCHEMA_INCOMPLETE
SCORE_METHOD_UNFROZEN
VALIDATOR_FAILED
OWNER_BLOCKED
```

These are Skill-output classifications. Do not insert them into a ledger unless the canonical schema contains the relevant field and allows the value.

## Validator delegation

Use the existing owner-defined validator. Do not reproduce validator logic manually when executable control code exists.

For current M3 work, the authoritative validator is:

```text
04_MARKET_LEARNING/truth_layer/tools/validate_m3_coverage.py
```

and the current workflow is:

```text
.github/workflows/validate_m3_forward_ledger.yml
```

Respect its current ledger paths, source requirements, hash checks, timestamp checks, duplicate checks, event-window calculations and coverage gates.

A validator failure prevents completion.

If no validator exists, report:

```text
VALIDATOR_UNAVAILABLE
```

and limit the result to contract-level review. Do not claim a validated row.

## Scoring delegation

This skill does not invent or modify scoring.

Before calculating a score, verify:

```yaml
scoring_method_frozen: YES
scoring_formula_owner:
benchmark_frozen: YES
required_actuals_complete: YES
score_category:
```

If no frozen scorer exists, return:

```text
SCORE_METHOD_UNFROZEN
```

Raw actuals may still be preserved when the ledger contract allows them.

Never combine separately governed categories merely to produce one attractive score.

## Current special protocol rule

When processing Transmission Matrix rows, obey:

```text
04_MARKET_LEARNING/shadow_protocols/2026-07-12__transmission-matrix-forward-falsification-protocol-v0-1__canonical.md
```

In particular:

- freeze inputs at row creation;
- leave outcomes empty until maturity;
- do not infer missing altcoin breadth;
- preserve the declared CMC and DeFiLlama semantics;
- attach outcomes through the protocol-defined reference to the original `transmission_row_id`;
- do not treat the descriptive state label as a trade signal;
- do not discuss promotion before the protocol gate permits governance review.

## Coverage calculation

Report coverage separately from performance.

Required output fields where supported:

```yaml
eligible_rows_before:
eligible_rows_after:
forward_eligible_rows_before:
forward_eligible_rows_after:
independent_event_windows_before:
independent_event_windows_after:
source_families_before:
source_families_after:
largest_window_concentration_before:
largest_window_concentration_after:
coverage_gate_pass:
ready_for_governance_review:
```

Rules:

- A schema row is not an eligible row.
- A source row is not an outcome row.
- An initialization row is not automatically eligible.
- A validator PASS is not a performance PASS.
- `ready_for_governance_review` is not rule promotion.
- Coverage improvement is not evidence that the tested idea works.

## Three-layer result separation

Every run must report:

```yaml
row_validity:
coverage_readiness:
edge_or_promotion_status:
```

Example:

```yaml
row_validity: PASS
coverage_readiness: NOT_READY
edge_or_promotion_status: NO_CHANGE
```

Never compress these into one general `PASS`.

## Evidence decision manifest

Before any write, prepare:

```yaml
test_id:
test_owner:
ledger_path:
operation:
row_type:
row_id:
original_row_reference:
ledger_contract_status:
causal_pre_registration:
frozen_fields_preserved:
maturity_status:
source_lineage_status:
duplicate_status:
event_window_status:
procedural_eligibility:
validator_path:
validator_result:
scorer_path:
score_status:
coverage_before:
coverage_after:
write_intent:
write_paths:
next_due_action:
authority_boundary:
```

This manifest may appear in the PR body or implementation receipt when the change is material.

## Repository-write boundary

This skill may prepare a row and validation result.

It must not write to GitHub unless:

```yaml
user_write_intent: EXPLICIT
archive_governance_invoked: YES
target_branch_verified: YES
```

All GitHub writes must pass through `archive-governance`.

The repository branch, PR, read-back, addendum registration and backup-scope controls remain owned by that Skill.

## Required output

Return:

```markdown
# PROSPECTIVE EVIDENCE LEDGER VERDICT

## Context
Test ID:
Test status:
Test owner:
Ledger owner:
Ledger path:
Operation:

## Contract
Schema:
Row identity:
Frozen fields:
Outcome fields:
Horizon:
Timezone:
Validator:
Scorer:

## Proposed or referenced row
Row ID:
Row type:
Original row reference:
Lifecycle state:

## Causality
Issued before outcome:
Timestamp quality:
Retrospective reconstruction:
Frozen horizon:
Frozen benchmark:

## Maturity
Evaluation due:
Full horizon elapsed:
Actual source complete:
Revision status:

## Source lineage
Provider:
Convention:
Source:
Source hash:
Commit receipt:
Data quality:

## Integrity
Duplicate status:
Event-window status:
Frozen fields preserved:
Missing fields:

## Eligibility
Procedural classification:
Eligible for target ledger:
Reason:

## Validation
Validator:
Validation result:
Errors:

## Coverage delta
Rows before / after:
Independent windows before / after:
Source families before / after:
Concentration before / after:
Coverage gate:

## Scoring
Scorer:
Score status:
Score:
Benchmark:

## Authority boundary
Row validity:
Coverage readiness:
Edge or promotion status:
Market call:
Portfolio action:
Automatic ratification:

## Write plan
Write intent:
Paths:
Required branch:
Next skill:

## Next due action
```

Keep the output concise when the row is straightforward. Expand only when a conflict, failure or correction exists.

## Hard rules

- No new test creation.
- No new scoring method.
- No schema invention.
- No retrospective row counted as prospective.
- No backdating.
- No silent interpolation.
- No missing value converted to zero.
- No source row counted as outcome.
- No initialization row counted as evidence.
- No frozen input changed after outcome observation.
- No non-empty outcome silently overwritten.
- No duplicate ID bypass.
- No overlapping event automatically counted as independent.
- No score without a frozen canonical method.
- No validator PASS presented as edge.
- No coverage PASS presented as promotion.
- No market call.
- No portfolio action.
- No automatic rule ratification.
- No repository write without explicit user intent and `archive-governance`.
- No automation or recurring scheduling created by this Skill.

## Validation loop

Before completing:

1. Verify the test exists in the Active Test Registry.
2. Verify the current owner and ledger path.
3. Verify the ledger contract is complete for the requested operation.
4. Verify the row identity is unique or correctly linked to an original row.
5. Verify issued timestamp and timezone.
6. Verify the input predates the outcome.
7. Verify the horizon and benchmark were frozen.
8. Verify no frozen field changed.
9. Verify full outcome maturity.
10. Verify source provider, convention and lineage.
11. Verify source hash and commit receipt when required.
12. Verify duplicate and source-conflict status.
13. Verify event-window independence classification.
14. Run the existing validator.
15. Run the existing scorer only when frozen and applicable.
16. Recalculate coverage using the owner-defined method.
17. Separate row validity, coverage readiness and promotion status.
18. Verify no market or portfolio authority was created.
19. Invoke `archive-governance` before any write.
20. Read back the final written row and validator receipt after merge.

A failed check requires correction and a complete re-run.

## Failure modes

- **Test missing from registry** -> `ACTIVE_TEST_NOT_REGISTERED`
- **Owner unresolved** -> `LEDGER_OWNER_UNRESOLVED`
- **Contract incomplete** -> `LEDGER_CONTRACT_INCOMPLETE`
- **Required schema field absent** -> `SCHEMA_INCOMPLETE`
- **Timestamp not exact** -> `TIMESTAMP_NOT_EXACT`
- **Input created after outcome began** -> `RETROSPECTIVE_INELIGIBLE`
- **Horizon not mature** -> `OUTCOME_NOT_MATURE`
- **Source missing** -> `SOURCE_LINEAGE_UNRESOLVED`
- **Source hash mismatch** -> `SOURCE_HASH_MISMATCH`
- **Duplicate row** -> `EXACT_DUPLICATE_NOOP`
- **Conflicting duplicate** -> `CONFLICTING_DUPLICATE`
- **Event overlap unresolved** -> `EVENT_WINDOW_UNRESOLVED`
- **Required data missing** -> `BLOCKED_DATA_MISSING`
- **Validator absent** -> `VALIDATOR_UNAVAILABLE`
- **Validator error** -> `VALIDATOR_FAILED`
- **Scoring method not frozen** -> `SCORE_METHOD_UNFROZEN`
- **Owner blocks collection** -> `OWNER_BLOCKED`
- **Write intent not explicit** -> `READ_ONLY_RECOMMENDATION`
- **Repository branch unsafe** -> defer to `archive-governance` and stop with `WRITE_BRANCH_UNVERIFIED`

## Pilot metrics

For each qualified use, record:

```yaml
skill_name: prospective-evidence-ledger
run_date:
test_id:
operation:
trigger_correct: YES | NO | PARTIAL
correct_test_owner_found: YES | NO | PARTIAL
correct_ledger_found: YES | NO | PARTIAL
ledger_contract_complete: YES | NO
causal_pre_registration_correct: YES | NO | NOT_APPLICABLE
frozen_fields_preserved: YES | NO | NOT_APPLICABLE
maturity_classification_correct: YES | NO | NOT_APPLICABLE
source_lineage_complete: YES | NO | PARTIAL
duplicate_prevented: YES | NO | NOT_APPLICABLE
event_window_classification_correct: YES | NO | NOT_APPLICABLE
validator_executed: YES | NO | NOT_APPLICABLE
invalid_forward_row_blocked: YES | NO | NOT_APPLICABLE
unsupported_score_blocked: YES | NO | NOT_APPLICABLE
unsupported_promotion_blocked: YES | NO
manual_corrections_required:
false_eligible_incidents:
write_governance_result:
final_repository_state:
notes:
```

## Pilot success criteria

Keep the Skill only if it:

- increases valid prospective row production;
- reduces retrospective reconstruction;
- prevents frozen-field mutation;
- prevents source rows from being counted as outcomes;
- catches duplicates and event-window dependence;
- routes scoring to the correct owner;
- produces fewer manual corrections than the prior workflow;
- does not create parallel ledger authority.

## Modification or kill criteria

Modify, suspend or kill the Skill if:

- it marks any retrospective row as forward eligible;
- it changes a frozen forecast or decision;
- it creates duplicate evidence rows;
- it repeatedly misses source-lineage defects;
- it overstates event-window independence;
- it becomes a parallel scorer;
- it treats coverage readiness as edge;
- it creates new tests or schemas without authority;
- it produces portfolio language;
- it requires repeated ledger-specific exceptions that should remain domain-owned;
- it increases archive inflation or manual repair.

## Pilot review

Review under `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md` after:

- 10 qualified uses, or
- the existing Agent Skills pilot review date,

whichever occurs first.

Recommended first pilot cases:

1. one valid M3 prospective decision row;
2. one M3 retrospective row that must be blocked;
3. one Transmission Matrix frozen input row;
4. one Transmission Matrix maturity check;
5. one duplicate row attempt;
6. one overlapping event-window case;
7. one source-hash mismatch;
8. one FRLP actual with an available frozen scorer;
9. one ledger with an unfrozen score method;
10. one coverage gate that passes but cannot self-promote.
