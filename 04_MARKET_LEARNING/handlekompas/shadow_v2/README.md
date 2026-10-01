# Shadow Compass v2

Status: FORWARD-ONLY SHADOW EXPERIMENT

Purpose: test whether richer existing market evidence plus GPT-6.1 Sol reasoning improves prospective 12h / 72h / 168h forecasts versus Official Daily Compass and simple baselines.

This lane is not an Official Compass replacement.

## Inputs

The reasoner consumes a compact, hash-bound subset of existing owners:

- completed hourly BTC / ETH / ETHBTC price and flow evidence;
- spot volume, quote volume, trade count and taker-buy share;
- Binance spot microstructure;
- OKX OI / OI-change / long-short / funding context;
- freshest same-family breadth point plus rich breadth statistics;
- BTC dominance;
- settled BTC / ETH ETF flows;
- stablecoin supply liquidity;
- FRED macro context;
- CFGI sentiment;
- altseason context;
- Entry Signal reference;
- Cycle Navigator as structural prior only.

It does **not** consume Official Compass as an answer key.

## Outputs

Each immutable forecast contains separate 12h, 72h and 168h rows with:

- direction;
- expected path;
- supporting evidence;
- contradicting evidence;
- missing evidence;
- pullback risk;
- transmission state;
- confidence;
- falsification conditions.

## Authority

Shadow only.

No portfolio execution.
No BUY/SELL authority.
No Official Compass override.
No source override.
No threshold or model-weight changes.
No automatic promotion.

Promotion requires prospective outcome evidence under a separate preregistered comparison contract.
