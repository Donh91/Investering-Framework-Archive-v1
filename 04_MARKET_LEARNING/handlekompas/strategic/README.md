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
python -m unittest discover -s tests/learning -p test_strategic_compass_long_range_validation.py
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

## Prospective 14/21-day price-range preflight (candidate only)

The owner-approved D8–14 / D15–21 source-clock validator is
`validate_forward_range_candidate` inside the existing
`scripts/learning/strategic_compass.py`; its negative controls are exercised
by the existing Official Compass Outcomes PR CI through
`tests/learning/test_strategic_compass.py`.

`COMPASS_14_21D_RANGE_PREFLIGHT_v1` accepts **only** structurally
source-bound research candidates or explicit `UNAVAILABLE` / `ABSTAIN`
intervals. The exact two window boundaries are measured from the published
CN forecast ISO week's Monday UTC: D8–14 and D15–21. It requires issued
week/issue identity, strict source first-known <= cutoff <= issued ordering,
bounded pre-outcome issuance, independently specified BTC/ETH intervals,
positive finite ordered USD low/high, and no self-promoted publication,
score or portfolio authority. Future daily/hourly expected prices and
post-outcome results are not part of this contract. Existing frozen W43
weekly and intraday forecasts are never transformed into longer ranges.

If no source receipt exists, the candidate object's `source` may be `null`
**only** for `UNAVAILABLE`/`ABSTAIN` windows; no dummy hash or inferred
price band is required or permitted. Any non-null proposed price band must
bind syntactically to the original source metadata, which remains subject
to independent proof outside this preflight.

**Important:** This is **NOT** a newly active 14/21-day forecast producer,
no source first-knowable attestation, no Monday freeze or scoring endpoint,
and not proof that the source's hash or receipt is real. It provides a
negative-guard preflight only. Real issued price ranges require original
source/receipt custody, prospective independent publication readback,
immutable issuance and weekly forecast ID binding, plus separately governed
producer/consumer integration with Master Monday/CN #1593 and the site
#1578. If evidence is absent, the correct production result remains
`UNAVAILABLE`; no continuous/fictitious blue path is authorized.
