# Task 2, W39–W45 equal-width benchmark, 13 November 2026

**Status:** `RETROSPECTIVE_DESCRIPTION_ONLY_NO_MODEL_PROMOTION`. Source-pinned independent readback and arithmetic, not a verified prospective forecast or trading edge. Original owner: Task2 [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), independent falsification: Claude [Bridge #173 / 6856493637](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/173#issuecomment-6856493637).

**Public source commit**: `20fc2ccabc75165257215d5c4ee255ecb55dac59` (Archive main readback 2026-11-13). All 15 underlying JSON source files were read on this **exact ref**: seven `05_CYCLE_NAVIGATOR/weekly/2026/Wxx/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`, eight `03_DAILY_CAPTURE_LOGS/weekly_close/2026/Wxx/WEEKLY_MARKET_CLOSE_PACKAGE.json` for W38–W45. No private data, model API, research source fabrication or official freeze changes.

## Method, fixed before interpretation

For each BTC/ETH ISO week W39–W45:
- `CN = [forecast_low,forecast_high]` from that week's historical machine freeze.
- `EQW_PRIOR = [prior_week_close - (CN_high-CN_low)/2, prior_week_close + (CN_high-CN_low)/2]`. The benchmark has **the same width** as CN. It is not the narrower previous-week-high/low naive interval.
- Outcome is each maturity-complete week's original 168h `weekly_low,weekly_high,weekly_close`, Binance `WEEKLY_MARKET_CLOSE_PACKAGE_v3`. Full-range containment is distinct from close containment.
- Mean boundary breach = `(max(0,band_low-actual_low)+max(0,actual_high-band_high))/prior_week_close`. An after-outcome `actual_close` must **not** normalize this measure.
- Sensitivity-only interval score at assumed `alpha=0.2`: `[width + 2/alpha * (max(0,band_low-close)+max(0,close-band_high))] / prior_close`. CN interval has **no validated 80% nominal prediction-interval promise**, so this is an explicit comparative sensitivity, not admitted probability calibration.
- Each unique 2026 ISO week is one independent cluster **per asset**. BTC/ETH share market episodes and may not be pooled as 14 independent experiments.

## Directly recomputed aggregate

| Metric, 7 mature weeks each asset | BTC CN | BTC equal-width | ETH CN | ETH equal-width |
|---|---:|---:|---:|---:|
| Full 168h range contained | 6/7 | 5/7 | 6/7 | 6/7 |
| End-of-week close contained | 7/7 | 7/7 | 6/7 | 7/7 |
| Mean normalized boundary breach | 0.2652% | 0.4452% | 0.8062% | 0.6330% |
| Mean assumed-alpha close interval score / prior close | 12.4372% | 12.4372% | 18.5843% | 17.3762% |

**Interpretation:** relative to the equal-width **prior-close** control, BTC has one additional full-range containment, and ETH has **no** containment edge. ETH's mean boundary breach and close score are **worse** than the control. An apparent advantage over the narrower previous-week high/low control was mainly a width effect. None of these prove information-time-matched forecast placement or after-cost capital protection.

## Reproducibility, immutable source Git blobs

| ISO week | CN freeze Git blob | Weekly actual Git blob |
|---|---|---|
| W39 | `cb1aaa77c3a4b1c6f40e37d384acfdf933d502d7` | `020385ac375ded5df3c04f2b3b660f7eea25877f` |
| W40 | `4f867d594c355c31ede8a3718638c6e72249a5a8` | `8b0a8e225cae6e730634492f539dd936cea35afb` |
| W41 | `91702e1bed4981e7b76bc07e990b7a676f9c0e57` | `de9d54c5d6db22299db7c8ba18b18174d6fbae5e` |
| W42 | `71704b60f7a5c7f41c553e0ddfab6ef9ccd5c95b` | `0fe1ec8aa4fc17483309bed673c41451a62331cd` |
| W43 | `472885ed2eb145bab303c8f26308c5261ddb8ded` | `e114b9047b635e54791f023a2f37ce00d605eb2d` |
| W44 | `4920c9f5c23279ecd540948b19cbd92c34dbebdf` | `003ebf591caa00aeb551b1e3ee919baebb429576` |
| W45 | `2e78b08162f9592c643722ee4596072b77c7c7c0` | `99da396c2e374c997bd342995c38cfe5e4fa9357` |

The prior week closes come from the same source package family, W38–W44, read and source-pinned at the same commit. Companion new implementation: `scripts/research/task2_cn_equal_width_sidecar_v1.py`, ten adversarial tests in `tests/research/test_task2_cn_equal_width_sidecar_v1.py`. The code consumes the old replay's machine CSV rather than silently altering original historical reports.

## Hard scientific caveats and next admission gates

1. This replays **entire** calendar weeks, including pre-issuance Monday prices. Historic machine freeze first-publication/source-first-known and consumer receipt have not been independently established. Original first-in-main lag is material, especially W39. Strict prospective eligible sample remains zero.
2. Claude's separate **first-in-main-price-centered** equal-width control yielded lower mean normalized breach than CN for both assets, BTC 0.113% vs 0.265% and ETH 0.623% vs 0.806%, but information-time matched post-freeze observations are still required to validate forecast skill. The first-in-main control is **not** implemented or backfilled without its verified anchor.
3. W40 current structural/internal score versions differ from the earliest issued version (Claude original `0e67a4b8` vs later `e64e4c52`, five INTERNAL claim changes). This standalone **price-range** study does not score changed structural claims as originals.
4. CN #21 published scores are method-unreproducible; CN #8/#14 public text versions have publication-provenance gaps. Do not rewrite them or silently declare them verified.
5. Need post-first-known hourly outcome slices, truly source-legal first-known/first delivery clocks, native version join, and independent no-event risk controls before promotion, portfolio simulations or capital utility claims.

No Fable R5 W47+ duplication, new scheduled workflow, paid Astra, model-weight change, official signal, or automatic buy/sell.
