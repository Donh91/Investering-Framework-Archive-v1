# Forecast Skill Preregistration v1.3.1

**Date:** 2026-09-03  
**Status:** CANONICAL_PREREGISTRATION_PENDING_MERGE  
**Area:** forecast accountability / confirmatory prospective skill inference  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/forecast_skill_preregistration/`  
**Supersedes for operational study semantics:** `FORECAST_SKILL_PREREGISTRATION_v1.3`  
**Depends on:** `FORECAST_SKILL_PREREGISTRATION_v1.3.zip` SHA-256 `d4f3e8c0f27a40bbfac0af41ab57a9752586becd871307b2f18cb061f9a8ee8d`

## Scientific status

```text
FORECAST SKILL STATUS: UNPROVEN
CONFIRMATORY STUDY: NOT_STARTED_SCIENTIFIC_FIREWALL
PRIMARY EVIDENCE CLASS: API_AGENT_OWNER_RATIFIED_PROSPECTIVE_v1
PRIMARY FORECAST FAMILY: F1_DIRECTIONAL_ONLY
PORTFOLIO AUTHORITY: NONE
MODEL-WEIGHT AUTHORITY: NONE
AUTOMATIC PROMOTION: FORBIDDEN
```

No pre-v1.3.1 candidate, forecast, replay, experiment, shadow record, historical reconstruction or calibration row can enter the confirmatory cohort.

The methodology cutoff remains:

```text
2026-09-02T18:54:03Z
```

No prospective F1 outcome was used to select this procedure. The two natural post-hardening candidates created on 2026-09-02 remain outside the confirmatory cohort because the study firewall was not yet activated.

## Source package acceptance

The Claude v1.3 bundle is accepted as the immutable statistical-method evidence package, subject only to the two narrowing corrections below.

Independent acceptance audit verified:

```text
external_zip_sha256: d4f3e8c0f27a40bbfac0af41ab57a9752586becd871307b2f18cb061f9a8ee8d
manifest_entries_verified: 47/47
bundled_verifier_checks: 22/22
embedded_original_v1_1_engine_sha256: df263ac23fb6ff28594590b3f6cb1110a03adaeac211e8267c1add88dca871db
embedded_original_v1_1_price_history_sha256: e2871550e90c154c6847ba720c2249fa1f0fda787c90a68d70f0c761ee09a3f1
sealed_validation_populations: 12
sealed_trials_per_population: 5200
sealed_trials_total: 62400
selected_candidate: B_CALENDAR_BATCH_MEANS_T
selected_block_length_calendar_days: 28
one_sided_alpha: 0.025
```

The sealed validation PASS means `PASS_UNDER_FROZEN_SIMULATION_VALIDATION_CRITERION`. It is not a theorem that the true rejection probability equals or is below 0.025 in every possible population.

## Binding correction 1 — the 240-day quantity

The v1.3 prose and JSON label the frozen `span_days=240` as 240 days on the OUTCOME_DUE axis. The simulation code does not implement that definition.

The load-bearing generators create forecast opportunities over exactly 240 consecutive **freeze/accrual calendar days** and only afterwards transform each admitted forecast to:

```text
outcome_due_day = freeze_day + horizon_days
```

Therefore the only semantics actually sealed-validated are:

```text
FREEZE_ACCRUAL_WINDOW_DAYS = 240
```

The confirmatory cohort must use one fixed UTC window:

```text
COHORT_START_UTC = first 00:00:00Z strictly after BOTH:
  1. this preregistration is merged and read back on main; and
  2. STUDY_ADMISSION_LEDGER_v1 plus OUTCOME_BLIND_TECHNICAL_REVALIDATION are merged, CI-verified and read back on main.

