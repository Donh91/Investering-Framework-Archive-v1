# DATA PING top-up and buy-window rule activation receipt

```yaml
activated_at_utc: 2026-07-30T20:05:00Z
status: COMPLETE
user_decision: MAKE_PERMANENT_FOR_DATA_PING_PROCESSING
canonical_rule: governance/DATA_PING_TOP_UP_BUY_WINDOW_OUTPUT_RULE_v1_0.md
translation_layer: governance/OPERATIONAL_TRANSLATION_LAYER_v1_0.md
active_pointer: 02_DATA_PING/operational_handoffs/latest_user_facing_output_rules.json
future_thread_inheritance: REQUIRED
chat_memory_dependency: FORBIDDEN
market_state_change: NONE
portfolio_state_change: NONE
```

## Activated behavior

Every user-facing DATA PING reconciliation must end with one short, adaptive and unambiguous sentence beginning:

```text
**Top-up og købsvindue:**
```

The sentence must state a definite action, a reassessment horizon or trigger, and the decisive reason. It must remain consistent with canonical framework and portfolio locks.

## Scope

The behavior applies to accepted successors, bounded observations and partial runs. Pure duplicates or runs without usable new market evidence must use the fail-closed `NO_NEW_ASSESSMENT` formulation rather than inventing a new timing call.

## Governance effect

This is a user-facing output and accountability rule. It does not change market state, gates, rotation, rebuy, entry permission or portfolio action.
