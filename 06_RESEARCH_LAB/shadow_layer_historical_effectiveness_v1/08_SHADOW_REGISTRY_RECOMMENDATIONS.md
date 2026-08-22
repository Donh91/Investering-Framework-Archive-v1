# Shadow Registry Recommendations

## Objective

Make the Shadow Registry the durable index for the full non-canonical research universe without pretending that every historical sensor is currently scorable.

## Recommended registry model

Each sensor/research family should expose:

- `sensor_id`
- `family`
- `status`
- `information_role`
- `evidence_paths`
- `definition_quality`
- `historical_event_state_quality`
- `current_forward_evidence_quality`
- `redundancy_cluster`
- `relevance_state`
- `old_claims_status`
- `next_scientific_action`

## Information-role vocabulary

Use one or more of:

- `EARLY_WARNING`
- `CONFIRMATION`
- `VETO`
- `TIMING`
- `REGIME_CLASSIFIER`
- `RISK_DETERIORATION`
- `META_CONTROL`
- `CONTEXT_ONLY`

This prevents a useful veto sensor from being incorrectly rejected because it is not a good predictor.

## Redundancy clusters

Recommended cluster IDs:

- `ROTATION_RELATIVE_STRENGTH`
- `BREADTH_PARTICIPATION`
- `BTC_CONCENTRATION_DOMINANCE`
- `LIQUIDITY_AVAILABILITY_DEPLOYMENT`
- `ETF_ABSORPTION_QUALITY`
- `LEVERAGE_VOLATILITY_STRESS`
- `MACRO_CYCLE_CONTEXT`
- `ADAPTIVE_META_LEARNING`

A weekly calibration should explicitly flag if several active shadow observations come from the same redundancy cluster.

## Old-claim status

Add a field such as:

- `REPRODUCED`
- `NOT_REPRODUCED`
- `UNVERIFIED_ARCHIVE_CLAIM`
- `NOT_APPLICABLE`

Recommended immediate labels:

- Fake Rotation Type 3 55-75% failure: `NOT_REPRODUCED`
- Early Rotation Pre-Trigger near-perfect history: `UNVERIFIED_ARCHIVE_CLAIM`
- old microcap 75-85% failure wording: `UNVERIFIED_ARCHIVE_CLAIM`
- Shadow v1-v8 cycle hit-rate table: `UNVERIFIED_ARCHIVE_SYNTHESIS`

## Weekly calibration behavior

Weekly Shadow calibration should ask:

1. Did a registered shadow family produce a new immutable observation?
2. Did a prior observation mature at any fixed horizon?
3. Did a simpler baseline produce the same conclusion?
4. Did several named sensors merely repeat one redundancy cluster?
5. Did any shadow family create a false negative by delaying recognition without reducing risk?
6. Did source identity or semantics change?
7. Does any old claim need downgrade or retirement?

## Registry relationship to this archive

The registry should link this research directory as its broad historical map:

`06_RESEARCH_LAB/shadow_layer_historical_effectiveness_v1/`

The current 14-sensor `LEGACY_RECOVERY_QUEUE.json` remains useful, but must be interpreted as one recovered legacy family within the broader Shadow Layer.

## No automatic promotion

The registry must continue to enforce:

- research-only authority,
- no portfolio execution,
- no automatic rule changes,
- no automatic weighting changes,
- no promotion from historical fit alone.

The most a historical review can do is prioritize a clean prospective test or justify retirement.