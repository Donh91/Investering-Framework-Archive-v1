# TechDev Claim and Revision Ledger

**Dato:** 2026-07-10  
**Status:** OPERATIONAL_APPEND_ONLY / SOURCE_IMPORT_PENDING  
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
rows_total: 0_SOURCE_BACKED_ROWS
valid_rows: 0
source_import_status: PENDING_ORIGINAL_ISSUE_EXTRACTION
scoring_status: BLOCKED_UNTIL_ORIGINAL_SOURCE_LINKED
```

The fresh-eyes audit identified claims from Issues #92, #94 and #95, but this file does not convert audit summaries into scorable rows.

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
source_rows_imported:
roadmap_rows_scored:
timing_rows_scored:
range_rows_scored:
trade_rows_scored:
revisions_logged:
framework_actions_influenced:
calibration_change_recommended:
```
