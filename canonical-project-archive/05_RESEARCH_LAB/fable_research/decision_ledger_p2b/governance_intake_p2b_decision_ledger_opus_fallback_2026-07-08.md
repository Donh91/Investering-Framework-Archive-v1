# Governance Intake — P2b Decision Ledger Opus Fallback 2026-07-08

Status: RESEARCH INTAKE / OPUS FALLBACK / GOVERNANCE-USABLE  
Source: User-supplied Opus 4.8 fallback output from intended Fable research thread  
Scope: Decision ledger reconstruction and backtest readiness.

---

## 1. Intake verdict

Accepted as usable research output, with provenance caveat.

Provenance status:

`OPUS_FALLBACK_RESEARCH_OUTPUT / FABLE_INTENDED_RUN / NOT_FABLE_CANONICAL`

Research verdict:

`DECISION_BACKTEST_BLOCKED_LEDGER_MISSING`

Governance interpretation:

The benchmark side is ready. The framework side is not measurable because no populated decision ledger exists.

---

## 2. Accepted findings

### Finding A — decision backtest is blocked

Accepted.

All three ledger templates were reported as header-only with 0 populated rows. No action/exposure/stance rows were found in market data.

Status:

`FRAMEWORK_DECISION_BACKTEST_BLOCKED_BY_EMPTY_DECISION_LEDGER`

### Finding B — forecast is not decision

Accepted as a hard governance rule.

Rule:

`Forecast-only, regime-only, CN-post, and Master Monday range rows cannot be promoted into portfolio exposure decisions unless explicit action/stance/exposure exists.`

### Finding C — benchmark side is ready

Accepted.

Market benchmark data exists for BTC, ETH, BTC/ETH, BTC/stables and DCA style comparisons, but framework NAV cannot be reconstructed without target exposure rows.

Status:

`BENCHMARK_SIDE_READY / FRAMEWORK_SIDE_EMPTY`

### Finding D — CN independent actuals ledger can be seeded now

Accepted.

The supplied seeded ledger creates 7 provisional independent OHLC actual rows for CN #2-#7. This is usable as provisional scoring truth source, replacing CN self-reported actuals for this subset.

Status:

`CN_INDEPENDENT_ACTUALS_LEDGER_SEEDED_PROVISIONAL`

---

## 3. Governance updates allowed now

Allowed as scoring/logging architecture only:

1. Adopt decision-ledger, forecast-ledger and CN-independent-actuals schemas as logging standards.
2. Require explicit action/stance/exposure before any row can be used in decision backtest.
3. Begin daily/weekly forward logging of decision rows even when decision is NO_ACTION.
4. Use seeded CN independent actuals ledger for provisional CN #2-#7 scoring.
5. Continue to separate composite score from independent range score.

---

## 4. Not allowed

Do not:

- infer historical exposure from forecasts
- infer portfolio stance from regime labels
- treat rebuy LOCKED as a numeric allocation unless explicitly logged
- update public track record
- claim framework edge
- run framework-vs-benchmark return without a decision ledger
- alter rebuy or portfolio rules

---

## 5. Required next actions

Highest priority:

1. Create/populate `framework_decision_ledger_actual.csv` forward from now.
2. Backfill only where explicit source-backed action/stance/exposure exists.
3. Populate `forecast_ledger_actual.csv` for RAW, Master Monday and CN ranges.
4. Use independent OHLC actuals for CN scoring.
5. Create an automation/process rule so DATA PING and Master Monday output a decision row every time.

Decision row minimum:

- decision_id
- created_at_utc
- information_cutoff_utc
- framework_state
- rebuy_status
- portfolio_stance
- target_exposure_btc_pct
- target_exposure_eth_pct
- target_exposure_alt_pct
- target_exposure_stable_pct
- source_layer
- provenance_status
- no_hindsight_status

---

## 6. Final governance line

No market call. No portfolio action. No rule ratification. No public track-record update.
