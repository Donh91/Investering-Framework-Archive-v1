# M6 prospective challenger readiness gate v1

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`
**Date:** 2026-10-06
**Status:** `PARTIAL_READY / COLLECTION_ONLY / ZERO_AUTHORITY`
**Authority:** `RESEARCH_ONLY / NO_SELL / NO_TRIM / NO_PORTFOLIO_ACTION`

## Purpose

Freeze the post-HCEL prospective readiness decision after the repaired historical challenger lab was adjudicated. This checkpoint prevents historical HCEL semantics from being silently mapped onto different prospective owners.

## Deterministic fresh-read

### Lane C

Frozen protocol:
`06_RESEARCH_LAB/m6_protocols/2026-10-05__lane-C-prospective-warning-survival-v1.md`

Primary warning remains:
`pullback_risk_state in {ELEVATED,HIGH,CONFIRMED}`.

`BUILDING` remains watch-only.

Warning has zero automatic sell/trim authority.

### F1 PRICE_TREND

Decision: `SOURCE_AVAILABLE / TRANSFORM_CONTRACT_REQUIRED_BEFORE_CHALLENGER_OUTPUT`.

Direct BTC/ETH/ETHBTC capture exists through the governed hourly owner. Exact prospective daily resampling, warm-up, missingness and execution clock must remain explicit.

### F2 BREADTH

Latest owner:
`03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json`

Observed latest aggregate:
- constituent_count: 100
- advance_ratio: 0.39
- membership_hash present

Decision:
`AVAILABLE_BUT_HCEL_THRESHOLD_INCOMPATIBLE_UNTIL_PROVEN`.

The historical HCEL F2 variable was a 35-asset research-panel breadth series. The current owner is Top-100 and is not semantic parity evidence for the historical `0.45` threshold.

Therefore:
`F2=UNKNOWN_FOR_PROSPECTIVE_E3_PARITY`.

Forbidden:
- copying 0.45 to Top-100;
- tuning a replacement threshold on current outcomes;
- calling current Top-100 breadth a historical HCEL-equivalent family.

A future new breadth hypothesis requires separate preregistration before outcome inspection.

### F3 ETHBTC

Direct ETHBTC source is available.

Decision:
`SOURCE_AVAILABLE / 30D_TRANSFORM_NOT_YET_BYTE_FROZEN`.

Before first prospective challenger row, freeze:
1. exact daily observation/decision clock;
2. exact 30d return formula and endpoint convention;
3. minimum history/warm-up;
4. missing-row behavior;
5. source-age/provenance fields;
6. right-truncation rule.

No threshold search is authorized.

### F4 EUPHORIA_FADE

No clean prospective canonical owner with historical Alternative.me parity has been established.

Decision:
`F4=UNKNOWN/NO_SIGNAL`.

Forbidden:
- silent CFGI substitution;
- latest-vintage historical reconstruction presented as PIT;
- adding a source only to rescue E3 parity.

Any four-family challenger must visibly carry `DEGRADED_INPUT_PARITY`.

### F5 STABLECOIN_SUPPLY

Latest owner:
`03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json`

Contract:
`DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1`

Observed latest:
- `global.change_30d_pct = 1.070836`
- evidence role `SUPPLY_LIQUIDITY`
- deployment confirmation `NOT_ESTABLISHED`
- authority flags false
- interpolation false
- forward_fill false
- historical backfill provenance/hash present

Decision:
`RESEARCH_SOURCE_READY / NO_DEPLOYMENT_INFERENCE`.

F5 may only represent stablecoin supply/liquidity semantics. It cannot become a deployment/market-action signal.

### Action Compass outcome accountability

Latest:
`research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json`

Observed:
- source_outcome_count: 238
- eligible_series_row_count: 0
- warning_series_row_count: 0
- evidence_state: `COLLECTING_PROSPECTIVE_TYPED_ROWS`
- status: `NO_ELIGIBLE_MATURED_ROWS`

Exclusions are dominated by pre-decision-integrity schema/policy and non-prospective projection provenance.

Decision:
`COLLECTOR_FAIL_CLOSED_CORRECTLY / WAIT_FOR_NATURAL_MATURATION`.

No prose backfill, no retroactive relabeling, no eligibility relaxation.

## Readiness matrix

| Component | State | Prospective challenger use |
|---|---|---|
| F1 price/trend | source available | only after exact transform/clock freeze |
| F2 breadth | semantic mismatch | UNKNOWN for HCEL parity |
| F3 ETHBTC30 | source available | blocked until transform byte-freeze |
| F4 euphoria | owner unavailable | UNKNOWN/NO_SIGNAL |
| F5 stablecoin30 | research source ready | allowed as supply/liquidity research input only |
| Lane C warning collector | protocol frozen | collection allowed |
| Action Compass calibration | 0 eligible matured rows | wait prospectively |
| Live exit authority | none | forbidden |

## Gate decision

`PROSPECTIVE_HCEL_CHALLENGER_READY=NO`

Reason:
F2 parity is unproven, F3 transform is not frozen, F4 is unavailable, and no eligible prospective typed Action Compass outcome has matured.

`PROSPECTIVE_COLLECTION_READY=YES`

The correct next action is continued typed collection plus a narrow F3 transform freeze. Do not create a live sell rule and do not weaken eligibility to manufacture sample size.

## Scientific boundary

Historical HCEL repair is validated, but policy ranking remains unresolved. The prospective program must test warning survival and opportunity cost before it can test action authority.

`WARNING != SELL`

`LIVE_EXIT_RULE = NONE`

`NEXT_GATE = F3_TRANSFORM_FREEZE + NATURAL_TYPED_OUTCOME_MATURATION`
