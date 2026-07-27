# F1 death-zone experiment — interim status

```yaml
experiment_id: F1_DEATH_ZONE
observed_at_utc: 2026-07-27T05:39:20Z
window_end_utc: 2026-07-28T00:00:00Z
maturity_status: NOT_MATURED
final_score: WITHHELD
current_directional_status: NO_FAILURE_OBSERVED_TO_DATE
threshold_attribution: OPEN_62200_VS_62342
canonical_state_change: NONE
portfolio_action: NONE
```

## Evidence supplied to date

```yaml
lowest_settled_close: 64139.99
lowest_intraday_low: 63739.75
buffer_vs_62200_settled_close_pct: 3.12
buffer_vs_62200_intraday_low_pct: 2.48
```

Neither candidate threshold has been breached in the evidence received so far. The result is currently invariant to the unresolved 62,200 versus 62,342 threshold attribution.

## Governance decision

The remaining observation window is material. Therefore:

```yaml
NOT_FAILED_final_score_now: REJECTED_AS_PREMATURE
allowed_interim_label: NO_FAILURE_OBSERVED_TO_DATE
final_adjudication_required_after: 2026-07-28T00:00:00Z
```

The final F1 result must be issued only after the full window closes and the final settled observations are available. Threshold provenance should still be repaired even if the eventual outcome remains invariant.
