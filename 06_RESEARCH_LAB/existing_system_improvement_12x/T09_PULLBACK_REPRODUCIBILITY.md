# T09 - Pullback Policy v0.2 Reproducibility / Guidance Containment

**State:** FINDING_FROZEN
**Existing owner:** Pullback Policy v0.2 governance correction / T4 event outcomes

## Current evidence

The canonical correction is explicit:

- `PULLBACK_POLICY_V0_2_STATUS: GUIDANCE_ONLY`
- `MECHANICAL_CLASSIFICATION_AUTHORITY: SUSPENDED_UNTIL_SPEC_COMPLETE`
- qualitative labels alone have no portfolio authority.

It also lists the exact fields required before a pullback label may be treated as mechanically derived and forbids inventing numeric bands.

No source-backed complete asset-specific bands / anchors / reset rules / hard-trigger specification was found in the current owner reviewed here.

## Frozen decision

`KEEP_GUIDANCE_ONLY_AND_HARDEN_CONTAINMENT`

This program will not manufacture a reproducible numeric policy from incomplete provenance.

## Required improvement

Add a static contract/consumer guard that verifies current active code/prompts do not use `Mild`, `Moderate`, `Large` or `Extreme` pullback labels as standalone mechanical inputs for:

- TRIM/REDUCE/EXIT;
- rebuy unlock/lock;
- recovery-failure classification;
- calibration hit/miss;
- automatic market-state promotion.

Where these words are used as descriptive text, the guard should allow them only when the relevant artifact preserves the guidance-only boundary or the full required reproducibility fields.

The guard is not a policy engine and creates no bands.

## Acceptance

Positive: descriptive/guidance-only usage passes; a fully specified future artifact may pass only when all required fields are explicit and owner-authorized.

Negative: a fixture that maps `Moderate` directly to `REDUCE` or uses a qualitative label as a calibration outcome fails.

## Exit condition

This track remains `GUIDANCE_CONTAINED` until a separate source-backed governance review freezes a complete reproducible specification. No urgency to invent one is implied.
