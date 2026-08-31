# T2 Sminston BTC Challenger - Forward Ledger

**Created:** 2026-08-31  
**Status:** OPERATIONAL_APPEND_ONLY  
**Parent test:** `GATE_BTC_PARTIAL_FT_1`  
**Candidate:** `SMINSTON_BTC_CHALLENGER_V0_1`  
**Authority:** SHADOW_ONLY

## 1. Ledger contract

This ledger is append-only.

A source row is not automatically an evidence row.

A valid T2 divergence row requires a same-cutoff frozen canonical framework action plus a frozen experimental Sminston action that differs from it.

Rows created for initialization, source QA, same-action observations or retrospective replay are never counted as forward decision evidence.

## 2. Row schema

```yaml
row_id:
row_type: SOURCE_INITIALIZATION | FORWARD_SOURCE | VALID_DIVERGENCE | OUTCOME_UPDATE | QA
created_at_utc:
information_cutoff_utc:
source_snapshot_date:
source_run_id:
canonical_framework_binding:
canonical_framework_action:
canonical_framework_state:

brk_price_close:
q05_formula:
q05_value:
q05_distance_pct:
structural_permission:

mvrv_raw:
mvrv_z_author:
mvrv_z_condition:
cvdd_author:
cvdd_ratio_author:
cvdd_condition:
lth_supply_in_loss_pct:
lth_expanding_percentile:
lth_condition:
bottom_quality_true_count:
bottom_quality_permission:

cuau_residual:
pmi_residual:
modem:
macro_permission:

full_package_permission:
experimental_action:
position_fraction_assumed:
actual_decision_divergence:
evidence_eligibility:
blocked_reason:

episode_id:
episode_state:
horizon_24h_due:
horizon_72h_due:
horizon_7d_due:
horizon_14d_due:
horizon_30d_due:

btc_return_24h:
btc_return_72h:
btc_return_7d:
btc_return_14d:
btc_return_30d:
mae_7d:
mfe_7d:
mae_30d:
mfe_30d:
portfolio_divergence_30d:
opportunity_cost_recovered:
false_permission_cost:
classification:
source_integrity_status:
notes:
```

## 3. Initialization row

### SM-T2-INIT-20260831-01

```yaml
row_id: SM-T2-INIT-20260831-01
row_type: SOURCE_INITIALIZATION
created_at_utc: 2026-08-31T21:10:02Z
information_cutoff_utc: 2026-08-31T21:10:02Z
source_snapshot_date: 2026-08-31
source_run_id: SMINSTON_SOURCE_AUDIT_20260831
canonical_framework_binding: NOT_BOUND_TO_FRESH_SAME_CUTOFF_OWNER_STATE
canonical_framework_action: UNBOUND
canonical_framework_state: UNBOUND

brk_price_close: 78643.30
q05_formula: "2.952e-18 * d^5.8837; d=days_since_2009-01-03"
q05_value: 76564.36
q05_distance_pct: 2.7153
structural_permission: BTC_PARTIAL_10

mvrv_raw: 1.4825645229631894
mvrv_z_author: 0.81
mvrv_z_condition: FALSE
cvdd_author: 47511
cvdd_ratio_author: 1.63
cvdd_condition: FALSE
lth_supply_in_loss_pct: 34.12221242483711
lth_expanding_percentile: NOT_COMPUTED_POINT_IN_TIME
lth_condition: UNKNOWN
bottom_quality_true_count: 0_OF_2_KNOWN
bottom_quality_permission: WAIT

cuau_residual: DATA_BLOCKED
pmi_residual: DATA_BLOCKED
modem: DATA_BLOCKED
macro_permission: DATA_BLOCKED

full_package_permission: DATA_BLOCKED
experimental_action: STRUCTURAL_SUBTEST_WOULD_GRANT_BTC_PARTIAL_10
position_fraction_assumed: 0.10_FOR_STRUCTURAL_SUBTEST
actual_decision_divergence: NOT_SCOREABLE_BASELINE_UNBOUND
evidence_eligibility: INITIALIZATION_ONLY
blocked_reason: NO_FRESH_CANONICAL_FRAMEWORK_ACTION_BOUND_AT_SAME_INFORMATION_CUTOFF

episode_id: NOT_OPENED
sample_state: INITIALIZATION
horizon_24h_due: NOT_APPLICABLE
horizon_72h_due: NOT_APPLICABLE
horizon_7d_due: NOT_APPLICABLE
horizon_14d_due: NOT_APPLICABLE
horizon_30d_due: NOT_APPLICABLE

classification: SOURCE_INITIALIZATION_NOT_FORWARD_EVIDENCE
source_integrity_status: PASS_WITH_PARTIAL_DATA_BLOCKS
notes: >-
  The reproducible structural subtest is within the preregistered +5% q05 proximity band.
  Bottom-quality does not confirm because MVRV Z and CVDD proximity are both false; LTH point-in-time expanding percentile remains uncomputed.
  Macro-relative and full-package decisions are data-blocked.
  No T2 evidence row is created because a fresh canonical benchmark action was not bound at the same cutoff.
```

## 4. Initialization source bindings

```yaml
q05_source:
  url: https://www.sminstonwith.com/retirement-guide
  class: REPRODUCIBLE_FORWARD_ONLY
  capture_date: 2026-08-31

brk_price_source:
  url: https://bitview.space/api/series/price_close/date
  series: price_close
  class: REPRODUCIBLE
  observation_date: 2026-08-31

mvrv_source:
  url: https://bitview.space/api/series/mvrv/date
  series: mvrv
  class: REPRODUCIBLE_RAW
  observation_date: 2026-08-31

mvrv_z_author_source:
  url: https://www.sminstonwith.com/chart/mvrv-zscore
  class: AUTHOR_DERIVED_WITH_REPRODUCIBLE_INPUTS
  capture_date: 2026-08-31

lth_loss_source:
  url: https://bitview.space/api/series/lth_supply_in_loss_share/date
  series: lth_supply_in_loss_share
  class: REPRODUCIBLE
  observation_date: 2026-08-31

cvdd_author_source:
  url: https://www.sminstonwith.com/chart/cvdd
  class: AUTHOR_DERIVED_WITH_REPRODUCIBLE_INPUTS
  capture_date: 2026-08-31
```

## 5. Source-verified initialization interpretation

The initialization snapshot contains a useful disagreement that must remain frozen rather than reconciled:

```text
Structural q05 subtest: BTC_PARTIAL_10
Bottom-quality family: WAIT
Macro-relative family: DATA_BLOCKED
Full package: DATA_BLOCKED
```

This disagreement is research information, not a portfolio recommendation.

The next row may become forward evidence only when a fresh canonical framework benchmark is frozen at the same information cutoff and an actual action divergence exists.

## 6. Outcome update rule

Outcome fields may be appended only after the exact frozen horizon matures.

No source input, action, threshold, formula, position fraction or horizon may be rewritten during outcome evaluation.
