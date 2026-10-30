# Task 2 · Kompas/EDGE October 2026 development baseline

**Status:** EXECUTED_DETERMINISTIC_EX_POST_DIAGNOSTIC / NOT_PIT_ADMITTED / NO_FORECAST_OR_ACTION_EDGE  
**Research date:** 2026-10-30. **Controlling issue:** [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596). **Mission identifier:** `TASK2-KOMPAS-EDGE-R2-MISSION-20261030`.  
**Scope:** Read-only arithmetic on public original archived hourly BTCUSDT bars, not new original issued Compass forecasts. Independent API model calls: **0**. Market/portfolio authority: **NONE**.

## 1. Original input population and provenance

The 30 UTC daily CSVs from `03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-01.csv` through `2026-10-30.csv` were actually retrieved with the connected GitHub source reader and parsed as CSV by timestamp. First 29 files have 24 UTC opening timestamps each, Oct30 currently has nine (00:00–08:00Z). This makes **705 contiguous observed hourly rows**, 705 distinct UTC opening timestamps, 0 gaps, 0 duplicates, 0 non-PASS `spot_status` rows on the fetched version of main. BTC price quote is **USDT**, not a USD conversion. The individual `timestamp_utc` is **bar opening time**; the corresponding trading bar must finish at `open+1h`. Historical as-issued vendor/public first-known source validity is NOT proven by a currently complete archive.

Input-version caveat: the earlier investigation had inspected only 21 available Oct29 hourly entries through 20:00Z, while the *current* main `2026-10-29.csv` contains 24 entries through 23:00Z. The remaining three are included for ex-post market-price outcomes only; no inferred original vendor availability. Verifying original commit/collect/publication clocks for late-arriving or repaired rows remains C02.

**All 30 inspected Git blob SHA-1 identities** (Git object SHA, not SHA256 of normalized CSV; originally observed on main):

| UTC date | Original CSV blob SHA-1 |
|---|---|
| 2026-10-01 | `c2b3ac0bdf1a7bf616779ff2ad25c6bf7aa351fd` |
| 2026-10-02 | `c0d0f2abc3633d9459292ef7dd90c72ba4ea4394` |
| 2026-10-03 | `80338c7ed3936a1ed9a3fb22816d239e73341828` |
| 2026-10-04 | `760415ac7f52aae862036976cb4639685950dd17` |
| 2026-10-05 | `c6c08469f901611de95fc04fab7855313db26535` |
| 2026-10-06 | `32bb979ab199f66c070e83a9ac1d2337facc444e` |
| 2026-10-07 | `4ca0ffbfcbc4395b4cee0c6adf73bc68a787a923` |
| 2026-10-08 | `e8321a5531e147a79f11f375673127d3231fd79f` |
| 2026-10-09 | `43c965b5cd83e277c6d43e66ccc1cccaa5bdc712` |
| 2026-10-10 | `4bfac584f1cd4bb0c592f9c7dc7df7f63d3eed8d` |
| 2026-10-11 | `a605e0d0d2169c844e9afc9c9a2d312be5f88588` |
| 2026-10-12 | `9e525b261ea11b05aab58601dc7e2ea51b067d5d` |
| 2026-10-13 | `ced07a092ff0f4e4ac17c4139afd9f45f0c62e7e` |
| 2026-10-14 | `37e437bbeca1bcd3d1248b945b891576d19c7e5c` |
| 2026-10-15 | `20acce69b60ae79d938bc57f0c692c731d50dd69` |
| 2026-10-16 | `127094125f712c5eed06972aaade46054cce5293` |
| 2026-10-17 | `8a5f675e475d537162b55cf4cf39293627824e7c` |
| 2026-10-18 | `0a8a66405ee90b38d8d379c5c3af82091b9fabdd` |
| 2026-10-19 | `8f4fdef8ff23c0c9a5dfeb2a69ec35a5ba571cbd` |
| 2026-10-20 | `14b69ca05ac77d0746517760e2e22cbd162b2081` |
| 2026-10-21 | `fc69c76b86da6c0af6ea8e2971c23d6950463024` |
| 2026-10-22 | `b8acc37486523519e080caca32c2c7b593ccc282` |
| 2026-10-23 | `beddb7dc1a6afbf25f8cc3b8e28dd6c590bff12d` |
| 2026-10-24 | `4141c9d77992fade862b61f05cdebc7289a234da` |
| 2026-10-25 | `5ff99a1f531056d77a4ddf67d5aa76cb4434dd8a` |
| 2026-10-26 | `9866e34b490d1684514ed31eddf35000db131ec4` |
| 2026-10-27 | `8cb948f024418d6be3497968f11eedc62e0f0a1d` |
| 2026-10-28 | `fb34cd6299b9e1a97b7a06e70f7070cf38b6eb85` |
| 2026-10-29 | `a7ab3bd312ef5ecc5a40ab0d3996540671afc59c` |
| 2026-10-30 | `241efed4aa6e500f12311f7e4c806f6a435c464f` |

