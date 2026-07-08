# P2b Decision Ledger Reconstruction & Backtest Readiness — Opus Fallback Report

Date: 2026-07-08  
Intended lane: Fable compute/research thread  
Actual provenance: OPUS 4.8 FALLBACK OUTPUT supplied by user  
Status: RESEARCH-USABLE / NOT FABLE-CANONICAL / GOVERNANCE INTAKE REQUIRED  
Authority: Research-only. No governance authority.

---

## 1. Executive verdict

`DECISION_BACKTEST_BLOCKED_LEDGER_MISSING`

The run verified against the supplied P2b bundle that all three ledger templates contained 0 data rows. A token scan for buy/sell/rebalance/deploy/target_exposure/allocation/stance/unlock over market data returned 0 decision-row hits. The only match was prose in a summary file, not an actionable decision row.

Framework-vs-benchmark returns therefore cannot be measured yet.

Important progress:

The Cycle Navigator independent actuals ledger was seeded from raw OHLC with 7 rows for CN #2-#7, turning the empty CN actuals template into a usable provisional scoring artifact.

---

## 2. Data validation table

| File | Purpose | Usable for decision backtest | Limitation | Confidence |
|---|---|---|---|---|
| framework_decision_ledger_template | decision schema | NO | 0 rows | HIGH |
| forecast_ledger_raw_export_template | forecast schema | NO | 0 rows | HIGH |
| cn_independent_actuals_template | CN actuals schema | NO when empty; now SEEDED | seeded 7 rows from OHLC | HIGH |
| btc_ohlc_master_p1b.csv | benchmark/outcome prices | outcome side only | no decisions to score | HIGH |
| btc_ohlc_investing_2010_2026.csv | multi-cycle benchmark | benchmark side | anchors not re-verified here | MEDIUM |
| eth_ohlc_investing_2015_2026.csv | ETH benchmark/outcome | benchmark side | ends 2026-06-14 | MEDIUM |
| ethbtc_daily_2023_2026.csv | rotation context | NO | ends 2026-06-14 | MEDIUM |
| daily_replay_rows_partial_compact.csv | mechanical gate-state rows | NO | state + outcome, no exposure column | PARTIAL |
| btc_etf_flow_daily.csv | flow context | NO | not a decision | HIGH |
| 03_FABLE_P2_OUTPUTS/* | prior P2 results | context | already known | HIGH |

---

## 3. Decision row classification

| Source | Row type | Timestamp quality | Action quality | Exposure quality | Usable status |
|---|---|---|---|---|---|
| decision-template | empty | none | none | none | NOT_USABLE, 0 rows |
| CN #2-#7 seed | FORECAST_ONLY | week-level | no action/stance | none | NOT_USABLE as decision |
| CN #8 | FORECAST_ONLY | week-level | none | none | NOT_USABLE |
| daily replay 32 rows | REGIME_ONLY | daily, clean cutoff | gate-state only | no exposure | NOT_USABLE as decision |
| Master Monday from P2 | PUBLIC_COMPOSITE_ONLY / MEMORY_RECONSTRUCTION | mixed | range + precision score | no exposure | NOT_USABLE |
| governance notes | GOVERNANCE state labels | n/a | rebuy LOCKED constant | no numeric exposure | NOT_USABLE as decision |

No row in the bundle met the decision-spec rule:

`Forecast-only rows are not decision rows unless they include explicit portfolio stance or action.`

---

## 4. Backtest feasibility

Benchmarks can be calculated now. P2 already calculated BTC B&H, ETH B&H, 70/30 BTC/stable, DCA and 50/50 benchmarks.

Framework-vs-benchmark cannot be calculated because there is no timestamped exposure series to hold against prices.

Without these per-decision fields, there is no framework NAV to compare against benchmark NAV:

- target_exposure_btc_pct
- target_exposure_eth_pct
- target_exposure_alt_pct
- target_exposure_stable_pct
- information_cutoff_utc

Conclusion:

`BENCHMARK_SIDE_READY / FRAMEWORK_SIDE_EMPTY / BACKTEST_BLOCKED`

---

## 5. Minimum decision ledger schema

The bundle specification was judged complete and sufficient for no-hindsight backtesting, if populated.

Backtest-critical fields:

- decision_id
- created_at_utc
- information_cutoff_utc
- asset_scope
- target_exposure_btc_pct
- target_exposure_eth_pct
- target_exposure_alt_pct
- target_exposure_stable_pct
- benchmark_set
- no_hindsight_status
- provenance_status

State/context fields:

- framework_state
- rebuy_status
- portfolio_stance
- btc_action
- eth_action
- alt_action
- confidence
- primary_trigger
- blocker
- invalidation_condition

Outcome fields to be computed later:

- outcome_7d_return
- outcome_30d_return
- outcome_drawdown
- benchmark_delta_7d
- benchmark_delta_30d
- outcome_status

Critical rule:

`Exposure columns must sum to 100 percent per row, or NAV reconstruction is impossible.`

---

## 6. Forecast ledger raw export schema

The forecast ledger specification was judged sufficient.

Non-negotiable fields for calibration:

- forecast_id
- information_cutoff_utc
- horizon: 1_3D / 5_7D / 2_3W / WEEKLY
- asset
- forecast_low
- forecast_high
- confidence
- actual_basis

Actual basis must be one of:

- RAW_OHLC
- INDEPENDENT_LEDGER

Self-reported actuals are diagnostic only.

Mandatory baseline columns:

- baseline_prior_week_jaccard
- baseline_atr_1_5_jaccard
- baseline_atr_2_0_jaccard
- baseline_fixed_5_jaccard

Suggested addition:

- confidence_reliability_bucket

Purpose: test whether high-confidence forecasts are calibrated to actual hit rates.

---

## 7. Independent CN actuals ledger — seeded

The CN independent actuals ledger was populated from raw OHLC for CN #2-#7.

The seeded ledger includes:

- actual_low
- actual_high
- actual_open_first_day
- actual_close_last_day
- self_reported_low
- self_reported_high
- self_reported_diff_low
- self_reported_diff_high
- canonical_status

Key confirmation from P2:

CN self-reported actuals differ from independent OHLC actuals.

Examples:

- CN #2 high difference: -3,936.9
- CN #3 low difference: -4,298.01
- CN #3 becomes a full miss under independent OHLC actuals

Status:

`INDEPENDENT_OHLC_RECONCILED_PROVISIONAL`

This can be used as provisional scoring truth source for CN #2-#7, with n<=7 caveat.

---

## 8. Backfill protocol

No hindsight reconstruction rules:

1. State-at-time only. Each reconstructed decision row must use data with `information_cutoff_utc <= decision_time`.
2. Future OHLC/returns are allowed only in outcome columns.
3. Source hierarchy:
   - DATA PING 22:00 rows as primary timestamped source
   - Master Monday raw as secondary source
   - CN publications only if explicit stance/action exists
   - chat-memory only as RECONSTRUCTED, never SOURCE_BACKED
4. Exposure may only be derived where a post explicitly gave stance/allocation.
5. Missing exposure = NOT_EVALUABLE, not guessed.
6. Each row must include provenance_status and no_hindsight_status.
7. Only PASS + SOURCE_BACKED rows enter the primary backtest.
8. Exposure must sum to 100 percent.
9. Timestamps must be monotonic.
10. Outcome fields must not be read before cutoff.

---

## 9. Automation / future operating model

Recommended future operating model:

- DATA PING exports one daily decision row with state, exposure snapshot and cutoff.
- DATA PING exports forecast rows for each active horizon.
- Master Monday exports weekly forecast rows and decision-state rows.
- Cycle Navigator publishes composite score and independent range quality separately.
- All rows are append-only.
- All rows include information_cutoff_utc.

Future CN publication scoring should separate:

- displayed composite score
- independent Jaccard vs raw OHLC
- baseline comparison
- regime/rotation call if independently labeled

---

## 10. Next data requests

Critical next data requests:

1. `framework_decision_ledger_actual.csv`
   - at least 20-30 historical rows
   - target_exposure_* fields populated
   - information_cutoff_utc populated
   - without this, backtest is impossible

2. `forecast_ledger_actual.csv`
   - RAW 1-3D, 5-7D, 2-3W, Master Monday and CN rows
   - RAW_OHLC actual basis

3. DATA PING 22:00 raw rows
   - historical source for decision and forecast backfill

4. ETH/ETHBTC after 2026-06-14
   - needed for full current-episode rotation analysis

5. Meta-score formulas and sequence ledger
   - still outstanding from prior requests

---

## 11. Safe governance updates

Allowed now as scoring/logging architecture only:

1. Adopt the three schemas as logging standards.
2. Replace CN self-reported actuals with the seeded independent OHLC ledger in future scoring.
3. Publish composite score and independent Jaccard side by side.
4. Make the baseline columns mandatory in forecast logs.

Not allowed:

- no market call
- no portfolio action
- no rule ratification
- no public track-record update
- no rebuy status change

---

## 12. Final governance line

No market call. No portfolio action. No rule ratification. No public track-record update.
