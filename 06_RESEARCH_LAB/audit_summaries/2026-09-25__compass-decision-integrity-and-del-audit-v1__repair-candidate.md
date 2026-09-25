# Compass decision-integrity and DEL audit v1

**Date:** 2026-09-25  
**Status:** VERIFIED_REPAIR_CANDIDATE_PENDING_PR_CI  
**Base main SHA:** `29aa2fde7b19d3eb56851f07f376470394cd3176`  
**Scope:** Official Daily Compass, Native Handlekompas, Cycle Navigator machine projection, Compass outcomes, event-driven refresh, Decision Economics Ledger  
**Authority:** audit and shadow-learning only; no portfolio execution, no silent forecast rewrite, no automatic promotion

## Purpose

This audit was run after the independent Nightshift Omega package identified a mismatch between Compass action logic and the framework's own rule registry. The objective here was not to search for more problems for their own sake. It was to verify the high-impact findings against current main and inspect adjacent runtime, outcome and refresh layers for the same failure class.

## Verified finding 1 - retired breadth/ETHBTC proxy regained action authority

Canonical governance in:

`01_CORE_FRAMEWORK/governance/2026-07-12__rule-and-evidence-registry-sensor-audit-v1__canonical-addendum.md`

marks `FROZEN_BREADTH_PREDICTIVE_GATE` as `RETIRED_ZERO_WEIGHT` with no entry permission, hard-gate, standalone rotation-prediction or portfolio-action authority.

The current entry-signal owner repeats the same boundary in:

`04_MARKET_LEARNING/entry_signals/README.md`

and the current intraday execution owner reports:

- `breadth_entry_permission = RETIRED_ZERO_WEIGHT`
- `breadth_role = DESCRIPTIVE_RESEARCH_CONTEXT_ZERO_EXECUTION_WEIGHT`
- `entry_signal_state = WAIT`

Despite this, current `scripts/data_ping/native_handlekompas.py` used:

- Top-100 advance ratio < 0.40 -> `HOLD_DEFENSIVE_WAIT`
- ETHBTC > 0.03 plus advance ratio >= 0.50 -> `PREPARE`

This was a real cross-layer governance bypass.

### Repair

The repair candidate gives breadth and the ETHBTC 0.03 gate explicit zero action weight. They remain descriptive evidence only. Legacy `GRADUATED_ALTCOIN_TOPUP_ACTIVE` observer labels also cannot reactivate action by themselves. Any later promotion requires a deliberate canonical implementation change.

## Verified finding 2 - free-form prose was machine authority in three places

The Compass was not only displaying Cycle Navigator prose. It was parsing it into machine state.

Current main used free-text keyword parsing for:

1. `NEXT_1_3D` / `NEXT_5_7D` direction through `_weekly_direction()`.
2. The 4-8 week altcoin state through `_altcoin_cycle_lane()`.
3. Pullback/distribution/re-entry protection through `protection_tracker()`.

The protection case is operationally material because `scripts/data_ping/compass_event_refresh.py` compares protection state and can request an event-driven Compass refresh when that state changes. A prose interpretation could therefore affect both display and refresh behavior.

### Repair

Cycle Navigator now has a required typed machine object:

`decision_projection.contract = CYCLE_NAVIGATOR_DECISION_PROJECTION_v1`

with explicit lanes for:

- 1-3 days
- 5-7 days
- 4-8 weeks
- protection / distribution

Compass consumers no longer translate prose into machine authority. Old Cycle Navigator packages without the typed object fail closed for those lanes instead of guessing.

Narrative fields remain available as explanation only.

## Verified finding 3 - Native Handlekompas could log a stale action

Official Daily Compass already called:

`action_context(auto_state, as_of=issued)`

and therefore enforced owner freshness at issuance.

Native Handlekompas called:

`action_context(auto_state)`

without an issuance time. In `_health_ok()`, missing `as_of` skips the owner-freshness check.

This matters because Native Handlekompas runs are later read by `scripts/learning/compass_outcomes.py` as action-event evidence for confirmation/invalidation timing. A stale native owner packet could therefore contaminate timing learning even while Official Compass itself failed closed correctly.

### Repair

Native Handlekompas now evaluates action against its own generation timestamp. `DATA_HEALTH` also carries the evaluated owner-freshness result and degrades when the owner is stale.

