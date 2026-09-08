# BlockHorizon Astra Historical Research Protocol v1

**Dato:** 2026-09-08  
**Status:** RESEARCH_PROTOCOL / NO_PROMOTION_AUTHORITY  
**Område:** historical replay / simulation / feature survival / Astra research  
**Primary folder:** `06_RESEARCH_LAB/blockhorizon_source_candidate_v1/`

## Mission

Use BlockHorizon historical data to try to falsify, simplify and improve the existing framework. Do not search for pretty historical fits.

## Required run header

Every run must freeze:

```yaml
source_contract_id:
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

## Cycle and regime robustness

When enough observations exist, report at minimum:

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
