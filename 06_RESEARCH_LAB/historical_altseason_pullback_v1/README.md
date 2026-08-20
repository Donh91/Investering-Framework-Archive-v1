# Historical Altseason Pullback Laboratory v1

Purpose: bootstrap a realistic, research-only historical laboratory for learning the sequence around altseason expansion, local tops, pullbacks, troughs, reloads and continuation.

## Scientific question

Can a combination of cross-sectional altcoin breadth, BTC/ETH/ETHBTC leadership, spot/taker-flow structure, sentiment and liquidity identify useful pullback-risk and reload windows early enough that a hypothetical 10% trim + reload improves token quantity versus HOLD after friction?

This is not a rule generator and never executes trades. Historical findings may inform prospective research, but promotion into framework rules requires separate review and out-of-sample evidence.

## Phase A - free reconstruction first

The free bootstrap reconstructs two windows:

1. `2020-09-01 -> 2021-12-31`, the broad 2020-21 crypto expansion / altseason study window.
2. `2025-01-01 -> 2026-07-31`, a modern analogue window that overlaps CFGI history at useful intraday density.

Primary free sources:

- Binance spot 1H klines for BTCUSDT, ETHUSDT, direct ETHBTC and a fixed research alt universe.
- Binance quote volume, trade count and taker-buy quote volume from the same 1H rows.
- Alternative.me daily Fear & Greed as a free sentiment control only.
- DefiLlama stablecoin global history where available.

The alt universe is deliberately labelled `SURVIVORSHIP_LIMITED_RESEARCH_UNIVERSE`. It includes several assets that later failed or were delisted when archived Binance data can be retrieved, but it is not claimed to be a perfect historical Top100 membership reconstruction.

## Phase B - objective episode catalogue

Episodes are labelled from market outcomes before CFGI is examined. The synthetic equal-weight index uses only assets with valid observations at both endpoints of each step. The lab records continuous drawdown and creates objective episode rows when the equal-weight index falls at least 5% from a local running peak. Larger 8%, 12% and 20% severity flags are retained rather than optimized away.

For every episode the feature matrix preserves observations at T-72h, T-48h, T-24h, T-12h, T-6h, T-3h, local top, trough, +3h, +6h, +12h and recovery where available.

Tracked free features include:

- BTC, ETH and direct ETHBTC returns and acceleration
- equal-weight and median alt returns
- 1H / 6H / 24H breadth
- return dispersion
- cross-sectional quote volume acceleration
- median taker-buy share
- trade-count acceleration
- ETH leadership vs BTC and alt-universe leadership vs BTC
- free daily sentiment control
- stablecoin-liquidity context where source coverage allows

## Phase C - CFGI enrichment

CFGI is especially valuable because the API exposes far more than the headline fear/greed score. The enrichment requests all 11 requested fields:

`score,price,volatility,volume,impulse,technical,social,dominance,trends,whales,orders`

for `MARKET,BTC,ETH`.

Important coverage fact: CFGI's public documentation says crypto history begins in March 2022, so CFGI cannot be fabricated for the 2021 altseason. The 2021 lab is therefore price/breadth/flow/liquidity only. CFGI is used on later analogue episodes, especially 2025-26, and those relationships are then tested prospectively against 2026 observations.

The paid enrichment is deliberately targeted. It first reads the free episode catalogue, chooses representative pullback episodes plus matched continuation controls, merges overlapping windows, and requests static 1H CFGI only around those windows. The hard expected-cost cap is 25,000 credits and the script also preserves a configurable credit reserve before making another request.

## Controls against overfitting

- outcome labels are generated before CFGI is queried
- no hindsight-perfect top/trough prices are used as executable fills
- a separate perfect-hindsight ceiling is reported only as an upper bound
- realistic model fills are next-observation, not same-observation
- fixed round-trip friction is included for trim/reload comparisons
- continuation windows are negative controls
- 2021 and 2025-26 are not silently pooled as if data coverage were identical
- no missing historical source is forward-filled as a new observation
- all source/coverage limitations stay explicit

## Outputs

`artifacts/FREE_SOURCE_AUDIT.json`
`artifacts/hourly_features.csv.gz`
`artifacts/EPISODE_CATALOG.json`
`artifacts/EPISODE_FEATURE_MATRIX.jsonl.gz`
`artifacts/CFGI_COVERAGE.json`
`artifacts/cfgi_targeted.jsonl.gz`
`artifacts/CFGI_BILLING.json`
`artifacts/BACKTEST_SUMMARY.json`

## Authority

Research-only. No portfolio execution, no canonical market-state changes, no automatic threshold or weight changes, and no retrospective rewriting of live 2026 signal history.
