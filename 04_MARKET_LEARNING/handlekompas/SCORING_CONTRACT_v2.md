# Official Daily Compass Scoring Contract v2

Status: PROSPECTIVE TIME-BASIS CORRECTION

Contract ID: `OFFICIAL_DAILY_COMPASS_SCORING_v2`

## Why v2 exists

V1 treated hourly row labels as if they were observation-close timestamps and anchored the horizon to forecast issuance time even when the frozen market reference was an earlier completed hourly candle. That can lengthen the realized measurement window, especially for the 12h lane.

V2 changes only outcome time-basis semantics. It does not rewrite any forecast, threshold, direction, action posture, market authority, model weight, or portfolio decision.

## Scoring time basis

For 12h / 72h / 168h:

1. The immutable forecast's market reference remains the start value.
2. Start time is the completed source observation time:
   - `source_window_end_utc` when present; otherwise
   - `observation_open_utc + 1h` for the governed hourly source.
3. Target time is `start_reference_at_utc + nominal_horizon`.
4. Hourly `*_close` values are timestamped by their completed-candle close time, not the candle-open label.
5. The endpoint must be the closest completed hourly close within one hour of target.
6. If no such endpoint exists, the outcome remains unscored/pending.
7. Outcomes persist:
   - nominal horizon;
   - start-reference timestamp;
   - forecast issue-to-reference age;
   - effective window hours;
   - window deviation;
   - endpoint semantics.

A realized endpoint whose effective window differs from nominal by more than one hour is not scored.

## Immutability and versioning

- Existing `OFFICIAL_DAILY_COMPASS_SCORING_v1` outcomes remain immutable historical evidence.
- No existing outcome file is rewritten.
- Newly matured outcomes after deployment use v2.
- Shadow Compass uses the same corrected close-time semantics under `SHADOW_COMPASS_V2_SCORING_v2`.
- Comparisons across v1 and v2 must disclose the scoring-contract version.

## Unchanged components

Direction tolerances remain:
- 12h: ±1.5% for SIDEWAYS
- 72h: ±3.0%
- 168h: ±5.0%

MFE/MAE, persistence baseline, action-utility proxy, trigger timing, and zero portfolio authority remain otherwise unchanged.
