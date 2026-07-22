# Sensor Relationship Learning Integration Receipt

**Dato:** 2026-07-22  
**Status:** IMPLEMENTATION_RECEIPT  
**PR:** `#120`  
**Område:** framework governance / shadow integration / archive control  
**Primary folder:** `changelog/`

## Purpose

Integrate the permanent learning from the closed-lab public-repo methods audit into the existing framework brain and archive without creating a new engine, runtime dependency or market-state authority.

## Updated canonical controls

```text
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
01_CORE_FRAMEWORK/architecture/2026-07-10__simplified-active-framework-map-and-crosswalk__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-10__rule-and-evidence-registry__canonical.md
06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md
```

## Existing learning anchors

```text
01_CORE_FRAMEWORK/governance/2026-07-22__sensor-relationship-and-incremental-value-standard__canonical.md
06_RESEARCH_LAB/audit_summaries/2026-07-22__public-repo-methods-closed-lab-audit__shadow.md
06_RESEARCH_LAB/forward_tests/2026-07-22__relationship-methods-closed-lab-results__historical-test.csv
00_ARCHIVE_CONTROL/2026-07-22__index-addendum-sensor-relationship-standard.md
```

## Integration decisions

1. The learning is a cross-cutting Shadow / Research Lab audit overlay, not an eighth framework layer.
2. DATA PING remains an unchanged truth-layer and does not calculate the mathematical audits inside each packet.
3. Relationship, survival, drift and compression diagnostics run on persisted source-traceable rows after collection.
4. `SENSOR_RELATIONSHIP_INCREMENTAL_VALUE` is registered as active governance with canonical sensor rows still required.
5. T4 Pullback Edge is repaired with event age, state survival and right-censoring fields.
6. T6 Rotation Survival is repaired with `TIME_IN_STATE`, axis-survival, redundancy, incremental value and delay-cost fields.
7. T8 Multi-Ping Aggregation is repaired with dependency, redundancy, unique-information and delay-cost fields.
8. No new test ID is created during the active new-engine freeze.
9. Historical proxy results do not promote coefficients, thresholds or live sensor weights.
10. Preferred simplification remains one primary sensor, one optional validation sensor and audit-only supporting fields when redundancy is demonstrated.

## Authority guards

```yaml
new_engine_created: false
new_test_created: false
runtime_changed: false
data_ping_contract_changed: false
market_state_changed: false
gates_changed: false
rebuy_or_deployment_changed: false
portfolio_action_changed: false
numeric_threshold_promoted: false
existing_tests_repaired: [T4, T6, T8]
permanent_methodology_integrated: true
```

## Separate reconciliation boundary

The archive currently names DATA PING V4 as the active operational feed while project development contains newer V6 work. This integration does not infer or change the active runtime version. Issue `#119` owns the separate runtime-versus-archive reconciliation and must identify the latest explicitly ratified operational state before any archive anchor is changed.

## Core receipt statement

```text
Do not count aligned sensors as independent confirmation.
Measure unique value, redundancy, synergy, survival and regime stability.
Route the learning through existing ledgers, registries and governance.
Do not expand runtime merely because an offline method is mathematically interesting.
```
