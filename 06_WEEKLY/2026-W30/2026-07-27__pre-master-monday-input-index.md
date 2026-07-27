# W30 pre-Master Monday input index

```yaml
week: 2026-W30
prepared_at_utc: 2026-07-27T05:44:21.819Z
master_monday_execution: NOT_RUN
precision_score_execution: NOT_RUN
backtest_execution: NOT_RUN
framework_state_change: NONE
portfolio_action: NONE
```

## Newly accepted inputs

### Final settled weekly BTC/ETH price ranges

```yaml
source: BINANCE_SPOT
basis: EUROPE_COPENHAGEN_LOCAL_DAYS
week_status: FULLY_SETTLED
BTC_range: 63100.00_to_66956.15
ETH_range: 1843.14_to_1956.45
owner_for_final_W30_extrema: BINANCE_SPOT_RANGE_REPORT
```

### H7 transmission-rate challenger

```yaml
maturity: COMPLETE_5_OF_5
score: EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION
mechanical_conditions: MET
interpretive_weight: LIMITED
rotation_effect: NONE
```

### F1 death-zone experiment

```yaml
maturity: PENDING_WINDOW_CLOSE
current_status: NO_FAILURE_OBSERVED_TO_DATE
final_score: WITHHELD
window_end_utc: 2026-07-28T00:00:00Z
```

### Source-QA

```yaml
incident: OTA23_GROUPBY_RUN_LENGTH_FALSE_BLOCK
severity: HIGH
caught_before_canonical_harm: YES
automated_H7_scoring_status: BLOCKED_UNTIL_PATCH
manual_current_H7_adjudication: COMPLETE
```

## Master Monday boundaries

- Use the final settled Binance Spot ranges for W30 weekly extrema.
- Preserve the earlier OKX hourly pack for path and replay analysis only.
- Do not reopen F4 from post-window ETH/BTC movement.
- Do not treat H7 as rotation confirmation.
- Do not finalize F1 before its window closes.
- Do not run Precision Score until the complete scheduled Master Monday evidence set is assembled.
