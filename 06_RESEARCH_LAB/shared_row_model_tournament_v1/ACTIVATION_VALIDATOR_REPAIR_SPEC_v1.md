# Shared Row Tournament - Activation Validator Repair Spec v1

**Date:** 2026-10-05  
**Status:** DESIGN_FROZEN / NOT_IMPLEMENTED  
**Authority:** RESEARCH_ONLY / NON_CANONICAL  
**Framework main at freeze:** `0d1e12638761e00d151f2444bb5f99c1f7fba1ee`

## Purpose

Permit the existing Shared Row Tournament Research Gate to validate either of two legitimate repository phases:

1. pre-activation quarantine;
2. post-review prospective collection.

The repair must not weaken any P0 causal-binding or negative-control invariant.

The repair itself must not activate collection.

## Current blocker

`scripts/research/validate_core_prospective_freeze.py` currently asserts only the quarantine configuration:

- contract `prospective_eligibility_status = CONTAINMENT_SENTINEL_NOT_AN_ACTIVATION_FLOOR`;
- core rule `containment_floor_sentinel = true`;
- core rule `collection_state = QUARANTINED_PENDING_POST_REPAIR_EVIDENCE`.

The runtime materializer/controller/monitor and test fixtures already support the intended active state:

- `ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION`;
- `containment_floor_sentinel = false`;
- `ACTIVE_POST_REPAIR_FLOOR`.

Therefore a legitimate activation PR would currently fail the top-level validator even if all runtime invariants were correct.

## Allowed implementation scope

Primary code:
- `scripts/research/validate_core_prospective_freeze.py`

Test updates:
- `tests/research/test_shared_row_p0_integrity.py`
- a new narrow validator-state test is allowed only if cleaner than extending the existing file.

Contract/state files must not be changed in the validator-repair PR except documentation describing the future activation transition.

Forbidden in this repair:
- collection-state change;
- prospective floor assignment;
- threshold changes;
- candidate changes;
- model weight changes;
- owner changes;
- source substitution;
- market or portfolio authority;
- outcome/scoring semantics changes.

## Required validator state machine

### MODE_A_QUARANTINED

Accept only if all existing quarantine invariants hold:

- `prospective_eligibility_status = CONTAINMENT_SENTINEL_NOT_AN_ACTIVATION_FLOOR`;
- `collection_state = QUARANTINED_PENDING_POST_REPAIR_EVIDENCE`;
- `containment_floor_sentinel = true`;
- current 2026-09-30 sentinel remains non-active;
- no eligible rows are implied by configuration;
- `no_backdating = true`;
- core C01-C07 decision contracts remain READY;
- P0 repaired core-family states remain intact.

This mode must preserve current fail-closed behavior byte-for-semantics.

### MODE_B_ACTIVE_POST_REPAIR

Accept only if every item below is true.

#### State agreement

- contract `prospective_eligibility_status = ACTIVE_POST_REPAIR_FLOOR`;
- contract `prospective_activation.collection_state = ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION`;
- freeze `core_activation_rule.collection_state = ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION`;
- freeze `core_activation_rule.containment_floor_sentinel = false`.

No mixed quarantine/active state may pass.

#### One frozen future floor

The exact same ISO timestamp must appear in:
- contract `prospective_eligibility_start`;
- freeze `core_activation_rule.prospective_eligibility_start`;
- each of the three core families' `prospective_eligibility_start`;
- runtime status after the later activation PR.

The validator must reject any mismatch.

#### Floor chronology

The floor must be strictly later than:
- P0 implementation merge time `2026-08-23T08:18:29Z`;
- the source-readiness evidence set used by the activation review;
- the activation decision/freeze time.

The activation PR must record a machine-readable `readiness_evidence_cutoff_utc`.

Required rule:

`floor > max(implementation_merge_time, readiness_evidence_cutoff_utc, activation_freeze_time_utc)`

No equality.

No reuse of the 2026-09-30 containment sentinel.

No retrospective eligibility.

#### Activation provenance

Require non-empty immutable references for:
- activation PR number;
- activation review/adjudication path;
- readiness evidence cutoff;
- readiness evidence commit;
- validator-repair version;
- activation freeze timestamp.

