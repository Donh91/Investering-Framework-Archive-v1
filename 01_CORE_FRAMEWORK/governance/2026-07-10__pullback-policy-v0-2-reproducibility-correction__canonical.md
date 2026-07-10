# Pullback Policy v0.2 — Reproducibility Correction

**Dato:** 2026-07-10  
**Status:** CANONICAL_GOVERNANCE_CORRECTION  
**Område:** pullback classification / action permissions / reproducibility  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Related folders:** `02_DATA_PING/`, `04_MARKET_LEARNING/stress_flush/`  
**Depends on:** DATA PING Hybrid v0.5.1; active gate registry; GPT-5.6 Fresh Eyes Audit Implementation

---

## Decision

```text
PULLBACK_POLICY_V0_2_STATUS: GUIDANCE_ONLY
MECHANICAL_CLASSIFICATION_AUTHORITY: SUSPENDED_UNTIL_SPEC_COMPLETE
PORTFOLIO_ACTION_AUTHORITY_FROM_QUALITATIVE_LABEL_ALONE: FORBIDDEN
```

The current qualitative sequence remains useful as human guidance:

```text
Mild → observe
Moderate → hold quality
Large → review risk
Extreme → defense first
```

It is not sufficiently reproducible to act as a deterministic policy because exact drawdown bands, measurement anchors and hard moderate-to-large triggers are not frozen in the canonical source reviewed by the audit.

---

## What remains active

This correction does not invalidate:

- framework-owned active price gates;
- source-backed event paths;
- EDGE_STATE and ALERT_STATUS;
- mandatory downgrade checks;
- framework-approved trim, no-buy or rebuy decisions;
- position-specific weakness review;
- the current pullback edge-event ledger.

These remain governed by their own canonical protocols.

---

## What is blocked

Until a complete specification exists, DATA PING and main framework must not treat `Mild`, `Moderate`, `Large` or `Extreme` as mechanically derived unless the output includes:

```yaml
measurement_asset:
reference_anchor:
reference_time:
drawdown_method:
drawdown_value:
volatility_adjustment:
classification_band_source:
hard_trigger_count:
hard_trigger_definitions:
source_quality:
framework_acceptance:
```

A qualitative pullback label alone may not:

- trigger `TRIM_A_BID`;
- unlock or lock rebuy;
- force mid-cap reduction;
- classify recovery failure;
- create a calibration success/failure row.

---

## Required future specification

A reproducible version must define:

1. asset-specific drawdown bands;
2. reference point and reset rule;
3. intraday versus close treatment;
4. volatility normalization, if any;
5. the exact list of hard triggers;
6. trigger count required for mid-cap `REDUCE`;
7. position-specific override rules;
8. missing-data behavior;
9. false-positive and false-negative outcome rows;
10. kill criteria.

Thresholds must be source-backed, replay-derived or explicitly labeled forward-test candidates.

No numeric bands are invented by this correction.

---

## Standing action rule

```text
STABILIZATION_IS_NOT_RECOVERY
RECOVERY_IS_NOT_ROTATION
FLOW_WARNING_IS_URGENCY_NOT_AUTOMATIC_TRIM
MID_CAP_DEFAULT_IN_UNSPECIFIED_MODERATE_PULLBACK: HOLD_QUALITY / REVIEW_POSITION_SPECIFIC_WEAKNESS
```
