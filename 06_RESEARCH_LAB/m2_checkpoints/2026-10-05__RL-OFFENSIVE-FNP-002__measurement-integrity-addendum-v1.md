# M2 Measurement Integrity Addendum v1

**Mission:** `RL-OFFENSIVE-FNP-002`  
**Date:** 2026-10-05  
**Status:** POST_FINAL_MEASUREMENT_INTEGRITY_ADDENDUM  
**Authority:** RESEARCH_ONLY / DOES_NOT_REOPEN_ECONOMIC_VERDICT  
**Framework main:** `2e1ea071551e7be7457557f05584e0c13c409ca7`

## Executive decision

M2's final economic verdict remains:

`INSUFFICIENT_EVIDENCE / MEASUREMENT_DEFICIT_BEFORE_AGGRESSION_DEFICIT`

This addendum strengthens that conclusion.

It does not justify more aggression.

It identifies why prospective false-negative measurement remained empty despite a prior "post-fix" status.

## 1. T5 downstream fix was not an end-to-end T2/T5 fix

The Sep-23 candidate:
`codex-research-t5-fnp-prospective-row-instrumentation-v1`

was merged and marked `POST_FIX_OBSERVATION`.

Fresh diff review shows it added:
- T5 scanner/consumer logic;
- workflow invocation for T5;
- tests and runtime state.

It did **not** add the upstream T2 observer/receipt producer.

Current state:
- T5 `PASS_NO_ELIGIBLE_INPUT`;
- source rows = 0;
- outcome rows = 0;
- evaluator unavailable.

Therefore the old post-fix label was true only for the T5 consumer layer, not for end-to-end FNP measurement.

Classification:
`FALSE_GREEN_END_TO_END_REMEDIATION_STATUS`.

## 2. T2 has two blockers, not one

Current contracts require T2 to compare BTC partial permission versus WAIT.

But Shadow Registry says:

`LEGACY_GATE_BTC_PARTIAL_FT1`
- evaluator = `NONE_RECOVERY_REQUIRED`;
- forward_observation_enabled = false;
- historical recoverability = source available, exact evaluator recovery required;
- output semantics = source availability / registered-output review only;
- no market permission.

Therefore:

### Blocker A
`EXACT_EVALUATOR_RECOVERY`

### Blocker B
`OBSERVER_WIRING_AFTER_EVALUATOR_RECOVERY`

Do not wire automatic divergence generation before A is solved.

The forward observer contract explicitly forbids inferring divergence from threshold proximity or trigger-candidate state.

## 3. Historical FT-1 recovery state

Project archive recovery supports:

### Verified
- `GATE-BTC-PARTIAL-v0.1.1` was frozen as a preregistered forward test on 2026-06-10.
- It was to be evaluated no later than 2026-07-10.
- No rule change / narrative reinterpretation before outcome.
- Default WAIT allocation:
  - BTC 0%
  - Stable 100%
  - Alt 0%
- FT-1 after `ENTERED`:
  - BTC 10%
  - Stable 90%
  - Alt 0%
- mechanical divergence versus WAIT = 10% × BTC return.
- FT-1 later recorded as invalidated/dead after `FAILED_RESET` around 2026-06-30.
- later archive notes a close-basis failure around 58.524K and old 64K reclaim becoming stale/dead.
- 5–7% expected FNP cost is a historical research heuristic unless a raw derivation is recovered.

### Not recovered
- exact `ENTERED` trigger/evaluator;
- exact persistence requirement;
- exact reclaim/failure state machine before the FAILED_RESET;
- exact daily owner row that would mechanically assert BTC_PARTIAL permission.

Therefore current recovery classification:

`PARTIALLY_RECOVERED_TRIGGER_UNRECOVERED`

The recovered 10% allocation may be used to understand economic divergence after a legally recovered ENTERED row.

It may **not** be used to manufacture ENTERED rows.

## 4. DRQ-018 coverage false-green fixed

Prior coverage gate accepted:
- correct contract;
- `COMPLETE_FOR_EXPECTED_CHECK_SET`;
- `checks_total >= 1`.

That meant one `NOT_EVALUABLE_DATA_BLOCKED` check could satisfy the gate and release DRQ-018 with zero evaluable evidence.

Current main now requires:
`no_divergence_checks + divergence_source_rows >= minimum_evaluable_checks_total`.

Policy:
`minimum_evaluable_checks_total = 1`.

Blocked checks do not satisfy the gate.

Focused owner-gated smoke:
- run 37344904014
- conclusion SUCCESS.

This is research-governance only.
No market rule changed.

## 5. Legacy graduated-alt top-up is not eight independent successes

Entry Signal archive Aug-20 through Aug-29 contains:
- 8 `GRADUATED_ALTCOIN_TOPUP_ACTIVE` bursts;
- each later returned to WAIT;
- median active duration ≈ 14.85h;
- mean ≈ 12.45h;
- 3 bursts <6h;
- 4 bursts <12h;
- breadth failure drove 5 WAIT flips;
- ETH-vs-BTC failure drove 4 WAIT flips.

These rows are highly overlapping and represent a noisy transition period, not eight independent deployment wins.

Current strict performance summary has:
- valid 24h = 0;
- valid 72h = 0;
- valid 7d = 0;
- valid 14d = 2;
- valid 30d = 0.

The legacy breadth permission is now retired/zero-weight and not a current canonical permission owner.

Interpretation:
`FIRST_TRIGGER_WHIPSaw_HIGH / SURVIVAL_QUESTION_REMAINS_MORE_RELEVANT`.

This supports T6's conceptual emphasis on survival versus first-cross logic.

It does not prove a current offensive edge.

## 6. Research-governance consequences

Do not:
- reopen M2 economics from the August path statistics;
- count the 8 top-up bursts as 8 trials;
- invent the missing BTC-partial evaluator;
- generate no-divergence rows when the owner question was never evaluable;
- treat blocked-only coverage as evidence.

Do:
- recover exact FT-1 evaluator if source-backed;
- otherwise preserve it as unrecovered;
- keep T5 fail-closed;
- keep DRQ-018 held until at least one evaluable owner check exists;
- use T6 prospective survival rows when a genuine first cross eventually occurs.

## Current verdict

`M2_ECONOMIC_VERDICT=UNCHANGED`

`T5_END_TO_END_STATE=BLOCKED_UPSTREAM`

`T2_EVALUATOR=PARTIALLY_RECOVERED_TRIGGER_UNRECOVERED`

`DRQ018_GATE=REPAIRED_FAIL_CLOSED`

`LEGACY_TOPUP=WHIPSAW_DESCRIPTIVE_NOT_PROMOTION_EVIDENCE`

`LIVE_PERMISSION_CHANGE=NONE`
