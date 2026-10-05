# M6 HCEL O-1 adjudicated delta for independent Sol review

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Status:** SOL_CROSS_EXAM_READY  
**Authority:** RESEARCH_ONLY  
**Framework main:** `9fa634010260b3aaf9a268fce48fb659a30e7c2f`

## What changed materially

Claude independently reproduced the original HCEL 504-row result and exact sha256:
`4e259e868281d91baa7f3662e8350144e3b2224d0560e7fb89291150e5b77489`.

Therefore the original artifact is reproducible.

Claude also independently reproduced the temporal seam defect identified by ChatGPT:

- 2020-09-01..2021-12-31 and 2025-01-01..2026-07-31 were concatenated into one positional daily list;
- rolling windows ignored research-window continuity;
- Jan-2025 features borrowed late-2021 rows;
- 54/504 result rows changed under continuity-aware replay;
- only EP-03 and CTRL-03 were affected;
- EP-04 modern holdout remained clean.

The defect is causal/mechanical, not a stale-file issue.

## Material ranking changes

At 20 bps per side:

E3 EP-03 TWR vs HOLD:
- BTC 1.097 -> 0.990
- ETH 1.788 -> 1.205
- ALT_EW 1.359 -> 1.079

E3 max-DD:
- ETH 19.8% -> 39.3%
- ALT_EW 33.8% -> 48.1%

Aggregate:
- E3 W_A cost20 +0.0096 -> -0.0208
- E3 median top TWR 1.089 -> 1.037
- E3 median top DD reduction 11.4pp -> 9.0pp
- W_C winner changes E3 -> E1 at 0/20/50 bps
- LOEO W_C cost20 first-place counts change E3x5/E1x3 -> E1x6/E3x2

Interpretation:
the historical claim "E3 is the winner" is rejected.
The repaired evidence does not establish E1 as a winner either.
Both remain small-N descriptive candidates.

## ChatGPT disposition

Original v0:
`CONTAMINATED_V0_NOT_FOR_MODEL_SELECTION`

Claude corrected replay:
`PREFERRED_CORRECTED_REFERENCE_PENDING_INDEPENDENT_REPLICATION`

E3:
`PROMISING_STAGED_POLICY_FAMILY / NEED_MORE_DATA / NO_SUPERIORITY_CLAIM`

E1:
`PROMISING_TREND_BASELINE / NEED_MORE_DATA`

No policy is promoted.

## ChatGPT amendments to Claude POLICY_SPEC_v0_1 draft

### Accepted
- segment-aware rolling and warm-up UNKNOWN;
- explicit family ACTIVE/INACTIVE/UNKNOWN;
- UNKNOWN resets persistence;
- per-family provenance;
- observed-data re-entry only;
- missingness semantics applied across policies.

### Rejected/modified

1. Generic freshness defaults such as "3 days" are rejected.
Freshness must come from bound owner/source contracts; otherwise UNKNOWN.

2. The proposed hard-exit auto-release after 5 F1-missing frames is rejected.
Missing data cannot manufacture a release.
While F1 is UNKNOWN:
`STALE_DATA_NO_NEW_DECISION`;
prior exposure/state is frozen until observed evidence resumes.

3. Partial missingness:
if any family is UNKNOWN, missingness alone may not increase exposure.
Observed newly-active evidence may still reduce exposure.
All unknown => freeze prior exposure.

### Added

R9 decision clock:
- Binance kline open timestamp is not knowledge time of its close;
- signal time must be after final input is knowable;
- legacy same-close convention is comparison-only;
- repaired replay must include a strict delayed-execution sensitivity.

R10 evidence classes:
- FROZEN_NATIVE_KNOWLEDGE_TIME
- RECONSTRUCTED_EVENT_TIME_PROXY
- CURRENT_MACHINE_RETRO
- UNAVAILABLE

Historical HCEL F4/F5 are reconstructed event-time proxies unless vintage evidence proves otherwise.

## PB-02

Accepted as frozen diagnostic control only.

It is:
- outcome-selected;
- overlapping another control;
- warm-up constrained;
- not an independent episode.

It must not increase independent N.

## Sol cross-examination questions

Do not rescue the old E3 headline.

1. Is the contamination adjudication logically sound?
2. Does the material ranking flip justify permanently quarantining original v0 for model selection?
3. Does the corrected evidence support any policy winner?
4. Challenge ChatGPT R1-R10 semantics, especially:
   - UNKNOWN exposure behavior;
   - no hard-exit timeout;
   - owner-contract freshness;
   - decision-time vs execution-time separation.
5. Is the proposed strict delayed-execution sensitivity necessary and sufficient to address the candle-clock issue?
6. Should the corrected continuity-aware replay replace v0 for citation, remain parallel, or require another independent reproduction first?
7. Does E1/E3 scalar-rank instability imply frontier/dominance reporting is superior to a weighted winner?
8. Is the proposed future prospective path scientifically legitimate given:
   - effective n about two cycles;
   - current F2 breadth semantic mismatch;
   - absent prospective F4 owner?
9. Is there any justified live sell/trim rule now?
10. What is the cheapest decisive next test after this cross-exam?

## Hard constraints

- no new signal;
- no threshold tuning;
- no model-weight tuning;
- no portfolio action;
- no live exit rule;
- no repository writes by Sol;
- `selected_live_rules=[]`.

Return:
- `CONTAMINATION_ADJUDICATION`
- `SPEC_SEMANTICS_VERDICT`
- `WINNER_CLAIM_VERDICT`
- `INDEPENDENT_REPLICATION_REQUIREMENT`
- `NEXT_TEST`
- `UNKNOWN_LIST`
- `selected_live_rules`
