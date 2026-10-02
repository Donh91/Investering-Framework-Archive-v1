# Shadow Compass v2 Scoring Contract v2

Status: OPERATIVE TIME-BASIS CONTRACT

Contract ID: `SHADOW_COMPASS_V2_SCORING_v2`

## Purpose

Materialize the scoring contract already referenced by the active Shadow Compass v2 outcome scorer and matured outcome files.

This contract changes only outcome time-basis semantics relative to the preregistered v1 document. It does not alter any frozen Shadow forecast, direction, confidence, pullback-risk state, model output, threshold, market authority or portfolio action.

## Inherited v1 semantics

The following remain unchanged from the preregistered Shadow Compass v2 v1 contract:

- horizons: 12h, 72h and 168h;
- direction scoring for UP, DOWN, SIDEWAYS and abstentions;
- SIDEWAYS tolerances identical to Official Daily Compass;
- BTC and ETH direction scoring;
- BTC/ETH MFE and MAE;
- ETH/BTC realized return when available;
- always-hold, persistence and no-edge baseline context;
- no interpolation or synthetic price path;
- shadow-only authority and no automatic promotion.

## Corrected scoring time basis

For every horizon:

1. The bound Auto Market State market reference remains the frozen start value.
2. Start time is the completed source observation close:
   - `source_window_end_utc` when present; otherwise
   - `observation_open_utc + 1h` for the governed hourly source.
3. Target time is `start_reference_at_utc + nominal_horizon`.
4. Hourly price rows are interpreted by completed-candle close time, not the candle-open label.
5. The endpoint must be the closest completed hourly close within one hour of target.
6. If no such endpoint exists, the outcome remains pending/unscored.
7. An effective window whose deviation from nominal exceeds one hour is not scored.
8. The outcome records:
   - nominal horizon;
   - start-reference timestamp;
   - issue-to-reference age;
   - target time;
   - target observation close;
   - effective window hours;
   - window deviation;
   - endpoint semantics.

## Source integrity

The frozen forecast must remain bound to its original Auto Market State packet.

If the bound packet is missing, unreadable or hash-incompatible, the outcome must fail closed and must not be substituted with a later packet.

## Versioning and immutability

- Historical forecast files remain immutable.
- Existing outcome files remain immutable.
- Newly matured Shadow Compass v2 outcomes use `SHADOW_COMPASS_V2_SCORING_v2`.
- Comparisons with Official Compass must disclose scoring-contract versions where they differ.
- No historical row may be rescored merely to improve apparent accuracy.

## Shadow vs Official pairing

The deterministic comparison layer uses `SHADOW_OFFICIAL_PAIRING_v1`.

A comparable pair requires identical:

- horizon;
- start-reference close;
- target time;
- target observation close.

Pair selection is outcome-blind and one-to-one. Correctness and realized returns are inspected only after selection as comparison evidence and integrity checks.

The pairing layer carries no aggregate-winner authority, no automatic model promotion, no threshold or weight change, no Official Compass override and no portfolio execution authority.

## Authority

Research / challenger evidence only.

No portfolio execution.
No Official Compass override.
No source override.
No automatic promotion.
No market-gate change.
No model-weight change.
No threshold change.
