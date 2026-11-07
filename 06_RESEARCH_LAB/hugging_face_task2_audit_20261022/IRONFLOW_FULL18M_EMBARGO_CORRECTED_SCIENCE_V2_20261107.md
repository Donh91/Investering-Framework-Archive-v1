# 50 | SCIENTIFIC CORRECTION: 25-hour purged-label Ironflow 18-month replay and Feb-2026 failure atlas

**As of:** 2026-11-07 UTC. **Status:** CORRECTED_HISTORICAL_DEVELOPMENT_ONLY / PUBLIC_T1_PASS / PROSPECTIVE_EDGE_UNPROVEN. **Source:** Ironflow (ironflow.sh), CC BY 4.0. **Original owners:** Task 2 #1596, Derivatives #387, Alpha Lab #22. 
**Authoritative for model figures:** This file supersedes `IRONFLOW_FULL18M_ACTUAL_RESULTS_20261107.md` (initial UNEMBARGOED training-label result) and supersedes the **Brier performance inference only**, not the actual source file and historical-value evidence, in `IRONFLOW_T2_T3_CHRONOLOGICAL_ABLATION_RESULT_20261106.md` from the 3-month pilot. Preserve those earlier dated execution receipts as error history; do NOT cite them as final chronological score comparisons.

## 1. The scientifically material bug caught before release
For any evaluation month beginning on `YYYY-MM-01 00:00 UTC`, a previous-month day anchor at `23:00 UTC` has a *forward 24h minimum-low label* that is not complete until **anchor timestamp +25 hours**. The original monthly training selected prior calendar months without purging rows whose labels matured in the test month. These rows leaked future outcome information across the boundary, most commonly six asset/day records per month. Since "out-of-time" does not necessarily mean "matured-label-safe", this was a **real retrospective leakage hazard**, regardless of whether the numeric impact proves small.

**Code repair:** `scripts/research/ironflow_oot_ablation_v1.py` AND `scripts/research/ironflow_full18m_walkforward_v1.py` now exclude any train row with `anchor_timestamp +25h >= test_month_start_utc`. The eligible training sample for February is now **741**, with six boundary train labels purged, maximum train label maturity **2026-01-31 00:00 UTC**, before test start February 1. Adversarial source-fixture tests inject an unmatured month-final row and prove it is excluded.

Actual embargo-corrected full source reread and all three jobs **SUCCESS** on GitHub [#42314538645](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42314538645), source artifact `13549444774`, ZIP SHA256 `756202fe6a939bcddf82f016ae403cb7bb1cd58c908be2a3190f113ba39f4479`; second confirmation with explicit original Feb source gap census [#42314816983](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42314816983), artifact `13549684489`, ZIP SHA256 `1b47fc701dcfb149fab7fbba5d0d8eed6334da5aa835a6cc831ccb3fad1bb93d`. Both actual runs inspected from output ZIP, not inferred from run status. Any further head/source edits still require exact current-head CI for eventual merge.

## 2. Corrected 12-month measured comparisons

Target: next 24 completed hours contains any low >=2% under last fully completed-hour close. Month x asset daily anchors across BTC/ETH/HYPE. Positive Brier delta means derivative model helps relative to price/vol/market baseline; negative means it worsens. **Historical retrospective chronology only, no original publisher-asof, no sealed independent test.**

| Month evaluated | n | Price/vol Brier | +LiQ/OI/Funding Brier | Improvement (Brier delta) | Approx day-cluster bootstrap 95% |
|---|---:|---:|---:|---:|---|
| Nov 2025 | 90 | 0.215895 | 0.223324 | **-0.007429** | [-0.017548,+0.003318] |
| Dec 2025 | 93 | 0.248762 | 0.242618 | +0.006144 | [-0.001179,+0.013114] |
| Jan 2026 | 93 | 0.219457 | 0.216118 | +0.003339 | [-0.007352,+0.014554] |
| Feb 2026 | 78 | 0.229567 | 0.260175 | **-0.030608** | [-0.048587,-0.014122] |
| Mar 2026 | 93 | 0.242557 | 0.240411 | +0.002146 | [-0.006942,+0.011182] |
| Apr 2026 | 90 | 0.240885 | 0.235086 | +0.005799 | [-0.004877,+0.015367] |
| May 2026 | 87 | 0.233697 | 0.236509 | -0.002812 | [-0.009227,+0.003039] |
| Jun 2026 | 90 | 0.202184 | 0.198902 | +0.003281 | [-0.001934,+0.008101] |
| Jul 2026 | 87 | 0.231265 | 0.231627 | -0.000363 | [-0.005248,+0.004334] |
| Aug 2026 | 93 | 0.204821 | 0.207334 | -0.002513 | [-0.008278,+0.002394] |
| Sep 2026 | 90 | 0.231728 | 0.230608 | +0.001120 | [-0.003619,+0.005219] |
| Oct 2026 | 90 | 0.239308 | 0.237935 | +0.001372 | [-0.003447,+0.006270] |

**Full corrected summary:** 12 test months, 7 improved, 5 worsened, **1,074 scored test asset-days**, **mean equal-month Brier delta -0.001710**, month-bootstrap 95% **[-0.007503,+0.002501]**, includes zero. **NO_REPLICATED_INCREMENTAL_INFORMATION_EDGE**. Source 72/72 SHA-verified files / 374,343,275 bytes / 14,572,946 original cross-market source rows / 37,758 matched market-hours. Mean performance is weakly worse, not proof that all derivat signals lack information; no economically executable before-crash benefit has been proven.

The February result has a potentially material deviation, but 12 parallel month checks, model-family selection after initial results and shared market shock mean the month-specific interval cannot be called an untouched independent prospective failure rate.

## 3. February 2026 failure mechanism, actual source QA and calibrated probabilities

The 18-month model analysis enrolled **26 out of 28 February UTC days** in each of the BTC, ETH and HYPE test cohorts. Original source inspect from the time-aligned hourly panel and explicit day census in #42314816983 shows:

- **Feb 12, 2026:** all **24 hourly OI USD observations are null** for BTC, ETH and HYPE. Price OHLC and settled funding are available for each hour, and 24h future price-path truth labels are present. This is an original upstream OI USD coverage gap, not price or funding absence.
- **Feb 13:** OI USD itself is back, but a previous-24h OI-change feature requires Feb 12, so Feb 13 day anchor also fails the complete as-of feature gate.
- Dates Feb 12 and Feb 13 are **properly excluded for all three assets**, not zero-filled or late-restored. Missingness can cause selection bias in historical crash/stress samples. We do not claim the missing days were profitable, catastrophic or quiet without additional separately marked outcome-only QA.

### Frozen February market calibration, no model retuning
| Market | Actual 2% adverse-path incidence (n=26) | Mean probability, price-only baseline | Mean probability, +derivatives | Baseline Brier | Deriv Brier |
|---|---:|---:|---:|---:|---:|
| BTC | **20/26 = 76.92%** | 39.98% | **34.55%** | 0.293328 | **0.337630** |
| ETH | **20/26 = 76.92%** | 54.36% | **47.37%** | 0.201440 | **0.238290** |
| HYPE | **20/26 = 76.92%** | 71.33% | **67.69%** | 0.193935 | **0.204606** |

All three market groups show lower assigned risk probability *after* inclusion of derivat features, while the true subsequent intraday drawdown incidence is 76.9%. February cohort 78 observations /60 adverse outcomes, historical six-month-plus training prior risk 48.18%. This is **underprediction of risk in this development sample**, particularly BTC/ETH; it is not a causal identification of which individual feature caused it. AUC for February marginally increases **0.6315→0.6398** even as Brier worsens **0.2296→0.2602**, illustrating ranking vs calibration divergence. Don't judge protective warnings solely by AUC or directional hit rate.

**Critical next tests, frozen before evaluation:** source-gap sensitivity for Feb 12/13 with label-only true prices, missingness reporting, source-vintage checks for original OI base units, and independent original cross-venue OI source, but no historical data fabrication or unregistered imputation. Separate regime-specific hypotheses must have correction for multiple testing and fresh forward holdout. **Do not tune the production Kompas simply because February was adverse.**

## 4. Full-risk scientific and custody status

- Trained on historical months and corrected *matured labels* only, but Ironflow's HF source was first released Nov 2026: no proof the exact 2025/Oct-2026 values were original decision-time available. `SOURCE_FIRST_KNOWN_UNVERIFIED`.
- Those datasets may be used for historical market truth / T1 quality / retrospective stress, not originally frozen 2025/2026 Kompas predictions. No actual investor alert delivery or execution quality.
- The source benchmark includes only three selected perp assets, all correlated, noncommercial prospective deployment still unproven, and a small number of calendar-month clusters (12).
- Recreating historical risk scoring after researching Feb2026 would be classic overfitting. Preserve the baseline and failure receipts; any challenger needs independent prospective testing, nontrading shadow only.
- **T3 offline durable source archive is still pending**. Public-source hash registry `IRONFLOW_FULL18M_SOURCE_SHA256_REGISTRY_20261107.md` is durable T0, but original 374MB files are on frozen external HF revisions and transient 30-day Actions artifacts only.

**Decision:** `T1_SOURCE_QA_PASS`, `TRAIN_LABEL_25H_EMBARGO_PASS`, `FEB12_OI_DATA_GAP_VERIFIED`, `FEB13_LOOKBACK_CENSOR_VERIFIED`, `HISTORICAL_STRESS_TRUTH_REPLAY_PASS`, `INCREMENTAL_EDGE_UNPROVEN`, `PROSPECTIVE_PIT_BLOCK`, `TASK2_AS_A_WHOLE_NOT_COMPLETE`.
