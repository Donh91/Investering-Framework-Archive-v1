# Intraday Execution Research Layer

Research-only timing and calibration layer for forward observation inside the existing framework.

## Purpose
This layer does not decide whether altseason, rotation or portfolio permission exists. It studies whether intraday evidence contains incremental timing information while the current Entry Signal Ledger remains in its explicit forward-only observation context.

Current collection eligibility is deliberately narrow and non-binding:

```text
Entry Signal Ledger contract: ENTRY_SIGNAL_LATEST_v1
entry state: WAIT
promotion status: FORWARD_ONLY_NOT_PROMOTION_READY
permits_active_state: false
breadth entry permission: RETIRED_ZERO_WEIGHT
hourly source: completed UTC 1H BTC/ETH/ETHBTC owner evidence
```

These conditions authorize research collection only. They do not authorize staged top-ups, trims, reloads, market-state changes, model promotion or portfolio execution. Missing or incompatible owner evidence fails closed to `REGIME_NOT_ACTIVE`.

The layer studies candidate timing context including:
- local expansion / overheat telemetry
- pullback recognition
- reload-watch telemetry
- continuation telemetry
- calibrated BTC/ETH direction forecasts in the separately registered T12 shadow test

## Inputs
The layer reuses existing GitHub evidence and does not require a new external paid data source:
- hourly BTC/ETH/ETHBTC archive
- quote/base volume for session VWAP
- taker-buy share
- open interest and 1h OI change
- funding events
- direct ETHBTC
- Top100 breadth snapshot and constituent prices
- Entry Signal Ledger state, promotion status and measurement-validity context
- Adaptive Pullback Learning state

## Research eligibility boundary
The Entry Signal Ledger is an observation-context owner here, not a permission source for portfolio action.

The intraday owner is collection-eligible only when all of the following remain true:
- completed hourly BTC/ETH/ETHBTC evidence is available;
- Entry Signal Ledger contract is current;
- Entry Ledger state is `WAIT`;
- promotion status is `FORWARD_ONLY_NOT_PROMOTION_READY`;
- `permits_active_state=false`;
- `breadth_entry_permission=RETIRED_ZERO_WEIGHT`;
- both Entry Ledger and this layer remain non-canonical and non-executing.

The retired `GRADUATED_ALTCOIN_TOPUP_ACTIVE` state is not an eligibility gate. Source-quality, proxy breadth, canonical-compatible breadth or Shadow Direction Confidence may not reactivate it indirectly. If canonical promotion governance changes later, this research eligibility contract fails closed until separately reviewed.

## Execution features
For BTC and ETH the owner calculates:
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

Top100 evidence is currently limited to snapshot breadth, equal-weight/median 24h return and constituent-price context. Breadth is descriptive research context with zero execution weight. The canonical archive does **not** currently provide historical per-coin Top100 intraday VWAP/opening-range data, so the layer must never claim that it does.

## Adaptive research states
The research labels use empirical percentile ranks after a warmup period. They are telemetry labels, not production thresholds and cannot trigger portfolio execution.

Possible research labels:
`LEARNING_WARMUP`, `REGIME_NOT_ACTIVE`, `NORMAL`, `MOMENTUM_EXPANSION_RESEARCH`, `OVERHEAT_WATCH_RESEARCH`, `LOCAL_TRIM_WATCH_RESEARCH`, `PULLBACK_ACTIVE_RESEARCH`, `RELOAD_WATCH_RESEARCH`, `CONTINUATION_RESEARCH`.

A label may be observed and archived without becoming a valid outcome-bearing forward-test row.

## Legacy execution-event lane
The pre-existing `events/` lane is currently:

```text
FROZEN_PENDING_SEPARATE_REGISTERED_TEST
new_event_creation: false
outcome_maturation: false
historical_rows_preserved: true
```

Historical event files remain immutable context. No new event creation or maturation is allowed until that distinct outcome question has its own governed Active Test Registry binding, benchmark, validator and scorer. This prevents ordinary research telemetry from silently becoming unregistered prospective evidence.

## T12 Shadow Direction Confidence
The BTC/ETH 1H/4H/24H direction-calibration lane is separately registered as:

`INTRADAY_DIRECTION_CONFIDENCE_V1`

It owns `UP`, `DOWN`, `NO_EDGE`, exact-horizon outcome maturation and empirical calibration. It remains shadow-only. Evidence agreement is not probability, numerical probability is suppressed during warmup, and 99% language is available only through the explicit high-assurance machine gate.

The first eligible canonical-main Actions run freezes `DIRECTION_REGISTRATION.json`. Its timestamp, registry/configuration hashes and production commit/run binding separate forward evidence from branch QA. The bound configuration and registry block must already exist in that main snapshot at registration time. Existing rows cannot be adopted into this registration. Prediction identity is the source candle, so a retry cannot create another forecast for the same source observation.

Prediction start prices are verified against the canonical main snapshot recorded at issuance, not a later rewritten hourly CSV. Provider revisions cannot silently change or invalidate a frozen forecast. Source commits must belong to main's first-parent history; a QA branch commit is not eligible even if it later becomes an ordinary merge ancestor. The PR validator also rejects creation, rewriting or deletion of canonical direction ledgers relative to its main merge parent, preventing QA rows from entering production through a code PR.

Each outcome links to the exact frozen prediction path and SHA-256, and to the exact due owner candle and its price binding. The validator checks actual UTC maturity, source prices, unchanged forecast fields, HIT/MISS arithmetic, Brier arithmetic and reproducible calibration from validated outcomes. A first production prediction is not a matured 1H outcome. Rounding cannot display 99% without `HIGH_ASSURANCE_99_ELIGIBLE`.

Retries display the frozen BTC and ETH forecast, including its original probability, maturity, independent sample count and descriptive agreement, rather than recomputing it from mutable breadth or later calibration. The RAW bridge carries these fields for both targets at each horizon and explicitly distinguishes agreement from probability. Missing or ineligible frozen horizons remain `NO_EDGE(UNAVAILABLE)`.

Censoring is allowed only for missing exact-due owner evidence after the configured grace period. Maturation and validation use the canonical main source snapshot available no later than `due_at_utc + max_outcome_evidence_lag_hours`, following first-parent Git history from the recorded production commit. Evidence published on time remains scoreable after an adjudication outage; a later backfill is censored even if the next research run can already see it. Each scored row binds the selected source commit and its publication timestamp. Unreadable or incomplete history fails validation; shallow CI may fetch canonical main history into its object cache without changing checkout or branch refs. There is no market API call, historical outcome rewrite or later-price substitution.

## Authority
- research_only: true
- portfolio_execution: false
- canonical_market_state: false
- automatic_rule_changes: false
- breadth execution weight: zero
- Shadow Direction Confidence regime/entry permission: none
- legacy event outcome creation: frozen
- historical findings ceiling: FORWARD_TEST
- any promotion requires separate review
