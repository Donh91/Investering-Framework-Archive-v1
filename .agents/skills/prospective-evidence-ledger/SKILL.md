---
name: prospective-evidence-ledger
description: 'Capture, mature, classify, validate, and route prospective evidence rows for active Investering tests and ledgers. Use when the user asks to freeze a forecast or decision, add a forward row, attach verified actuals, close an outcome horizon, update M3, FRLP, FNP, Pullback Edge, Transmission Matrix, reconcile source lineage, or check coverage readiness. Differentiator: enforces active-owner discovery, causal pre-registration, frozen-field immutability, maturity, lineage, duplicate and event-window controls, validator delegation, and no-promotion boundaries before any row is counted.'
---

# Prospective Evidence Ledger

## Purpose

Govern prospective evidence for existing registered tests and owner-defined ledgers.

The Skill verifies that a row is attached to the correct owner, existed before the outcome, preserves frozen inputs, is mature, source-backed, non-duplicative and valid under the existing contract.

It does not create tests, schemas, scores, market calls, rule promotions or portfolio actions.

## Core contract

```text
Test owner = question
Ledger owner = schema
Source = proof of what existed
Clock = maturity
Validator = row validity
Scorer = score
Governance = promotion
```

```text
VALID_ROW != PROVEN_EDGE
COVERAGE_READY != PROMOTION
SOURCE_ROW != OUTCOME_ROW
```

## Composition

```text
canonical-context-router
-> prospective-evidence-ledger
-> existing validator or scorer
-> research-lab-red-team only for interpretation or promotion review
-> archive-governance before repository writes
```

## Required sources

Read:

1. `AGENTS.md`
2. `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`
3. `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`
4. `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`
5. `01_CORE_FRAMEWORK/governance/2026-07-10__rule-and-evidence-registry__canonical.md`
6. `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`
7. the active test owner, ledger schema/header, validator, scorer and relevant source.

Do not load unrelated ledgers or the full archive.

## Trigger scope

Use for freezing inputs, adding forward rows, attaching actuals, closing horizons, updating M3/FRLP/FNP/Pullback Edge/Transmission Matrix, reconciling lineage, or checking row and coverage eligibility.

Do not use to create a test, ledger, schema, score, indicator, recurring schedule or portfolio action.

## 1. Active-test and contract gate

The target test must exist in the Active Test Registry. Otherwise return:

```text
ACTIVE_TEST_NOT_REGISTERED
```

Resolve:

```yaml
test_id:
test_status:
test_owner:
ledger_owner:
ledger_path:
row_identity_field:
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
benchmark:
promotion_condition:
kill_condition:
```

Allowed write modes:

```text
APPEND_INPUT_ROW
APPEND_OUTCOME_ROW
POPULATE_EMPTY_OUTCOME_FIELDS
APPEND_CORRECTION_ROW
READ_ONLY
```

Missing required contract fields produce `LEDGER_CONTRACT_INCOMPLETE`. Never invent contract rules.

## 2. Operation and row type

Choose one operation:

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

Choose one row type:

```text
FROZEN_INPUT_ROW
SOURCE_CLAIM_ROW
OUTCOME_ROW
SCORE_ROW
CORRECTION_ROW
COVERAGE_RECEIPT
NOT_A_LEDGER_ROW
```

Creating tests, defining scores, promoting rules and changing live state are outside authority.

## 3. Causal pre-registration

A forward-eligible row requires:

