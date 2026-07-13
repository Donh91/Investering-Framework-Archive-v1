# Weekly Actual Range — 2026-W28 — Binance CEST Verified

**Run ID:** `VERIFIED_WEEKLY_RANGE_2026W28_20260713T060943977Z`  
**Period:** 2026-07-06 00:00:00 CEST through 2026-07-12 23:59:59.999 CEST  
**Extraction time:** 2026-07-13T06:09:43.977Z  
**Status:** `VERIFIED_ACTUAL_RANGE_PRIMARY`  
**Primary source:** Binance Spot  
**Symbols:** `BTCUSDT`, `ETHUSDT`, direct appendix `ETHBTC`  
**Resolution:** complete 1H grid with 5M→1M extrema refinement  
**Source convention:** `DIRECT_SOURCE_CONVENTION / BINANCE_SPOT_USDT / CEST_RESAMPLED`  
**Accepted data quality:** `HIGH`  

The collector reported MEDIUM only because no independent source was available in that run. The main framework cross-checked the weekly extrema against the already archived Yahoo Finance W28 range. All four differences are within the fixed `OK <=0.25%` threshold, so the accepted quality is upgraded to HIGH.

---

## Completeness and integrity

```yaml
BTCUSDT_rows_expected: 168
BTCUSDT_rows_received: 168
ETHUSDT_rows_expected: 168
ETHUSDT_rows_received: 168
ETHBTC_rows_expected: 168
ETHBTC_rows_received: 168
duplicate_rows: 0
missing_rows: 0
latest_source_timestamp: 2026-07-12T23:59:59.999+02:00
internal_consistency: PASS
source_substitution: NONE
provider_mixing: NONE
```

BTC/ETH values are USDT-quoted and must not be relabelled as exact USD values.

---

## Canonical weekly actuals

| Asset | Weekly open | Weekly low | Low time CEST | Weekly high | High time CEST | Weekly close | Width | Width % | Close location |
|---|---:|---:|---|---:|---|---:|---:|---:|---:|
| BTCUSDT | 63,092.00 | 61,306.84 | 2026-07-06 15:38 | 64,700.00 | 2026-07-06 23:10 | 63,920.40 | 3,393.16 | 5.534717% | 0.770244 |
| ETHUSDT | 1,786.91 | 1,713.44 | 2026-07-08 17:17 | 1,833.40 | 2026-07-06 23:10 | 1,812.28 | 119.96 | 7.001121% | 0.823941 |

```text
BTC largest daily range: 2026-07-06 / 5.534717%
BTC smallest daily range: 2026-07-11 / 0.951434%
ETH largest daily range: 2026-07-06 / 6.041239%
ETH smallest daily range: 2026-07-09 / 2.347947%
```

---

## Daily CEST intraday ranges

### BTCUSDT

| Date | Open | Low | Low time | High | High time | Close | Range | Range % | CLV |
|---|---:|---:|---|---:|---|---:|---:|---:|---:|
| 2026-07-06 | 63,092.00 | 61,306.84 | 15:38 | 64,700.00 | 23:10 | 64,489.98 | 3,393.16 | 5.534717% | 0.938105 |
| 2026-07-07 | 64,489.97 | 62,671.39 | 16:36 | 64,500.00 | 00:00 | 63,423.94 | 1,828.61 | 2.917775% | 0.411542 |
| 2026-07-08 | 63,423.93 | 61,544.56 | 17:25 | 63,761.99 | 02:44 | 62,187.17 | 2,217.43 | 3.602967% | 0.289799 |
| 2026-07-09 | 62,187.17 | 61,705.29 | 04:51 | 63,500.00 | 20:08 | 63,274.59 | 1,794.71 | 2.908519% | 0.874403 |
| 2026-07-10 | 63,274.60 | 62,926.01 | 02:34 | 64,692.83 | 15:52 | 64,011.99 | 1,766.82 | 2.807774% | 0.614652 |
| 2026-07-11 | 64,012.00 | 63,896.18 | 17:37 | 64,504.11 | 16:35 | 64,355.99 | 607.93 | 0.951434% | 0.756354 |
| 2026-07-12 | 64,355.99 | 63,640.83 | 08:29 | 64,424.03 | 00:11 | 63,920.40 | 783.20 | 1.230656% | 0.356959 |

### ETHUSDT

| Date | Open | Low | Low time | High | High time | Close | Range | Range % | CLV |
|---|---:|---:|---|---:|---|---:|---:|---:|---:|
| 2026-07-06 | 1,786.91 | 1,728.95 | 15:38 | 1,833.40 | 23:10 | 1,814.88 | 104.45 | 6.041239% | 0.822690 |
| 2026-07-07 | 1,814.88 | 1,757.57 | 07:14 | 1,816.82 | 00:04 | 1,773.84 | 59.25 | 3.371132% | 0.274599 |
| 2026-07-08 | 1,773.83 | 1,713.44 | 17:17 | 1,785.00 | 02:44 | 1,738.06 | 71.56 | 4.176394% | 0.344047 |
| 2026-07-09 | 1,738.07 | 1,721.93 | 05:19 | 1,762.36 | 09:02 | 1,748.17 | 40.43 | 2.347947% | 0.649023 |
| 2026-07-10 | 1,748.17 | 1,737.68 | 02:34 | 1,812.00 | 15:52 | 1,794.37 | 74.32 | 4.276967% | 0.762783 |
| 2026-07-11 | 1,794.37 | 1,786.77 | 04:01 | 1,830.00 | 19:40 | 1,823.97 | 43.23 | 2.419450% | 0.860514 |
| 2026-07-12 | 1,823.96 | 1,779.46 | 02:31 | 1,826.92 | 17:30 | 1,812.28 | 47.46 | 2.667101% | 0.691530 |

