# Shared Row Tournament activation adjudication — 2026-10-05

**Verdict:** `ACTIVATION_REQUIRES_ONE_SMALL_REPAIR`  
**Authority:** RESEARCH_ONLY / NON_CANONICAL  
**Framework main:** `eb332a9e4bdeb0d38b6cba392a88314ab1bd64d6`  
**Activation executed:** NO  
**Backdating allowed:** NO

## Executive conclusion

The core prospective shared-row tournament is no longer blocked by missing source evidence.

Current main has enough post-repair evidence to satisfy the three mechanical owner requirements simultaneously, and the current P0 Research Gate has been rerun successfully through PR #1498.

However, a real activation PR cannot yet be safely merged because the top-level validator still hardcodes the quarantine state as the only valid repository configuration.

The runtime engines themselves already understand the intended ACTIVE state.

Therefore the remaining blocker is a small validator state-machine repair, not a market-data gap or model/research redesign.

## Current owner readiness

### ETHBTC_PERSISTENCE
PASS.

Independent current-main reconstruction:
- 168 unique direct hourly timestamps;
- 2026-09-28T14:00:00Z -> 2026-10-05T13:00:00Z;
- exact 167-hour span;
- zero gaps;
- zero duplicates;
- zero non-PASS spot rows;
- all source-window availability legal under a common Oct-05 cutoff;
- all source evidence after the 2026-08-23T08:18:29Z repair boundary.

### BREADTH_SURVIVAL
PASS.

Dated immutable bundle:
`03_DAILY_CAPTURE_LOGS/breadth_rich/2026/10/2026-10-05/`

Verified:
- C5E_TOP100_BREADTH_OWNER_v1_2;
- TOP100_FILTERED_STABLE_EXCLUSION_RICH_BREADTH_v1_2;
- COINGECKO_MARKET_CAP;
- 100 constituents;
- receipt PASS;
- aggregate replay PASS;
- run-id agreement;
- membership-hash agreement;
- manifest present;
- captured 2026-10-05T12:17:44.779378Z.

### BTCD_PATH_RECLAIM
PASS.

Current CMC direct-source ledger contains the required settled chronological prints before the common cutoff, including:
- 2026-10-02;
- 2026-10-03;
- 2026-10-04.

Rows are:
- CoinMarketCap;
- CMC direct-source convention;
- SETTLED_COMPLETE_DATE;
- PASS;
- PUBLIC_SOURCE_BACKED;
- verified 2026-10-05T12:34:53Z.

## Fresh P0 gate

Documentation-only PR #1498 intentionally triggered the current:
`.github/workflows/shared-row-tournament-research-gate.yml`

Gate result:
`PASS`

Successful steps included:
- Python compile gate;
- tournament contract validation;
- `validate_core_prospective_freeze.py`;
- `validate_next_action_controller.py`;
- controller status-only;
- maturation;
- weekly tournament;
- relevance;
- monitor;
- next-action dry run.

Storage gates also passed.

PR #1498 was merged only after these checks passed.

## Old PR #519 review findings

Two post-merge automated review findings were rechecked on current main.

### Frozen row provenance
RESOLVED on current main.

`shared_row_outcome_owner.py` now calls:
`verify_frozen_provenance(row)`

before source reconstruction and outcome maturation.

### Consumer integrity population
RESOLVED on current main.

`shared_row_tournament_weekly.py` filters:
- duplicate event IDs;
- wrong row-integrity contract;
- pre-floor or timestamp-invalid rows;
- source-binding failures;
- invalid divergence parent/provenance.

`shared_row_tournament_relevance.py` reuses the same `filter_consumer_rows`.

## Remaining blocker

`scripts/research/validate_core_prospective_freeze.py`

still asserts unconditionally:

- `prospective_eligibility_status == CONTAINMENT_SENTINEL_NOT_AN_ACTIVATION_FLOOR`
- `containment_floor_sentinel is True`
- `collection_state == QUARANTINED_PENDING_POST_REPAIR_EVIDENCE`

This is correct for the pre-activation phase but means the Research Gate necessarily rejects the intended legitimate ACTIVE repository state.

Meanwhile the actual runtime code already supports ACTIVE:

- materializer requires `ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION`;
- materializer requires `containment_floor_sentinel == false`;
- materializer requires `ACTIVE_POST_REPAIR_FLOOR`;
- evidence controller uses the same state;
- monitor understands active vs quarantine;
- unit tests construct ACTIVE fixtures.

Therefore the current blocker is validator phase-awareness.

## Smallest repair

Version or modify only the existing validator so it validates one of two explicit modes.

### Mode A: QUARANTINED
Require current existing sentinel/quarantine invariants.

### Mode B: ACTIVE_POST_REPAIR
Require:
- collection_state = ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION;
- containment_floor_sentinel = false;
- prospective_eligibility_status = ACTIVE_POST_REPAIR_FLOOR;
- one identical frozen floor across core rule and core families;
- floor > P0 implementation merge timestamp;
- floor > the complete source-readiness evidence cutoff frozen by the activation review;
- no_backdating = true;
- activation PR/reference recorded;
- core C01-C07 READY only;
- optional blocked families remain blocked;
- all current P0 negative controls continue to pass.

Do not weaken any existing negative control.

## Future floor

No floor is selected in this adjudication.

The eventual activation PR must choose a timestamp that is genuinely in the future at merge/review time and later than the complete source-readiness set.

No retrospective rows from the current ready window may become eligible.

## Governance decision

Do not activate by editing JSON around the validator.

Do not disable or skip the Research Gate.

Do not backdate to 2026-09-30.

Do not reuse the containment sentinel as the first eligible row.

Repair the validator first, rerun the full gate, then separately adjudicate activation.

## Current state

`SOURCE_READINESS=PASS`

`CURRENT_P0_GATE=PASS`

`OLD_REVIEW_FINDINGS=RESOLVED`

`ACTIVATION_READINESS=ONE_SMALL_REPAIR`

`COLLECTION_STATE=QUARANTINED`

`ELIGIBLE_ROWS=0`

`CANONICAL_EFFECT=NONE`

`PORTFOLIO_EFFECT=NONE`
