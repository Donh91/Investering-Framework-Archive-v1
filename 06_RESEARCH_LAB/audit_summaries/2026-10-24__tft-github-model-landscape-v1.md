# Task 2 | Open-source forecasting model screen and TFT falsification v1

**As-of:** 2026-10-24. **Scope:** source screen + executable SYNTHETIC negative controls only.
**Authority:** RESEARCH_ONLY / NON_CANONICAL / NO_TRADE / NO_FORECAST_ISSUANCE / NO_MODEL_PROMOTION.
**Owner:** existing scientific Task 2 #1596; Compass BTC range integration #1516; supervisor #1156.
**Approval:** user authorized end-to-end bounded research on 24 October and explicitly expanded GitHub source discovery. This research note is not approval to override platform or model-promotion gates.
**Main starting SHA:** 18c5277d6c35fce249d5146d8af9ef3b3cd3ce63.
**Original example frozen SHA:** zadescoxp/Temporal-Fusion-Transformer-Price-Prediction@f1d35896a02ba054c5abf5ac08fc8f627d504f2c.

## A. Deduplication and domain ownership

Read canonical AGENTS.md, cross-repository data boundary, 06_RESEARCH_LAB/README.md, Task 2 #1596, range owner #1516, existing HF research package 13_HF_SOURCE_PILOTS_AND_MODEL_CHALLENGERS.md, 14_SCIENTIFIC_TEST_MATRIX_AND_KILL_GATES.md, existing research PR #1781 and model tournament 25_FINAL_MACHINE_READABLE_VERDICT.json. The existing HF note already lists Chronos-Bolt-small and cheap baselines. It is not necessary to build a second model-runner, queue, alert, source pipeline, scorer, scheduler, site authority or training infrastructure.

This note adds **GitHub implementation/library triage plus source-code negative controls**, not another literature review: #1781 remains the scholarly calibration and backtest-bias source note; #1596 retains the R0-R7 science gates; #1516 retains range/issuer authority; #1156 retains PR release governance. No new GitHub issue is required.

Existing Task 2 R1 remains NOT_ADMITTED for full historical knowability despite selected recovered GitHub publication/byte evidence. Shared-row scores have no admitted matured denominator yet. The BTC range owner still holds source-governance integration pending independently verifiable recovery/separation. Nothing here amends those states.

## B. 12 verified GitHub repositories (pin at screen time, not installation manifest)

Repository metadata, default branch HEAD and license were checked with the GitHub API on 24 October 2026. The code license is NOT proof that model weights, datasets, remote endpoints or examples carry identical rights.

| Library / repo | Screen HEAD SHA | Repo license | Role / admission | Initial verdict |
|---|---|---|---|---|
| Nixtla/statsforecast | 8e0f32724f1649163e5a562f18fe351ce08e2ebd | Apache-2.0 | Seasonal naive/ETS/ARIMA/statistical point or interval baseline | P1 shortlist |
| Nixtla/mlforecast | b07ddbb60c40b3937e1d5e011a8fed7cd3357b6e | Apache-2.0 | Low-overhead feature-aware ML challenger; train-only transforms | P1 shortlist |
| scikit-learn-contrib/MAPIE | f1cc3d07460b2d7198f557d40d60cd563c51822b | BSD-3-Clause | Conformal calibration methods; test serial-dependence limits | P1 method screen |
| Nixtla/neuralforecast | 6c11accfbcfdd62a40ef69a7c81e3d9c7f272682 | Apache-2.0 | One vetted environment to compare NHITS and possibly TFT/PatchTST | P2 candidate |
| amazon-science/chronos-forecasting | 1224fafa91e1ecd6674f5204066b159e40b5e4a1 | Apache-2.0 | Tiny/small Chronos-Bolt zero-shot challenger if compute allows | P2 conditional |
| unit8co/darts | 555c8d1c4753e63c679507073f4f1fbe7d245a4b | Apache-2.0 | Common evaluation interface; avoid duplicating existing scorer | Reference only |
| google-research/timesfm | e51928e27119cb17bebc005be2696b75e0a9e688 | Apache-2.0 | Independent foundation-model sensitivity if P1/P2 reveal headroom | Defer |
| SalesforceAIResearch/uni2ts | cfd46d4510ed8896f263116f32928eede05b0a75 | Apache-2.0 | Moirai multimodal/multivariate research, heavier dependency path | Defer |
| THUML/Time-Series-Library | 4e938a1767106324dd753b2a44832bf870a0252e | MIT | Additional transformer families, replication overhead | Defer |
| autogluon/autogluon | 9ad8e9a9d8028f87d6b1e8572191389351f9a351 | Apache-2.0 | Existing-environment evaluation/orchestration option | Reference only |
| sktime/pytorch-forecasting | a35e765be5250ec6a0a01b6273b99603894524ce | MIT | Core TFT upstream library / security and version reference | Reference only |
| zadescoxp/Temporal-Fusion-Transformer-Price-Prediction | f1d35896a02ba054c5abf5ac08fc8f627d504f2c | Apache-2.0 | Fresh equity-oriented demonstration; no verified crypto skill | Falsify only |

