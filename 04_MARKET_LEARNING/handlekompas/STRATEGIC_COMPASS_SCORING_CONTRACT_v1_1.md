# Strategic Compass Scoring Contract v1.1

Status: PRE-REGISTERED BEFORE FIRST STRATEGIC ANCHOR / OUTCOME

Contract ID: `STRATEGIC_COMPASS_SCORING_v1_1`

Supersedes `STRATEGIC_COMPASS_SCORING_v1` before first live strategic anchor. The supersession fixes asset-specific direction and scenario-weight semantics; it does not rewrite any realized outcome because none existed at activation.

## Purpose

Extend Compass accountability beyond 12h / 72h / 168h without creating a parallel cycle engine.

- `21-30D`: strategic market-path anchor.
- `4-8W`: Cycle Navigator structural overlay only.

## 21-30D immutable anchor

Freeze prospectively:
- overall market direction;
- BTC direction;
- ETH direction;
- ETH/BTC direction;
- ordered path;
- regime destination;
- pullback / distribution posture where supportable;
- rotation / transmission expectation;
- action posture within existing authority;
- falsification conditions;
- confidence and missingness;
- BASE / BULL / BEAR scenario **weights** summing to 100.

Scenario weights are explicitly `UNCALIBRATED_SCENARIO_WEIGHT_NOT_PROBABILITY`.
They must not be described as calibrated probabilities until a future preregistered calibration contract is satisfied.

## 4-8W

Cycle Navigator remains the structural owner. The Strategic Compass only binds its immutable 4-8W projection and lineage.

A generic 4-8W cycle direction must **not** be scored as if it were a BTC or ETH price-direction forecast unless the frozen source explicitly contains asset-specific directions.

## Thesis state

Live readback may classify the frozen thesis:

`ON_TRACK | ACCELERATING | WEAKENING | INVALIDATED | DATA_DEGRADED`

The readback never mutates the anchor.

## Checkpoints

21-30D:
- T+7 monitor only
- T+14 monitor only
- T+21 strategic checkpoint
- T+30 final maturity

4-8W:
- T+14 monitor only
- T+28 monitor only
- T+42 strategic checkpoint
- T+56 final maturity

## Scoring

Where governed evidence exists, report separately:
1. BTC direction against frozen `btc_direction`;
2. ETH direction against frozen `eth_direction`;
3. ETH/BTC direction against frozen `ethbtc_direction`;
4. MFE / MAE;
5. path / sequence;
6. regime destination;
7. pullback class / timing;
8. breadth / transmission;
9. rotation ladder;
10. distribution warning;
11. action utility;
12. falsification timing;
13. abstention / missingness.

Do not substitute the overall market direction for a missing asset-specific direction.

4-8W BTC/ETH direction scoring remains `UNAVAILABLE_NO_ASSET_SPECIFIC_FORECAST` unless future frozen CN evidence explicitly provides those fields.

## Cross-horizon learning

Preserve disagreement across 12h / 72h / 168h / 21-30D / 4-8W.

Measure, after sufficient mature evidence:
- lead time from tactical deterioration/confirmation to strategic invalidation/confirmation;
- false tactical alarms;
- missed strategic transitions;
- false-negative opportunity cost.

## Statistical safeguards

Rolling weekly strategic anchors overlap heavily and are serially correlated.
Never count overlapping anchors as independent trials.
No flattering aggregate accuracy score.
No hindsight reconstruction.
Missing evidence stays missing.
Simple baselines must be reported where applicable.

## Master Monday

Master Monday is the calibration/orchestration point:
- consume mature tactical and strategic outcomes;
- inspect recurring errors;
- never rewrite prior anchors;
- freeze new prospective strategic anchors only from eligible evidence.

## Authority ceiling

Navigation and forecast-accountability only.

No portfolio execution.
No source override.
No market-threshold or model-weight changes.
No automatic promotion of research or shadow evidence.
