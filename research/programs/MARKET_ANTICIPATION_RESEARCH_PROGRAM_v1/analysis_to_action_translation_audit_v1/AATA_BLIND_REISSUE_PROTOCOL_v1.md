# AATA Blind Reissue Protocol v1

**Date:** 2026-07-31  
**Status:** PREREGISTERED / REISSUE_REQUIRED  
**Applies to:** Claude Stage 1B and Stage 1C only

## Problem being corrected

The initial Stage 1 package shipped AATA's own derived rows but no primary source documents. It therefore asked the auditor to reconstruct from the same file it was meant to test.

It also shipped a W30 owner-outcome block while declaring the package outcome-free.

## New unit of audit

The blind unit is one target forecast week, not an all-weeks bundle.

```text
AATA_STAGE1_W28
AATA_STAGE1_W29
AATA_STAGE1_W30
AATA_STAGE1_W31
```

A later weekly report may include the prior week's outcome. That does not contaminate the later target week's extraction, but the later report may never be supplied as a source for auditing the prior target week.

## Stage 1B: independent source extraction

For each target week, supply:

- the target week's exact primary Master Monday artifact when one exists;
- the target week's exact Forecast Ledger artifact;
- full-file SHA-256 and repository blob identity;
- AATA methodology and the applicable row schema;
- this protocol;
- no `SOURCE_ROWS` file;
- no expected decomposition;
- no ChatGPT labels;
- no owner outcome for the target week;
- no later weekly report.

Claude must independently extract analysis, price translation, action translation and temporal metadata.

Claude must return:

- byte manifest;
- independent extraction;
- source spans;
- ambiguities;
- signed extraction hash;
- statement that no later target-week outcome was used.

The extraction is frozen before Stage 1C.

## Stage 1C: parity reveal

Only after the Stage 1B extraction hash is archived, reveal:

- the corresponding expected AATA source row;
- its exact hash;
- no target-week outcome fields beyond null or pending status.

Claude compares its frozen extraction against the expected row.

It may add a discrepancy report, but it may not silently rewrite its Stage 1B extraction. Any amended extraction must preserve both old and new values and state why the primary source compelled the amendment.

## Source map

### W28

Primary source:

```text
03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-06__forecast-ledger-2026-w28__official.md
```

No later Master Monday may be used in Stage 1B for W28.

### W29

Primary sources:

```text
03_WEEKLY_OPERATIONS/master_monday/2026-W29/03_framework_ratified_final.md
03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-13__forecast-ledger-2026-w29__official.md
```

The W29 Master Monday contains W28 outcome context. This is permitted because W29 is the target and W28 is not being scored in this blind unit.

### W30

Primary sources:

```text
03_WEEKLY_OPERATIONS/master_monday/2026-W30/03_framework_ratified_final.md
03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-20__forecast-ledger-2026-w30__official.md
```

The W31 Master Monday is forbidden in W30 Stage 1B because it contains the W30 outcome.

### W31

Primary sources:

```text
03_WEEKLY_OPERATIONS/master_monday/2026-W31/03_framework_ratified_final.md
03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-27__forecast-ledger-2026-w31__official.md
```

The W31 Master Monday contains W30 outcome context. This is permitted because W31 is the target. W31 outcome fields remain absent and W31 must not be scored.

## Mixed score-and-forecast artifact rule

The archive is not rewritten retroactively.

For prospective AATA capture from W32 forward:

- source spans for prior-week scoring and new-week forecasting must be separately recorded;
- an auditor receives only the spans and files appropriate to the target week and audit stage;
- scoring and forecasting may coexist in one publication, but they must be separately addressable;
- no later report may be used to reconstruct an earlier forecast.

## Blindness checks

A Stage 1B package fails closed when any of the following is present:

- `SOURCE_ROWS` or expected extraction;
- target-week actual ranges or owner scores;
- later weekly reports;
- ChatGPT parity labels;
- action-utility labels;
- reconstructed missing timestamps;
- unverified source bytes.

## Completion rule

Stage 1 is not `PASS` until all of the following hold:

```yaml
stage_1A_byte_integrity: PASS
stage_1B_independent_extraction: PASS
stage_1B_extraction_hash_archived: PASS
stage_1C_expected_row_reveal_after_freeze: PASS
stage_1C_source_parity: PASS_OR_PASS_WITH_CORRECTIONS
stage_1D_method_red_team: PASS_OR_PASS_WITH_CORRECTIONS
```

`DATA_BLOCKED` is retained when source documents or source identity are missing.

## Authority boundary

No Stage 1 result may alter framework state, thresholds, entries, rebuy, deployment or portfolio action.
