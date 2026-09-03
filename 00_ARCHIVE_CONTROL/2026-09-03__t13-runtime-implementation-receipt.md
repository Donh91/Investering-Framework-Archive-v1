# T13 Forecast Skill Runtime Implementation Receipt

Date: 2026-09-03
Status: PROPOSED_PENDING_PR_CI_MERGE_READBACK
Scientific status: FORECAST SKILL = UNPROVEN
Confirmatory cohort: NOT_STARTED_SCIENTIFIC_FIREWALL

This branch implements the preregistered T13 runtime without changing the sealed statistical method.

Binding scientific authorities:
- `FORECAST_SKILL_PREREGISTRATION_v1_3_1`
- `FORECAST_SKILL_PREREGISTRATION_v1_3_2_ERRATUM`
- primary evidence class `API_AGENT_OWNER_RATIFIED_PROSPECTIVE_v1`
- F1 directional only
- fixed 240-day freeze/accrual cohort
- B1 climatology frozen before outcome access
- equal-weight observed OUTCOME_DUE calendar-day endpoint
- non-overlapping 28-calendar-day batch-means CR0 variance
- Student-t reference with df=G-1 and one-sided alpha=0.025
- zero unavailable outcomes for the confirmatory decision

Runtime firewall order:
1. natural forecast candidate materialization and owner-ratified immutable freeze;
2. source-temporal provenance binding to the original candidate;
3. B1 historical source/climatology freeze with strict no-lookahead;
4. append-only `STUDY_ADMISSION_LEDGER_v1`;
5. due-time `OUTCOME_BLIND_TECHNICAL_REVALIDATION_v1`;
6. Git commit/push/readback of admission/revalidation state;
7. only after that durable barrier may settlement source access begin;
8. exact settlement/maturation continues through the existing production owner;
9. confirmatory owner stays outcome-blind until fixed-window closure, all due/revalidation/accrual gates and publication grace pass;
10. the final confirmatory test is written at most once.

The legacy calibration sidecar is narrowed to `SETTLEMENT_TIMING_ONLY`; settlement eligibility cannot establish forecast skill.

No cohort activation receipt is included in this implementation PR. Activation is a separate prospective governance action permitted only after this implementation is merged, CI/readback verified and recovery/Vault state is refreshed.

Authority: RESEARCH_ONLY_NO_PORTFOLIO_NO_MODEL_WEIGHT_NO_AUTOMATIC_PROMOTION.