The 12 project count represents source discovery, not 12 eligible experimental arms. Repository popularity or licence is not predictive evidence. Source code and weights must be pinned and independently inspected before execution. No dependency was installed, no model was downloaded or trained, and no third-party endpoint was sent restricted data.

## C. Verified defects and scientific issues in original TFT example

- Source model/test_methodology.py imports engineer_features, extend_with_future_calendar and nyse_holidays from model/features.py, which does not currently export them. This points to a failing unittest import, not a validated all-tests-PASS pipeline. Actual upstream full-suite execution remains UNTESTED locally.
- Source model/evaluate.py _max_drawdown computes peaks from a compounded curve without prepending initial capital = 1. A first -20% return followed by +25% has reported 0% drawdown in this pattern, versus correct -20%. Deterministic standalone reproduction is in the accompanying test.
- Source model/intervals.py builds horizon 10-90% bounds from per-day q10/q50/q90 marginal log returns by square-root-sum-of-squares, implicitly omitting time covariance and distribution dependence. It is an approximation, not a calibrated horizon quantile. A Gaussian equicorrelation counterexample with daily q10/q90 exactly specified gives 7-step nominal 80% actual coverage: 80% if rho=0; 47.8% if rho=0.5; 37.2% if rho=1. At 21 steps and rho=1 it is 22.0%. These are SYNTHETIC analytic illustrations, NOT market performance claims.
- Daily stock exchange calendar, yfinance price bars and earnings/dividends require redefinition or removal for 24/7 crypto. Its one-ticker 2010-2023 train and 2024+ holdout is not a crypto PIT proof.
- Source inference artifact loader uses torch.load(..., weights_only=False) for a dataset object. Never load untrusted remote pickles/checkpoints; isolated reviewed code only, no arbitrary external artifact execution.
- Essential target distinction for #1516: final CLOSE price quantiles, future window extreme LOW/HIGH and daily expected-close PATH are distinct random variables. A model of CLOSE cannot be presented as an honest within-window LOW/HIGH envelope.
- Fixed round-trip commission/slippage (30 bp) and long-only strategies cannot be transferred to microcaps, illiquid pairs or any user portfolio. No economic alpha conclusion follows from source backtests.

## D. Actually executed cheap negative-control harness

File: 06_RESEARCH_LAB/audit_summaries/test_tft_assumptions_v1.py.
Command run in isolated local stdlib interpreter prior to submission:
  python -m unittest -v /mnt/data/tft_audit/test_tft_assumptions_v1.py
Result: **5 tests run; 5 PASS**. No market data, private repo reads, training, GPU, source provider calls or CI usage.
Tests: independent Gaussian nominal 80% coverage; positive correlation violates nominal interval; starting-capital drawdown; distinct CLOSE vs future LOW/HIGH targets; impossible equicorrelation rejected.
Verification limit: the standalone helper independently mirrors source mathematical assumptions; this is not an execution of upstream test suite, not a TFT checkpoint run and not an economic backtest.

## E. Minimal, non-duplicative trial protocol after actual gate admission

One pinned dataset/cohort and one target family per trial, with source issue-time/known-time and separate event/target timestamps. If private source authority is required and unavailable, halt with PRIVATE_DATA_AUTHORITY_UNAVAILABLE. No Round 3 analysis while its signed analysis gate is OFF.

