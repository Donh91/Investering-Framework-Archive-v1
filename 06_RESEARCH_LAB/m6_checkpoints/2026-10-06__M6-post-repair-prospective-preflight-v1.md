# M6 post-repair prospective preflight, 2026-10-06

Status: PRE_REGISTERED_EXPECTATION / RESEARCH_ONLY
Authority: ZERO_LIVE_ACTION_AUTHORITY

## Purpose
Freeze the expected interpretation before the next automated ACTION_COMPASS_PROTECTION_CALIBRATION_v2 rebuild.

## Current owner observation
Latest Official Compass:
- compass_id: CMP-20261006-627e461586fd
- issued_at_utc: 2026-10-06T14:37:16Z
- decision_policy_version: 2026-09-30_DIRECTION_ACTION_SEPARATION_V4_0
- data_status: OK
- Cycle Navigator projection source: MACHINE_PACKAGE
- protection contract: COMPASS_PROTECTION_TRACKER_v1
- protection data_quality: OK
- pullback_risk_state: BUILDING
- distribution_risk: UNKNOWN
- action_now: HOLD_WAIT

## Eligibility expectation
Under the repaired calibration gate, once a valid matured Official Compass outcome exists for this freeze:
- the V4 policy itself must NOT cause exclusion;
- distribution_risk=UNKNOWN must NOT cause exclusion;
- BUILDING is eligible as a typed calibration/control state if all remaining immutable outcome/provenance gates pass;
- BUILDING is NOT a primary Lane-C warning;
- warning_series_row_count must not increase from this observation alone.

Primary Lane-C warning remains only:
ELEVATED / HIGH / CONFIRMED.

## Falsification check for the repair
The next automated calibration rebuild falsifies this repair if a matured V4 + MACHINE_PACKAGE + data_quality OK + assessable pullback state row is excluded solely because of:
- old decision-policy prefix logic; or
- distribution_risk UNKNOWN.

If zero eligible rows remain, inspect explicit exclusion classes. Do not weaken the gate merely to obtain N.

## Current market-research interpretation boundary
BUILDING means watch-only.
It is not SELL, TRIM or portfolio authority.
No re-entry review is active.
No live exit rule exists.

## M2 interaction
No legitimate new typed M2 challenger/decision owner was found on fresh main.
M2 therefore remains blocked by design rather than being wired to the superseded BTC_PARTIAL gate.

## Next automatic gate
Wait for natural outcome maturation and the next Framework Learning Operations rebuild, then compare the produced calibration report against this frozen expectation.

WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE
