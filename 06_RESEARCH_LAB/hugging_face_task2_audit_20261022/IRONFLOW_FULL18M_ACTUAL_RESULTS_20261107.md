> **SUPERSEDED FOR MODEL PERFORMANCE:** This original successful CI receipt used an unembargoed month-boundary train label. The corrected, actual 25-hour purged results and Feb 12/13 OI source QA are authoritative in [IRONFLOW_FULL18M_EMBARGO_CORRECTED_SCIENCE_V2_20261107.md](IRONFLOW_FULL18M_EMBARGO_CORRECTED_SCIENCE_V2_20261107.md). Its 72-source-hash/byte QA and execution receipts remain historically valid. Do not cite the old Brier numbers below as final model results.

# 48 | Ironflow complete 18-month actual public-data replay: 12 chronological monthly results

**Executed at:** 2026-11-06 23:39 UTC. **Original source:** Ironflow (ironflow.sh), CC BY 4.0. **Source gate:** T1_SOURCED_PARQUET_READBACK_PASS / HISTORICAL_DEVELOPMENT_ONLY. **Model status:** NO_REPLICATED_INCREMENTAL_EDGE. **Owner:** existing Task 2 #1596, derivatives #387, Research Lab. This report complements the prior three-month pilot merged in #1988, and extends it on PR #1989.

