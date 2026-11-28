# C5_MM_CONTEXT_PREREG_v1

Status: FROZEN_ON_MERGE. Freeze identity is the first main commit containing these exact bytes; no prospective issue may be enrolled before that commit. Owner decision: #1596 and #2318, 2026-11-28; Bridge C5_REROUTE_OWNER_DECISION_20261128.md.

## Authority and cohort
Context-only, non-scoring in live Master Monday. No alteration to frozen BTC/ETH weekly forecast, CRE d30dbc36, Task2 live_consumption_allowed, or production decision authority. No paid calls. Derived-only public output; open endpoints. Only NATIVE_CAPTURE rows with observation/capture times at or before original issue cutoff, valid source digest and native run ID qualify for future evaluation. CONSERVATIVE_RELEASE_LAG and any backfill are never scored. No retrospective enrollment or reconstruction from later captures. Persist first issued context and baseline identity; if not immutable, exclude the issue.

## Hypotheses and design
H0 = no C5: existing same-clock Official Compass downside-risk flag (HIGH/ELEVATED vs other explicitly classified states) unchanged. H1 research-only = H0 OR (VIX term structure INVERTED AND asset-specific observed long/short liquidation pressure HIGH for either window). Pressure HIGH >=2x, LOW <=0.5x, otherwise NORMAL relative to trailing median of disjoint 28 daily or 4 weekly windows; require available positive baseline and coverage evidence. If any required component or baseline is unavailable, exclude the matched pair; never infer a negative signal. Context does not amend H0 or the original forecast. Candidate threshold is fixed before enrollment.

Endpoint: adverse price move, defined as minimum observed UTC daily close at least 5% below original same-clock asset reference over days 1–7, 1–14, 1–21 and 1–28. One week primary, 2–3 weeks and 4 weeks secondary. Same venue and immutable close evidence for both arms; no incomplete outcome windows. BTC and ETH are paired observations within a weekly cluster, not independent weeks.

Holdout: first eight or more eligible consecutive prospective weekly issue clusters after freeze, fixed rule, no training or tuning. Minimum N=8 distinct weekly issue clusters with mature paired outcomes per endpoint; report missing weeks and coverage, wait for 28-day maturity. Primary statistic paired difference in mean binary Brier loss (0/1 flags); report per-asset and cluster means, sensitivity, specificity and false-positive delta with uncertainty; no claim of statistical significance from eight weeks. Secondary results cannot rescue primary failure. No threshold tuning on holdout. Any new version requires new preregistration and new prospective cohort.

## Kill / hold
Immediately stop evaluation on PIT leakage, hash mismatch, raw publication, source/identity inconsistency, changed frozen bytes or authority breach. Hold if N<8 or incomplete observations, report reason. Kill challenger if primary holdout loss does not improve over H0, or improvement comes with higher false-positive rate, or paired coverage below 80% of prospective issues. No promotion from this protocol; independent review and separate explicit owner decision required even if improved. No scoring backfill, no CRE protocol changes.

## Production acceptance
C5 on/off yields byte-identical existing weekly BTC/ETH forecast freeze; demonstrate in integration tests before release. Site shows derived labels/as-of or explicit UNAVAILABLE reason, never raw source rows.
