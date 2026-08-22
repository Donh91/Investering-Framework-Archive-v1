# PT-HS-001 — Early Rotation Pre-Trigger v1.1

Status: `PREREGISTERED_DATA_READINESS_PENDING`
Authority: `RESEARCH_ONLY_NON_CANONICAL`
Promotion: `NO`

## Frozen definition

Trigger only when all four recovered conditions are simultaneously true at the observation cutoff:

1. Stablecoin Alt Inflow 3D > +3%
2. Large-cap Alt Volume Share 3D > +4%
3. ETH/BTC < 0.032
4. BTC dominance > 56

Role is frozen as an early rotation-window observation, never a standalone buy signal.

## Primary research question

Does the four-component composite provide useful incremental lead-time or calibration beyond its own simple components and combinations?

## Required prospective row

Each eligible observation must freeze before outcome access:

- observation_timestamp_utc
- information_cutoff_utc
- exact four component values
- source identity/version for each component
- trigger state
- current breadth context
- current-stack context
- matched non-trigger/control IDs
- dependence group IDs
- all eight maturation horizon statuses

Missing required components make the row `INELIGIBLE_DATA_MISSING`, not inferred.

## Baselines and negative controls

Report on the same prospective windows:

- stablecoin-alt-inflow only
- large-cap-alt-volume-share only
- ETH/BTC only
- BTC.D only
- all simple two-component combinations
- matched non-trigger periods
- timestamp-shift placebo where meaningful
- breadth-only and current-stack context

## Outcomes

Freeze and report all horizons without winner selection:

`6h, 12h, 24h, 48h, 72h, 7d, 14d, 30d`

Track:

- lead time to independently defined rotation confirmation
- false starts
- missed opportunities
- BTC outcome separately from ecosystem/alt outcome
- regime stratum and sample n
- incremental information relative to baselines

## Falsifier

The hypothesis is not supported if, after a sufficient eligible prospective sample, the composite fails to add useful lead-time, calibration or filtering information beyond simpler component baselines after dependence is accounted for.

No threshold may be changed after observing outcomes to rescue the test. Any new descendant definition requires a new test ID.

## Stop rules

- Do not score before data readiness is frozen.
- Do not backfill pre-registration rows.
- Do not select the best horizon post hoc.
- Do not count RRS or Type 3 as independent confirmation of this sensor.
- Historical success-language is not evidence for this prospective test.
