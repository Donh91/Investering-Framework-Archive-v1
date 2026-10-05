# M6 Lane C prospective warning-survival protocol v1

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Status:** FROZEN_RESEARCH_PROTOCOL / NOT_LIVE_AUTHORITY  
**Authority:** RESEARCH_ONLY / NO_PORTFOLIO_ACTION / NO_EXIT_EXECUTION  
**Framework main at freeze:** `59428fd7eaa49d5f308f75a6b9d0c80ff96bc198`

## Why Lane C exists

Claude RL-010 slice 2 v2 established:

`LANE_A_ZERO_USABLE_EPISODES`

The typed framework has not yet lived through a qualifying historical-as-was BTC >=10% or ETH >=15% drawdown episode in its archived operating window.

Therefore exit/distribution skill must accumulate prospectively rather than be inferred from the shallow Aug-Oct tape.

## Primary warning identity

Primary typed warning state:

`pullback_risk_state in {ELEVATED, HIGH, CONFIRMED}`

First warning time:
the first legally knowable transition from a non-warning state into any primary warning state.

If the system jumps directly into HIGH or CONFIRMED, that timestamp is the first warning.

`BUILDING` is a watch state only.

`NORMAL` is non-warning.

`UNAVAILABLE`, DATA_DEGRADED or missing is non-assessable and must never be translated into bearish evidence.

Reason for adding CONFIRMED:
the active `COMPASS_PROTECTION_TRACKER_v1` contract explicitly includes CONFIRMED. No historical CONFIRMED row exists in the slice-2 sample, so this semantic completeness change uses no observed outcome.

## Warning is not action

A primary warning row has zero automatic sell/trim authority.

The current Protection Tracker contract explicitly states BUILDING/ELEVATED are watch states and HIGH/CONFIRMED trigger reassessment, not automatic portfolio execution.

Framework false exit may only be recorded when a separate typed reduce-capable decision actually exists.

Until then:
- score warning lead;
- score warning survival;
- score warning recovery;
- score missed qualifying drawdowns;
- do not call a warning a trade.

## Reduce-capable identity

No generic mapping from `distribution_risk` or `pullback_risk_state` to a sell is permitted.

A reduce-capable row requires a separately frozen typed execution/decision contract, such as:
- a governed non-UNAVAILABLE sell/trim assessment with explicit action semantics; or
- a future typed reduce stage whose mapping was frozen before the episode.

If none exists:
`REDUCE_CAPABLE_DECISION=UNAVAILABLE`.

## Outcome episode definition

Primary episode grids:

BTC:
- >=10%
- >=15%
- >=20%

ETH:
- >=15%
- >=20%
- >=30%

Alt index:
- disabled until a clean prospective index owner exists;
- no silent proxy substitution.

Primary family independence rule:
- same family if peak-to-trough windows overlap; OR
- later candidate peak occurs <14 calendar days after prior family trough.

Sensitivity only:
- 7 days
- 30 days

Never choose the family-gap rule after inspecting performance.

## Prospective scoring horizons

For each legal warning/control row:
- 24h
- 72h
- 7d
- 14d
- 30d

For episode-family evaluation, 7d/14d/30d are primary economic horizons.

## Minimum outcome vector

For warning identity:
- warning timestamp;
- knowledge timestamp;
- source/commit timestamp;
- BTC/ETH price at warning;
- time to episode threshold crossing;
- time to trough;
- MAE;
- MFE;
- terminal return;
- warning survived / invalidated;
- recovered warning;
- qualifying drawdown missed;
- state transition history;
- data-health history.

For a future staged policy:
- exposure path;
- net terminal wealth vs HOLD;
- net terminal wealth vs frozen price-only baseline;
- policy max drawdown;
- drawdown avoided;
- upside surrendered;
- false exit;
- whipsaw;
- confirmation delay;
- re-entry time/price;
- re-entry drag/benefit;
- time out of market;
- fees/slippage assumptions.

## Price-only comparator

Research comparator:
first hourly close >=5% below running peak.

Sensitivity:
3% below running peak.

This is a comparator only, not portfolio authority.

Comparator timestamps must be computed on the same legally knowable clock as framework warnings.

## Current input readiness for an HCEL-style prospective challenger

### F1 PRICE_TREND

Source candidate:
`03_DAILY_CAPTURE_LOGS/hourly/`

Current owner:
`HOURLY_SEQUENCE_LATEST_POINTER_v2_2`

Latest inspected state:
- COMPLETE
- 26/26 requested spot hours
- current direct BTC/ETH/ETHBTC capture exists

Readiness:
`SOURCE_AVAILABLE`

Caveat:
the prospective policy must define the exact daily resampling clock and warm-up from immutable historical owner rows before first shadow output.

### F2 BREADTH

Source candidate:
`03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json`

Current contract:
`C5E_TOP100_BREADTH_OWNER_v1_2`

Current field:
`aggregate.advance_ratio`

Owner self-labels:
- `evidence_role=PROXY_ONLY`
- `canonical_compatible=false`
- `registered_threshold_compatibility=UNCONFIRMED`
- `substitution_policy=NO_HIDDEN_SUBSTITUTION`

Readiness:
`AVAILABLE_BUT_THRESHOLD_PARITY_UNPROVEN`

Critical rule:
HCEL historical E3 used a 35-asset research-panel breadth series.
Do not silently apply its historical 0.45 threshold to Top-100 advance_ratio as if they are the same variable.

Until a separate pre-outcome owner-parity decision is frozen:
`F2=UNKNOWN_FOR_PROSPECTIVE_E3_PARITY`.

This is not a reason to tune 0.45 on current outcomes.

### F3 ETHBTC

Source candidate:
direct ETHBTC from hourly owner.

Readiness:
`SOURCE_AVAILABLE_TRANSFORM_NOT_YET_FROZEN`

Required before prospective use:
- freeze daily decision clock;
- freeze exact 30d-return computation;
- prove right-truncation;
- bind source age and missingness.

No new threshold search.

### F4 EUPHORIA_FADE

Historical HCEL input:
Alternative.me Fear & Greed.

Current prospective canonical owner:
not found.

Framework source policy explicitly prevents Alternative.me from being silently renamed CFGI.

Readiness:
`UNAVAILABLE_FOR_PARITY`

Prospective rule:
`F4=UNKNOWN/NO_SIGNAL`

Do not add a new data source merely to reproduce historical E3 unless independently justified by a separate value-of-information decision.

A four-family prospective implementation is not directly comparable to five-family historical E3 without visible `DEGRADED_INPUT_PARITY`.

### F5 STABLECOIN_SUPPLY

Source:
`03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json`

Current contract:
`DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1`

Current field:
`global.change_30d_pct`

Readiness:
`RESEARCH_SOURCE_AVAILABLE`

Semantic boundary:
supply/liquidity only.
No deployment inference.

This matches HCEL F5's historical supply-growth concept more closely than a deployment metric.

## Lane-C event admission

An episode may enter the primary prospective score only if:
1. outcome price tape is continuous enough for the episode;
2. at least one warning-capable typed owner existed before the trough;
3. warning timestamp is legally knowable;
4. data-health status is preserved;
5. any revised owner input uses historical knowledge time, not latest vintage;
6. episode family assignment follows the frozen rule;
7. the row was not created after observing the episode outcome.

## First-family kill/readout

After the first completed qualifying family:

If no typed warning occurred before trough:
- record a false negative / no-warning episode;
- do not invent a warning from prose.

If a warning occurred but no reduce-capable field existed:
- score warning lead/survival only;
- exit economics remain unobserved for the framework itself.

If a reduce-capable state existed:
- score its actual frozen action semantics against HOLD and price-only baseline.

One family cannot prove edge.

## Recovered warning controls

T4 July 2026 and the two Sep 2026 ELEVATED/HIGH episodes remain descriptive recovery controls.

They cannot be promoted to independent distribution families.

They exist to penalize any future policy that converts warnings too aggressively into lost exposure.

## Promotion rule

No market or portfolio rule may be promoted from Lane C until:
- HCEL O-1 reproduction/parity repair is adjudicated;
- a prospective policy spec is byte-frozen before its first row;
- simple baselines are emitted on the same clock;
- false positives and false negatives are both measurable;
- re-entry is defined;
- sufficient independent families exist for the claimed scope.

## Current decision

`LANE_A=CLOSED_ZERO_USABLE_EPISODES`

`LANE_C=PROSPECTIVE_COLLECTION_PROTOCOL_FROZEN`

`WARNING_IDENTITY=ELEVATED_OR_HIGH_OR_CONFIRMED`

`BUILDING=WATCH_ONLY`

`WARNING_IS_SELL=FALSE`

`HCEL_O1=NEXT_POLICY_RESEARCH_GATE`

`LIVE_RULE=NONE`
