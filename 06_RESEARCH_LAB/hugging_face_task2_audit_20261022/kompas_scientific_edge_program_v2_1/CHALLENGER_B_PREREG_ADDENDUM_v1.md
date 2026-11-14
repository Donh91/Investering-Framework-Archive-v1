# Challenger B, prospective week-validity implementation addendum v1

**Status:** documentation only, SHADOW research.  
**Applies to:** `TASK2_CHALLENGER_B_KOMPAS_TILT_v1`, original #2131 @ `4262cd46552f027d663515eb06c10298bad0ffa1`.  
**Immutable registration:** `CHALLENGER_B_KOMPAS_TILT_PREREG_v1.json`, Git blob `7ec3bf430d58bfc3aba6e4676535452176c74873`, unchanged.

## Week validity, not an outcome-dependent filter

For a prospective ISO week starting 2026-W47, a scored weekly Challenger B result requires:
1. The weekly outcome window has fully matured. Until the final governed hourly close evidence is available for each participating asset, the week is `PENDING`, not a B win or baseline win.
2. At least **8 paired valid asset-day scoring rows** across BTC and ETH, using the same minimum as Challenger A, `A.DECISION["min_paired_rows_per_week"]`. A paired row requires an eligible pre-issuance frozen source, a complete day-window hourly census and a non-tied close versus P0.
3. A fully mature week with fewer than 8 paired rows is `MISSING`, regardless of whether its observed Brier loss looked favorable or unfavorable. This minimum is fixed across the evaluation; never tune it to observed results.
4. A week whose model has no actual directional view is a `TIE`. A week with a valid mean Brier below 0.25 is `B`; above 0.25 is `BASE`; equality is `TIE`.

The confirmatory comparison continues to require **the first 8 eligible non-tied prospective weekly clusters**, with a one-sided exact sign test, `B_HAS_DIRECTION` only if B wins at least 7 of 8 (p approximately 0.0352). Invalid, missing, duplicated, disputed or unresolved earlier-week evidence must not be silently replaced with favorable later observations. The implementation's contiguous-week fail-closed guards are safety controls, not authority to revise the registered primary rule or select outcomes after observing them.

## Integrity and interpretation

This addendum documents the pre-outcome, outcome-independent operational eligibility rule used by the merged #2131 code and identified as a P3 documentation gap by Claude on Bridge #173/6875241317. It does **not** alter the frozen JSON, fixed tilt 0.5, 0.25 baseline, horizons, statistical rule, Official Compass authority, or site publication permissions.

**Known postmerge blocker (separate, not repaired here):** Codex P1 #2131/4572618575 found that deletion/rename of a historical official packet can evade a census of only current-main paths. See operational incident Archive #1156/6875886705. Challenger B remains SHADOW/HOLD for promotion until a separate reviewed source-provenance hotfix is merged and validated. This documentation PR is not that hotfix.
