# M6 HCEL dedupe checkpoint v1

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Status:** EXISTING_RESEARCH_OWNER_DISCOVERED / CONTINUATION_UNFINISHED  
**Authority:** RESEARCH_ONLY

## Finding

The Bridge already contains a substantial pre-M6 Historical Cycle & Exit Lab (HCEL) from 2026-09-27.

This materially overlaps M6.

M6 must not create a parallel exit-policy program.

## Existing HCEL evidence

Bridge program:
`programs/historical_cycle_exit_lab/`

Key frozen research artifact:
`programs/historical_cycle_exit_lab/runs/2026/09/POLICY_SPEC_v0.json`

Evidence label:
`RETROSPECTIVE_FROZEN_POLICY_REPLAY`

Seven policies E0-E6 were tested on the same two-cycle historical panel.

Most relevant historical discovery:
`E3_CROSS_FAMILY_LADDER`

E3 characteristics:
- staged;
- reversible;
- multi-family;
- explicit re-entry;
- E0 HOLD and E1 trend baselines;
- research-only.

Reported 20 bps/side aggregate:
- tops median TWR vs HOLD: 1.089
- minimum top TWR: 0.843
- controls median TWR: 0.952
- median top max-DD reduction: 11.4 percentage points
- median premature cost: 3.9%
- median time out of market: 12%

At 50 bps/side:
- HOLD ranked first on wealth-only utility.
- E3 remained strongest under drawdown-aware utility.

Historical conclusion:
No policy proved universal dominance.
The scientific case for staged exits is tail-risk / drawdown control, not guaranteed wealth improvement.

## Important negative evidence

Standalone sentiment-only exit logic was rejected as weak in this frozen family.

Single-family trend/drawdown policies often cut drawdown but incurred large recovery-leg opportunity cost and/or whipsaw.

This is consistent with M6 T4:
warning or stress evidence is not equivalent to immediate sell authority.

## Existing ChatGPT adjudication from 2026-09-27

HCEL was adjudicated:
`HIGH VALUE / MODIFIED / PRESERVE AS DISCOVERY EVIDENCE`

E3:
`PROMISING HISTORICAL DISCOVERY / NOT YET PROSPECTIVE_TEST_READY`

Q-1 prospective exit challenger:
`ACCEPTED IN PRINCIPLE, BLOCKED PENDING REPAIR + REPRODUCTION`

## Unfinished required continuation

Search on 2026-10-05 finds no evidence that the approved O-1 continuation was completed.

Required sequence remains:

1. reproduce the original 504-row result file hash;
2. add PB-02, the preregistered 2020-09 -> 2020-11 drawdown/recovery negative control, with no threshold change;
3. audit E3 implementation against written spec;
4. explicitly test partial missingness semantics;
5. freeze `POLICY_SPEC_v0_1` before any repaired rerun;
6. if ranking materially changes, stop for ChatGPT adjudication;
7. if clean, add right-truncation invariance + per-family availability/provenance tests;
8. only after those gates consider a zero-authority prospective shadow emitter.

## Known v0 defect

The written v0 missing-data contract and implementation do not fully match.

A previously active family can remain counted while its current input is unavailable.

Future v0.1 must explicitly freeze one semantics, with per-family:
- available/unavailable;
- active/inactive/unknown;
- source timestamp;
- source age;
- reason unknown.

No threshold tuning is permitted during the repair.

## M6 routing decision

Do not build a new standalone SPAR-derived exit engine.

SPAR remains useful as sequence/lead-time evidence.

The exit-policy owner should be the already-adjudicated HCEL continuation unless new evidence falsifies it.

Claude slice 2 remains focused on historical-as-was Aug-Oct overlap.

After slice 2:
- if lane A has usable explicit warning episodes, bind them as external outcome cases against HCEL-style staged decision economics;
- if lane A has zero usable episodes, prioritize HCEL O-1 reproduction/spec repair plus prospective lane C.

No live market rule.
No portfolio action.
No production exit authority.
