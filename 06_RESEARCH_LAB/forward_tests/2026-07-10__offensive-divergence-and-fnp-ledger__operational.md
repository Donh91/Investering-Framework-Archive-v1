# Offensive Divergence and FNP Ledger

**Dato:** 2026-07-10  
**Status:** OPERATIONAL_APPEND_ONLY / NOT_CANONICAL_LEARNING  
**Område:** BTC partial / WAIT benchmark / FNP / opportunity cost  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** Active Test Registry; GPT-5.6 Fresh Eyes Audit Implementation

---

## Purpose

This ledger records actual decision divergence. It is not a theory file.

```text
WAIT
versus
GATE_BTC_PARTIAL
versus
GRADUATED_DEPLOYMENT_WHEN_DATA_COMPLETE
```

No row is valid unless the actions genuinely differ at the timestamp.

---

## Current status

```yaml
ledger_start: 2026-07-10
rows_total: 0_NEW_VALID_ROWS
valid_rows: 0
BTC_partial_status: ACTIVE_NEEDS_ROWS
graduated_alt_deployment_status: DATA_BLOCKED
FNP_status: ACTIVE_NEEDS_ROWS
canonical_learning_status: NONE
```

Initialization or schema rows do not count as valid evidence.

---

## Required divergence row

```yaml
row_id:
timestamp_utc:
source_run_id:
framework_state:
asset_tier:
benchmark_action_WAIT:
experimental_action_BTC_PARTIAL:
experimental_action_GRADUATED:
decision_divergence:
permission_reason:
blocking_reason:
required_data_complete:
entry_reference_price:
position_fraction_assumed:
frozen_horizon_24h:
frozen_horizon_72h:
frozen_horizon_7d:
max_favorable_excursion_pct:
max_adverse_excursion_pct:
return_at_horizon_pct:
benchmark_return_pct:
drawdown_pct:
opportunity_cost_pct:
false_permission_cost_pct:
correct_restraint_value_pct:
final_classification:
  GENUINE_FALSE_NEGATIVE
  CORRECT_RESTRAINT
  FALSE_PERMISSION
  NO_MEANINGFUL_DIVERGENCE
  DATA_INSUFFICIENT
source_lineage:
framework_acceptance:
```

---

## Frozen-horizon rule

Horizons must be fixed at row creation.

Do not choose the most flattering later interval.

```text
RETROSPECTIVE_HORIZON_SELECTION: FORBIDDEN
RETROSPECTIVE_ACTION_REWRITE: FORBIDDEN
```

---

## Graduated deployment block

No graduated alt-deployment row may be created as if valid while any critical field is missing:

```text
breadth
BTC.D
ETH/BTC
deployment
stablecoin transmission
alt proxy
fake-rotation density
```

When blocked, log only:

```yaml
status: DATA_BLOCKED
missing_fields:
decision_divergence: NOT_EVALUABLE
```

This does not count as a valid test row.

---

## Weekly summary contract

```yaml
rows_added_this_week:
valid_rows_total:
divergence_days_total:
BTC_partial_wins:
WAIT_wins:
false_permissions:
genuine_false_negatives:
correct_restraints:
median_opportunity_cost_pct:
median_drawdown_difference_pct:
missing_field_rate:
next_review:
```

No conclusion may be promoted until main framework reviews a sufficient series.
