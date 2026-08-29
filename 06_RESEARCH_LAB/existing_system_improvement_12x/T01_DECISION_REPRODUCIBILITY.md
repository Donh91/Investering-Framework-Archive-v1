# T01 - Decision Reproducibility / T9 Controlled Replay

**State:** FINDING_FROZEN
**Existing owner:** `CHIEF_REPRODUCIBILITY` / T9
**Authority:** research and code-instrumentation only

## Current evidence

The Active Test Registry defines T9 as `QUEUED_RECEIPT_VALIDATOR_AVAILABLE`, with zero rows and `CONTROLLED_REPLAY_FIXTURES_NOT_CREATED` as its blocker. The Three-Horizon Action Compass v1.1 owner already provides an immutable receipt schema/writer/validator and explicitly binds T9 as the existing reproducibility owner.

At audit time, `research/framework_memory/action_compass_receipts/` does not exist on current main, so there is not yet a natural receipt population available for replay sampling. The absence of natural rows must not be solved through historical chat backfill; the Action Compass owner explicitly forbids it.

## Frozen finding

`T9_CONTROLLED_REPLAY_FIXTURE_AND_COMPARATOR_MISSING`

This is a bounded instrumentation gap, not a market-rule gap.

The framework cannot currently answer its registered T9 question mechanically:

> Does the same frozen framework input produce the same action class across repeated runs/models?

The receipt validator verifies a produced decision receipt, but no existing controlled replay harness freezes one eligible input packet and compares repeated decision outputs using exact machine fields plus explicitly allowed non-semantic variance.

## Minimal remediation

Implement a deterministic research-only replay fixture/comparator that:

1. accepts only explicitly prepared synthetic or post-activation eligible frozen fixture packets;
2. never turns real-world duplicates into new prospective decision rows;
3. compares machine-semantic fields separately from bounded wording/model metadata;
4. requires exact agreement for actions, Lane-3 state, warning, horizons/validity semantics and data-quality classification where the fixture fixes those fields;
5. reports semantic disagreement, metadata/wording variance and invalid output separately;
6. produces no market action, threshold, score promotion or canonical state;
7. can later consume natural post-activation receipt populations without reconstructing historical decisions.

## Positive acceptance

- Identical semantic decisions with allowed producer/interpretation metadata variance classify `SEMANTIC_MATCH`.
- A controlled fixture can be replayed N times without creating N prospective Action Compass receipts.

## Negative acceptance

- Any changed action, altcoin state or warning under the same frozen fixture is detected as semantic disagreement.
- Historical chat, mutable `LATEST` reconstruction or pre-activation evidence cannot be admitted as a valid prospective T9 row.
- Wording equality must never be required when machine semantics are equal.

## Post-fix gate

`CONTROLLED_REPLAY_FIXTURE_PASS + 10_ELIGIBLE_REPLAYS_BEFORE_ANY_REPRODUCIBILITY_CONCLUSION`

No conclusion about model reproducibility is authorized from schema tests alone.
