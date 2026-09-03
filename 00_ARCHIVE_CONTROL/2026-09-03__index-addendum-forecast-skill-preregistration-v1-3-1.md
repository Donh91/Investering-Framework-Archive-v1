# Index Addendum — Forecast Skill Preregistration v1.3.1

**Date:** 2026-09-03  
**Status:** CANONICAL_INDEX_ADDENDUM_PENDING_MERGE  
**Domain:** Research Lab / forecast accountability / prospective evidence / scientific governance  
**Parent index:** `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`

## Purpose

Route repository-aware agents to the current forecast-skill confirmatory preregistration without changing the high-impact canonical index directly.

## Current owner

```text
06_RESEARCH_LAB/forward_tests/forecast_skill_preregistration/FORECAST_SKILL_PREREGISTRATION_v1_3_1.json
06_RESEARCH_LAB/forward_tests/forecast_skill_preregistration/FORECAST_SKILL_PREREGISTRATION_v1_3_1.md
06_RESEARCH_LAB/forward_tests/forecast_skill_preregistration/FORECAST_SKILL_PREREGISTRATION_v1_3_SOURCE_BINDING.json
06_RESEARCH_LAB/forward_tests/2026-09-03__active-test-registry-forecast-skill-v1-3-1__canonical-addendum.md
```

## Binding status

```text
FORECAST_SKILL_CONFIRMATORY_V1_3_1: REGISTERED_NOT_STARTED_SCIENTIFIC_FIREWALL
FORECAST SKILL: UNPROVEN
PRIMARY EVIDENCE CLASS: API_AGENT_OWNER_RATIFIED_PROSPECTIVE_v1
PRIMARY FAMILY: F1_DIRECTIONAL_ONLY
SOURCE METHOD PACKAGE SHA-256: d4f3e8c0f27a40bbfac0af41ab57a9752586becd871307b2f18cb061f9a8ee8d
SELECTED INFERENCE: B_CALENDAR_BATCH_MEANS_T
FIXED FREEZE/ACCRUAL WINDOW: 240 UTC calendar days
PRIMARY TIME INDEX: OUTCOME_DUE_CALENDAR_DAY
CALENDAR BLOCK: 28 days
ALPHA: 0.025 one-sided
MAX CONFIRMATORY OUTCOME UNAVAILABLE SHARE: 0.0
```

## Overrules for v1.3 wording

V1.3 remains the immutable statistical evidence bundle, but these operational labels are superseded by v1.3.1:

1. `span_days=240` means a fixed 240-day freeze/accrual opportunity window, not exactly 240 days on the OUTCOME_DUE axis.
2. The confirmatory missingness cap is 0.0, not 0.10, because the selected t procedure was sealed-validated at zero missingness and missing-to-zero is not generally monotone-conservative for a studentized statistic.

No sealed simulation artifact is rewritten by these corrections.

## Activation firewall

No T13 confirmatory row may be admitted until current main contains and verifies:

```text
STUDY_ADMISSION_LEDGER_v1
OUTCOME_BLIND_TECHNICAL_REVALIDATION
B_CALENDAR_BATCH_MEANS_T confirmatory owner
fixed cohort activation receipt
```

The current production candidate/queue plumbing may continue while this firewall remains closed.

## Authority

This addendum creates no market signal, market state, threshold, model weight, portfolio action, automatic forecast ratification or automatic scientific promotion.
