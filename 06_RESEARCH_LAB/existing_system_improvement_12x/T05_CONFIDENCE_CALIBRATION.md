# T05 - Confidence Calibration

**State:** FINDING_FROZEN
**Existing owners:** Daily Director shadow output; existing forecast/outcome accountability

## Current evidence

The current Daily Director prompt requires a machine-readable first-line header containing `CONFIDENCE=LOW|MEDIUM|HIGH` alongside canonical phase/warning vocabulary.

Existing `FORECAST_CANDIDATE_v1` and `FROZEN_FORECAST_v1` artifacts preserve target, horizon, source/output hashes and experimental lineage, but confidence is not carried as a causally bound forecast field. Historical Director outputs may mention confidence only in prose or may predate the structured header.

Therefore a retrospective calibration of LOW/MEDIUM/HIGH would require heuristic text extraction and source reconstruction for older rows, which conflicts with prospective evidence discipline.

## Frozen finding

`STRUCTURED_CONFIDENCE_NOT_PROSPECTIVELY_BOUND_TO_OUTCOME_LINEAGE`

Confidence exists as communication metadata, but its empirical calibration is not yet directly measurable without reconstruction.

## Required improvement

Add a research-only immutable confidence-binding sidecar for future valid Daily Director outputs. It should freeze:

- source Daily Director output path + hash;
- context hash / receipt identity;
- exact `CYCLE_HEADER` phase, warning, direction and confidence;
- exact forecast-candidate IDs emitted by that output, if any;
- creation timestamp;
- authority flags excluding canonical state, portfolio action, weight changes and automatic confidence tuning.

Later calibration may consume only matured, non-censored outcomes for causally linked candidate/forecast IDs. It should report sample count and empirical outcome quality by LOW/MEDIUM/HIGH, plus whether ordering is monotonic. It must not auto-change prompts, thresholds, model choice or market actions.

## No historical backfill

Older prose-only confidence statements are context only. They must not become prospective calibration rows unless an immutable machine field and exact lineage already existed at the time.

## Acceptance

Positive: a future Director output with a valid structured header produces exactly one immutable binding to its exact output/receipt and candidate IDs; matured eligible outcomes can later be grouped by the frozen confidence label.

Negative: malformed/missing header produces explicit `CONFIDENCE_BINDING_UNAVAILABLE`; no inference from rationale prose; censored outcomes do not count as success/failure; no automatic confidence remapping.

## Review gate

Do not draw ordering conclusions until each confidence bucket has a meaningful eligible sample. Until then report `LOW_SAMPLE`.
