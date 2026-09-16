# Official Daily Compass Scoring Contract v1

Status: PRE-REGISTERED BEFORE FIRST OFFICIAL DAILY COMPASS OUTCOME

Contract ID: `OFFICIAL_DAILY_COMPASS_SCORING_v1`

## Purpose

Score the official daily Compass prospectively without rewriting its frozen forecast. Forecast artifacts are immutable. Outcome artifacts are separate and may only be created after their registered horizon has matured.

## Horizons

- `12h` matures at issued time + 12 hours and scores `NEXT_12H`.
- `72h` matures at issued time + 72 hours and scores `NEXT_1_3D`.
- `168h` matures at issued time + 168 hours and scores `NEXT_5_7D`.

No outcome may be scored before maturity. Missing outcome evidence remains missing and is not converted to zero or a miss.

## Direction scoring

The frozen market-direction call is evaluated independently against realized BTC and ETH returns.

- `UP`: correct when realized return is greater than 0%.
- `DOWN`: correct when realized return is less than 0%.
- `SIDEWAYS`: correct when absolute realized return is within the registered tolerance.
- `MIXED`, `NO_EDGE`, `UNAVAILABLE`: abstention; excluded from directional hit denominators.

Sideways tolerances are frozen here before first outcome:

- 12h: ±1.5%
- 72h: ±3.0%
- 168h: ±5.0%

These are accountability tolerances only. They are not market-state thresholds and have no execution authority.

## Trigger scoring

The official Compass uses registered Native Handlekompas action-state transitions as observable trigger events.

Confirmation event:
`PREPARE` or `GRADUATED_TOPUP_ACTIVE`

Deterioration event:
`HOLD_DEFENSIVE_WAIT` or `HOLD_WAIT_DATA_DEGRADED`

For each matured horizon, the scorer records whether either event occurred and the first observed timestamp from immutable Native Handlekompas runs. If the relevant historical runs are unavailable, trigger timing remains unavailable.

## Excursion evidence

Where hourly owner data exists, record BTC and ETH:

- realized end-of-horizon return;
- maximum favorable excursion (MFE);
- maximum adverse excursion (MAE).

No interpolation or synthetic price path is allowed. Target observations may use the nearest governed hourly close within ±2 hours; otherwise the target outcome remains missing.

## Action utility

Action quality is deliberately separate from direction accuracy. V1 records a transparent proxy only:

- `DEPLOY` / `PREPARE`: positive realized BTC return is `FAVORED`; non-positive is `NOT_FAVORED`.
- `WAIT` / `HARD_WAIT` / `HOLD`: negative realized BTC return is `PROTECTIVE`; otherwise `OPPORTUNITY_COST_OR_NEUTRAL`.
- unsupported/no-edge actions abstain.

This is not portfolio PnL and cannot be presented as execution performance.

## Rotation ladder scoring

BTC and ETH realized outcomes may be measured directly. Large-, mid-, small- and micro-cap ladder accuracy is not proxy-scored until a governed capitalization-bucket outcome series exists. V1 therefore records `UNAVAILABLE_NO_GOVERNED_CAP_BUCKET_RETURN_SERIES` rather than inventing a benchmark.

## Baselines

Every mature outcome records:

1. `always_hold_btc_return_pct` — realized BTC return over the horizon;
2. `persistence` — direction implied by the pre-freeze BTC change when that exact value exists;
3. `no_edge` — 0% reference only.

The framework must not celebrate Compass direction accuracy without comparing it against these simple references when sufficient rows accumulate.

## Aggregate reporting

Do not create one flattering composite score. Report components separately:

- direction accuracy by horizon and asset;
- trigger occurrence/timing;
- action-utility proxy;
- MFE/MAE;
- abstention count/quality;
- false-positive / false-negative counts when the sample is sufficient;
- rotation-ladder accuracy only where governed bucket outcomes exist;
- baseline comparisons.

Any future aggregate or weighted score requires a new pre-registered contract before it is applied to new outcomes.

## Authority ceiling

`OFFICIAL_NAVIGATION_OUTPUT` only.

No portfolio execution authority. No source override authority. No post-hoc forecast rewrite. No change to Master Monday, Cycle Navigator history, market thresholds or model weights.
