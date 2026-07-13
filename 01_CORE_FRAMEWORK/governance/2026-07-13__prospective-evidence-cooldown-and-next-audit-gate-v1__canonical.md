# Prospective Evidence Cooldown and Next Audit Gate v1

**Dato:** 2026-07-13  
**Status:** CANONICAL  
**Område:** research cadence / evidence maturity / next major audit  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`

## Decision

```text
NEW_BROAD_SENSOR_ENGINE: FORBIDDEN
LARGE_PARAMETER_BACKTEST: FORBIDDEN
PROSPECTIVE_ROW_PRODUCTION: ACTIVE
earliest major decision-value review: 2026-08-10
hard-stop evidence review: 2026-09-07
automatic promotion: NO
```

This contract implements the active new-engine freeze and prevents repeated mining of the same historical datasets.

## Existing lanes that must produce rows

- C2 Pullback Edge rows with exact source and operational-availability timestamps;
- Daily Sensor Pair Lab 24h, 72h and 7d outcomes;
- M3 material-decision rows;
- Rotation Survival and Graduated Deployment forward rows;
- FRLP scored weekly rows;
- TechDev new claim and revision rows frozen before outcomes.

No new duplicate test, engine or score is created.

## Early readiness gate

A major decision-value audit may run on or after 2026-08-10 only when:

```yaml
independent_event_windows_minimum: 3
review_ready_existing_lanes_minimum: 2
retrospective_rows_counted: 0
source_lineage_complete: YES
```

Existing lane gates remain authoritative, including:

```text
M3: >=30 eligible rows, >=3 windows, <=50% largest-window concentration, >=3 source families
FRLP: >=8 scored forward rows
Sensor Pair Lab: candidate review at >=20 mature rows and >=3 independent windows
C2: prospective rows across >=3 independent pullback events
Rotation/Deployment: independent breadth-complete real/fake attempts
```

## Hard-stop review

On or after 2026-09-07, run an evidence-sufficiency and machinery-drift audit even if samples remain insufficient. The hard stop does not weaken row gates and does not force an edge conclusion.

## Review output

The gate review must separately report:

```text
row_validity
coverage_readiness
independent_event_count
source_family_count
largest_window_concentration
behavior_changed
promotion_status
```

Passing coverage permits governance review only.

No market call. No portfolio action. No automatic threshold or rule promotion.
