# Alpha Lab Proof Supervisor v2

Owner: #1087
Execution packet: #1134
Plane: research/evidence only
Portfolio execution: FORBIDDEN

## Purpose

Replace the reviewed v1 supervisor design from PR #1131 with a governed state machine that can advance prospective proof without bypassing repository safety or rewriting scientific outcomes.

## Hard invariants

- Only workflow-run evidence produced from `main` is eligible.
- Freeze and result must bind to the exact upstream `head_sha`.
- The preregistration hash is recomputed from the frozen spec before any PASS.
- First observed block and observation time must be after the frozen future-start boundary.
- Failed collector runs consume a bounded retry budget instead of disappearing.
- `SHADOW04_PASS`, `SHADOW04_FAIL` and `HALT_CRITICAL` are terminal.
- Operational proof state is written only to `automation/alpha-proof-state-v1`, never directly to `main`.
- The SHADOW-04 collector self-NOOPs after a terminal proof state.
- Only major PASS/FAIL/HALT transitions are surfaced to #1087.
- No scanner, score, portfolio action, autonomous buying, or canonical market effect is authorized.

## State transition

`WAIT_SHADOW04 -> RETRY_SHADOW04 | SHADOW04_PASS | SHADOW04_FAIL | HALT_CRITICAL`

`SHADOW04_PASS -> START_SHADOW07`

A SHADOW-04 PASS proves only that the preregistered prospective collection survived its integrity gate. It does not prove project identity, predictive alpha, wallet edge, or compounding alpha.

## Review defects explicitly closed from v1

1. No direct push to main.
2. No non-main upstream artifact can advance a gate.
3. `spec_sha256` is recomputed and bound to the exact freeze.
4. Outcomes must occur after the frozen start.
5. A terminal PASS cannot be overwritten by later scheduled runs.
6. Failed collector runs are adjudicated for bounded retry.

## Tests

`python 06_RESEARCH_LAB/alpha_lab/tools/test_alpha_proof_supervisor_v2.py`

The workflow executes these regressions before mutating proof state.
