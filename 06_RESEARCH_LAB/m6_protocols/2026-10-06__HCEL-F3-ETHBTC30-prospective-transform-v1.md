# HCEL F3 ETHBTC30 Prospective Transform Contract v1

**Mission:** RL-DISTRIBUTION-SURVIVAL-META-006
**Parent:** RL-OPEN-SOURCE-VALIDATION-HARVEST-007
**Date:** 2026-10-06
**Status:** BYTE_FROZEN_RESEARCH_TRANSFORM
**Authority:** RESEARCH_ONLY / ZERO_LIVE_ACTION_AUTHORITY

## Purpose
Close the M6 F3 transform blocker without threshold search or historical outcome tuning.

F3 represents sustained 30-day ETH/BTC relative weakness for an HCEL-style prospective research challenger.

## Historical identity preserved
Frozen historical HCEL v0.1 defines:
- feature: ethbtc30 = pct_change(ETHBTC, 30 daily observations);
- candidate ACTIVE when ethbtc30 < -10.0%;
- E3 persistence: 3 consecutive OBSERVED daily decisions;
- UNKNOWN resets consecutive persistence;
- no cross-segment borrowing.

The -10% threshold and 3-observation persistence are inherited research parameters only. They are NOT live market or portfolio rules.

## Prospective source owner
Primary source:
03_DAILY_CAPTURE_LOGS/hourly/

Owner contract:
HOURLY_SEQUENCE_LATEST_POINTER_v2_2 and governed immutable hourly CSV rows.

Field:
ethbtc_close

Use direct source-reported ETHBTC close. Do not derive ETH/BTC from separate USD pairs when direct ETHBTC is available.

Required source row:
- spot_status = PASS;
- finite positive ethbtc_close;
- immutable stored owner row;
- provenance/hash available.

Otherwise observation = UNKNOWN.

## Daily observation clock
Daily F3 observation for UTC date D uses the direct ETHBTC hourly candle whose timestamp_utc is D 00:00:00Z.

That timestamp identifies the candle OPEN. Its close is not legally knowable at 00:00Z.

Feature observation/knowledge time is therefore no earlier than D 01:00:00Z, subject to the owner row actually being available and provenance-valid.

No signal may be timestamped at the candle-open time.

This preserves the historical daily sampling convention while repairing the clock-label/lookahead ambiguity identified by HCEL R9.

## Exact 30-day transform
For daily observation D:

ETHBTC30_pct(D) = 100 * ( ETHBTC_close(D) / ETHBTC_close(D-30 calendar days) - 1 )

Requirements:
- both endpoint observations must exist and be valid;
- D-30 means the daily observation exactly 30 UTC calendar days earlier;
- do not substitute nearest prior row;
- do not forward-fill or interpolate;
- all required continuity semantics below must pass.

This is equivalent to the historical corrected engine's _pct(series, i, 30, segment_floor) when daily observations are continuous.

## Dependency / purge identity
Information dependency length = 30 calendar days plus the close-availability boundary of the current observation.

Any future train/test or calibration split using F3 must purge overlapping feature dependency so training information cannot reuse observations that cross the evaluation boundary.

A generic arbitrary purge length is forbidden. Purge derives from the actual 30-day dependency and any longer dependency in the full model.

## Continuity
A continuity segment breaks when:
- the exact expected daily observation is missing or invalid;
- owner semantics/version changes incompatibly;
- provenance cannot establish legal availability;
- a declared source discontinuity occurs.

Fewer than the required endpoint/history observations inside the current valid segment => UNKNOWN.

No cross-gap borrowing.

## Warm-up
First 30 calendar days of a fresh valid continuity segment cannot emit ETHBTC30.

State = UNKNOWN until an exact D-30 endpoint exists inside the same valid segment.

## F3 family state
Given valid ETHBTC30:
- ACTIVE_CANDIDATE if ETHBTC30_pct < -10.0;
- INACTIVE_CANDIDATE otherwise.

UNKNOWN if transform unavailable.

Prospective E3 persistence:
- ACTIVE only after 3 consecutive OBSERVED ACTIVE_CANDIDATE daily decisions;
- UNKNOWN resets persistence to zero;
- an observed INACTIVE_CANDIDATE resets active persistence to zero.

This is research-challenger state only.

## Right truncation
At decision time T, only owner rows whose candle close and source availability are legally knowable by T may be used.

No current/future LATEST pointer may retroactively establish what was known at an earlier decision time without immutable historical row/provenance evidence.

## Source age
No invented generic freshness window.

Validity follows the bound hourly-owner contract and exact observation semantics. If owner freshness/availability cannot be proven at decision time, F3 = UNKNOWN.

## Provenance required per emitted research observation
Store:
- contract_id;
- utc_date;
- candle_open_timestamp_utc;
- feature_observation_time_utc;
- current_row logical path/hash;
- endpoint D-30 logical path/hash;
- current ethbtc_close;
- endpoint ethbtc_close;
- ethbtc30_pct;
- family candidate state;
- persistence count;
- final F3 state;
- continuity_segment_id;
- evidence_class;
- missingness reason when UNKNOWN.

## No-threshold-search boundary
Forbidden:
- tuning -10% on current/prospective outcomes;
- changing 3-day persistence after observing outcomes;
- replacing direct ETHBTC with a better-looking proxy;
- nearest-row endpoint substitution;
- cross-gap borrowing;
- timestamping signal at candle open;
- treating F3 as SELL or TRIM authority.

A future alternative threshold is a new preregistered challenger family with its own trial identity.

## External-method harvest applied
RL-OPEN-SOURCE-VALIDATION-HARVEST-007 contributes one generalization here:
temporal purge/embargo must follow actual information dependency rather than an arbitrary fixed duration.

No external signal, return claim or threshold is imported.

## Readiness ruling
F3_TRANSFORM_BYTE_FROZEN=YES
F3_SOURCE_AVAILABLE=YES
F3_LIVE_AUTHORITY=NONE

This closes only the F3 transform-definition blocker.

It does NOT make the full prospective HCEL challenger ready because F2 semantic parity remains unproven, F4 remains unavailable, and prospective typed outcome evidence remains immature.

WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE
