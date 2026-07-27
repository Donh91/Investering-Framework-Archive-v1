# FORECAST SCORE — 2026-W30 — TRANSPARENT AUDIT

score_date: 2026-07-27
source_forecast: 03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-20__forecast-ledger-2026-w30__official.md
source_actuals: DP-W30-2026-BTCETH-20260727T054421819Z
status: OUTCOME_MATURED_TRANSPARENT_AUDIT
canonical_score_engine_created: NO
portfolio_authority: NONE

## Method

Range precision uses one explicit formula:

`range_coverage_pct = width(actual_interval ∩ forecast_interval) / width(actual_interval) × 100`

State calls are scored as binary HIT or MISS. The overall audit score is the unweighted mean of the four range-coverage values and four state-call values. This summary metric is transparent and non-binding; the individual outcome labels remain the authoritative record.

## Range outcomes

| Item | Frozen forecast | Settled actual | Coverage | Label |
|---|---:|---:|---:|---|
| BTC 1-3d | 62,700-65,700 | 63,100.00-66,956.15 | 67.42% | PARTIAL |
| ETH 1-3d | 1,780-1,935 | 1,843.14-1,956.45 | 81.07% | PARTIAL |
| BTC 5-7d | 61,900-66,800 | 63,100.00-66,956.15 | 95.95% | NEAR_FULL_PARTIAL |
| ETH 5-7d | 1,720-2,010 | 1,843.14-1,956.45 | 100.00% | HIT |

Range precision subscore: **86.11 / 100**.

## State outcomes

| Frozen call | Outcome | Score |
|---|---|---:|
| REPAIR_PRESENT_MATURING | Repair survived and weekly structure remained above the load-bearing BTC supports | 100 |
| NO_ROTATION | Correct. H7 reached candidate status only; no broad rotation permission | 100 |
| LARGE_CAP_WINDOW_WATCH_ONLY_NOT_OPEN | Correct. Breadth and flow confirmation remained insufficient | 100 |
| BTC_LED_STRUCTURAL_REPAIR | Leadership qualifier missed. ETH led the final transmission sequence and outperformed BTC | 0 |

State precision subscore: **75.00 / 100**.

## Transparent audit score

```yaml
range_precision: 86.11
state_precision: 75.00
overall_unweighted_audit_score: 80.56
rounded_precision_score: 81_of_100
classification: GOOD_WITH_LEADERSHIP_MISS
```

## Interpretation

The forecast was strong on the broad weekly envelope and excellent on ETH's 5-7 day range. BTC's weekly high exceeded the frozen upper bound by only 156.15 USDT. The main analytical miss was not direction or risk state, but leadership: the official BTC-led qualifier did not survive the week's ETH-relative acceleration.

No retrospective threshold, range or weight is changed after observing the outcome.