# H7 Lifecycle Governance Decision v1

```yaml
decision_date_local: 2026-08-07
triggering_observation: H7_ROW_16_JOINT_CONDITION_REQUALIFICATION
applies_to: H7_transmission_challenger
historical_rule_version: v1
```

## Decision

H7's original preregistered rule defined satisfaction conditions but did not define lapse, retirement or retrigger semantics.

Therefore:

1. The historical first satisfaction remains the sole scored H7 signal event.
2. Any later recurrence of the same conditions is retained as prospective follow-through evidence.
3. A later recurrence must not be labeled a new trigger, retrigger or new score event when retrigger semantics were absent from preregistration.
4. Missing lifecycle semantics fail closed; they are never invented after an outcome is observed.
5. This decision does not change H7's original conditions, historical score or outcome.
6. Future experiment versions may allow repeated signals only when lapse, reset, minimum separation and retrigger rules are preregistered before row 1.

Current row-16 classification:

```yaml
joint_conditions_satisfied: true
classification: JOINT_CONDITION_REQUALIFICATION_FOLLOW_THROUGH
new_signal_event: false
retrigger_event: false
historical_score_change: none
rotation_permission: closed
```

## Future-design note

The Claude CE-01/CE-02 null-frequency and possible BTC-volatility-confound observations are preserved as design backlog only. They may inform a future H8 or H7-v2 preregistration but may not be tested on the current arc and then used to rescore H7.

Principle: lifecycle semantics belong to experiment design, not outcome interpretation.
