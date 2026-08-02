# Claude OTA velocity flag — framework reconciliation

## Acceptance

```yaml
source_run_timestamp_utc: 2026-08-01T19:20:42.768Z
run_type: VELOCITY_FLAG_NOT_FULL_RUN
main_framework_acceptance: NONCANONICAL_INTRADAY_DESIGN_AND_SOURCE_QA_EVIDENCE
matured_experiment_count: 0
canonical_state_change: NONE
portfolio_action_change: NONE
```

## F1 boundary stress

```yaml
F1_window_closed: YES
F1_window_end_utc: 2026-07-28T00:00:00Z
F1_rule_basis: SETTLED_CLOSES
current_session_status: IN_PROGRESS
intraday_low: 62275.00
higher_candidate: 62342
higher_candidate_relation: BELOW_BY_0_11_PERCENT
lower_candidate: 62200
lower_candidate_relation: ABOVE_BY_0_12_PERCENT
F1_historical_score: NOT_FAILED
F1_score_change: NONE
```

The intraday low is accepted as post-window boundary-stress evidence only. It cannot rescore F1 because the scoring window is closed and the rule measured settled closes. The source claim that price moved below both candidates is corrected: 62,275 was below 62,342 but remained above 62,200.

## H-WIN-01

```yaml
status: UNPROVEN_DESIGN_HYPOTHESIS
confidence: LOW_MODERATE
confidence_change: NONE
framework_authority: NONE
```

The deliberate decision not to raise confidence is accepted. Repeated intraday extremes without settled confirmation are not sufficient evidence. The preregistered multi-window falsification path remains the only formal resolution route.

## ETHBTC and H7

```yaml
ETHBTC_session: 2026-08-01_UTC_IN_PROGRESS
running_value_supplied: 0.02938
intraday_low_supplied: 0.02923
intraday_high_supplied: 0.02974
touched_0_0300: NO_REPORTED
settled_threshold_status: NOT_AVAILABLE
H7_row_11: NOT_FORMED
H7_score_change: NONE
post_maturity_follow_through: INACTIVE_CONFIRMED_UNCHANGED
```

The in-progress ETHBTC weakness is directionally adverse and consistent with the already inactive post-maturity transmission diagnostic. It is not a settled row and cannot update H7 conditions, threshold persistence or the historical score.

## Source QA

The Coinbase HTTP 503 is recorded as an isolated venue failure. With three of four venues reachable and no repeated Coinbase-specific history established, no venue-reliability hypothesis is created.

## Framework effect

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
new_policy_event: NO
new_A_class_receipt: NO
A_rows_total: 2
new_shadow_dual_run: NO
shadow_dual_run_valid_runs: 5
canonical_state_change: NONE
portfolio_action_change: NONE
```

This velocity flag adds useful point-in-time stress evidence but does not supersede the latest DATA PING. The current operational class remains WAIT_FOR_BETTER_WINDOW pending settled and full-sensor evidence.