## Verified finding 4 - Compass persistence baseline was structurally unreachable

`scripts/learning/compass_outcomes.py` requests the feature:

`btc_delta_since_prior_packet_pct`

for its persistence baseline.

Before this repair, no Compass evidence snapshot emitted that feature. Repository search found the feature identifier only in the outcome reader.

The baseline therefore remained `UNAVAILABLE` by construction.

### Repair

Official Compass evidence snapshots now include:

- `btc_delta_since_prior_packet_pct`
- `eth_delta_since_prior_packet_pct`
- `ethbtc_delta_since_prior_packet_pct`

Historical immutable freezes are not rewritten. The baseline becomes reachable prospectively only.

## DEL v1.1 - corrections to the Nightshift proposal

The Decision Economics Ledger is retained as the winning capability, but the original prototype's economic semantics were not merged unchanged.

### Action semantics

The original prototype treated status words as fixed portfolio weights. That is not faithful to the Compass contract.

DEL v1.1 instead uses two stateful synthetic interpretations:

- **INCUMBENT_HOLDER:** starts invested. HOLD, PREPARE, WAIT and HARD_WAIT are no-trade states. Exposure changes only on an explicit BUY/DEPLOY or SELL/EXIT.
- **FRESH_CAPITAL:** starts in cash. HOLD, PREPARE, WAIT and HARD_WAIT are no-trade states. It only enters on BUY/DEPLOY.

This makes the current absence of a core de-risk action measurable rather than silently translating WAIT into SELL.

### Transaction costs

Costs are charged only on actual exposure change:

`abs(current_exposure - prior_exposure) * one_way_cost`

Persistent exposure is not charged again at every freeze.

The first observed policy state is initialization and carries zero synthetic turnover cost, avoiding an arbitrary sample-start penalty.

### Data authority

The Cowork historical segment-return CSV remains research evidence only.

DEL v1.1 will not schedule or produce governed results until it receives a metadata contract:

`GOVERNED_SEGMENT_RETURN_SERIES_v1`

with `status = GOVERNED`.

This deliberately leaves the new capability data-blocked rather than laundering a useful research proxy into canonical evidence.

### Experiment status

`research/decision_economics/DEL_PREREGISTRATION_v1_1.json`

is frozen shadow-only. The primary inference unit is the first healthy Compass freeze per ISO week. No automatic Compass change or challenger promotion is possible.

## Scope audit - what was not found

The audit searched active runtime code for other breadth-to-PREPARE or breadth-to-defensive-action translations.

No second active runtime owner was found. Other `advance_ratio` references are collectors, research, materializers or shadow/learning consumers. The action-authority regression is localized to Native Handlekompas plus stale design language in the open Compass PR.

The event-refresh owner already performs an explicit owner-freshness check before materiality evaluation. Its freshness handling does not need a parallel replacement.

The current intraday/entry owner already exposes breadth as retired zero-weight research context. It does not need to be reworked.

Historical Compass freezes, historical action logs and matured outcomes are evidence. They must remain immutable even though the old action semantics are now known to be flawed.

## Open PR #1085

PR #1085 contains useful UX/learning scope but still describes ladder progression after "ETH/breadth confirmation". That wording conflicts with the verified retired-gate governance.

The PR must not be merged under its old semantic assumptions. It should be rebased onto the repaired owner semantics and retain breadth only as descriptive confirmation until a future registered signal earns action authority.

## Remaining data gap

The largest unresolved dependency is not another indicator. It is a governed per-segment return series for BTC, ETH, large, mid, small and micro caps.

Until that owner exists:

- DEL remains shadow/data-blocked.
- `rotation_ladder_accuracy` remains unavailable for lower-cap segments.
- the framework must not infer economic ladder quality from BTC as a substitute.

## Audit conclusion

Nightshift Omega's central diagnosis survives independent review.

The additional material findings are:

1. stale Native Handlekompas actions could contaminate timing learning,
2. protection prose parsing could cascade into event-driven refresh,
3. the persistence baseline was impossible to score because its input feature was never frozen.

No evidence supports creating another market engine. The correct repair is tighter semantic authority, typed producer-consumer contracts, prospective economic accountability and fail-closed missingness.