The activation PR number may be self-referential only if the repository's existing convention safely supports it. Otherwise use a stable activation receipt written immediately after merge and keep collection fail-closed until that receipt is present.

Do not weaken the gate merely to avoid the self-reference problem.

#### Core families

Exactly the frozen core family set remains activation-capable:
- ETHBTC_PERSISTENCE;
- BREADTH_SURVIVAL;
- BTCD_PATH_RECLAIM.

Each must remain:
- status READY;
- candidate_decision_contract_status READY;
- repair_state P0_REPAIRED_AWAITING_ACTIVATION_OR_ACTIVE.

C01-C07 candidate definitions must remain unchanged.

#### Optional families

ETF, leverage, stablecoin deployment, CFGI and any Full Stack candidates must preserve their own current BLOCKED/PARTIAL/independent activation states.

Activating the core must not make optional candidates eligible.

#### Authority firewall

Require:
- research-only / non-canonical authority unchanged;
- canonical_effect = false where represented;
- no portfolio execution authority;
- no automatic promotion/retirement authority.

## Required new negative controls

The validator-repair PR must add explicit tests that fail for:

1. ACTIVE contract + quarantine freeze state.
2. Quarantine contract + ACTIVE freeze state.
3. ACTIVE collection + sentinel=true.
4. Quarantine collection + sentinel=false.
5. active floor equal to implementation merge time.
6. active floor before readiness evidence cutoff.
7. active floor equal to readiness evidence cutoff.
8. active floor before activation freeze time.
9. mismatch between contract floor and core-rule floor.
10. mismatch between any core-family floor and core-rule floor.
11. missing activation provenance.
12. malformed activation provenance.
13. C01-C07 definition mutation.
14. core family not READY.
15. optional blocked family accidentally becoming core-eligible.
16. no_backdating=false.
17. activation that would make any pre-floor ledger row eligible.
18. reuse of 2026-09-30 containment sentinel as active floor.

Required positive controls:

A. existing quarantine repository state passes unchanged.
B. a fully valid synthetic ACTIVE configuration passes.
C. existing P0 production-shaped source-binding tests still pass.
D. outcome/provenance negative controls still pass.
E. weekly/relevance/monitor consumers remain fail-closed on invalid rows.

## Required gate behavior

`.github/workflows/shared-row-tournament-research-gate.yml`

must remain mandatory and unchanged in strength.

After validator repair, the same gate must be capable of passing:
- the current quarantine state;
- a later correctly specified active state.

No test may be skipped conditionally merely because the state is ACTIVE.

## Separate activation PR after repair

The validator-repair PR and activation PR must be separate changes.

Activation PR must:

1. fresh-reproduce source readiness;
2. record a new readiness evidence cutoff;
3. choose a genuinely future floor after the review;
4. change only the already-designed state/floor/provenance fields needed to activate;
5. rerun the full Research Gate;
6. prove zero rows become eligible before the new floor;
7. preserve all old rows as quarantined/excluded;
8. leave optional families unchanged;
9. leave all market/portfolio authority false.

## Rollback rule

If post-activation collection cannot bind all three core owners under the same cutoff, the individual row is NOT_ELIGIBLE.

Do not automatically disable the whole program for ordinary source missingness.

Re-quarantine the program only for:
- integrity-contract violation;
- provenance/hash reconstruction failure indicating systemic corruption;
- repeated material source semantic drift;
- validator/gate regression;
- explicit owner adjudication.

A re-quarantine must never rewrite already frozen valid rows.

## Current evidence basis

Readiness review:
`06_RESEARCH_LAB/shared_row_model_tournament_v1/ACTIVATION_READINESS_REVIEW_2026-10-05.md`

Activation adjudication:
`06_RESEARCH_LAB/shared_row_model_tournament_v1/ACTIVATION_ADJUDICATION_2026-10-05.md`

PR #1498:
full current Shared Row Tournament Research Gate PASS before merge.

## Terminal design state

`VALIDATOR_REPAIR_SPEC=FROZEN`

`IMPLEMENTATION=NOT_STARTED`

`COLLECTION_STATE=QUARANTINED`

`ACTIVE_FLOOR=NOT_SELECTED`

`BACKDATING=FORBIDDEN`

`CANONICAL_EFFECT=NONE`

`PORTFOLIO_EFFECT=NONE`
