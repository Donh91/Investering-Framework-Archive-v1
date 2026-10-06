# S5 - Derivatives Crowding to Pullback v1

Status: REPRODUCTION_BUILD / RESEARCH_ONLY / NO_COMPASS_AUTHORITY
Priority: P0-P1
Master queue: README.md
Master issue: #1512
Execution issue: #1514

## Purpose

Test whether exchange-native derivatives structure adds prospective information about pullback/distribution risk before price weakness becomes obvious.

This lane extends existing owners. It does not create a new market engine.

Owners reused:
- Meme Alpha `SPOT_PERP_FLOW_DIVERGENCE_V1` for the spot/perp state vocabulary;
- `COMPASS_PROTECTION_TRACKER_v1` for canonical protection-state ownership;
- M6 Lane C and `M6_EVENT_OUTCOME_CONTRACT_v1` for prospective warning/outcome measurement.

## Core question

Does:

`spot taker flow x futures taker flow x delta OI x funding/basis x price response`

improve pullback/distribution discrimination beyond simpler baselines?

Liquidation maps and options positioning are later challengers, not prerequisites.

## Source strategy

### Baseline first

Use reproducible exchange-native/public data before paid composite providers.

A live source proof on 2026-10-06 confirmed the connected Binance public read-only source exposes:
- USDS perpetual hourly OI statistics;
- hourly futures taker buy/sell volume;
- hourly spot klines with quote volume and taker-buy quote volume;
- funding history;
- perpetual basis;
- price klines;
- current ADL risk.

This closes the source-capability question for a baseline, but not runtime reliability.

### Source-agnostic requirement

The Framework archive also records historical cases where Binance Futures returned HTTP 451 and OKX was used instead.

Therefore:
- every capture keeps `source_id` and `venue`;
- transformer logic is provider-neutral;
- Binance is not permanent sole authority;
- a future runtime collector must have explicit source-health/fallback semantics.

## Point-in-time capture contract

Each immutable capture contains:
- source_id;
- venue;
- symbol;
- decision_cutoff_utc;
- source/retrieval provenance;
- hourly spot rows;
- hourly futures taker rows;
- hourly OI rows;
- hourly basis rows;
- funding events.

`decision_cutoff_utc` is the start of the first not-yet-admitted interval.

Only complete hourly intervals strictly before the cutoff may be used.

An incomplete/live current bar may exist in the raw capture but must not affect the feature vector.

## Continuous features

For each 1h / 4h / 12h / 24h window:

### Price response

`close_last_completed / close_h_hours_before - 1`

### OI value change

`OI_value_last_completed / OI_value_h_hours_before - 1`

Use OI notional value for the primary baseline so cross-price changes are not silently ignored.

### Futures taker imbalance

`(buy_volume - sell_volume) / (buy_volume + sell_volume)`

This is aggressive futures-flow imbalance, not proof of opening longs/shorts.

### Spot taker imbalance

Spot klines expose total quote volume and taker-buy quote volume.

`taker_sell_quote = total_quote - taker_buy_quote`

`spot_taker_imbalance = (taker_buy_quote - taker_sell_quote) / total_quote`

Equivalent:
`(2 * taker_buy_quote - total_quote) / total_quote`

### Context fields

Freeze:
- latest basis known before cutoff;
- latest funding known before cutoff;
- source coverage and missingness.

No future funding event may leak into the vector.

## Threshold-free compatibility tags

v1 does not tune numeric thresholds.

It may emit non-exclusive logical compatibility tags using sign only:

- `SPOT_ABSORPTION_SHORT_PRESSURE_COMPATIBLE`
  - spot imbalance > 0
  - futures imbalance < 0

- `BROAD_RISK_ON_COMPATIBLE`
  - spot > 0
  - futures > 0
  - OI change > 0
  - price return > 0

- `LEVERAGE_LED_PUMP_COMPATIBLE`
  - spot <= 0
  - futures > 0
  - OI > 0
  - price > 0

- `DISTRIBUTION_INTO_LEVERAGED_LONGS_FLOW_COMPATIBLE`
  - spot < 0
  - futures > 0
  - OI > 0
  - price response is preserved separately

- `HEALTHY_DELEVERAGING_COMPATIBLE`
  - futures < 0
  - OI < 0
  - spot >= 0
  - price >= 0

- `BROAD_WEAKNESS_COMPATIBLE`
  - spot < 0
  - futures < 0
  - price < 0

Multiple tags are allowed.

A compatibility tag is not a Compass state, warning or action.

Near-zero handling is deliberately not optimized in v1. If later evidence shows sign noise dominates, an epsilon family must be separately preregistered before evaluation.

## Baselines

S5 must beat simpler views before it matters:

1. price return only;
2. OI + funding only;
3. spot taker imbalance only;
4. futures taker imbalance only;
5. spot/futures divergence only;
6. full crowding vector.

No benefit from extra complexity means simplify/kill.

## Outcome binding

Do not invent new pullback truth.

Join frozen S5 observations to the existing M6 prospective outcome clock.

M6 horizons:
- 24h
- 72h
- 7d
- 14d
- 30d

Primary continuous outcomes:
- terminal return;
- MAE;
- MFE;
- time to MAE;
- time to MFE.

Existing BTC adverse barriers:
-10%, -15%, -20%.

Existing ETH adverse barriers:
-15%, -20%, -30%.

BUILDING remains watch-only.
ELEVATED/HIGH/CONFIRMED remain the existing warning-family admission states.

S5 cannot create a warning after observing the outcome.

## Research hypotheses

### H-S5-001 - leverage-led fragility

Rising OI + positive futures imbalance with weak/non-positive spot imbalance has worse later MAE/terminal outcomes than matched spot-supported states.

### H-S5-002 - distribution into leveraged demand

Negative spot imbalance + positive futures imbalance + rising OI adds drawdown/distribution information beyond OI/funding alone.

### H-S5-003 - healthy deleveraging

OI contraction + futures sell pressure + resilient positive spot flow is less fragile than deleveraging accompanied by spot selling.

### H-S5-004 - incremental value

The full vector must improve discrimination beyond its simplest dominant component.

## CoinGlass / Laevitas posture

CoinGlass:
use later as liquidation/aggregation challenger if source/cost audit passes.

Laevitas:
use later as options-IV/skew/GEX challenger if it adds information beyond baseline derivatives state.

Do not buy complexity before the exchange-native baseline is graded.

## Promotion boundary

Possible terminal states:
- `FULL_VECTOR_INCREMENTAL_VALUE_SUPPORTED`
- `SIMPLER_BASELINE_SUFFICIENT`
- `SOURCE_COVERAGE_TOO_UNSTABLE`
- `NO_PROSPECTIVE_EDGE`
- `INSUFFICIENT_INDEPENDENT_EPISODES`

None creates SELL/TRIM/BUY authority.

Any future Compass use requires a separate governed promotion decision after prospective evidence.

## Authority

RESEARCH_ONLY.
No portfolio execution.
No new protection state.
No threshold changes.
No alert authority.
No canonical Compass mutation.
