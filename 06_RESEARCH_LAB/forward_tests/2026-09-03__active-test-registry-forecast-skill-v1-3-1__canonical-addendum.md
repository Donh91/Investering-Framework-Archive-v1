# Active Test Registry — Forecast Skill Confirmatory v1.3.1 Addendum

**Date:** 2026-09-03  
**Status:** CANONICAL_ADDENDUM_PENDING_MERGE  
**Parent registry:** `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`  
**Owner contract:** `06_RESEARCH_LAB/forward_tests/forecast_skill_preregistration/FORECAST_SKILL_PREREGISTRATION_v1_3_1.json`  
**Source-method binding:** `06_RESEARCH_LAB/forward_tests/forecast_skill_preregistration/FORECAST_SKILL_PREREGISTRATION_v1_3_SOURCE_BINDING.json`

## T13 — API-Agent Forecast Skill Confirmatory v1.3.1

```yaml
test_id: FORECAST_SKILL_CONFIRMATORY_V1_3_1
status: REGISTERED_NOT_STARTED_SCIENTIFIC_FIREWALL
question: Does the prospectively owner-ratified API-agent F1 directional forecast population contain positive predictive information relative to the frozen B1_CLIMATOLOGY baseline under the preregistered dependent-data inference procedure?
canonical_exception: EXISTING_FORECAST_ACCOUNTABILITY_OWNER_CONFIRMATORY_PREREGISTRATION_2026_09_03
new_market_engine_created: false
new_market_signal_created: false
start: DETERMINISTIC_COHORT_ACTIVATION_RECEIPT_AFTER_IMPLEMENTATION_MERGE
prior_rows_status: PRE_ACTIVATION_INELIGIBLE_FOR_T13
primary_evidence_class: API_AGENT_OWNER_RATIFIED_PROSPECTIVE_v1
primary_forecast_family: F1_DIRECTIONAL_ONLY
required_fields:
  - forecast_id
  - candidate_id
  - evidence_class
  - frozen_at_utc
  - freeze_day_utc
  - horizon_days
  - outcome_due_utc
  - outcome_due_day_utc
  - direction
  - baseline_evidence_path
  - baseline_evidence_sha256
  - baseline_evidence_observed_at_utc
  - candidate_sha256
  - ratification_sha256
  - source_output_sha256
  - prompt_sha256
  - context_sha256
  - settlement_contract_version
  - study_admission_contract
  - study_admission_id
  - study_admitted_at_utc
  - preregistration_contract
  - preregistration_sha256
  - cohort_activation_receipt_sha256
  - outcome_blind_technical_revalidation_status
  - exact_due_outcome_binding
  - B1_climatology_probability
  - directional_hit
  - d_r
rows_total: 0_POST_ACTIVATION
valid_source_rows: 0
valid_outcome_rows: 0
benchmark: B1_CLIMATOLOGY
primary_time_index: OUTCOME_DUE_CALENDAR_DAY
freeze_accrual_window_days: 240
calendar_block_length_days: 28
confirmatory_inference: B_CALENDAR_BATCH_MEANS_T
alpha_one_sided: 0.025
min_admitted_F1_rows: 200
min_unique_outcome_due_days: 85
min_unique_freeze_days: 50
max_share_rows_on_any_outcome_due_day: 0.06
max_share_rows_in_any_28_calendar_day_block: 0.23
max_outcome_unavailable_share: 0.0
blocked_by:
  - STUDY_ADMISSION_LEDGER_v1_NOT_IMPLEMENTED_ON_MAIN
  - OUTCOME_BLIND_TECHNICAL_REVALIDATION_NOT_IMPLEMENTED_ON_MAIN
  - CONFIRMATORY_ANALYSIS_OWNER_NOT_IMPLEMENTED_ON_MAIN
  - COHORT_ACTIVATION_RECEIPT_NOT_FROZEN
next_review: AFTER_IMPLEMENTATION_MERGE_AND_ACTIVATION_READBACK
promotion_condition: No automatic promotion. A positive single confirmatory test may support at most the preregistered non-replicated prospective-edge vocabulary; REPLICATED_PROSPECTIVE_SKILL additionally requires the independent replication gate and separate governance review.
kill_condition: Fail closed on retrospective admission, pre-activation row inclusion, evidence-class mixing, outcome-aware admission/revalidation, baseline look-ahead, mutable freeze fields, non-exact settlement substitution, missing outcome in the confirmatory cohort, post-activation method/gate changes, or a second unregistered confirmatory test.
owner: FORECAST_ACCOUNTABILITY_RESEARCH_GOVERNANCE
preregistration_owner: 06_RESEARCH_LAB/forward_tests/forecast_skill_preregistration/FORECAST_SKILL_PREREGISTRATION_v1_3_1.json
study_admission_ledger_owner: research/api_agent/forecast_skill/STUDY_ADMISSION_LEDGER_v1
validator_path: scripts/learning/validate_forecast_skill_study_admission.py
confirmatory_analysis_path: scripts/learning/run_forecast_skill_confirmatory_test.py
authority: RESEARCH_ONLY_NO_PORTFOLIO_NO_MODEL_WEIGHT_NO_AUTOMATIC_PROMOTION
```

## Cohort activation rule

T13 does not start merely because this registration is merged.

The first cohort may activate only after all implementation prerequisites in the preregistration exist on current `main`, required CI is green, and exact remote readback is verified.

The activation receipt must then freeze:

```text
COHORT_START_UTC = first 00:00:00Z strictly after implementation-readback completion
COHORT_END_UTC_EXCLUSIVE = COHORT_START_UTC + 240 calendar days
```

The window is prospective and fixed before any T13 row is admitted. It may not be rolled or extended after outcomes are observed.

## Scientific firewall

```text
FORECAST SKILL = UNPROVEN
ENGINEERING / PRODUCTION PASS != PREDICTIVE SKILL
PRE-ACTIVATION PENDING OR FROZEN FORECASTS != T13 EVIDENCE
HISTORICAL REPLAY != T13 EVIDENCE
AUTOMATED_SCIENTIFIC_EXPERIMENT != T13 EVIDENCE
MISSING OUTCOME != MISS AND != DROPPED ROW; ANY MISSING OUTCOME BLOCKS THE CONFIRMATORY TEST
```

The existing forecast-accountability infrastructure may continue to materialize, quarantine, expire and observe candidates. T13 admission authority remains OFF until the implementation firewall is satisfied.