**Pilot 1: fastest baselines**: naïve last-observation/random walk, trailing historical realized volatility/EWMA or ATR bands, followed by a small StatsForecast member only if source quality and matched targets allow. Quantile scoring must have proper empirical reference coverage and penalty for useless width.

**Pilot 2: calibration**: train-calibrate-test split in time, use MAPIE/conformal only with a declared serial-dependence policy and rolling/blocked sensitivity. Never claim distribution-free IID guarantees in crypto time series.

**Pilot 3: ONE advanced challenger**: choose either NeuralForecast NHITS/TFT or tiny Chronos-Bolt as-of a frozen decision, by matching metric, runtime, source rights and vintage. Do not test both on repeatedly inspected holdout until a fresh untouched evaluation can support selection.

**Pilot 4: extra models** only after significant, robust, preregistered headroom is demonstrated. Darts/AutoGluon are potential wrappers; TimesFM/Moirai/THUML are parked to avoid a large GPU shootout.

At the experiment registration gate freeze: full attempted denominator, baseline assets/quote/venue, task target and horizon, outcome source and original availability clocks, train and embargo schedule, validation vs final holdout, optimizer budget/seeds, model-weights vintage, sample-size/effective-independent-event threshold, block/bootstrap treatment of dependence, proper score (e.g. WIS, pinball), coverage, width, PIT eligibility, all negative controls and stop criteria. No target-metric choices after observing test outcomes. Compare on identical rows; include no-trade, no-issue, censored, UNKNOWN and abstentions separately. Brier/log scores only for actual probabilities. Explicit no-skill/no-edge and complexity-cost paths.

**Priorities:** information accuracy first, then prospective range calibration, then shadow operational reliability, then conditional economic decision utility. Do not route any TFT result into Official BUY/SELL or a user-facing future blue path. Delivery latency, fees, realistic fills and missed rebound must be considered for any later action hypothesis.

## F. Gate decisions and next executable owner steps

0. **Current disposition:** PUBLIC_SOURCE_SCREEN_VERIFIED + SYNTHETIC_NEGATIVE_CONTROL_PASS; TRAINING_NOT_RUN; PIT_NOT_ADMITTED; OOS_ALPHA_NOT_ESTABLISHED; RELEASE_NOT_AUTHORIZED.
1. Existing Task 2 #1596: separately resolve original vendor first-known and prospectively matured independent source-bound rows; no R2 skill on 0 eligible mature rows. This source screen is NOT a new required blocker for ongoing Task 2.
2. Existing #1516/#1593: resolve source and independent recovery approval before live receiver-only issuance. Do not unblock with this research.
3. Existing Supervisor #1156: review isolated research PR; when exact-head checks, independent technical review and current recovery/platform gates allow, integrate source note/tests; verify main SHA/blobs and report naturally.
4. If and only if research R1 is actually admitted and a frozen trial exists, execute Pilot 1 first; stop cheap when no non-naive improvement. No need for additional user approval for scoped free/local analysis already covered by the user's mandate, but no automatic elevation past immutable signed scientific/security gates.
5. No automation, GitHub workflow, external paid service, additional credentials, API spending or broker action authorized or created by this package.

## G. Sources and source hierarchy

- Original pinned: https://github.com/zadescoxp/Temporal-Fusion-Transformer-Price-Prediction/tree/f1d35896a02ba054c5abf5ac08fc8f627d504f2c
- Established package metadata: https://github.com/Nixtla/neuralforecast and https://github.com/Nixtla/statsforecast
- Calibration: https://github.com/scikit-learn-contrib/MAPIE
- Foundation: https://github.com/amazon-science/chronos-forecasting and https://github.com/SalesforceAIResearch/uni2ts
- Existing scientific controls: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596
- Existing range owner: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516
- Existing research prior-art intake: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1781
- Existing broader HF challenger inventory: 06_RESEARCH_LAB/hugging_face_task2_audit_20261022/13_HF_SOURCE_PILOTS_AND_MODEL_CHALLENGERS.md

No external upstream repo was modified. No model performance is claimed.
