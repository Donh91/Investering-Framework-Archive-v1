# T11 - Forecast Error Taxonomy and Consistent Failure-Mode Learning

**State:** FINDING_FROZEN
**Existing owners:** `MATURED_OUTCOME_v3`; Model Calibration Ledger; existing forecast accountability

## Current evidence

The canonical maturation/calibration path currently preserves robust frozen target semantics and outcome lineage, but the model calibration ledger primarily reduces eligible matured rows to:

- `HIT` / `MISS`;
- realized return;
- model/task/path/horizon identifiers;
- forecast/evidence hashes.

That is correct for mechanical target scoring but insufficient to explain *how* a forecast failed. Existing research and operational layers separately discuss timing, range, sequence, regime, false-positive/false-negative and action-translation errors, but those labels are not unified into one causally constrained learning sidecar.

## Frozen finding

`FORECAST_FAILURE_MODE_LEARNING_IS_FRAGMENTED_ACROSS_OWNERS`

The solution is not to replace HIT/MISS or create a new market score. It is to add a read-only error-classification sidecar only where the immutable forecast/outcome contract contains enough information.

## Existing-only taxonomy

The sidecar may use these explanatory dimensions when objectively evaluable from frozen fields and immutable outcome/path evidence:

- `TARGET_RESULT`: HIT / MISS / CENSORED;
- `DIRECTION`: CORRECT / WRONG / NOT_EVALUABLE;
- `MAGNITUDE`: SUFFICIENT / INSUFFICIENT / OVERSHOT / NOT_EVALUABLE;
- `TIMING`: EARLY / LATE / WITHIN_FROZEN_WINDOW / NOT_EVALUABLE only when a frozen timing window and path evidence actually exist;
- `SEQUENCE`: MATCH / MISMATCH / NOT_EVALUABLE only when sequence was frozen prospectively;
- `STATE_OR_PHASE`: MATCH / MISMATCH / NOT_EVALUABLE only for contracts that froze such a claim;
- `ACTION_TRANSLATION`: EVALUABLE / NOT_EVALUABLE, never inferred from market outcome when no frozen action semantics exist;
- `PRIMARY_FAILURE_CLASS`: one of the above causal dimensions or `MULTI_FACTOR / DATA_QUALITY / NOT_EVALUABLE`.

No dimension may be filled by hindsight narrative.

## Required improvement

Materialize immutable/read-only failure-analysis sidecars for newly matured eligible rows, or a deterministic report over existing rows where all required frozen fields already existed. Missing dimensions remain `NOT_EVALUABLE`.

The taxonomy must preserve the original HIT/MISS result and cannot alter scoring.

## Acceptance

Positive: a directional forecast that moved correctly but failed its required magnitude can be distinguished from a wrong-direction miss when frozen fields allow it.

Negative: no timing or sequence label is created unless the original forecast froze timing/sequence semantics; censored rows cannot be assigned an error class implying prediction failure; no score or market rule changes.

## Learning purpose

Use failure categories to target improvements to the correct owner rather than responding to every MISS with a broad model change.
