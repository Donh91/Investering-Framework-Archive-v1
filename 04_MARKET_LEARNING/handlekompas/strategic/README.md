# Strategic Compass

Status: ACTIVE FORWARD-ONLY RUNTIME CONTRACT

Purpose: extend Compass accountability beyond the existing 12h / 72h / 168h daily scoring without creating a parallel market-state or cycle engine.

## Runtime chain

`Master Monday -> Cycle Navigator weekly freeze -> final CN consumer-receipt binding -> Strategic Compass anchor -> checkpoint outcomes -> next Master Monday calibration`

Owners:
- 12h / 72h / 168h: Official Daily Compass.
- 21-30D: explicit `decision_projection.next_21_30d` from the weekly Cycle Navigator generation. Never stretch the existing 2-3W field into a month forecast.
- 4-8W: Cycle Navigator `weeks_4_8` projection only. No parallel 4-8W engine.

## Artifacts

- `LATEST_STRATEGIC_COMPASS.json` - mutable pointer only.
- `anchors/YYYY/MM/DD/SC-*.json` - immutable prospective anchors.
- `outcomes/YYYY/MM/DD/SC-*_*.json` - immutable checkpoint/maturity evidence.

The materializer is `scripts/learning/strategic_compass.py`.
The maturity writer is `scripts/learning/strategic_compass_outcomes.py`.
The scoring/governance contract is `../STRATEGIC_COMPASS_SCORING_CONTRACT_v1_1.md`.

## Fail-closed rules

- Missing 21-30D projection => `UNAVAILABLE`; never infer it from 2-3W.
- Missing/maturing 4-8W CN evidence => `UNAVAILABLE`.
- Horizon disagreement is preserved.
- Stabilization is not continuation; absorption is not recovery.
- No portfolio execution, threshold changes, source overrides or post-hoc forecast rewrites.
- No synthetic aggregate accuracy score.
- Overlapping rolling anchors are not independent trials.

## Weekly learning

Matured tactical and strategic Compass outcomes are ingested into the frozen Master Monday calibration context under `compass_learning`. They are calibration evidence only and cannot automatically promote rules or weights.

## Long-range candidate validation (research only, no publication)

An optional offline preflight for proposed 1–12 month SHADOW scenario packets is
`scripts/learning/strategic_compass_long_range_validation.py`.
It validates the isolated `LONG_RANGE_SCENARIO_v0_1_CANDIDATE` format;
**it is not wired to the official producer, site, API gateway, or outcome scorer**.

Run explicitly on a private-data-safe candidate JSON:
```sh
python -m scripts.learning.strategic_compass_long_range_validation candidate.json
python -m unittest tests.learning.test_strategic_compass_long_range_validation
```

Fail-closed rules include UTC knowledge/cutoff/issue order, future and ordered
scenario windows, finite positive price bands, exact evidence-source clock,
no unsettled inputs for supported scenarios, `UNAVAILABLE` versus `ABSTAIN`,
invalidation/falsifier dates, no fabricated calibrated probabilities, and no
self-revision or unbound original forecast references. A revision is rejected
until the caller independently supplies immutable earlier-original receipts
to `validate_candidate(..., prior_issues=...)`.

**Scope ceiling:** validation is not first-known provider proof, GitHub release
attestation, event/outcome evidence, calibrated decision quality, or forecast
performance. It must not be used to rewrite existing 21–30D/4–8W source
anchors, to manufacture future predictions, or to change official Compass /
PATH / CN ranges. The proposed research contract needs a separately reviewed
owner integration and Task 2 scientific admission before any broader use.
