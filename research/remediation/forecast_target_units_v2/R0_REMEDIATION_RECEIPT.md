# R0 Forecast Target Unit Remediation

Status: implementation candidate on isolated branch.

## Defect verified

The prior pipeline exposed a generic `threshold` field without units. The experiment lifecycle and manual ratification paths copied that value into `threshold_pct`, while the maturation engine compared it with percentage return.

Concrete repository examples include directional forecasts where an absolute BTC or breadth target was persisted as `threshold_pct`.

## Fix boundary

- no market rule change
- no sensor change
- no portfolio authority
- no historical frozen forecast rewrite
- no silent rescore
- no Gauntlet outcome execution

## Forward contract

Directional forecasts must use one of:

- `PCT_MOVE` + positive `threshold_pct`
- `ABSOLUTE_VALUE` + `target_value`

Range forecasts use:

- `ABSOLUTE_RANGE` + `range_low` + `range_high`

Absolute targets are converted once at freeze using the frozen `start_value`. The resulting frozen row records `unit_contract_version=FORECAST_TARGET_UNITS_v2`.

## Legacy handling

Old directional `FROZEN_FORECAST_v1` rows without the explicit unit contract are treated as unit-ambiguous and censored rather than scored HIT/MISS. Existing immutable rows are preserved.

Old automatic experiment RANGE rows with `source_candidate_id` remain admissible because their historical creation path converted absolute bounds into percent bounds before freeze. Other legacy range rows without explicit unit lineage remain censored.

Old `FORECAST_TEST` experiment candidates without an explicit unit contract are quarantined and cannot re-fire after the upgrade.

The model calibration ledger excludes outcomes linked to unit-ambiguous legacy forecasts, including already-created outcomes.

## Validation

Deterministic pre-publish checks covered:

- directional percentage target
- absolute BTC target conversion
- absolute range conversion
- ambiguous legacy candidate rejection
- legacy directional maturation quarantine
- calibration exclusion
- legacy experiment candidate no-refire after upgrade

Repository CI must pass before merge.
