# Research sidenote - prospective intraday execution layer

This note extends the existing Cowork historical-altseason research package with one bounded 2026-only question.

## Why this matters
The historical lab is primarily built to study pullback precursors, local overheat, reload and continuation. The new `04_MARKET_LEARNING/intraday_execution/` layer studies a narrower problem: execution timing inside a regime that has already been established elsewhere.

It does **not** decide whether altseason, rotation or top-up permission exists. It must never replace Entry Signal Ledger, Cycle Navigator, Master Monday or the canonical regime stack.

## Prospective research question for Cowork
When the 2026 prospective archive becomes sufficiently populated, test whether the intraday execution features add incremental information beyond the existing pullback-learning and breadth layers for:

- avoiding locally poor top-up timing during short-lived overheat,
- identifying unusually favorable staged top-up/reload windows,
- separating a healthy momentum expansion from a local exhaustion event,
- improving trim/reload timing versus HOLD without increasing false-trim cost.

## Feature families to inspect
Use only actually available timestamped evidence, including:

- BTC and ETH UTC-session VWAP deviation,
- rolling relative quote volume,
- previous-day high/low context,
- 2-hour opening range context,
- distance from 24h high/low,
- 1h and 4h momentum plus short acceleration,
- taker-buy share and short change,
- 1h open-interest change,
- latest observed funding,
- direct ETHBTC momentum and 24h position,
- Top100 breadth snapshot and cross-sectional return context,
- existing pullback-learning state and Entry Signal Ledger state.

## Important limitation
The current canonical archive does **not** contain historical per-coin Top100 intraday VWAP or opening-range series. Do not infer or fabricate them. BTC/ETH intraday execution features and Top100 breadth/constituent outcomes must remain clearly separated.

## Required evaluation
Treat every emitted research state as a prospective hypothesis, not a signal victory. Compare state transitions against matched forward outcomes and against:

1. HOLD,
2. the existing adaptive pullback-learning ledger,
3. simple naive timing baselines,
4. continuation controls where price keeps expanding instead of pulling back.

Report false trims, missed pullbacks, false reloads, late reloads, opportunity cost, lead time and any incremental value after existing breadth/pullback evidence is known.

## Anti-overfit boundary
Do not tune exact fixed thresholds from a small 2026 sample. Prefer percentile/rank and sequence representations. Any relationship discovered here is limited to `OBSERVE` or `FORWARD_TEST` until it survives sufficient prospective evidence and separate governance review.

## Authority
- research only
- no portfolio execution
- no canonical market-state authority
- no automatic rule, threshold or weight changes
- no retrospective rewriting of 2026 decisions
- historical/prospective findings ceiling: `FORWARD_TEST`

This sidenote is intentionally subordinate to the main Cowork research brief. It adds a focused prospective execution-timing question, it does not change the mission of the historical altseason pullback laboratory.
