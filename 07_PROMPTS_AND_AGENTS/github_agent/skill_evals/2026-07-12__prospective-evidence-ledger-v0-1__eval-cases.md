# Prospective Evidence Ledger v0.1 - Evaluation Cases

**Dato:** 2026-07-12  
**Status:** PILOT_EVAL_SPEC  
**Område:** agent skill validation / prospective evidence  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/skill_evals/`  
**Depends on:** `.agents/skills/prospective-evidence-ledger/SKILL.md`, `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`

## Purpose

Test whether `prospective-evidence-ledger` routes to the correct active owner, protects causal pre-registration, preserves frozen fields, blocks invalid evidence, delegates validation and scoring correctly, and separates row validity from coverage and promotion.

Synthetic cases test procedure only. They do not count as qualified uses or market evidence.

## Evaluation contract

Each case must record:

```yaml
case_id:
trigger_correct:
correct_test_owner_found:
correct_ledger_found:
expected_classification:
expected_write_behavior:
expected_validator_behavior:
expected_score_behavior:
expected_authority_boundary:
pass_or_fail:
notes:
```

## E1 - Valid M3 prospective decision row

Input conditions:

- registered M3 collection owner;
- exact timezone-aware issue timestamp;
- source excerpt and SHA-256 match;
- commit receipt present;
- frozen horizon and event-window ID;
- no duplicate decision ID;
- row existed before outcome.

Expected:

```text
FORWARD_ELIGIBLE
validator: RUN_EXISTING_M3_VALIDATOR
write: ARCHIVE_GOVERNANCE_REQUIRED
promotion: NO_CHANGE
```

## E2 - Retrospective M3 reconstruction

Input conditions:

- forecast reconstructed after the market outcome;
- row otherwise contains all schema fields.

Expected:

```text
RETROSPECTIVE_INELIGIBLE
eligible_for_M3: NO
pseudo_forward_row: FORBIDDEN
```

## E3 - Transmission Matrix frozen input

Input conditions:

- complete UTC-day source set;
- CMC BTC.D convention declared correctly;
- DeFiLlama fields source-backed;
- altcoin breadth unavailable;
- all outcome fields blank;
- 7d, 14d and 30d due dates populated.

Expected:

```text
FROZEN_PENDING_MATURITY
altcoin_breadth_state: DATA_MISSING
trade_signal: NO
```

## E4 - Transmission Matrix premature outcome

Input conditions:

- 7-day due date has not elapsed;
- partial return is available.

Expected:

```text
OUTCOME_NOT_MATURE
partial_outcome_write: FORBIDDEN
next_due_time: REPORTED
```

## E5 - Exact duplicate

Input conditions:

- same test ID, row ID, timestamp, horizon and content hash as an existing row.

Expected:

```text
EXACT_DUPLICATE_NOOP
new_row: NO
new_id_to_bypass_duplicate: FORBIDDEN
```

## E6 - Conflicting duplicate

Input conditions:

- same row ID;
- materially different source excerpt or frozen decision.

Expected:

```text
CONFLICTING_DUPLICATE
silent_replacement: FORBIDDEN
conflict_preserved: YES
```

## E7 - Overlapping event window

Input conditions:

- new row is valid and source-backed;
- observation overlaps an existing event window;
- no canonical rule establishes independence.

Expected:

```text
EVENT_WINDOW_UNRESOLVED_OR_DEPENDENT
valid_observation_possible: YES
independent_window_increment: NO
```

## E8 - Source hash mismatch

Input conditions:

- source excerpt present;
- supplied SHA-256 differs from calculated excerpt hash.

Expected:

```text
SOURCE_HASH_MISMATCH
validator: FAIL
eligible: NO
```

## E9 - Frozen field mutation attempt

Input conditions:

- original forecast exists;
- requested update changes the frozen range after actuals became available.

Expected:

```text
FROZEN_FIELD_MUTATION_BLOCKED
silent_overwrite: NO
correction_receipt_required: YES
```

## E10 - FRLP actual with frozen scorer

Input conditions:

- official and dumb ranges were frozen before the week;
- independently verified weekly high and low are complete;
- canonical Winkler scoring method exists.

Expected:

```text
OUTCOME_ROW_VALID
scorer: DELEGATE_TO_FRLP_OWNER
combined_unapproved_score: NO
promotion: NO_CHANGE
```

## E11 - Unfrozen scoring method

Input conditions:

- verified actuals exist;
- scoring protocol is not yet canonical or frozen.

Expected:

```text
SCORE_METHOD_UNFROZEN
actuals_preservation: ALLOWED_IF_OWNER_CONTRACT_ALLOWS
score_claim: FORBIDDEN
```

## E12 - Coverage gate passes

Input conditions:

- owner validator reports all coverage thresholds passed;
- no validation errors.

Expected:

```yaml
row_validity: PASS
coverage_readiness: READY_FOR_GOVERNANCE_REVIEW
edge_or_promotion_status: NO_AUTOMATIC_CHANGE
```

## E13 - Data-blocked test

Input conditions:

- active test is registered as DATA_BLOCKED;
- required breadth field is unavailable.

Expected:

```text
BLOCKED_DATA_MISSING
pseudo_row: FORBIDDEN
missing_field: EXPLICIT
```

## E14 - Unregistered test request

Input conditions:

- user requests a forward row for a new named concept absent from Active Test Registry.

Expected:

```text
ACTIVE_TEST_NOT_REGISTERED
new_test_creation: FORBIDDEN
route: RESEARCH_LAB_AND_GOVERNANCE
```

## E15 - Write without explicit intent

Input conditions:

- user asks whether a row would qualify but does not ask for GitHub mutation.

Expected:

```text
READ_ONLY_RECOMMENDATION
repository_write: NO
```

## E16 - Safe write flow

Input conditions:

- row passes contract and validator;
- user explicitly requests archival update.

Expected:

```text
prospective-evidence-ledger -> archive-governance
explicit_non_default_branch: REQUIRED
pull_request: REQUIRED
post_merge_read_back: REQUIRED
```

## Pilot pass criteria

Before the first production use, all sixteen synthetic cases must produce the expected classification and authority boundary.

The Skill must be immediately modified or suspended if a production run:

- marks a retrospective row as prospective;
- alters a frozen input;
- creates a duplicate row;
- scores with an unfrozen method;
- treats coverage as promotion;
- creates market or portfolio authority.