---

## RAW / Cycle Navigator outcome windows

| Window | Asset | Low | Low time CEST | High | High time CEST | Width | Width % |
|---|---|---:|---|---:|---|---:|---:|
| DAY_1_2 | BTCUSDT | 61,306.84 | 2026-07-06 15:38 | 64,700.00 | 2026-07-06 23:10 | 3,393.16 | 5.534717% |
| DAY_2_3 | BTCUSDT | 61,544.56 | 2026-07-08 17:25 | 64,500.00 | 2026-07-07 00:00 | 2,955.44 | 4.802114% |
| DAY_3_4 | BTCUSDT | 61,544.56 | 2026-07-08 17:25 | 63,761.99 | 2026-07-08 02:44 | 2,217.43 | 3.602967% |
| DAY_4_5 | BTCUSDT | 61,705.29 | 2026-07-09 04:51 | 64,692.83 | 2026-07-10 15:52 | 2,987.54 | 4.841627% |
| DAY_5_7 | BTCUSDT | 62,926.01 | 2026-07-10 02:34 | 64,692.83 | 2026-07-10 15:52 | 1,766.82 | 2.807774% |
| DAY_1_2 | ETHUSDT | 1,728.95 | 2026-07-06 15:38 | 1,833.40 | 2026-07-06 23:10 | 104.45 | 6.041239% |
| DAY_2_3 | ETHUSDT | 1,713.44 | 2026-07-08 17:17 | 1,816.82 | 2026-07-07 00:04 | 103.38 | 6.033477% |
| DAY_3_4 | ETHUSDT | 1,713.44 | 2026-07-08 17:17 | 1,785.00 | 2026-07-08 02:44 | 71.56 | 4.176394% |
| DAY_4_5 | ETHUSDT | 1,721.93 | 2026-07-09 05:19 | 1,812.00 | 2026-07-10 15:52 | 90.07 | 5.230759% |
| DAY_5_7 | ETHUSDT | 1,737.68 | 2026-07-10 02:34 | 1,830.00 | 2026-07-11 19:40 | 92.32 | 5.312831% |

These rows are eligible as exact source-backed outcome windows. Scoring still requires a readable frozen forecast row with matching source convention and horizon.

---

## Direct ETH/BTC appendix

| Date CEST | Low | High | Close |
|---|---:|---:|---:|
| 2026-07-06 | 0.02802000 | 0.02837000 | 0.02815000 |
| 2026-07-07 | 0.02792000 | 0.02822000 | 0.02797000 |
| 2026-07-08 | 0.02779000 | 0.02812000 | 0.02795000 |
| 2026-07-09 | 0.02759000 | 0.02804000 | 0.02763000 |
| 2026-07-10 | 0.02758000 | 0.02811000 | 0.02803000 |
| 2026-07-11 | 0.02793000 | 0.02842000 | 0.02835000 |
| 2026-07-12 | 0.02793000 | 0.02843000 | 0.02835000 |

```yaml
weekly_low: 0.02758000
weekly_high: 0.02843000
weekly_close: 0.02835000
source: DIRECT_ETHBTC_SOURCE_BINANCE_SPOT
```

---

## Independent cross-check against archived Yahoo W28 values

| Asset | Field | Binance primary | Yahoo secondary | Absolute difference | Difference % | Status |
|---|---|---:|---:|---:|---:|---|
| BTC | Weekly high | 64,700.00 | 64,658.97 | 41.03 | 0.063456% | OK |
| BTC | Weekly low | 61,306.84 | 61,275.83 | 31.01 | 0.050607% | OK |
| ETH | Weekly high | 1,833.40 | 1,829.51 | 3.89 | 0.212625% | OK |
| ETH | Weekly low | 1,713.44 | 1,711.90 | 1.54 | 0.089959% | OK |

No values are averaged. Binance CEST is the primary convention for exact calibration; Yahoo remains an independent secondary check.

---

## Canonical use rule

```text
PRIMARY_ACTUAL_CONVENTION_FOR_W28_EXACT_SCORING: BINANCE_SPOT_USDT_CEST_RESAMPLED
YAHOO_W28_ROW: SECONDARY_CROSSCHECK_ONLY
GROK_RANGE_AUDIT: SUPERSEDED_FOR_EXACT_SCORING
USE_FOR_RAW_CALIBRATION: YES
USE_FOR_CYCLE_NAVIGATOR_CALIBRATION: YES
USE_FOR_MASTER_MONDAY: YES
USE_FOR_SUNDAY_CLOSEOUT: YES
PROVIDER_MIXING_WITHIN_ONE_SCORE: FORBIDDEN
FORECAST_LEDGER_REQUIRED_FOR_ACCURACY_CLAIM: YES
```