## 2. Exact deterministic diagnostic procedure

For each possible hourly decision, source bar `i` is a fully completed BTCUSDT hourly bar (at or later than open+1h). Require **24 previous including current** contiguous completed hourly high/close bars and **72 subsequent contiguous hourly low bars**. No interpolated gaps or revisional provider quote. The hypothetical decision reference is `close[i]`. The ex-post target is:

`Y[i] := min(low[i+1],...,low[i+72]) / close[i] <= 0.95`.

This is a newly proposed **development label**, *NOT* the original M6 -10/-15/-20% peak-to-trough barrier or a published Official 72h forecast target. The future 72 bars complete 72h after decision-bar close. Missing endpoint => **CENSORED**, never counted as a non-event.

Two 17-file overlapping read batches were used to stay below connector call limits. Their **decision populations do not overlap**: batch A Oct01–Oct17 contributes Oct02 00Z–Oct14 23Z (312 eligible decisions); batch B Oct14–Oct30 contributes Oct15 00Z–Oct27 08Z (297 decisions). Overlapping Oct14–17 price rows are only history/outcome context. Aggregate **609** unique eligible decisions. The 96-hour length exclusion per batch is exactly 24-hour warm-up + 72-hour target maturation. 24h warm-up uses `high[i-23:i]`.

Illustrative reference rules, not trained or previously issued: `B1_RET4` fires if `close[i]/close[i-4]-1 <= -0.01`; `B2_DD24_3` if `1-close[i]/max(high[i-23:i]) >= 0.03`; `B3_DD24_5` if drawdown >=0.05. Thresholds were not fitted, calibrated or selected on a legally unseen holdout; they are only ex-post descriptive comparisons. Label is BTC-only and ignores user-specific portfolio liquidity/cost.

## 3. Actually computed results

| October development statistic | Value |
|---|---:|
| Unique continuous hourly input bars | **705** |
| Complete 72h decision windows | **609** |
| Windows with future >=5% BTC decline | **47 / 609, 7.72%** |
| Approximate independent adverse episodes | **two** (Oct05–07 and Oct21–22 decision families, needs formal M6 clustering) |
| No-event windows | **562** |

**By original non-overlapping decision batch:**

| Batch / decision range | Eligible | Positive | B1 true positive / false alarm | B2 true positive / false alarm | B3 positive alerts |
|---|---:|---:|---:|---:|---:|
| A, Oct02–Oct14 | 312 | 35 | 3 / 21 | 0 / 25 | 0 |
| B, Oct15–Oct27 08Z | 297 | 12 | 1 / 15 | 0 / 29 | 0 |
| **Total** | **609** | **47** | **4 / 36** | **0 / 54** | **0** |

B1: 40 fired alert hours, **10.0% precision (4/40)** and **8.5% recall (4/47)**; the 36 false alert hours include strongly overlapping intraday samples. B2: 54 fired alert hours, **0/54 positive**, 0/47 recall. B3: zero fired alerts, zero recall, precision **UNDEFINED** (not 100%). Base prevalence 47/609 = 7.72%, but is *not* an independent 47-trial probability estimate.

