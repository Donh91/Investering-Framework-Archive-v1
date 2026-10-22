# 16 | Pinned BTCUSDT 1h file QA, first real T1 pilot (2026-10-22)

**Verdict: T1_FILE_QA_WITH_GAPS / AFTER_FACT_TRUTH_CANDIDATE. T2 PIT admission: NO.** This is an executed source-quality pilot, not a historical Compass backtest or evidence that the dataset was available to the original issuer.

## Exact source and rights boundary

- Public dataset: `linxy/CryptoCoin`, `BTCUSDT/BTCUSDT_1h.parquet`.
- Immutable Hub revision: `9288a8d3f5e8a3fd0af814c2429b4cb565356908`.
- Git LFS pointer at that revision declares SHA-256 `712fedb852b6eb26a2864959cf3c6c7cc1ee0ca80565ad12a264b84c0eb12772`, size 9,050,531 bytes. The downloaded single file independently matched both values. No full dataset mirror.
- Dataset card tags the repository MIT; underlying Binance data redistribution and commercial provenance were not independently adjudicated. Research-only file QA, no production ingestion or public row redistribution.
- Hub repository metadata at inspection: last modified `2026-10-22T00:48:45Z`; README says auto-updated daily and last updated `2026-10-22T00:48:34Z`. This is repository-level timing, **not original Binance first publication, file-level first-known, or 2017-2026 historical availability**.

## Reproducible QA

The companion `16_PINNED_BTCUSDT_1H_T1_QA.py` requires Python and `duckdb`, accepts the downloaded pinned Parquet file as its only input, hard-stops on a SHA mismatch, runs column and time/price/volume checks, and executes six adverse in-memory fixtures. Command:

```bash
python 16_PINNED_BTCUSDT_1H_T1_QA.py BTCUSDT_1h.parquet
```

Actual run on the exact blob (UTC semantics assumed from the card; Parquet timestamp physical type is `TIMESTAMP_NS` without an embedded independent first-known clock):

| Check | Measured result |
| --- | ---: |
| Rows / unique hour opens | 80,317 / 80,317 |
| First / last hour open | 2017-08-17 04:00 / 2026-10-21 00:00 |
| Hour-gap boundaries / omitted expected hours | 28 / 128 |
| Non-full one-hour close timestamps | 14 |
| Non-full close immediately before a gap | 11 |
| Null clock / unaligned hour open | 0 / 0 |
| Non-finite or unparsable numeric / impossible OHLC / invalid volume | 0 / 0 / 0 |

Largest observed gap skips 33 hourly openings after `2018-02-08T00:00:00` until `2018-02-09T10:00:00`. These 128 absent hours and 14 partial close timestamps must remain missing/partial, never forward-filled as completed candles. Beyond the core columns the schema has the documented `ignore` placeholder and an unexpected all-null column named `version https://git-lfs.github.com/spec/v1` (0 non-null rows). Prices and volumes are `VARCHAR` despite the card's numeric-field presentation. The QA script explicitly casts/checks numeric fields. This is a schema-compatibility observation, not proof of mislabeled prices.

Six injected cases were all caught by the same QA predicates: duplicate hour, missing hour, partial close, impossible OHLC, negative volume and `NaN` price. The file digest guard rejects an altered blob before row analysis. These are source-integrity tests, not predictive-skill tests.

## Decision impact and science gate

The exact file has Oct 12-13 BTCUSDT bars that may serve as a *retrospective* independent price-truth comparator or later price-only baseline diagnostic. Its pinned revision and repository update on Oct 22 occur after the 11 original Oct 12-13 native-v3 forecast issues. Historical row timestamps cannot establish what was in this particular HF file, in Binance's feed, or in the framework's original capture at those issue times. This source therefore changes **zero** of the existing 11/11 R1 non-admissions; independent market-event family count and actionable delivery clock remain unverified. No R2 same-clock original-framework skill comparison or R3 after-cost action conclusion was run.

Cheapest next evidence: resolve one of the 11 original issues against its immutable original per-field capture/first-known and actual first user delivery, with missing attempts retained. If admissible, preregister one price-only baseline on the *original* issue and target clocks. The HF file can then be considered as an after-fact outcome crosscheck, excluding its gaps and partial bars, subject to rights and source disagreement review. If original first-known is still unavailable, retain `NOT_IDENTIFIABLE_YET` and do not purchase compute to disguise that limit.

**Resources spent:** one public 9,050,531-byte file download, public Hub metadata/card reads, local DuckDB computation. HF FREE account observed, zero HF Jobs/GPU, zero paid API, zero GitHub Actions minutes. No raw row values committed here.
