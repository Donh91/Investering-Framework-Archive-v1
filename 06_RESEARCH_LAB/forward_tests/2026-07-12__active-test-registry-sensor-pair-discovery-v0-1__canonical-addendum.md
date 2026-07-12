# Active Test Registry — Sensor Pair Discovery Lab v0.1 Addendum

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** prospective sensor attribution / DATA PING-derived shadow tests  
**Depends on:** Active Test Registry canonical owner, Sensor Audit v1.1 addendum, Daily Sensor Pair Discovery Lab v0.1

## T7 — Sensor Pair Discovery Lab

```yaml
test_id: SENSOR_PAIR_DISCOVERY_LAB_V0_1
status: ACTIVE_SHADOW_PILOT
source_authority:
  primary: LATEST_COMPLETE_USER_SUPPLIED_ANALYSIS_IN_HIGHEST_USED_DATA_PING_VERSION
  fallback: THREAD_DERIVED_HANDOFF_MAX_36H
  independent_market_data_fetch: FORBIDDEN
  custom_gpt_scheduled_execution: NOT_SUPPORTED_NOT_CLAIMED
frozen_pairs: 8
horizons:
  - 24h
  - 72h
  - 7d
required_controls:
  - SENSOR_A_ONLY
  - SENSOR_B_ONLY
  - PRICE_REGIME_BASELINE
  - ALWAYS_WAIT
  - DETERMINISTIC_PLACEBO
  - CURRENT_FRAMEWORK_INTERPRETATION
initial_valid_rows: 0
initial_mature_rows: 0
initial_independent_event_windows: 0
coverage_status: INSUFFICIENT_SAMPLE
promotion_authority: NONE
portfolio_authority: ZERO
```

## Source selection rule

A newer version number is selected only when that DATA PING thread has actually received a complete user-supplied analysis. Within the highest used version, the latest complete analysis timestamp wins. Later casual comments do not supersede the source analysis.

## Eligibility

A pair/horizon row is eligible only when both pair sensors and all required source metadata are present in the same frozen DATA PING source message. Missing data is not negative evidence. Ineligible pairs do not block eligible pairs from the same source.

## Outcome and independence

Outcomes are populated only from later source-backed DATA PING analyses after 24h, 72h or 7d. Raw overlapping rows and effective independent event windows must be reported separately.

## Governance boundary

```text
retrospective_rows_promoted: 0
rule_promotion: NONE
automatic_weight_change: FORBIDDEN
automatic_threshold_change: FORBIDDEN
market_call: NONE
portfolio_action: NONE
```

The test exists to falsify and rank sensor pairs. It does not create a new live voting engine.