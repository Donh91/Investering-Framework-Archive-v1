# F1 death-zone experiment — final adjudication

```yaml
experiment_id: F1_DEATH_ZONE
maturity_status: MATURED_CLOSED
window_start: 2026-07-21
window_end_utc: 2026-07-28T00:00:00Z
primary_directional_score: NOT_FAILED
threshold_attribution: OPEN_62200_VS_62342
result_invariant_across_threshold_candidates: YES
canonical_state_change: NONE
portfolio_action: NONE
```

## Final evidence

```yaml
settled_sessions: 7_of_7
closes_below_62200: 0
closes_below_62342: 0
lowest_settled_close: 63755.86
lowest_intraday_low: 63605.56
minimum_close_buffer_vs_62200_pct: 2.50
minimum_close_buffer_vs_62342_pct: 2.27
minimum_intraday_buffer_vs_62200_pct: 2.26
```

## Adjudication

The preregistered window closed without a settled failure under either candidate threshold. The directional result is therefore `NOT_FAILED`.

The unresolved provenance and attribution of 62,200 versus 62,342 remains a documentation defect, but it does not alter this result.

## Critical framing boundary

BTC subsequently traded below every intraday low observed inside the F1 window. This occurred after the window closed.

Both statements are true:

1. F1 did not fail inside its preregistered window.
2. BTC weakened further after the window.

The first statement must not be interpreted as a claim that downside risk ended or that the market recovered.

## Lifecycle

```yaml
ledger_status: CLOSED
reopen_allowed: NO
retrigger_allowed: NO_WITHOUT_NEW_PREREGISTERED_EXPERIMENT
framework_authority: NONE
```
