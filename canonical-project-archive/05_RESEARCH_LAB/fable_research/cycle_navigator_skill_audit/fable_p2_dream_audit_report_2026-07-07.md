# FABLE P2 DREAM AUDIT — Report

Date: 2026-07-07  
Auditor: Claude Fable 5  
Status: RESEARCH-LAB OUTPUT / GOVERNANCE INTAKE REQUIRED  
Authority: No market call. No portfolio action. No rule ratification. No public track-record update.

---

## 1. Executive summary

Fable ran the integrated P2 Dream Audit across three blocks:

1. E7 Dumb Benchmark Arsenal
2. Cycle Navigator precision decomposition using independent OHLC recomputation of actuals
3. E2 ETH/BTC gate audit

Core finding:

`CLEAR_EDGE_NOT_PROVEN`

The displayed Cycle Navigator scores averaged approximately 88, but independent range quality was much weaker, with median independent Jaccard around 0.39. Fable found that self-reported CN actuals appeared to differ systematically from raw OHLC in a way that made forecasts look better than independent OHLC-recomputed actuals. Naive ATR/fixed-percent range bands matched or beat CN range skill in this small sample.

Framework-level edge could not be tested because no decision ledger exists. Therefore the benchmark verdict is `PROXY_LIMITED`.

The E2 ETH/BTC gate audit found a clearer signal at 0.0300 than 0.0275. ETH/BTC 0.0275 at one close should remain early pressure, not confirmation.

---

## 2. Executive verdict

`CLEAR_EDGE_NOT_PROVEN`

Reasons:

- Range skill does not beat naive baselines in the tested subset.
- Displayed public CN scores appear inflated relative to independent range quality.
- Regime/rotation skill is not independently confirmed because phase/rotation labels are self-reported/categorical.
- Framework-vs-benchmark performance cannot be measured without a decision ledger.

Fable challenges the interim hypothesis `REGIME_ROTATION_SKILL_STRONGER`; it may be true, but it is not yet proven because current regime/rotation performance is self-graded.

---

## 3. Data validation

Files/data used:

- BTC OHLC 2023 to 2026-07-02
- ETH OHLC 2016 to 2026-06-14
- ETHBTC 2023 to 2026-06-14
- CN #2-#7 source-backed rows
- CN #8 forecast-only row was not scored

Important limitations:

- ETH/ETHBTC end 2026-06-14, so latest active episode is only partly covered.
- CN #2-#7 weeks occur before user-verified W22-W27 actuals, so Fable recomputed actuals independently from daily OHLC.
- CN #11 contamination was not used.
- Master Monday was kept separate from public Cycle Navigator.

---

## 4. E7 benchmark results

| Strategy | Total return | CAGR | Max DD | Sharpe | Sortino | Calmar |
|---|---:|---:|---:|---:|---:|---:|
| BTC_BH aligned | +295.6% | 49.0% | -51.2% | 1.09 | 1.67 | 0.96 |
| ETH_BH aligned | +43.2% | 11.0% | -67.5% | 0.48 | 0.73 | 0.16 |
| BTC_ETH_50_50 | +152.7% | 30.8% | -59.2% | 0.78 | 1.16 | 0.52 |
| BTC_STABLE_70_30 | +183.7% | 35.3% | -38.5% | 1.09 | 1.67 | 0.92 |
| DCA_BTC weekly | +30.1% terminal multiple | n/a | -56.8% | n/a | n/a | n/a |

Adversarial interpretation:

BTC buy-and-hold is a hard benchmark to beat in this period. A mechanical 70/30 BTC/stables strategy produces lower drawdown with similar Sharpe, without framework intelligence. The framework's defensive value must be measured against this type of benchmark, not only against 100% BTC exposure.

Because no decision ledger exists, true framework performance is `PROXY_LIMITED`.

---

## 5. CN independent range metrics

| CN | Asset | Displayed | Forecast | Independent OHLC actual | Jaccard | Containment | Breach |
|---|---|---:|---:|---:|---:|---|---|
| #2 | BTC | 88 | 65.0-72.0K | 67.7-74.9K | 0.432 | PARTIAL | HIGH |
| #3 | BTC | 83 | 66.0-73.0K | 73.3-78.4K | 0.000 | NONE | HIGH |
| #4 | BTC | 86 | 73.0-79.0K | 73.7-79.5K | 0.806 | PARTIAL | HIGH |
| #5 | BTC | 85 | 76.5-83.5K | 74.9-79.5K | 0.349 | PARTIAL | LOW |
| #6 | BTC | 92 | 79.0-83.5K | 78.2-82.8K | 0.720 | PARTIAL | LOW |
| #7 | BTC | 91 | 79.5-84.0K | 76.7-82.4K | 0.393 | PARTIAL | LOW |
| #7 | ETH | 91 | 2.28-2.48K | 2.098-2.374K | 0.245 | PARTIAL | LOW |

Key findings:

