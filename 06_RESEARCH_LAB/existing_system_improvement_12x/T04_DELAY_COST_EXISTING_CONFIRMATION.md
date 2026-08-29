# T04 - Delay Cost Across Existing Confirmation Layers

**State:** FINDING_FROZEN
**Existing owners:** T6 `ROTATION_SURVIVAL_FORWARD`; T8 `MULTI_PING_AGGREGATION_VALUE`

## Current evidence

T6 already has a governed CODEX_READY candidate for prospective rotation survival, time-in-state and delay-cost instrumentation. This program therefore does not create a duplicate T6 task.

T8 remains registered with:

- `status: QUEUED`
- `rows_total: 0`
- `blocked_by: ROW_INSTRUMENTATION`
- baseline: `LATEST_PING_ONLY`
- required fields including `latest_ping_state`, `aggregation_state`, `eventual_framework_state`, dependency/redundancy, `unique_information_gain`, false-flip reduction, `delay_minutes` and `delay_cost`.

The registry already states the correct governing question: does 3-4 ping aggregation reduce false flips enough to justify its delay, and does it add unique information rather than merely smoothing the latest ping?

## Frozen finding

`T8_MULTI_PING_DELAY_COST_ROW_INSTRUMENTATION_MISSING`

This is an existing-test instrumentation gap, not authorization for a new consensus layer. Multi-ping aggregation remains feature-only.

## Required improvement

Instrument prospective T8 rows from eligible current DATA PING states while preserving:

- exact latest-ping baseline at the time aggregation is formed;
- aggregation state and window membership;
- dependency to the latest ping;
- timestamped delay in minutes;
- later verified framework state when eligible;
- false-flip count/reduction and delay cost only after outcome eligibility;
- explicit missingness and right-censoring when no valid later adjudication exists.

No historical chat sequence may be reconstructed into pseudo-forward rows.

## Interpretation rule

T8 wins only if it improves false-flip behavior **after** delay cost and redundancy are counted. Agreement between several pings is not independent confirmation by itself.

## Acceptance

Positive: frozen prospective fixture shows latest-ping baseline and aggregation output with exact timing; later outcome attachment measures false-flip reduction and delay without rewriting the source row.

Negative: identical repeated packets create no artificial persistence; aggregation agreement cannot be labeled unique information without explicit incremental evidence; missing later framework state remains censored/pending rather than inferred.

## Dependency

T6 and T8 should share timing-accountability concepts where practical, but neither may become a new combined engine or blended score.