## Actual machine and source receipts
- Exact source code: [PR #1989](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1989); initial source-bundle CI [run #42313211239](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42313211239) **SUCCESS** in all 3 jobs, including the 18-month job, original HEAD `2319320084c6d4d9a8c4303b5386051cdb6a7bf9`.
- Full 18m original source+model output artifact ID **13548748041**, artifact ZIP SHA256 `c3df97ecac2141d574de8e3849ca2c6d510b9d3ddbeabab279af5d983fdca139`, expiry 2026-12-06. Contents: `FULL18M_T1_SOURCE_QA.json`, `FULL18M_WALKFORWARD_RESEARCH.json`, `HF_MEMBER_SHA256SUMS`.
- **Actual binary downloads** 72/72, exact public pinned HF revision and actual SHA256 each file, full cross-market counts from T1 QA: 14,572,946 rows across 18-month *four-family* source panels, combined **374,343,275 downloaded bytes**. Families: 2,848,413 liquidation position events, 4,104,648 settled funding market observations, 3,977,432 OI rows and 3,642,453 hourly candles, all markets. Selected BTC/ETH/HYPE comparable completed hourly panel **37,758 rows** and **1,545 day anchors**. Do not mistake total 14.57m source rows for independent sample size.
- SHA256 for all 72 original binary files now permanently preserved as text in [full 18m registry](IRONFLOW_FULL18M_SOURCE_SHA256_REGISTRY_20261107.md). The raw 374MB itself is not retained in Git; **T3_DURABLE_OFFLINE_COPY_PENDING**.

## Fixed methodology
- Original source vintage Nov-2026, so *none* of the original 2025..Oct2026 early forecasts could have consumed this exact released file retrospectively as original first-known input. All data in this report are **after-fact truth/research only**, not already-issued predictions or prospective edge.
- BTC/ETH/HYPE perp-specific day anchored at completed UTC hour ending 00:00 on next day. Past 24h only to form price return, realized volatility, realized liquidation notional / approximate volume, settled funding and OI change. Forward **24h minimum low vs last close** classifies 2% drawdown; do not equate with executable sale.
- Complete train-only sklearn scaling and frozen logistic C=1, fixed price+market dummy baseline versus same baseline + 3 lagged derivative features; previous 6 completed calendar months before Nov2025, expanding with each new completed month. **12 rolling historical out-of-time test months Nov2025..Oct2026**. BTC, ETH, HYPE are correlated by UTC day and not treated as independent tail events. Month-level bootstrap 2,500 resamples for mean Brier delta.
- All recipe and feature choices were exposed to some later outcomes from initial 3mo pilot, therefore this is a **retrospective chronological development test, NOT sealed untouched out-of-sample**. Publication time and actual user alerts excluded from execution scope.

## Actual 12-month historical model comparison
Positive Brier delta means added derivs improve prediction relative to price+vol baseline, negative means worsen it. The 95% per-month date-block interval tests only sampling uncertainty within studied monthly days and was not adjusted for model selection or 12 parallel tests.

| Evaluation month | n daily x asset observations | Price/vol Brier | Plus liq/OI/funding Brier | Incremental Brier delta | Per-month 95% day-block interval |
|---|---:|---:|---:|---:|---|
| 2025-11 | 90 | 0.217843 | 0.225558 | **-0.007715** | [-0.017639, +0.002655] |
| 2025-12 | 93 | 0.248927 | 0.242867 | +0.006060 | [-0.001266, +0.012987] |
| 2026-01 | 93 | 0.219492 | 0.216180 | +0.003312 | [-0.007298, +0.014499] |
| 2026-02 | 78 | 0.226524 | 0.257582 | **-0.031058** | [-0.048681, -0.014629] |
| 2026-03 | 93 | 0.242718 | 0.240581 | +0.002137 | [-0.006142, +0.010360] |
| 2026-04 | 90 | 0.241163 | 0.235157 | +0.006005 | [-0.005227, +0.016092] |
| 2026-05 | 87 | 0.233783 | 0.236593 | -0.002810 | [-0.009164, +0.003083] |
| 2026-06 | 90 | 0.202184 | 0.198902 | +0.003281 | [-0.001934, +0.008101] |
| 2026-07 | 87 | 0.231284 | 0.231573 | -0.000289 | [-0.005117, +0.004360] |
| 2026-08 | 93 | 0.205191 | 0.207581 | -0.002390 | [-0.008057, +0.002454] |
| 2026-09 | 90 | 0.231596 | 0.230498 | +0.001098 | [-0.003606, +0.005126] |
| 2026-10 | 90 | 0.239380 | 0.237998 | +0.001382 | [-0.003649, +0.006358] |

**Month-wide summary:** 7/12 months improved, 5/12 worsened. Mean unweighted monthly difference = **-0.001749 Brier**. Month-level bootstrap 95% = **[-0.007628,+0.002512]**, spanning zero. **No stable incremental predictive advantage** has been demonstrated. In particular 2026-Feb has a large **negative** incremental delta -0.031058. The month’s interval does not include zero, but multiple testing, prior outcome exposure, possible regime drift and correlated asset outcomes prevent interpreting it as a sealed prospective failure estimate. However it is material enough to trigger independent source/time/market-specific failure QA.

## Core scientific implication
One may see a positive 1–3day association around liquidation cascades and another regime with the reverse. Original pilots on two months painted a mixed picture; the larger 12-month rolling test is also mixed, with slightly worse mean performance. More variables do **not** automatically improve the Compass. Do not promote raw liquidation counts or funding/OI combo to Compass `SELL`, `TRIM`, `RISK_DOWN`, automatic thresholds or portfolio allocation. A useful *narrative/contextual* stress signal is not proven early-warning edge.

## Next falsifiable and valid steps, existing owners only
1. **Failure localization, no retuning:** add per-market per-month frozen model report to the same code, especially Feb2026, with exact market denominators and price-only baseline losses. Distinguish asset/regime drift, base-rate shift, venue source anomalies, from true negative model edge.
2. Independent native Binance/other venue as-of 1h/24h price, OI and taker control. Test same-clock data availability and model lift, not just concurrent sign; avoid unsupported cross-venue aggregation and historical 451 blocks.
3. Source T3 custody: original 72 source blobs total 374MB; external frozen refs exist; temporary Actions artifact expires Dec6. Under `research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/DATASET_STORAGE_POLICY_v1.md`, use only verified approved T3 owner storage, read back member hashes and release durable object binding, or label permanent mirror `NOT_AVAILABLE`. No newly invented secrets/buckets, no public-main binary bloating.
4. A new distinct prospective period with **unmodified preregistered model**, original live source publication+collector receipt, 24h matured outcomes, cost/alert delivery/actuation semantics. Without these and blocked Round3 source authority, retain research-only status.
5. Framework Task2 original independent PIT/source identity and investor utility requirements remain open despite T1/data-quality completion of this specific external candidate.

**Terminal decision for this T1 history extension:** `72_FILES_SOURCE_QA_PASS`, `12_MONTHLY_REPLAY_PASS`, `INCREMENTAL_DERIVATIVE_EDGE_UNPROVEN`, `PIT_ADMISSION_BLOCK`, `OFFLINE_T3_CUSTODY_PENDING`. Preserve negative evidence; do not mandate unbounded search for a positive backtest.
