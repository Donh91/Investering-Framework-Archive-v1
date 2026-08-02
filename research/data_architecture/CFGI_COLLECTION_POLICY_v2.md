# CFGI Collection Policy v2

Status: SHADOW-ONLY DATA POLICY

## Objective

Use the 100,000-credit CFGI balance to maximize prospective learning over approximately 1-2 years, not to minimize spend indefinitely.

## Normal profile

Five owner captures per day for `MARKET,BTC,ETH`.

Fields per row:

`score,volatility,volume,impulse,technical,social,dominance,trends,whales,orders`

The separate `price` field is excluded because Binance is the framework price owner.

Timeframe rotation:

- 06:13 Europe/Copenhagen: `1d`
- 10:47: `4h`
- 15:22: `1h`
- 19:38: `15m`
- 23:11: `4h`

Expected normal cost:

- 3 symbols x 10 fields x 1 row = 30 credits per capture
- 5 captures per day = 150 credits per day
- 54,750 credits per 365 days
- theoretical life from 100,000 credits = 666.7 days, about 1.83 years

## Why this profile

The profile purchases all non-price CFGI dimensions and distributes observations across four timeframes. It supports research into sentiment divergence, component sequencing, pullback precursors, failed recoveries, rotation quality and confidence calibration.

## Reuse rule

Weekly, RAW, Cycle Navigator and Master Monday packages must derive CFGI ranges, changes and component summaries from persisted daily owner rows. They must not issue duplicate weekly API calls for data already captured.

## Adaptive governance

No component receives canonical weight from collection alone. Each component must be evaluated prospectively against matured outcomes.

At quarterly reviews, components may be:

- retained at current frequency,
- promoted to event-driven extra capture,
- reduced in frequency,
- or removed if they add no measurable information beyond existing owners.

Any change requires a versioned hypothesis, forward test and rollback condition.

## Credit reserve and refill

- Review remaining credits at 25,000.
- At 10,000 remaining, freeze optional experiments and preserve the five scheduled owner captures until refill decision.
- At 5,000 remaining, fail closed to score-only mode unless a refill has already been approved.
- No automatic purchase or billing action.

## Authority

CFGI is a shadow sentiment owner. It cannot create market truth, change framework state, alter model weights, replace canonical DATA PING or authorize portfolio action.
