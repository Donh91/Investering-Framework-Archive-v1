# Undefined Sensor Legs — External Source Design v0.1

**Date:** 2026-07-11  
**Status:** SOURCE_DESIGN / NEEDS_DATA  
**Purpose:** Operationalize or retire BTC.D, breadth and stablecoin deployment/velocity gates.

## 1. BTC Dominance

### Preferred reproducible route

Use CoinGecko Pro daily UTC series:

- global total crypto market cap: `/global/market_cap_chart`
- BTC market cap: `/coins/bitcoin/market_chart`
- derived total dominance: `btc_market_cap / global_market_cap`

Requirements:

- align both series to settled 00:00 UTC observations
- store source timestamps and missing dates
- no interpolation across missing source days without explicit flag
- log `BTC_D_TOTAL_DERIVED`

### Optional second convention

A separate `BTC_D_EX_STABLES` may be derived only if a stablecoin market-cap series with matching timestamps is available:

`BTC market cap / (global market cap - stablecoin market cap)`

Never mix the two conventions.

### Alternative

CoinMarketCap's professional API advertises historical global metrics and may provide direct historical dominance. Use only if endpoint access and definitions are verified.

## 2. Breadth

### Forward-operational definition

Create a daily frozen top-100 ex-BTC/ETH/stablecoin universe from CoinGecko `/coins/markets`.

Log:

- constituent IDs and ranks at freeze time
- percent above 30-day moving average
- percent with positive 7-day return
- percent with positive 30-day return
- median 7-day and 30-day return
- top-100 equal-weight index return
- data coverage percentage

Suggested labels remain shadow-only:

```text
BREADTH_WEAK
BREADTH_MIXED
BREADTH_BROAD
DATA_MISSING
```

Historical backfill using today's constituents is forbidden for promotion because of survivorship bias. Binding evidence should begin with daily frozen universe snapshots or a verified historical-listings source.

## 3. Stablecoin deployment

DeFiLlama's free API documents:

- total historical stablecoin market cap
- chain-level historical stablecoin market cap
- individual stablecoin history and chain distribution
- current stablecoin market cap by chain
- DEX volume histories

This supports a supply/deployment proxy, not true velocity.

Forward shadow fields:

- total stablecoin supply 3d/7d change
- chain stablecoin supply 3d/7d change
- share moving into selected risk chains
- DEX volume / stablecoin supply ratio
- change in that ratio over 3d/7d
- source coverage and revision status

Suggested name:

```text
STABLECOIN_DEPLOYMENT_PROXY
```

Do not call it velocity.

## 4. Stablecoin velocity

True velocity requires transfer-value, active-address or exchange-reserve data. DeFiLlama supply and DEX-volume endpoints cannot by themselves prove velocity or exchange deployment.

Governance status:

```text
DATA_MISSING
```

Until a documented source is available:

- remove velocity from any gate score
- retain as an explicit research field only
- do not let it block rotation confirmation

## 5. Recommended immediate action

1. Ask Custom GPT to deliver a daily BTC.D total series and, if possible, ex-stables series with exact source definitions.
2. Start forward breadth snapshots from a frozen daily top-100 universe.
3. Start DeFiLlama stablecoin-supply/deployment proxy rows.
4. Keep true stablecoin velocity unscored and non-blocking.
5. Run FULL M1 only after BTC.D passes source and anchor checks.

No market call. No portfolio action. No sensor promotion.