**Positive windows by original decision date:** Oct05=10, Oct06=24, Oct07=1, Oct21=10, Oct22=2. These are temporally correlated: classifying 47 forecast *hours* as 47 separate successes is pseudo-replication. Classifying these two clusters as truly causally independent without a frozen event-family join is also premature. Primary inference `INSUFFICIENT_INDEPENDENT_EVENT_POWER`.

**Oct22–30 restricted window check:** 201 original contiguous hours with 24h warm-up and 72h completed future => 105 eligible decision bars, **0 positive** for this 5% target. This earlier negative preliminary is consistent with the full-month expansion: Oct21–22 decision positives occur at the *beginning* of the expanded second batch and were outside the late-window eligible decision period. No model accuracy claim is valid from the 105 all-negative sample.

## 4. Scientific interpretation and negative evidence

1. **No proven predictive edge.** No Original issuance, provider-first-publication, original actual user delivery or independent held-out period binds this ex-post replay. Baselines selected descriptively after historical outcomes were known. External source collection and public GitHub backfilling do not establish original as-issued availability.
2. **Hard limitation is independent adverse-event N**, not 609-hour denominator or an AI model's reasoning power. Oct incident waves and overlapping 72h windows inflate apparent samples. Do not run/optimise a 150–400 candidate grid on this dataset.
3. **Simple price-only alarms are not useful here:** one 4h momentum rule has 4/47 alert-window overlaps while firing 36 non-events; a 24h peak drawdown threshold >=3% produces 54 non-events, zero correct alerts. Different outcomes, horizons and persistent normal market trends may change a fully registered result, but no claim is proven here.
4. **M6/Task2 separate clocks and targets:** This 5% prospective-72h label is distinct from previously frozen M6 drawdown severity and official 12/72/168h next-close direction; compare matched original targets only after source proof. The partial hourly archive has recently changed in coverage; backfilled rows are not evidence available at the earlier warning time.
5. **Missing family information is not zero.** This particular replay uses publicly captured price only; it does *not* test CFGI, ETF, ETH/BTC, OI, venue depth or multi-factor model quality. It must never be marketed as rejection of those families.
6. **Economic edge not tested.** HOLD comparison, signal delivery, quotes/fills/spread, live microcap liquidity and taxes require a separate original action experiment. Alert precision is not profit.

## 5. Required next gates before candidate tournament

- C01/C02: independently bind each of the 24 original fields per forecast to its source **first known** or an eligible original response; preserve 11 original R1 PIT admissions at 0 until verified; reconcile the three breadth fields that switch between `LIVE_ANCHOR_BREADTH_REFERENCE` and `RICH_BREADTH_OWNER`; don't double-count one CFGI vendor model as four independent votes.
- C03: finalize and publish a *versioned, prior-to-future-outcome* protocol for primary outcome and event family, train selection, embargo, proper Brier/calibration (when real probabilities exist), false-alarm budget and complete no-warning census. The [initial owner protocol](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596#issuecomment-6519870099) is a DRAFT, not a sealed holdout.
- C04: implement any real backtest **CODEX_ONLY** under a single original research owner/PR with source-hash regression, negative-source-clock mutants, row-freshness and 24h/72h censoring controls. No new production workflow/market scorer. Do not re-use this report's October outcomes as unseen validation.
- C05–C08: independent Oct29 and FTX 2022 cases, false-rebound controls, legally timed risk-stage comparison, then investor-action after-cost study and independent science review. Any low independent N warrants `NO_EDGE_TEST_POSSIBLE`, not a false performance win.
- **API:** all Terra 6.1 Extra High slots remain on HOLD for existing #1823 atomic budget/recovery-safety gate; no paid call performed or incurred by this report. The top-level mission [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596#issuecomment-6519531633) still owns the queue. Research-only documents must not alter model weights, source threshold, Official Kompas action or SELL permissions.

**Verdict:** `PILOT_BASELINE_REPRODUCED_DESCRIPTIVELY`; `COMPARATIVE_MODEL_EDGE=NOT_TESTED`; `R1_PIT=NOT_ADMITTED`; `PAID_TERRA_DISPATCH=BLOCKED`; `LIVE_ACTION=NONE`.

This report is proposed for a doc-only review PR. It is not an independent research review or an eligible source of forecast claims until reviewed, checked and merged according to actual repository governance.