COHORT_END_UTC_EXCLUSIVE = COHORT_START_UTC + 240 calendar days
```

The activation receipt must freeze both timestamps before any cohort row is admitted.

Only F1 forecasts with `frozen_at_utc` in `[COHORT_START_UTC, COHORT_END_UTC_EXCLUSIVE)` may enter the cohort.

After the accrual window closes, no new row may be added to this cohort. The system waits only for already-admitted forecasts to reach their frozen due times and technical revalidation. The OUTCOME_DUE calendar series then runs from the first admitted due day through the last admitted due day; because horizons are 1–7 days, this series is allowed to extend beyond the 240-day freeze/accrual window. It must not be truncated to 240 due-days.

Failure of an accrual gate after the fixed window closes produces:

```text
INSUFFICIENT_PROSPECTIVE_EVIDENCE
```

The window may not be extended, rolled or restarted after inspecting outcomes. Any successor cohort requires a new prospectively frozen cohort contract.

## Binding correction 2 — missing outcomes

V1.3 sealed Type-I validation was executed at:

```text
OUTCOME_UNAVAILABLE_SHARE = 0.0
```

V1.3 carried a 10% operational cap forward without revalidating the selected batch-means t procedure and justified it by claiming `HIT:=0` imputation is monotonically conservative.

That monotonicity does not hold generally for a t statistic because lowering an observation can reduce the numerator while reducing the estimated standard error by a larger proportion. A bounded counterexample used nine block values:

```text
before: mean=0.1687667, SE=0.0752336, t=2.24323
lower one high block by 0.10:
        mean=0.1576556, SE=0.0671244, t=2.34871
