# Intraday Execution Sidecar - Cowork Research Addendum

This addendum is mandatory challenger context for the Historical Altseason Pullback Laboratory.

## Why it exists
The core lab studies regime-relative pullback, trough and continuation behavior. The existing `04_MARKET_LEARNING/intraday_execution/` owner collects non-binding timing telemetry and runs the separately registered T12 direction-calibration test. Current `WAIT` is a forward-only observation context, not market permission. A research label does not authorize staged top-ups, trims or reloads.

## Current authority and collection eligibility
Read the current Entry Signal Ledger and intraday config rather than infer permission from a research label:

```text
Entry Signal Ledger contract: ENTRY_SIGNAL_LATEST_v1
entry state: WAIT
promotion status: FORWARD_ONLY_NOT_PROMOTION_READY
permits_active_state: false
breadth entry permission: RETIRED_ZERO_WEIGHT
hourly source: completed UTC 1H BTC/ETH/ETHBTC owner evidence
```

These are collection eligibility conditions only. Missing or incompatible owner evidence fails closed. The retired `GRADUATED_ALTCOIN_TOPUP_ACTIVE` state cannot authorize collection, and proxy or canonical-compatible breadth cannot reactivate it. Breadth remains descriptive research context with zero execution weight. T12 cannot grant itself regime, entry or portfolio permission.

The historical execution-event lane remains `FROZEN_PENDING_SEPARATE_REGISTERED_TEST`:

```text
new_event_creation: false
outcome_maturation: false
historical_rows_preserved: true
```

Historical rows remain context. Neither new events nor new outcomes for trim/reload hypotheses may be created until that separate question has a governed test registration, benchmark, validator and scorer. HOLD and false-trim comparisons below are challenger questions, not permission to resume that frozen lane.

## T12 prospective evidence boundary
Scheduled collection follows verified Hourly Sequence publication as a dependent Intraday job inside the same main-writer lock. It reads the frozen source commit, not an assumed later cron slot. The separate Intraday workflow is a guarded manual repair path. A delayed or missing source remains ineligible; queue or cron timing is not prospective evidence.

`INTRADAY_DIRECTION_CONFIDENCE_V1` is the registered BTC/ETH 1H/4H/24H direction-calibration test. Its owner is the existing intraday config, its scorer is `scripts/intraday_execution/shadow_direction_confidence.py`, and its validator is `scripts/intraday_execution/validate_direction_confidence.py`.

- Only canonical-main production after registration is eligible. Branch QA, historical telemetry and initialization rows are not forward evidence.
- Forecast time is the observable candle close, not the candle-open label. A 1H outcome remains pending until its frozen due time has actually passed.
- Outcomes require the exact due closed owner candle. A later price cannot substitute for missing evidence.
- `NO_EDGE` is an abstention, never a directional hit.
- Evidence agreement is not probability. Numeric probability remains hidden until empirical calibration permits it; 99% wording additionally requires `HIGH_ASSURANCE_99_ELIGIBLE`.
- Microcap remains `NO_EDGE` / `DATA_GAP` until a legitimate owner exists.
- Row validity, coverage readiness and promotion status remain separate. No automatic promotion or reweighting is permitted.

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
- never promote an execution state or T12 direction directly to a portfolio action
- compare every trim/reload hypothesis with HOLD
- report false positives and missed upside
- prefer percentile/regime-relative representations over cherry-picked fixed thresholds
- test incremental value conditional on existing free features and CFGI
- strongest historical recommendation remains `FORWARD_TEST`

## Suggested extra Cowork deliverable
Add an `INTRADAY_EXECUTION_INCREMENTAL_VALUE.md` section/file that ranks each execution family as `REJECT`, `OBSERVE`, or `FORWARD_TEST`, including sample size, lead time, false-positive rate, incremental effect versus the base model, and whether it improves trim/reload performance after friction.
