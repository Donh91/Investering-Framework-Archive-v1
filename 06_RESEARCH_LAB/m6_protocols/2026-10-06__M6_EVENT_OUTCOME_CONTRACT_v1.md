# M6 Event Outcome Contract v1

**Mission:** RL-DISTRIBUTION-SURVIVAL-META-006
**Parent:** RL-OPEN-SOURCE-VALIDATION-HARVEST-007
**Date:** 2026-10-06
**Status:** FROZEN_RESEARCH_MEASUREMENT_CONTRACT
**Authority:** RESEARCH_ONLY / NO_SELL / NO_TRIM / NO_PORTFOLIO_ACTION

## Purpose
Standardize how a legally knowable M6 warning is matured so repeated observations can measure drawdown-avoidance potential, false-warning opportunity cost, warning survival, recovery and re-entry friction without translating WARNING into SELL. This extends Lane C and does not replace its warning or episode definitions.

## Admission
Eligible only when warning identity/timestamp satisfy frozen Lane C.
Primary warning: pullback_risk_state in {ELEVATED,HIGH,CONFIRMED}.
BUILDING is watch only. UNAVAILABLE/degraded/missing is non-assessable.
No post-outcome reconstruction may create an eligible prospective row.

## Immutable event identity
Store event_id, warning_state, warning_timestamp, knowledge_timestamp, source_commit/source_hash, BTC price, ETH price, data-health state, episode_family_id when known and observation provenance. Duplicate event identity may not be silently rewritten.

## Maturation horizons
Existing Lane-C horizons remain 24h, 72h, 7d, 14d, 30d.
For each horizon record terminal_return, MAE, MFE, time_to_MAE, time_to_MFE, data completeness and maturity state.
If required tape is incomplete, result is UNKNOWN, never interpolated success/failure.

## Barrier outcome labels
Barrier labels are an additional research view, not a replacement for continuous MAE/MFE.

BTC adverse barriers: -10%, -15%, -20%.
ETH adverse barriers: -15%, -20%, -30%.
These are inherited from frozen Lane-C qualifying episode grids, not newly optimized.

Favorable barrier: NO PRIMARY FIXED FAVORABLE THRESHOLD in v1.
Lane C preregistered adverse episode grids but not symmetric profit barriers. Creating one now would introduce a new degree of freedom. Preserve continuous MFE and terminal return instead. A future favorable-barrier family requires separate preregistration before inspection.

For each adverse barrier record touched TRUE/FALSE/UNKNOWN, first_touch_timestamp, time_to_touch, trough_after_warning and recovered_by_horizon where deterministically definable.

## Episode clustering / dependence
Repeated warning rows must not inflate independent sample size.
Primary family rule remains Lane C: same family if peak-to-trough windows overlap OR later candidate peak occurs <14 calendar days after prior family trough.

Every matured warning carries episode_family_id, within_family_warning_index and independent_family_weight.
Primary inferential N is independent episode families, not raw warning rows.
Raw rows remain visible for calibration and state-transition analysis.

## Counterfactual action layer
Warning itself has no action semantics.
Counterfactual action evaluation is allowed only for a separately byte-frozen action challenger.

Any challenger must use same warning/event anchors, market tape, cost/fill model, latency assumptions, re-entry rule, horizon and immutable version identity.

Required outputs: net wealth vs HOLD, drawdown avoided, upside surrendered, peak giveback, time out of market, re-entry timestamp/price, re-entry drag/benefit, fees/slippage and false-exit state.

No action challenger exists merely because this outcome contract exists.

## Opportunity-cost vector
Preserve enough data to later calculate protective value, opportunity cost, delay cost, re-entry friction and whipsaw cost. Do not collapse these into one optimized score in v1.

## Price-only comparator
Retain Lane C comparator: first hourly close >=5% below running peak. Sensitivity only: 3%. Same legally knowable clock required. Comparator is research-only.

## Calibration readiness
If a future model emits a continuous distribution-risk probability, preserve probability at event time. No probability-to-action threshold may be tuned from this contract.

Before probability is used for action research require reliability/calibration curve, Brier-style proper scoring or justified equivalent, regime/episode-cluster aware uncertainty and sufficient independent families.

## External-method provenance
Method inspiration harvested from public research engineering includes event/barrier labeling and concurrency awareness, purged/embargoed temporal validation, non-overlapping event evaluation and negative-result/kill-list discipline.
External repositories provide method inspiration only. They do not validate M6 economic edge.

## Fail-closed rules
UNKNOWN if outcome tape incomplete, knowledge timestamp invalid, source provenance unavailable, event was created after outcome, horizon not matured, or episode assignment cannot yet be made where required.
Never backfill a missing prospective event from prose.

## Promotion boundary
This contract creates measurement, not authority.
No market-state, Compass action, SELL, TRIM, re-entry, portfolio weight or public claim changes from these labels.

WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE
