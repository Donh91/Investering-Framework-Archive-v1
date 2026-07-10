# TechDev Claim and Revision Ledger

**Dato:** 2026-07-10  
**Status:** OPERATIONAL_APPEND_ONLY / SOURCE_SEQUENCE_COMPLETE  
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
issues_imported: 15
issues_missing: []
source_backed_claim_rows: 72
historical_topping_signal_snapshot_rows: 7
valid_source_rows: 72_UNSCORED
valid_outcome_rows: 0
scored_rows: 0
source_import_status: COMPLETE
scoring_status: BLOCKED_PENDING_VERIFIED_ACTUALS_AND_FROZEN_OUTCOME_METHOD
```

Primary source-backed extractions:

```text
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claims-issues-81-95__source-backed-extraction-v0-1.md
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claims-issues-87-88-90__source-backed-addendum-v0-2.md
```

Source manifests:

```text
08_SOURCE_MATERIAL/techdev/2026-07-10__techdev-issues-81-95__source-manifest.md
08_SOURCE_MATERIAL/techdev/2026-07-10__techdev-topping-signals-updates-1-8__source-manifest.md
```

Historical calibration sequence:

```text
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-topping-signals-updates-1-8__historical-extraction-v0-1.md
```

Issue #90 now directly anchors the original BITI and ETHD setups. Later issues preserve their outcome/re-entry reports without replacing the original setup.

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

LATER_ISSUE_DESCRIPTION_OF_ORIGINAL:
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

## Historical topping-signal boundary

The 2024 Topping Signals sequence is preserved as historical calibration, not active doctrine.

```text
MECHANICAL_SIGNAL_STATUS and ANALYST_OVERRIDE must remain separate.
A discretionary trigger call may not be represented as a threshold hit.
A later downgrade to UNCERTAIN may not erase the earlier call.
No current framework weight changes before a separate outcome pass.
```

---

## Weekly summary

```yaml
source_rows_imported: 72
source_issues_imported: 15
source_issues_missing: 0
historical_signal_snapshot_rows: 7
roadmap_rows_scored: 0
timing_rows_scored: 0
range_rows_scored: 0
trade_rows_scored: 0
revisions_logged: SOURCE_CHAINS_FROZEN
framework_actions_influenced: NOT_BACKFILLED
calibration_change_recommended: NONE_BEFORE_OUTCOME_PASS
```

## Next review

1. Freeze verified actual-data methodology before scoring.
2. Score roadmap, timing, range and trades separately.
3. Preserve original claims next to all later revisions.
4. Import Topping Signals Update #5 if supplied.
5. Prefer original indicator-definition sources before evaluating the 2024 signal sequence.
6. Do not alter TechDev's framework weight from source extraction alone.
