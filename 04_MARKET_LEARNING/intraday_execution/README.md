# Intraday Execution Research Layer

Research-only timing layer for an already-established market regime.

## Purpose
This layer does not decide whether altseason or rotation exists. It studies *when* execution may be unusually favorable or unfavorable inside an active regime, especially for:
- staged top-ups
- local overheat / trim watch
- pullback recognition
- reload watch
- continuation after a reset

## Inputs
The layer reuses existing GitHub evidence and does not require a new external paid data source:
- hourly BTC/ETH/ETHBTC archive
- quote/base volume for session VWAP
- taker-buy share
- open interest and 1h OI change
- funding events
- direct ETHBTC
- Top100 breadth snapshot and constituent prices
- Entry Signal Ledger state
- Adaptive Pullback Learning state

## Execution features
For BTC and ETH it calculates:
- UTC-session VWAP and close deviation from VWAP
- rolling relative hourly quote volume
- previous-day high/low context
- 2-hour opening range context
- distance from rolling 24h high/low
- 1h/4h momentum and short acceleration
- taker-buy share and change
- OI change
- latest available funding

For ETHBTC it calculates short momentum and 24h-position context.

Top100 evidence is currently limited to snapshot breadth, equal-weight/median 24h return and constituent-price outcomes. The canonical archive does **not** currently provide historical per-coin intraday VWAP/opening-range data, so the layer must never claim that it does.

## Adaptive design
The research states use empirical percentile ranks after a warmup period. They are not production thresholds and cannot trigger portfolio execution.

Possible research labels:
`LEARNING_WARMUP`, `REGIME_NOT_ACTIVE`, `NORMAL`, `MOMENTUM_EXPANSION_RESEARCH`, `OVERHEAT_WATCH_RESEARCH`, `LOCAL_TRIM_WATCH_RESEARCH`, `PULLBACK_ACTIVE_RESEARCH`, `RELOAD_WATCH_RESEARCH`, `CONTINUATION_RESEARCH`.

Transition events are stored prospectively and later matured against matched constituent outcomes. A signal is not considered successful merely because it existed. Performance must be compared against HOLD and the existing pullback-learning ledger.

## Authority
- research_only: true
- portfolio_execution: false
- canonical_market_state: false
- automatic_rule_changes: false
- historical findings ceiling: FORWARD_TEST
- any promotion requires separate review
