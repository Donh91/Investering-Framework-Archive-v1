# Intraday Execution Sidecar - Cowork Research Addendum

This addendum is mandatory challenger context for the Historical Altseason Pullback Laboratory.

## Why it exists
The core lab studies regime-relative pullback, trough and continuation behavior. The new prospective `04_MARKET_LEARNING/intraday_execution/` layer studies a narrower question: once risk ownership is already permitted, can intraday execution evidence improve timing of staged top-ups, local trim watches and reloads without damaging HOLD performance?

## Prospective evidence to read
When present, read all files under:
- `04_MARKET_LEARNING/intraday_execution/`
- `scripts/intraday_execution/`
- existing `04_MARKET_LEARNING/pullback_learning/`
- Entry Signal Ledger
- hourly archive
- breadth_rich archive

## Candidate feature families
Challenge, rather than assume, incremental value from:
- session VWAP deviation
- rolling relative quote volume
- previous-day high/low behavior
- 2h opening-range behavior
- distance from 24h high/low
- 1h and 4h momentum acceleration/deceleration
- taker-buy share and change
- open-interest change
- funding
- ETHBTC short-term momentum
- Top100 breadth and equal-weight context

## Critical scientific questions
1. Do these execution features add information after breadth, ETHBTC and CFGI are already known?
2. Can they distinguish squeeze/expansion continuation from genuine local overheat?
3. Which features lead a pullback, and which merely react after price already moved?
4. Do reload signatures identify stabilization without catching falling knives?
5. Does a research-only `LOCAL_TRIM_WATCH` improve a realistic 10% trim/reload strategy versus HOLD after friction?
6. What is the false-trim cost when price never revisits the trim price?
7. Are results stable across episodes and eras, or driven by a few spectacular cases?

## Important data boundary
The current prospective archive supports BTC/ETH execution features from hourly OHLCV/quote volume/taker/OI/funding evidence. Top100 currently contributes snapshot breadth, cross-sectional returns and constituent outcome prices. Do NOT claim historical per-coin Top100 intraday VWAP, opening range, PDH/PDL or OI where those fields are not present.

## Required treatment
- keep this sidecar research-only
- never promote an execution state directly to a portfolio action
- compare every trim/reload hypothesis with HOLD
- report false positives and missed upside
- prefer percentile/regime-relative representations over cherry-picked fixed thresholds
- test incremental value conditional on existing free features and CFGI
- strongest historical recommendation remains `FORWARD_TEST`

## Suggested extra Cowork deliverable
Add an `INTRADAY_EXECUTION_INCREMENTAL_VALUE.md` section/file that ranks each execution family as `REJECT`, `OBSERVE`, or `FORWARD_TEST`, including sample size, lead time, false-positive rate, incremental effect versus the base model, and whether it improves trim/reload performance after friction.