```yaml
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

A reconstructed forecast, action, horizon or invalidator is `RETROSPECTIVE_INELIGIBLE`. It may remain historical research but cannot count as a forward row.

## 4. Frozen-field integrity

Never change after freeze:

- forecast or decision;
- action label or sequence expectation;
- horizon, benchmark or invalidator;
- source excerpt, hash or issued timestamp;
- original market state or test identity.

Outcome fields may be populated only after maturity, with verified source, owner-permitted write mode, and an empty target field or formal correction path.

A correction must preserve original row ID/value, corrected value, reason, source, timestamp and receipt.

## 5. Maturity and source lineage

Verify:

```yaml
horizon_start:
horizon_end:
evaluation_timezone:
full_horizon_elapsed: YES | NO
actual_source_complete: YES | NO
revision_status:
partial_window_used: NO
source_provider:
source_convention:
source_path_or_url:
source_timestamp:
verification_timestamp:
source_content_sha256:
source_commit_receipt:
data_quality:
```

Do not treat intraday as daily close, preliminary as settled, partial as mature, missing as zero, inferred as observed, or a model summary as independent actual.

If not mature, return `OUTCOME_NOT_MATURE` and the next eligible evaluation time when derivable.

If lineage is incomplete, return `SOURCE_LINEAGE_UNRESOLVED`.

Preserve provider conventions and source conflicts. CoinMarketCap BTC.D is not TradingView `CRYPTOCAP:BTC.D`.

## 6. Missing data, duplicates and event windows

```text
DATA_MISSING = UNKNOWN
```

Missing data cannot become negative evidence, zero, inferred outcome, pseudo-row or eligibility PASS. Use `BLOCKED_DATA_MISSING` and list missing fields.

Use the owner duplicate key. If none exists, a detection-only fallback is:

```text
test_id + row_identity + issued_timestamp + horizon + source_hash
```

Classify:

```text
NO_DUPLICATE
EXACT_DUPLICATE_NOOP
CONFLICTING_DUPLICATE
DUPLICATE_ID_DIFFERENT_SOURCE
```

A new ID cannot bypass a duplicate.

For event windows record ID, overlap, related rows and independence basis. A new row ID does not prove independence. Only the owner rule or validator determines coverage counting.

## 7. Procedural eligibility

Use one classification:

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

These are Skill-output labels. Do not insert them into a ledger unless its schema permits them.

## 8. Validator and scorer delegation

Use the owner-defined validator. Do not manually reproduce executable validation logic.

Current M3 controls:

```text
04_MARKET_LEARNING/truth_layer/tools/validate_m3_coverage.py
.github/workflows/validate_m3_forward_ledger.yml
```

A validator failure blocks completion. No validator means `VALIDATOR_UNAVAILABLE` and no claim of a validated row.

This Skill does not invent scoring. A score requires a frozen method, formula owner, benchmark, complete actuals and score category. Otherwise return `SCORE_METHOD_UNFROZEN`.

## 9. Transmission Matrix rule

For Transmission Matrix rows obey:

```text
04_MARKET_LEARNING/shadow_protocols/2026-07-12__transmission-matrix-forward-falsification-protocol-v0-1__canonical.md
```

Freeze inputs, leave outcomes empty until maturity, keep missing alt breadth as `DATA_MISSING`, preserve CMC/DeFiLlama semantics, reference the original `transmission_row_id`, and do not treat descriptive states as trade signals.

## 10. Coverage separation

Where supported report before/after values for eligible rows, forward rows, independent windows, source families and largest-window concentration, plus coverage-gate and governance-review readiness.

Always separate:

```yaml
row_validity:
coverage_readiness:
edge_or_promotion_status:
```

Validator PASS is not performance PASS. Coverage readiness is not promotion.

## 11. Evidence decision manifest

Before a write prepare:

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

## 12. Write boundary

This Skill may prepare a row and validation result. It may write only when:

```yaml
user_write_intent: EXPLICIT
archive_governance_invoked: YES
target_branch_verified: YES
```

`archive-governance` owns branch, PR, read-back, discoverability and backup-scope controls.

## Required output

Return a concise `PROSPECTIVE EVIDENCE LEDGER VERDICT` containing:

- test, owner, ledger and operation;
- contract, row identity and lifecycle state;
- causality, maturity and lineage;
- duplicate, event-window and missing-field status;
- procedural eligibility and validator result;
- coverage delta and score status;
- separate row-validity, coverage-readiness and promotion fields;
- write plan and next due action.

Expand only for conflicts, failures or corrections.

## Hard rules

- No new test, schema or score.
- No retrospective row counted as prospective.
- No backdating, interpolation or missing-to-zero conversion.
- No source or initialization row counted as outcome evidence.
- No frozen input changed after outcomes.
- No silent outcome overwrite or duplicate-ID bypass.
- No overlapping event automatically counted as independent.
- No validator or coverage PASS presented as edge.
- No market call, portfolio action or automatic ratification.
- No repository write without explicit intent and `archive-governance`.
- No recurring automation created by this Skill.

## Validation loop

1. Verify registered test, owner, ledger and complete contract.
2. Verify row identity, exact timestamp and causal ordering.
3. Verify frozen horizon, benchmark and fields.
4. Verify full maturity and source lineage.
5. Verify hashes, receipts, duplicates and event windows.
6. Run the existing validator.
7. Run the scorer only when frozen.
8. Recalculate owner-defined coverage.
9. Separate validity, readiness and promotion.
10. Verify zero market and portfolio authority.
11. Invoke `archive-governance` before writing.
12. Read back the final row and receipt after merge.

A failed check requires correction and full re-validation.

## Failure modes

```text
ACTIVE_TEST_NOT_REGISTERED
LEDGER_OWNER_UNRESOLVED
LEDGER_CONTRACT_INCOMPLETE
SCHEMA_INCOMPLETE
TIMESTAMP_NOT_EXACT
RETROSPECTIVE_INELIGIBLE
FROZEN_FIELD_MUTATION_BLOCKED
OUTCOME_NOT_MATURE
SOURCE_LINEAGE_UNRESOLVED
SOURCE_HASH_MISMATCH
EXACT_DUPLICATE_NOOP
CONFLICTING_DUPLICATE
EVENT_WINDOW_UNRESOLVED
BLOCKED_DATA_MISSING
VALIDATOR_UNAVAILABLE
VALIDATOR_FAILED
SCORE_METHOD_UNFROZEN
OWNER_BLOCKED
READ_ONLY_RECOMMENDATION
WRITE_BRANCH_UNVERIFIED
```

## Pilot metrics and kill criteria

Record trigger, test/ledger owner accuracy, contract completeness, causal classification, frozen-field preservation, maturity, lineage, duplicate prevention, event-window classification, validator execution, blocked invalid rows, blocked unsupported scores/promotions, manual corrections and false-eligible incidents.

Keep only if the Skill increases valid prospective rows and reduces hindsight, pseudo-rows, duplicates and manual repair.

Immediately modify or suspend if it marks a retrospective row eligible, changes frozen input, creates duplicate evidence, misses material lineage, overstates independence, becomes a parallel scorer, treats coverage as edge, creates tests without authority or produces portfolio language.

Review after 10 qualified stack uses or the existing pilot review date, whichever comes first. Require at least three real uses before KEEP is justified.
