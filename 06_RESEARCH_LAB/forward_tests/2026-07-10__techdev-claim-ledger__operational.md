# TechDev Claim and Revision Ledger

**Dato:** 2026-07-10  
**Status:** OPERATIONAL_APPEND_ONLY / SOURCE_IMPORT_PARTIAL_COMPLETE  
**Område:** TechDev roadmap / timing / range / trade calibration  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Related folders:** `08_SOURCE_MATERIAL/techdev/`, `01_CORE_FRAMEWORK/governance/`  
**Depends on:** Active Test Registry; TechDev macro-compass governance

---

## Purpose

TechDev remains a macro compass and roadmap input, not an execution motor.

This ledger separates:

```text
ROADMAP_ACCURACY
TIMING_ACCURACY
RANGE_ACCURACY
TRADE_ACCURACY
FRAMEWORK_ACTION_IMPACT
```

These categories must never be blended into one score.

---

## Current status

```yaml
source_sequence: ISSUES_81_TO_95
issues_expected: 15
issues_imported: 12
issues_missing: [87, 88, 90]
source_backed_claim_rows: 55
valid_source_rows: 55_UNSCORED
valid_outcome_rows: 0
scored_rows: 0
source_import_status: PARTIAL_COMPLETE_MISSING_87_88_90
scoring_status: BLOCKED_PENDING_SEPARATE_OUTCOME_PASS
```

Primary source-backed extraction:

```text
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claims-issues-81-95__source-backed-extraction-v0-1.md
```

Source manifest:

```text
08_SOURCE_MATERIAL/techdev/2026-07-10__techdev-issues-81-95__source-manifest.md
```

Issue #90 is especially important because Issue #91 reports BITI/ETHD outcomes and revisions from trades introduced in #90. Those derivative reports are preserved, but original-entry scoring remains blocked until #90 is supplied.

---

## Required claim row

```yaml
claim_id:
issue_number:
issue_date:
source_path:
source_status:
asset:
claim_type:
  ROADMAP
  TIMING_WINDOW
  PRICE_RANGE
  TRADE
  TRADE_POLICY
  SECTOR
original_claim_verbatim_or_precise_paraphrase:
target_low:
target_high:
time_window_start:
time_window_end:
invalidation:
position_or_trade_if_any:
framework_action_impact_at_time:
revision_ids:
final_outcome:
timing_error_days:
range_error_pct:
trade_return_pct:
roadmap_result:
  SUPPORTED
  PARTIAL
  NOT_SUPPORTED
  NOT_EVALUABLE
scoring_eligibility:
notes:
```

---

## Revision rule

Original claims and later revisions must remain side by side.

```text
SILENT_REPLACEMENT_OF_ORIGINAL_CLAIM: FORBIDDEN
LATEST_REVISION_ERASES_PRIOR_ERROR: NO
```

A revised target may be useful, but it does not retroactively improve the original claim.

---

## Source-status rule

```text
SOURCE_BACKED_CLAIM:
  may_be_imported: YES
  may_be_scored_without_actuals: NO

LATER_ISSUE_DESCRIPTION_OF_MISSING_ORIGINAL:
  may_be_preserved: YES
  may_replace_original_source: NO
  scoring_status: BLOCKED_FOR_ORIGINAL_CLAIM_ACCURACY
```

---

## Weighting rule

```yaml
macro_readiness_weight: MEDIUM_HIGH
exact_timing_weight: MEDIUM_LOW
standalone_execution_weight: ZERO
rotation_authority: SHADOW_ONLY
sector_selection: WATCHLIST_INPUT
```

---

## Weekly summary

```yaml
source_rows_imported: 55
source_issues_imported: 12
source_issues_missing: 3
roadmap_rows_scored: 0
timing_rows_scored: 0
range_rows_scored: 0
trade_rows_scored: 0
revisions_logged: SOURCE_CHAINS_FROZEN
framework_actions_influenced: NOT_BACKFILLED
calibration_change_recommended: NONE_BEFORE_OUTCOME_PASS
```

## Next review

1. Import Issues #87, #88 and especially #90 if supplied.
2. Freeze verified actual-data methodology before scoring.
3. Score roadmap, timing, range and trades separately.
4. Preserve original claims next to all later revisions.
5. Do not alter TechDev's framework weight from this extraction alone.
