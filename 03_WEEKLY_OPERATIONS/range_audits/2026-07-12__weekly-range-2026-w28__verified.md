# Weekly Actual Range — 2026-W28

**Run ID:** `WEEKLY_RANGE_2026_28_20260712_2210`  
**Period:** 2026-07-06 through 2026-07-12  
**Fetch time:** 2026-07-12 22:10 CEST  
**Status:** `VERIFIED_ACTUAL_RANGE`  
**Verification role:** `USER_VERIFIED`  
**Source convention:** `YAHOO_FINANCE_DAILY_OHLC`  
**Source note:** User states consistency with CoinGecko ranges. Values are retained under their explicit source convention and must not be silently merged with Binance CEST candles.

---

## Verified weekly actuals

```yaml
week: 2026-W28
period_start: 2026-07-06
period_end: 2026-07-12
btc_high: 64658.97
btc_low: 61275.83
eth_high: 1829.51
eth_low: 1711.90
price_source: USER_VERIFIED
source_provider: YAHOO_FINANCE
source_convention: DAILY_OHLC
fetch_time_cet: 2026-07-12T22:10:00+02:00
use_for_precision: true
use_for_master_monday: true
use_for_sunday_closeout: true
use_for_cycle_navigator: true
```

### Derived weekly widths

```text
BTC width: 3,383.14 USD
BTC width relative to weekly low: 5.5205%

ETH width: 117.61 USD
ETH width relative to weekly low: 6.8701%
```

---

## User-verified overlapping intraday blocks

These blocks are based on daily OHLC windows. They are suitable for coarse containment scoring, not exact intraday sequence reconstruction.

| Block | Dates | BTC high | BTC low | ETH high | ETH low | Status |
|---|---|---:|---:|---:|---:|---|
| DAY_1_2 | 2026-07-06 to 2026-07-07 | 64,597.57 | 61,275.83 | 1,829.51 | 1,728.97 | USER_VERIFIED |
| DAY_2_3 | 2026-07-07 to 2026-07-08 | 64,257.63 | 61,492.65 | 1,810.33 | 1,711.90 | USER_VERIFIED |
| DAY_3_4 | 2026-07-08 to 2026-07-09 | 63,706.89 | 61,492.65 | 1,782.86 | 1,721.30 | USER_VERIFIED |
| DAY_4_5 | 2026-07-09 to 2026-07-10 | 64,458.97 | 61,645.75 | 1,809.76 | 1,721.30 | USER_VERIFIED_APPROXIMATE_BTC_HIGH |
| DAY_5_7 | 2026-07-10 to 2026-07-12 | 64,658.97 | 62,902.06 | 1,827.83 | 1,736.72 | USER_VERIFIED |

### Intraday scoring restriction

```text
DAY_4_5_BTC_HIGH_EXACT_SCORING: EXCLUDED_PENDING_EXACT_SOURCE_ROW
OTHER_BLOCKS: ELIGIBLE_FOR_COARSE_CONTAINMENT_ONLY
SEQUENCE_SCORING: NOT_SUPPORTED_BY_DAILY_OHLC
```

---

## Cross-source convention note

The supplied Yahoo daily-OHLC weekly values differ slightly from the Binance CEST week-tracking values observed in DATA PING. This is expected because providers and candle boundaries differ.

```text
Yahoo BTC high:   64,658.97
Binance CEST high observed in DATA PING: 64,700.00
Difference: -41.03 USD / -0.0634%

Yahoo BTC low:    61,275.83
Binance CEST low observed in DATA PING: 61,306.84
Difference: -31.01 USD / -0.0506%

Yahoo ETH high:   1,829.51
Binance CEST high observed in DATA PING: 1,833.40
Difference: -3.89 USD / -0.2122%

Yahoo ETH low:    1,711.90
Binance CEST low observed in DATA PING: 1,713.44
Difference: -1.54 USD / -0.0899%
```

These are small source-convention differences, not evidence of an integrity failure. Precision scoring must use one frozen actual convention per scored forecast row.

---

## Narrative assessment governance

The source audit adds the following narrative:

- volatility was moderate;
- the weekly low arrived early;
- price rebounded and stabilized higher;
- daily ranges generally compressed toward the weekend;
- this may indicate accumulation before a larger move.

Framework treatment:

```text
EARLY_WEEK_LOW_AND_REBOUND: DESCRIPTIVE / ACCEPTED
LATE_WEEK_RANGE_COMPRESSION: DESCRIPTIVE / ACCEPTED
LOWER_THAN_EARLIER_2026_VOLATILITY: NOT_VERIFIED_BY_THIS_ROW
ACCUMULATION_BEFORE_NEXT_MOVE: HYPOTHESIS_ONLY
DIRECTIONAL_IMPLICATION_FROM_COMPRESSION: NONE
```

Compression can precede expansion in either direction. The verified values may score frozen forecasts, while the narrative must not be promoted into a directional rule.

---

## Precision rule

```text
ACTUAL_RANGE_VERIFIED does not equal forecast accuracy unless the prior forecast ledger is loaded.
If the forecast row is missing, mark FORECAST_LEDGER_MISSING and RANGE_SCORE_PARTIAL.
Do not score approximate DAY_4_5 BTC high as an exact hit/miss.
Do not mix Yahoo daily-OHLC actuals with Binance CEST actuals inside one score.
```
