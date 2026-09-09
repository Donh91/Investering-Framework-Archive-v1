# BlockHorizon Astra Historical Research Protocol v1

**Dato:** 2026-09-08  
**Updated:** 2026-09-09  
**Status:** RESEARCH_PROTOCOL / INPUTS_RECONCILED / NO_PROMOTION_AUTHORITY  
**Område:** historical replay / simulation / feature survival / Astra research  
**Primary folder:** `06_RESEARCH_LAB/blockhorizon_source_candidate_v1/`

## Mission

Use BlockHorizon historical data to try to falsify, simplify and improve the existing framework. Do not search for pretty historical fits.

## Current input authority and read order

Before any BlockHorizon research run, read in this order:

1. `SOURCE_CONTRACT_v1.json`
2. `CURRENT_PRIVATE_BINDING.json`
3. `METRIC_REGISTRY_v2.json`
4. this protocol
5. authorized private archive README
6. authorized private reconciliation receipt:
   `receipts/BH01_BLOCKHORIZON_MANUAL_EXPORT_HISTORICAL_V1/2026/09/09/2026-09-09__blockhorizon_combo_reconciliation_receipt_v1.json`
7. exact private raw artifacts only after binding their immutable path, bytes and SHA-256.

`METRIC_REGISTRY_v1.json` and `SEED_INVENTORY_METADATA_v1.json` remain historical seed-state records. They must not override the current v2 registry or current private binding.

Current readiness is:

```text
READY_FOR_SCHEMA_PROVENANCE_REDUNDANCY_AND_HYPOTHESIS_DESIGN
```

Full completion of every BlockHorizon age-band family is not required to begin research preparation. Missing family members remain explicit and must never be inferred from sibling metrics.

## Current execution gate

Reconciliation does not itself activate unrestricted historical outcome scoring.

Permitted immediately under the current source-health/research-preparation state:

- schema and metric-definition audit;
- provenance and revision-risk audit;
- missingness and coverage classification;
- duplicate and overlap mapping;
- family clustering and redundancy-test design;
- point-in-time feasibility classification;
- pre-registration of hypotheses, outcomes, baselines, regimes and kill criteria;
- preparation of walk-forward and leave-one-cycle-out specifications.

Any outcome scoring, retrospective edge claim, threshold search, PnL simulation or promotion attempt must also satisfy the framework's existing research/adjudication activation gates. Nothing in this source package overrides those gates.

## Required run header

Every run must freeze:

```yaml
source_contract_id:
private_binding_commit:
private_receipt_path:
retrieval_snapshot_or_local_bundle_hash:
metric_registry_version:
feature_list:
transform_definitions:
training_period:
validation_period:
holdout_period:
regime_splits:
outcome_definitions:
missing_data_policy:
revision_policy:
information_time_mode: RETROSPECTIVE_DESCRIPTIVE | CONTEMPORANEOUS_REPLAY | PROSPECTIVE_FORWARD
```

## Research order

1. Data integrity and semantics.
2. Mechanical baseline.
3. Single-feature behavior.
4. Redundancy and family clustering.
5. Incremental value after simpler features.
6. Regime robustness.
7. Negative controls and falsification.
8. Only then multi-feature simulation.

## Default outcome set

Prefer continuous, auditable outcomes:

```text
forward_return_7d / 30d / 90d / 180d
forward_max_drawdown_30d / 90d / 180d
forward_max_runup_30d / 90d / 180d
time_to_new_high
time_to_10pct_drawdown
time_to_20pct_drawdown
```

Outcome windows are examples for research design, not framework thresholds.

## Leakage prohibitions

- no future observations in a feature;
- no full-history z-score used as a historical feature;
- no centered smoothing;
- no post-event metric revision silently substituted for what was available then;
- no model refit date ignored in contemporaneous replay;
- no selecting event boundaries after inspecting the answer;
- no using final-holdout results to retune the candidate that is reported on that same holdout.

### Explicit PlanB future-grid guardrail

The private file `planb_moving_averages_2026-09-09T06-38-17.csv` contains 849 timestamps after its 2026-09-09 retrieval date, extending to 2029-01-05. These rows are model/projection-grid material pending definition review.

They must never be treated as observed future market actuals, realized outcomes or contemporaneously known historical evidence. Any PlanB feature must be clipped to information available at the simulated decision time and must preserve the model/refit date.

## Point-in-time classification

Every candidate series must receive one of these before causal or predictive interpretation:

```text
PIT_VERIFIED
PIT_APPROXIMATE
RETROSPECTIVE_RECONSTRUCTION_ONLY
MODEL_REFIT_HINDSIGHT_AWARE
SEMANTICS_OR_REVISION_STATE_UNVERIFIED
```

A full historical CSV downloaded in 2026 is not evidence that the same historical value or methodology was available at the historical timestamp.

## Cycle and regime robustness

When enough observations exist and scoring is governed/activated, report at minimum:

- pooled historical result;
- leave-one-cycle-out result;
- pre-ETF result;
- ETF-era result;
- sensitivity to reasonable transform/window choices;
- failure cases.

A signal that works only in one historical cycle is a regime-specific observation, not durable edge.

## Sensor survival test

For every candidate metric or family ask:

```text
Does it add information beyond price and realized-price state?
Does it add information beyond aggregate MVRV/NUPL?
Does STH/LTH decomposition add incremental value?
Does realized spending behavior add value beyond unrealized state?
Does age structure add lead-time or just explain the move after it happened?
Does the proprietary metric survive after simple baselines and complexity tax?
```

Possible outcomes:

```text
KEEP_FOR_RESEARCH
REDUNDANT_WITH_SIMPLER_FEATURE
REGIME_SPECIFIC
HINDSIGHT_CONTAMINATED
SEMANTICS_UNVERIFIED
INSUFFICIENT_SAMPLE
FORWARD_TEST_CANDIDATE
REJECT
```

None of these automatically changes framework authority.

## Additional collection rule

Do not collect more BlockHorizon charts merely because they exist. First run the governed schema/provenance/redundancy and incremental-value design against the current archive. Request additional series only when a specific unresolved hypothesis or family-symmetry test has positive information value.

The current v2 registry retains 17 missing core family bands for optional completeness. They are not blockers for research preparation.

## Astra expectation

Astra should be rewarded for deleting weak complexity. The preferred final report contains:

```text
what survived
what failed
what was redundant
what was hindsight-contaminated
what remains untestable
what should be tested prospectively next
```
