# Weekly Range Audit - 2026-W27 VERIFIED

**Dato:** 2026-07-05  
**Status:** VERIFIED_ACTUAL_RANGE  
**Run ID:** WEEKLY_RANGE_2026_27_20260705_2010  
**Week:** 2026-W27  
**Period:** 2026-06-29 to 2026-07-05  
**Source:** USER VERIFIED, CoinGecko 7d Range data / CoinGecko-Yahoo OHLC  
**Fetch time CET:** 2026-07-05 22:10 approx.  
**Use for Precision Score:** YES  
**Use for Master Monday:** YES  
**Use for Weekly RAW Learning Snapshot:** YES  
**Use for Cycle Navigator calibration:** YES

---

## Final weekly actual range

```yaml
BTC_HIGH: 63403.77
BTC_LOW: 57778.72
ETH_HIGH: 1802.38
ETH_LOW: 1549.83
```

Calculated range width:

```yaml
BTC_RANGE_USD: 5625.05
BTC_RANGE_FROM_LOW_PERCENT: 9.74
ETH_RANGE_USD: 252.55
ETH_RANGE_FROM_LOW_PERCENT: 16.30
```

---

## Intraday actual ranges

```yaml
DAY_1_2:
  period: 2026-06-29 to 2026-06-30
  BTC_HIGH: 60682.34
  BTC_LOW: 58111.67
  ETH_HIGH: 1633.65
  ETH_LOW: 1549.25

DAY_2_3:
  period: 2026-06-30 to 2026-07-01
  BTC_HIGH: 61223.77
  BTC_HIGH_STATUS: approx_from_intraday
  BTC_LOW: 58562.45
  ETH_HIGH: 1642.45
  ETH_LOW: 1549.25
  ETH_LOW_STATUS: carryover_low

DAY_3_4:
  period: 2026-07-01 to 2026-07-02
  BTC_HIGH: 61500+
  BTC_HIGH_STATUS: approximate_rising
  BTC_LOW: 58550
  BTC_LOW_STATUS: approximate
  ETH_HIGH: 1730
  ETH_HIGH_STATUS: approximate
  ETH_LOW: 1600
  ETH_LOW_STATUS: approximate

DAY_4_5:
  period: 2026-07-02 to 2026-07-03
  BTC_HIGH: 62879.01
  BTC_LOW: 61176.72
  ETH_HIGH: 1772.54
  ETH_HIGH_STATUS: approximate
  ETH_LOW: 1690
  ETH_LOW_STATUS: approximate

DAY_5_7:
  period: 2026-07-03 to 2026-07-05
  BTC_HIGH: 63403.77
  BTC_LOW: 62468.13
  ETH_HIGH: 1802.38
  ETH_LOW: 1750.45
```

---

## Volatility and structure read

Ugen viste moderat til høj volatilitet med klar recovery mod slutningen af perioden.

BTC bevægede sig fra ca. 57.8K til 63.4K. ETH bevægede sig fra ca. 1,550 til 1,802 og viste højere beta end BTC.

Framework interpretation:

```text
Post-flush recovery attempt survived.
Weekend repair was real.
Range expansion occurred from weekly low into weekend high.
This validates de-escalation candidate.
It does not by itself confirm recovery, rotation or rebuy.
```

---

## Precision classification

```yaml
price_source: USER_VERIFIED
actual_range_status: VERIFIED
range_scoring_allowed: YES
forecast_scoring_status: PARTIAL_UNTIL_PRIOR_FORECAST_LEDGER_FOUND
```

Important distinction:

```text
If the actual range exists but the previous forecast ledger is missing, the correct status is:
ACTUAL_RANGE_VERIFIED + FORECAST_LEDGER_MISSING + RANGE_SCORE_PARTIAL.

Do not mark this as PRICE_UNVERIFIED.
```

---

## Archive role

This file is the canonical verified actual range ledger for 2026-W27.

It must be loaded before Master Monday, Weekly RAW Learning Snapshot, Forecast Ledger evaluation, Cycle Navigator calibration and Precision Score scoring.
