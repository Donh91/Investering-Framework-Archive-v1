# Forecast Skill T13 Scientific Runtime

This directory is the durable runtime surface for `FORECAST_SKILL_CONFIRMATORY_V1_3_1` under the v1.3.1 preregistration plus the binding v1.3.2 endpoint erratum.

Before cohort activation it contains no confirmatory admissions and grants no forecast-skill authority.

After a separately merged prospective activation receipt, runtime owners may create only the following bounded scientific surfaces:
- `COHORT_ACTIVATION_v1.json`
- `STUDY_ADMISSION_LEDGER_v1/`
- `ADMISSION_FAILURES/`
- `B1_SOURCE_RECEIPTS/`
- `B1_CLIMATOLOGY/`
- `TECHNICAL_REVALIDATION/`
- `LATEST_STUDY_STATUS.json`
- at most one `FINAL_CONFIRMATORY_RESULT_v1_3_2.json`

Production forecasting, portfolio decisions and model weighting remain outside this directory's authority.

`FORECAST SKILL = UNPROVEN` until the prospective study reaches its frozen scientific gate.
