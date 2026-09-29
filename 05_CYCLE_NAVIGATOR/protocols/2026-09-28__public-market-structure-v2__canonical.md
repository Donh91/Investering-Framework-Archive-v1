# Cycle Navigator Public Market / Structure v2.1

Status: ACTIVE_LONG_TERM_FROM_PUBLIC_CN27
Effective forecast week: 2026-W40
Full v2.1 freeze semantics effective: next newly generated public issue after CN27
Authority: PUBLIC_FORECAST_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY

## Purpose

Market / Structure answers a different question from Price Ranges:

- **Price Ranges:** where did BTC/ETH trade?
- **Market / Structure:** what market state, leadership quality, capital transmission, rotation depth and confirmation quality actually developed?

The public score must represent CN's forward-looking structural edge, not facts a reader can obtain from a single price chart.

CN #26 closes the legacy structure method. Historical scores are never retroactively rewritten. CN #27/W40 is the first five-slot baseline under the final permanent slot design. Its final user-approved public copy is the scoring source for CN #28.

## Five permanent public slots

Every weekly CN uses the same five slots, in the same order:

1. **REGIME & RESILIENCE** - market phase and whether the structure survives volatility/retests.
2. **LEADERSHIP** - quality and persistence of relative leadership, not one ratio close in isolation.
3. **ROTATION / TRANSMISSION** - whether capital actually hands off from leadership into the next market-cap layers.
4. **BREADTH & PERSISTENCE** - whether participation is broad and durable rather than narrow or short-lived.
5. **FLOW QUALITY / FRAGILITY** - whether price action is internally supported or fragile, synthesizing canonical flow, spot/microstructure, breadth, sentiment, relative-strength and counterevidence when available.

These are five different questions. One thesis may provide evidence to more than one slot, but it may never create more than one vote in the same slot or be duplicated as separate headline calls.

## CN edge requirement

A public structural call should be the output of evidence synthesis, not a restatement of one visible chart.

Depending on availability and authority, evidence can include:
- BTC/ETH price structure and volatility;
- ETH/BTC relative strength and persistence;
- breadth / participation proxies;
- market-cap cohort transmission;
- spot microstructure;
- settled ETF / flow evidence;
- sentiment and short-horizon return deterioration or improvement;
- rotation-engine context and persistence;
- other canonical Master Monday evidence.

Internal inputs may remain internal. The public post shows the conclusion, forecast, actual and score - not every proprietary/internal signal.

No single public chart or metric is automatically sufficient to score a dimension HIT unless that dimension's frozen resolution rule explicitly makes it sufficient.

## Prospective freeze: STATE + CHANGE

From the first newly generated issue after CN27, every dimension must prospectively freeze:

- `forecast` - concise public-facing call;
- `expected_state` - the state expected by weekly close;
- `expected_change` - IMPROVE / STABLE / DETERIORATE / NO_EDGE versus the freeze-time state;
- `hit_if` - exact conditions for 100;
- `mixed_if` - exact conditions for 50;
- `miss_if` - exact conditions for 0;
- `evidence_required` - evidence families required for adjudication.

This prevents an easy persistence forecast from scoring highly merely because a condition such as "no altseason yet" remained true.

## Scoring

Each slot receives exactly one outcome:

- **HIT = 100**
- **MIXED = 50**
- **MISS = 0**
- **NOT_EVALUABLE = null**

The public Market / Structure score is:

`(REGIME_RESILIENCE + LEADERSHIP + ROTATION_TRANSMISSION + BREADTH_PERSISTENCE + FLOW_QUALITY_FRAGILITY) / 5`

but only when **all 5/5 dimensions are evaluable**.

If coverage is below 5/5:
- no headline percentage is published;
- show coverage, e.g. `4/5 evaluable`;
- do not shrink the denominator;
- do not convert missing evidence into HIT, MIXED or MISS.

No weighting changes are allowed week to week.

## Score authority

From CN #27 onward, only the five frozen Market / Structure dimensions are public headline score authority.

The following may support evidence but do not become extra votes:
- legacy machine `structural_score`;
- `public_continuity_score`;
- separate `ethbtc_condition`;
- separate `breadth_condition`;
- price-range scores;
- internal shadow/research claims.

Price Ranges and Market / Structure remain separate score families. No synthetic overall accuracy percentage is created.

## Fixed weekly public format

The public review must use the same compact point format every week:

**MARKET / STRUCTURE: XX%**

1. **REGIME & RESILIENCE** - Forecast: [call] -> Actual: [outcome] -> **HIT/MIXED/MISS · score**
2. **LEADERSHIP** - Forecast: [call] -> Actual: [outcome] -> **HIT/MIXED/MISS · score**
3. **ROTATION / TRANSMISSION** - Forecast: [call] -> Actual: [outcome] -> **HIT/MIXED/MISS · score**
4. **BREADTH & PERSISTENCE** - Forecast: [call] -> Actual: [outcome] -> **HIT/MIXED/MISS · score**
5. **FLOW QUALITY / FRAGILITY** - Forecast: [call] -> Actual: [outcome] -> **HIT/MIXED/MISS · score**

Then immediately freeze the next week's same five slots.

The section may be shortened for X, but slot identity, order and score semantics must remain unchanged.

## Edge benchmark

Because market structure is persistent, raw hit rate alone can overstate skill.

Therefore v2.1 also freezes `expected_change`. This enables a future shadow benchmark against a naive persistence model that always predicts **STABLE / same state as last week**.

After at least 8 fully evaluable v2.1 weeks:
- compare CN structural score with persistence-baseline score;
- measure directional-change hit rate separately;
- do not claim structural edge from raw accuracy alone if CN does not beat persistence.

The benchmark is diagnostic and does not alter the weekly public score.

## Migration

- CN #26/W39: legacy 60%, retained only for history.
- CN #27/W40: first permanent five-slot baseline under the final design; score its exact user-approved final calls in CN #28.
- CN #28 onward: continue the identical five slot names/order with full v2.1 STATE + CHANGE + frozen resolution criteria.
