# Shadow Compass v2 Scoring Contract v1

Status: PRE-REGISTERED BEFORE FIRST SHADOW OUTCOME

Contract ID: `SHADOW_COMPASS_V2_SCORING_v1`

## Purpose

Evaluate the forward-only GPT-6.1 Sol Shadow Compass v2 against the same governed BTC/ETH hourly evidence and the same directional tolerances used by Official Daily Compass.

This contract exists to answer whether the richer shadow reasoner adds prospective forecast value. It does not authorize automatic promotion.

## Horizons

- `12h` matures at issue + 12 hours.
- `72h` matures at issue + 72 hours.
- `168h` matures at issue + 168 hours.

No outcome may be written before maturity. Target observations use the nearest governed hourly close within ±2 hours, identical to Official Compass accountability semantics.

## Direction scoring

Score each frozen shadow direction independently against BTC and ETH realized returns.

- `UP`: correct if realized return > 0%.
- `DOWN`: correct if realized return < 0%.
- `SIDEWAYS`: correct if absolute realized return stays within the preregistered tolerance.
- `MIXED`, `NO_EDGE`: abstention.

Sideways tolerances are deliberately identical to Official Daily Compass:

- 12h: ±1.5%
- 72h: ±3.0%
- 168h: ±5.0%

## Excursion evidence

Record BTC and ETH:
- end-of-horizon return;
- MFE;
- MAE;
- ETH/BTC realized return when evidence exists.

No interpolation and no synthetic price path.

## Baselines

Every mature row records:
- always-hold BTC realized return;
- persistence baseline from the exact bound Auto Market State predecessor delta when available;
- no-edge 0% reference.

The shadow reasoner is not considered useful merely because it is directionally correct. Comparisons must account for simple baselines.

## Comparison with Official Compass

Shadow and Official rows remain separate immutable evidence families.

When enough rows exist, compare only prospectively comparable observations, preferably the same or nearest scheduled slot and clearly disclose:
- differing issue timestamps;
- differing source packets;
- overlapping horizons;
- abstentions;
- serial correlation.

Do not manufacture a head-to-head winner from mismatched observations.

## Model reasoning fields

Supporting evidence, counterevidence, missing evidence, confidence, pullback-risk and transmission-state are frozen forecast metadata.

V1 scores direction and realized path only. Narrative reasoning fields are retained for later governed error-taxonomy analysis and must not be retrospectively reinterpreted as scored predictions.

## Authority

Shadow learning only.

No portfolio execution.
No Official Compass override.
No source override.
No threshold or model-weight change.
No automatic promotion.
No aggregate flattering accuracy score.

## Deterministic Shadow vs Official pairing

The implementation uses `SHADOW_OFFICIAL_PAIRING_v1` and remains outcome-blind.

A pair is eligible only when the already-matured Shadow and Official outcomes have identical:
- horizon;
- start-reference close;
- target time;
- target observation close.

Among eligible rows, the nearest issue timestamp is selected deterministically. Each Shadow outcome and each Official outcome may be used at most once.

Correctness, realized return, MFE and MAE are not used to choose the pair. They are inspected only after pairing. A realized-path mismatch is an integrity failure; the comparator does not search for another row that would produce a better result.

The comparison may expose per-asset states such as both correct, both incorrect, one correct while the other is incorrect, or one side abstaining. It must not produce an aggregate winner, flattering accuracy score, automatic promotion, model-weight change, threshold change, Official Compass override or portfolio action.

The comparator is deterministic and read-only. It does not create or rewrite forecast/outcome evidence.