- Displayed score mean: about 88.
- Independent Jaccard median: about 0.39.
- 0 / 7 scored asset-rows fully contained independent actual range.
- CN #3 was a full miss under independent OHLC actuals.
- Breach sequence shifts from early HIGH breaches to later LOW breaches.

---

## 6. Self-reported actuals vs independent OHLC

Fable found material differences between CN self-reported actuals and independent OHLC actuals.

Examples:

| CN | Self-reported low difference | Self-reported high difference |
|---|---:|---:|
| #2 | -1,710 | -3,937 |
| #3 | -4,298 | -2,390 |
| #7 BTC | +927 | -79 |

Interpretation:

Self-reported actuals appear to pull toward the forecast range, especially by underreporting actual highs in the early upside-extension rows. Under CN's own actuals, average Jaccard was about 0.54; under independent OHLC, about 0.42.

---

## 7. CN vs naive baselines

Median Jaccard comparison:

| Model | Median Jaccard |
|---|---:|
| CN | 0.412 |
| Prior-week repeat | 0.404 |
| ATR-1.5 | 0.468 |
| ATR-2.0 | 0.507 |
| Fixed-5% | 0.502 |
| Fixed-7.5% | 0.460 |
| Fixed-10% | 0.345 |

Fable conclusion:

`RANGE_SKILL_WEAK + SCORE_INFLATION_RISK`

CN's range skill does not beat simple ATR/fixed-percent bands in this small source-backed sample.

---

## 8. Phase / rotation audit

Fable reported:

- Phase exact: 86%
- Rotation exact: 71%
- Independent range Jaccard >= 0.5: only 29%

However, Fable warns that this is not proof of regime/rotation edge because phase/rotation matches are:

- self-reported from CN evaluation sections,
- categorical,
- structurally easier to score high than continuous Jaccard,
- not independently labeled.

Therefore the interim hypothesis `regime/rotation skill > range skill` is not rejected, but it is not confirmed.

---

## 9. E2 ETH/BTC gate audit

| Threshold | Persistence | Signals | Fakeout | Median fwd10 | ETH outperform 10d |
|---|---:|---:|---:|---:|---:|
| 0.0275 | 1 close | 5 | 0.60 | -0.3% | 40% |
| 0.0275 | 3 closes | 3 | 0.33 | +5.8% | 67% |
| 0.0300 | 1 close | 6 | 0.50 | +1.3% | 83% |
| 0.0300 | 3 closes | 3 | 0.33 | +3.7% | 67% |
| 0.0325 | 1 close | 3 | 0.67 | +5.7% | 100% |

Fable conclusion:

- 0.0275 at one close = early pressure, not confirmation.
- 0.0300 at one close is cleaner than 0.0275.
- 0.0300 + persistence or 0.0275 + 3-close persistence reduces fakeout.
- Sample size remains small.

---

## 10. Failure modes

Framework failure modes:

1. Displayed score inflation: displayed 88 vs independent Jaccard around 0.39.
2. Self-reported actuals appear biased toward forecast range.
3. Range skill is weaker than naive baselines.
4. Regime/rotation skill remains unconfirmed due to self-grading.

Audit limitations:

1. CN sample size n<=7.
2. ETH/ETHBTC data ends 2026-06-14.
3. No decision ledger, so framework-vs-benchmark return cannot be tested.
4. CN #2-#7 evaluation actuals are partly self-reported, mitigated by OHLC recomputation.

---

## 11. Kill criteria status

| Criterion | Status | Interpretation |
|---|---|---|
| A — Framework Edge | PROXY_LIMITED | Cannot resolve without decision ledger. |
| B — CN Range | TRIGGERED | Range skill weak vs baselines; score-compression risk. |
| C — Rotation | TRIGGERED/PARTIAL | 0.0275@1close only early pressure; 0.0300 cleaner. |

---

## 12. Data requests

Critical missing data:

1. Forecast Ledger raw export.
2. Framework decision ledger.
3. Independent CN actual ledger.
4. Independent phase/rotation labels.
5. Canonical DATA PING rows.
6. Meta-score formulas.
7. Sequence ledger.
8. ETH/ETHBTC after 2026-06-14.

---

## 13. Recommendations from Fable

### Safe updates now

1. Replace CN self-reported actuals with raw-OHLC actuals in future scoring.
2. Report displayed score and independent Jaccard side by side.
3. Benchmark CN ranges against ATR-2.0 and fixed-5% bands.

### Shadow-only hypotheses

1. Raise rotation confirmation toward 0.0300, or require 3-close persistence at 0.0275.
2. Track the possibility that CN score is composite and overstates price-range skill.
3. Treat regime/rotation skill as promising but unproven until independent labels exist.

### Do not update

1. No regime/rotation edge claim yet.
2. No range-skill validation.
3. No public track-record update.
4. Rebuy remains LOCKED.
5. No portfolio or market action.

---

## 14. Final governance line

No market call. No portfolio action. No rule ratification. No public track-record update.
