# T10 - TechDev Claim Calibration / Existing Learning Reconciliation

**State:** FINDING_FROZEN
**Existing owner:** T7 `TECHDEV_CLAIM_LEDGER`

## Current evidence

The operational T7 ledger still reports 186 source-backed claim rows, zero valid outcome rows and scoring blocked pending verified actuals/method freeze.

However, a later canonical research artifact (`2026-07-13__techdev-category-outcome-calibration-and-b1-reconciliation-v1__canonical.md`) documents a materially newer state:

- 213 unique TechDev source documents;
- 257 source-backed claim rows in corpus;
- 50 high-decision-value anchor rows evaluated;
- 44 outcome-eligible anchor rows;
- category-specific calibration conclusions;
- machine-readable outcome/category/revision-cost files under `06_RESEARCH_LAB/audit_summaries/techdev_calibration_v1/`.

The category calibration explicitly separates roadmap, timing, price/range, conditional gates, trade, revision and framework-action impact and preserves revision cost. It does not grant standalone execution authority.

## Frozen finding

`TECHDEV_T7_NAVIGATION_STATE_STALE_RELATIVE_TO_CANONICAL_CALIBRATION`

The improvement need is reconciliation/discoverability, not a new scoring model.

## Required improvement

Reconcile the current T7 navigation/runtime summary with the later canonical category calibration and machine-readable owners so repository-aware agents do not incorrectly conclude that TechDev has zero outcome calibration.

The reconciled view must distinguish:

- full source corpus size;
- source rows versus the predeclared anchor cohort;
- outcome-eligible versus actually evaluated/scored-by-category rows;
- first-call information versus revision information/cost;
- category verdicts separately;
- blocked/non-evaluable trade or framework-impact rows;
- historical calibration versus future prospective claims.

It must not claim the 44 outcome-eligible anchors equal exhaustive scoring of all 257 source rows.

## Current durable learning to preserve

- macro compass: retain as context;
- exact timing: weak and revision-dependent;
- long-range price targets: not supported in the anchor cohort;
- near-term conditional gates: mixed to useful;
- revision value is real but revision cost is material;
- standalone execution authority remains zero.

## Acceptance

Positive: T7 navigation resolves to the newer canonical calibration and exact machine owners while preserving old source-ledger history.

Negative: old 186-row status is not silently deleted; anchor calibration is not marketed as full-corpus exhaustive score; no TechDev weight or portfolio action changes automatically.
