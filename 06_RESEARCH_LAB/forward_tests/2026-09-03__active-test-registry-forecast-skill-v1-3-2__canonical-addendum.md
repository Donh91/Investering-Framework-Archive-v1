# Active Test Registry — Forecast Skill Confirmatory v1.3.2 Endpoint Amendment

**Date:** 2026-09-03  
**Status:** CANONICAL_PRE_ACTIVATION_AMENDMENT  
**Test ID:** `FORECAST_SKILL_CONFIRMATORY_V1_3_1`  
**Parent registration:** `06_RESEARCH_LAB/forward_tests/2026-09-03__active-test-registry-forecast-skill-v1-3-1__canonical-addendum.md`  
**Binding erratum:** `06_RESEARCH_LAB/forward_tests/forecast_skill_preregistration/FORECAST_SKILL_PREREGISTRATION_v1_3_2_ERRATUM.json`

This addendum does not create a new test. It corrects the endpoint semantics of T13 before activation so runtime exactly matches the sealed v1.3 implementation.

Effective T13 contract:

```text
FORECAST_SKILL_PREREGISTRATION_v1_3_1
+ FORECAST_SKILL_PREREGISTRATION_v1_3_2_ERRATUM
```

Binding correction:

```text
within each OUTCOME_DUE calendar day: a_k = mean(d_r)
primary Theta_hat: equal-weight mean of observed due-day means
row-weighted mean(d_r) across all rows: FORBIDDEN for confirmatory inference
```

All existing T13 gates, scientific firewall, 240-day fixed freeze/accrual window, zero confirmatory missingness tolerance, evidence-class separation and no-authority rules remain unchanged.

```text
T13 STATUS: REGISTERED_NOT_STARTED_SCIENTIFIC_FIREWALL
FORECAST SKILL: UNPROVEN
PRE-ACTIVATION ROWS: INELIGIBLE
```
