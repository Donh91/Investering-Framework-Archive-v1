# F1 post-window boundary stress — settled confirmation

```yaml
source_run: CLAUDE_OTA_2026_08_02T06_14_13Z
session_date_UTC: 2026-08-01
observation_type: POST_WINDOW_BOUNDARY_STRESS_SETTLED_CONFIRMATION
window_closed: YES
rule_basis: SETTLED_CLOSES
score_changed: NO
canonical_effect: NONE
portfolio_effect: NONE
```

## Settled session

```yaml
settled_close: 62823.64
intraday_low: 62275.00
higher_candidate: 62342
lower_candidate: 62200
close_above_higher_candidate_pct: 0.77
intraday_low_below_higher_candidate_pct: 0.11
intraday_low_above_lower_candidate_pct: 0.12
```

The session confirms the prior velocity flag: price passed below the higher candidate intraday but closed above both candidates.

## Experiment treatment

F1's scoring window closed on 2026-07-28 and evaluated settled closes. The historical result remains `NOT_FAILED`. No settled close has breached either candidate in the supplied in-window or post-window evidence.

## H-WIN-01 treatment

```yaml
status: UNPROVEN_DESIGN_HYPOTHESIS
source_confidence: LOW_MODERATE
confidence_change: NONE
framework_authority: NONE
formal_resolution_path: AUDIT_AT_LEAST_10_CLOSED_WINDOWS
```

The predeclared requirement for a settled close was not met, so the source's deliberate decision to leave confidence unchanged is accepted.