```

The point estimate falls while the test statistic rises across the approximate df=8 one-sided 0.025 critical region. Missing-to-zero therefore cannot be assumed to preserve Type-I control for the selected procedure.

The confirmatory contract is narrowed to the domain actually sealed-validated:

```text
MAX_OUTCOME_UNAVAILABLE_SHARE = 0.0
```

If any admitted F1 row lacks its preregistered settlement-eligible outcome after outcome-blind technical revalidation, the confirmatory test is not run and the cohort verdict is:

```text
INSUFFICIENT_PROSPECTIVE_EVIDENCE
```

A future nonzero missingness tolerance requires a new prospectively frozen validation before it can be used.

## Frozen population and admission

A row is confirmatory-eligible only when all are true before outcome observation:

```text
evidence_class == API_AGENT_OWNER_RATIFIED_PROSPECTIVE_v1
forecast_family == F1_DIRECTIONAL
candidate source temporal provenance == PASS
owner ratification == prospective, outcome-blind and within current SLA
forecast immutable freeze == PASS
baseline == freshest eligible immutable archived capture at/before owner decision
baseline age <= current ratification contract maximum
settlement contract == exact frozen target-time owner contract
study admission record exists and is content/hash bound to the frozen forecast
study admission was written before the outcome became observable
frozen_at_utc is inside the fixed 240-day cohort window
historical replay == false
experimental/shadow evidence == excluded
```

Admission is frozen at forecast freeze. At outcome due time only an `OUTCOME_BLIND_TECHNICAL_REVALIDATION` may confirm that the already-admitted row still satisfies preregistered technical conditions. It may not decide de novo whether a forecast belongs to the study based on result, price path or ambient post-freeze market information.

## Primary endpoint and baseline

The primary endpoint remains the v1.3 F1 directional endpoint versus `B1_CLIMATOLOGY`.

For each admitted row `r`:

```text
d_r = HIT_r - p_clim_r
```

`B1_CLIMATOLOGY` must use only historical event windows whose entire realized horizon ends strictly before the current forecast freeze. The frozen 180-day trailing origin-window and minimum-event rules in v1.3 remain binding.

No probabilistic calibration claim is created. `PROBABILISTIC_CALIBRATION = NOT_TESTABLE` remains binding unless ex-ante probabilities are prospectively frozen under a separate contract.

## Primary time index

```text
PRIMARY_TIME_INDEX = OUTCOME_DUE_CALENDAR_DAY
outcome_due_day = freeze_day + horizon_days
```

Build one regular UTC calendar index from the first admitted outcome-due day to the last admitted outcome-due day. Empty calendar days remain explicit positions, occupy block footprint and contribute neither evidence nor zero.

Forecasts with different freeze days/horizons but the same outcome-due calendar day share the same primary daily cluster.

## Frozen confirmatory inference

The only confirmatory procedure is:

```text
candidate: B_CALENDAR_BATCH_MEANS_T
calendar_block_length: 28 days
block_tiling_origin: first outcome-due calendar position in the cohort series
point_estimate: Theta_hat = sum(d_r) / N across resolved admitted F1 rows
within-day aggregation: mean d_r for rows sharing an outcome-due calendar day
variance: non-overlapping calendar-block batch-means / cluster-robust CR0 variance
empty blocks: no evidence; calendar footprint retained; D_g=0 blocks excluded from G
reference_distribution: Student-t
reference_df: G - 1
alpha: 0.025 one-sided
resampling_in_confirmatory_decision: false
number_of_confirmatory_tests: exactly one
```

No block length, critical value, baseline, endpoint, horizon handling, evidence class, missingness rule or concentration gate may be changed after cohort activation.

## Binding accrual and concentration gates

The following are checked only after the fixed 240-day freeze/accrual window closes and every admitted row has reached due-time technical revalidation:

```yaml
freeze_accrual_window_days: 240
min_admitted_F1_rows: 200
min_UNIQUE_OUTCOME_DUE_DAYS: 85
min_UNIQUE_FREEZE_DAYS: 50
max_share_rows_on_any_OUTCOME_DUE_calendar_day: 0.06
max_share_rows_in_any_28_calendar_day_block: 0.23
max_OUTCOME_UNAVAILABLE_share: 0.0
```

`CALENDAR_BLOCKS_CONTAINING_ADMITTED_FORECASTS` remains a reported design diagnostic and the source of Student-t degrees of freedom. V1.3 sealed validation covered low-cadence populations with variable occupied-block count, so v1.3.1 does not invent an additional post-hoc occupied-block threshold.

If any gate fails, no confirmatory p-value is used for a skill claim.

## Power interpretation

V1.3 power work was run only after sealed Type-I acceptance. Its empirical MDE80 estimate of approximately +11.3 percentage points is descriptive planning context for the frozen design, not a success threshold and not evidence of current skill.

A negative confirmatory result under this relatively low-powered design means:

```text
ADEQUATE_SAMPLE_NO_DEMONSTRATED_EDGE
```

when all gates are met. It must not be translated into proof of no edge.

## Verdict vocabulary

Allowed top-level scientific states remain conservative:

```text
INSUFFICIENT_PROSPECTIVE_EVIDENCE
ADEQUATE_SAMPLE_NO_DEMONSTRATED_EDGE
REGIME_SPECIFIC_SIGNAL
WEAK_PROSPECTIVE_EDGE
REPLICATED_PROSPECTIVE_SKILL
PROBABILISTIC_CALIBRATION_NOT_TESTABLE
```

No `WEAK_PROSPECTIVE_EDGE` or stronger language may be emitted from engineering success, raw hit rate, historical replay, a single asset/regime cluster, or before the frozen confirmatory analysis.

`REPLICATED_PROSPECTIVE_SKILL` additionally requires the repository's independent replication gate; the confirmatory test alone is insufficient.

## Implementation firewall

Before the cohort can activate, current main must contain and CI/readback verify:

1. this preregistration and its active-test registration;
2. `STUDY_ADMISSION_LEDGER_v1` with append-only/content-bound row admission at freeze;
3. `OUTCOME_BLIND_TECHNICAL_REVALIDATION` before any confirmatory outcome is read;
4. an implementation of the frozen `B_CALENDAR_BATCH_MEANS_T` analysis that consumes only the admitted cohort and cannot run before the fixed window plus maturity/gates are complete;
5. explicit separation from legacy, historical replay and `AUTOMATED_SCIENTIFIC_EXPERIMENT` evidence;
6. an activation receipt freezing `COHORT_START_UTC` and `COHORT_END_UTC_EXCLUSIVE` before first admission.

Until all six exist:

```text
CONFIRMATORY_STUDY: NOT_STARTED_SCIENTIFIC_FIREWALL
FORECAST SKILL: UNPROVEN
```

## Final scientific gate

After implementation is merged and read back, freeze the activation receipt at the deterministic next UTC boundary, accrue only eligible new F1 forecasts for the fixed 240-day window, wait for every admitted row to become technically revalidated at due time, enforce every accrual/concentration/missingness gate, and then execute `B_CALENDAR_BATCH_MEANS_T` exactly once.

FORECAST SKILL STATUS: UNPROVEN
