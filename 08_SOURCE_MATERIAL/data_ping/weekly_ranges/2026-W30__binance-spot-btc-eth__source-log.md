# DATA PING settled weekly price ranges — W30 2026

```yaml
archive_id: DP-W30-2026-BTCETH-20260727T054421819Z
generated_at_utc: 2026-07-27T05:44:21.819Z
generated_at_cest: 2026-07-27T07:44:21.819+02:00
report_period_local: 2026-07-20T00:00:00+02:00/2026-07-26T23:59:59.999+02:00
source: BINANCE_SPOT
instruments:
  - BTCUSDT
  - ETHUSDT
timezone: Europe/Copenhagen
local_offset: UTC+02:00
week_status: FULLY_SETTLED
source_role: W30_FINAL_WEEK_RANGE_EVIDENCE
market_interpretation: NONE
precision_score_execution: NO
portfolio_action: NONE
```

## Weekly extrema

| Asset | Weekly low | Weekly high | Range |
|---|---:|---:|---:|
| BTC | 63,100.00 USDT | 66,956.15 USDT | 3,856.15 USDT |
| ETH | 1,843.14 USDT | 1,956.45 USDT | 113.31 USDT |

## Settled local-day ranges

| Local date | BTC low | BTC high | BTC width | ETH low | ETH high | ETH width |
|---|---:|---:|---:|---:|---:|---:|
| 2026-07-20 | 63,100.00 | 65,799.00 | 2,699.00 | 1,843.14 | 1,918.16 | 75.02 |
| 2026-07-21 | 65,092.66 | 66,956.15 | 1,863.49 | 1,894.40 | 1,953.00 | 58.60 |
| 2026-07-22 | 65,553.67 | 66,739.89 | 1,186.22 | 1,910.68 | 1,956.45 | 45.77 |
| 2026-07-23 | 64,650.00 | 66,313.14 | 1,663.14 | 1,869.44 | 1,941.50 | 72.06 |
| 2026-07-24 | 63,739.75 | 65,808.59 | 2,068.84 | 1,848.09 | 1,909.80 | 61.71 |
| 2026-07-25 | 63,810.00 | 64,475.28 | 665.28 | 1,851.22 | 1,877.07 | 25.85 |
| 2026-07-26 | 64,293.81 | 64,940.51 | 646.70 | 1,872.38 | 1,930.00 | 57.62 |

## Extrema lineage

```yaml
BTC_week_low:
  value: 63100.00
  local_date: 2026-07-20
BTC_week_high:
  value: 66956.15
  local_date: 2026-07-21
ETH_week_low:
  value: 1843.14
  local_date: 2026-07-20
ETH_week_high:
  value: 1956.45
  local_date: 2026-07-22
```

## Validation performed

- all seven Europe/Copenhagen local dates are present;
- every daily low is less than or equal to its daily high;
- the reported weekly lows equal the minimum daily lows;
- the reported weekly highs equal the maximum daily highs;
- all days are settled before package generation;
- no interpretation or forecast score is embedded.

## Relationship to earlier W30 package

The earlier OKX hourly W30 package was collected before the final Sunday session had completed and explicitly contained one incomplete bar. This Binance Spot report covers the complete local week through Sunday 23:59:59 CEST and is therefore the preferred source for **final W30 BTC/ETH price extrema**.

The earlier OKX package remains valuable for hourly replay, correlation and path analysis. The two sources must not be silently treated as one homogeneous venue series.
