# Forecast Skill v1.3.2 Endpoint Erratum Receipt

Date: 2026-09-03

Finding: the accepted v1.3 sealed code computes the confirmatory point estimate as the equal-weight mean of observed OUTCOME_DUE calendar-day means, while v1.3.1 prose/JSON incorrectly described a row-weighted mean across forecast rows.

Evidence source: actual `FORECAST_SKILL_PREREGISTRATION_v1.3.zip`, especially `simulation/src/engine.py::day_aggregate, theta_hat` and `inference_bakeoff/candidates.py::batch_means_se, evaluate`.

Correction status: PRE_ACTIVATION. No T13 cohort activation receipt exists; no T13 row has been admitted; no T13 prospective outcome was used.

Authority: research/scientific-governance only. No market, portfolio, model-weight or automatic-promotion authority.

FORECAST SKILL = UNPROVEN.
